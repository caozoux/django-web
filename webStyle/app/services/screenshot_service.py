"""
截图业务逻辑服务
"""
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.tasks.screenshot import capture_screenshot_task


class ScreenshotService:
    """截图服务"""

    @staticmethod
    def capture_website_screenshots(url: str, website_id: int) -> Dict:
        """触发网站截图任务"""
        task = capture_screenshot_task.delay(url, website_id)
        return {
            'task_id': task.id,
            'status': 'pending',
            'website_id': website_id
        }

    @staticmethod
    def get_screenshot_status(task_id: str) -> Dict:
        """获取截图任务状态"""
        from app.extensions import celery
        result = celery.AsyncResult(task_id)

        response = {
            'task_id': task_id,
            'status': result.status,
        }

        if result.ready():
            response['result'] = result.result
        elif result.failed():
            response['error'] = str(result.result)

        return response

    @staticmethod
    def batch_capture(urls: List[str], website_ids: List[int]) -> List[Dict]:
        """批量截图"""
        tasks = []
        for url, website_id in zip(urls, website_ids):
            task = capture_screenshot_task.delay(url, website_id)
            tasks.append({
                'url': url,
                'website_id': website_id,
                'task_id': task.id
            })
        return tasks

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
        from app.models.website import Website
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
        from app.models.website import Website

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
