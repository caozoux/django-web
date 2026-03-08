"""
截图业务逻辑服务
"""
import os
import uuid
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.website import Website


class ScreenshotService:
    """截图服务"""

    @staticmethod
    def capture_website_screenshots(url: str, website_id: int) -> Dict:
        """同步执行网站截图"""
        try:
            result = _capture_with_puppeteer(url, website_id)

            if result.get('success'):
                # 更新网站截图信息
                _update_website_screenshots(website_id, result.get('screenshots', []))
                return {
                    'status': 'SUCCESS',
                    'screenshots': result.get('screenshots', []),
                    'website_id': website_id
                }
            else:
                return {
                    'status': 'FAILED',
                    'error': result.get('error', 'Unknown error'),
                    'website_id': website_id
                }
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'website_id': website_id
            }

    @staticmethod
    def get_screenshot_status(task_id: str) -> Dict:
        """获取截图任务状态（已弃用，保留兼容性）"""
        return {
            'task_id': task_id,
            'status': 'DEPRECATED',
            'message': 'Screenshot tasks are now synchronous'
        }

    @staticmethod
    def batch_capture(urls: List[str], website_ids: List[int]) -> List[Dict]:
        """批量截图（同步执行）"""
        results = []
        for url, website_id in zip(urls, website_ids):
            result = ScreenshotService.capture_website_screenshots(url, website_id)
            results.append({
                'url': url,
                'website_id': website_id,
                'status': result.get('status'),
                'screenshots': result.get('screenshots', []),
                'error': result.get('error')
            })
        return results

    @staticmethod
    def upload_screenshot(website_id: int, file, screenshot_type: str = 'homepage') -> Dict:
        """手动上传截图"""
        from werkzeug.utils import secure_filename

        # 检查文件类型
        if not ScreenshotService.allowed_file(file.filename):
            return {'error': 'File type not allowed'}

        # 生成文件名
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{website_id}_{screenshot_type}_{uuid.uuid4().hex[:8]}.{ext}"

        # 确保上传目录存在
        upload_folder = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'screenshots'
        )
        os.makedirs(upload_folder, exist_ok=True)

        # 保存文件
        filepath = os.path.join(upload_folder, new_filename)
        file.save(filepath)

        # 获取图片尺寸
        try:
            from PIL import Image
            with Image.open(filepath) as img:
                width, height = img.size
        except Exception:
            width, height = None, None

        # 更新网站截图信息
        website = Website.query.get(website_id)
        if website:
            screenshot_url = f'/static/uploads/screenshots/{new_filename}'
            website.add_screenshot(screenshot_url, screenshot_type, width, height)
            db.session.commit()

            return {
                'success': True,
                'url': screenshot_url,
                'type': screenshot_type,
                'width': width,
                'height': height
            }

        return {'error': 'Website not found'}

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """检查文件类型是否允许"""
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def delete_screenshot(website_id: int, screenshot_url: str) -> bool:
        """删除截图"""
        website = Website.query.get(website_id)
        if not website or not website.screenshots:
            return False

        # 从列表中移除
        original_length = len(website.screenshots)
        website.screenshots = [
            s for s in website.screenshots if s.get('url') != screenshot_url
        ]

        if len(website.screenshots) < original_length:
            # 删除文件
            try:
                # 截图URL格式: /static/uploads/screenshots/xxx.jpg
                filename = screenshot_url.split('/')[-1]
                filepath = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'screenshots',
                    filename
                )
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass

            db.session.commit()
            return True

        return False

    @staticmethod
    def get_screenshot_path(filename: str) -> Optional[str]:
        """获取截图文件路径"""
        filepath = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'screenshots',
            filename
        )
        if os.path.exists(filepath):
            return filepath
        return None

    @staticmethod
    def cleanup_old_screenshots(days: int = 90) -> Dict:
        """清理旧截图"""
        from datetime import timedelta

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
    website = Website.query.get(website_id)
    if website:
        # 合并新旧截图
        existing = website.screenshots or []
        website.screenshots = existing + screenshots
        db.session.commit()
