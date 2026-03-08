"""
截图任务
"""
import os
import uuid
from datetime import datetime
from celery import shared_task
from flask import current_app

from app.extensions import db, celery
from app.models.website import Website


@celery.task(bind=True, name='capture_screenshot')
def capture_screenshot_task(self, url: str, website_id: int):
    """
    网站截图任务

    Args:
        self: Celery任务实例
        url: 网站URL
        website_id: 网站ID

    Returns:
        截图结果
    """
    try:
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Starting screenshot capture', 'url': url}
        )

        # 尝试使用Puppeteer截图
        result = _capture_with_puppeteer(url, website_id)

        if result.get('success'):
            # 更新网站截图信息
            _update_website_screenshots(website_id, result.get('screenshots', []))
            return {
                'status': 'SUCCESS',
                'screenshots': result.get('screenshots', [])
            }
        else:
            # Puppeteer失败，返回错误
            return {
                'status': 'FAILED',
                'error': result.get('error', 'Unknown error')
            }

    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        return {
            'status': 'FAILED',
            'error': str(e)
        }


def _capture_with_puppeteer(url: str, website_id: int):
    """
    使用Puppeteer截图

    注意：这需要安装Node.js和Puppeteer
    如果没有安装，将返回错误信息

    Args:
        url: 网站URL
        website_id: 网站ID

    Returns:
        截图结果
    """
    import subprocess
    import json

    try:
        # Puppeteer脚本路径
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'scripts',
            'screenshot.js'
        )

        # 检查脚本是否存在
        if not os.path.exists(script_path):
            return {
                'success': False,
                'error': 'Screenshot script not found. Please install Puppeteer and create scripts/screenshot.js'
            }

        # 生成输出文件名
        filename = f"{website_id}_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'screenshots',
            filename
        )

        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 执行Puppeteer脚本
        result = subprocess.run(
            ['node', script_path, url, output_path],
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
        )

        if result.returncode == 0:
            # 成功
            screenshot_url = f'/static/uploads/screenshots/{filename}'
            return {
                'success': True,
                'screenshots': [{
                    'url': screenshot_url,
                    'type': 'homepage',
                    'captured_at': datetime.utcnow().isoformat()
                }]
            }
        else:
            # 失败
            return {
                'success': False,
                'error': result.stderr or 'Puppeteer execution failed'
            }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Screenshot capture timeout'
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': 'Node.js not found. Please install Node.js to use Puppeteer screenshots'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def _update_website_screenshots(website_id: int, screenshots: list):
    """
    更新网站截图信息

    Args:
        website_id: 网站ID
        screenshots: 截图列表
    """
    from app import create_app

    app = create_app()
    with app.app_context():
        website = Website.query.get(website_id)
        if website:
            # 合并新旧截图
            existing = website.screenshots or []
            website.screenshots = existing + screenshots
            db.session.commit()


@celery.task(name='batch_screenshot')
def batch_screenshot_task(urls_and_ids: list):
    """
    批量截图任务

    Args:
        urls_and_ids: [(url, website_id), ...]

    Returns:
        批量截图结果
    """
    results = []
    for url, website_id in urls_and_ids:
        result = capture_screenshot_task.delay(url, website_id)
        results.append({
            'website_id': website_id,
            'task_id': result.id
        })

    return results


@celery.task(name='cleanup_old_screenshots')
def cleanup_old_screenshots_task(days: int = 90):
    """
    清理旧截图任务

    Args:
        days: 保留天数

    Returns:
        清理结果
    """
    from datetime import timedelta
    from app import create_app

    app = create_app()
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        websites = Website.query.filter(
            Website.updated_at < cutoff_date
        ).all()

        cleaned = 0
        for website in websites:
            if website.screenshots:
                # 保留最新的截图
                if len(website.screenshots) > 1:
                    old_screenshots = website.screenshots[:-1]

                    # 删除旧文件
                    for screenshot in old_screenshots:
                        try:
                            filepath = os.path.join(
                                current_app.config['UPLOAD_FOLDER'],
                                'screenshots',
                                screenshot['url'].split('/')[-1]
                            )
                            if os.path.exists(filepath):
                                os.remove(filepath)
                                cleaned += 1
                        except Exception:
                            pass

                    # 只保留最新的
                    website.screenshots = [website.screenshots[-1]]

        db.session.commit()

        return {
            'status': 'SUCCESS',
            'cleaned': cleaned
        }
