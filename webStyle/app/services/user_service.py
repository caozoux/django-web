"""
用户业务逻辑服务
"""
from typing import Optional, Dict
from datetime import datetime
from app.extensions import db, cache
from app.models.user import User
from app.models.favorite import Favorite
from app.models.view_history import ViewHistory


class UserService:
    """用户业务逻辑服务"""

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create_user(data: Dict) -> User:
        """创建用户"""
        password = data.pop('password')
        user = User(**data)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def update_user(user_id: int, data: Dict) -> Optional[User]:
        """更新用户信息"""
        user = User.query.get(user_id)
        if not user:
            return None

        # 不能通过此方法更新密码
        data.pop('password', None)
        data.pop('password_hash', None)

        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        db.session.commit()
        return user

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = User.query.get(user_id)
        if not user:
            return False

        if not user.check_password(old_password):
            return False

        user.set_password(new_password)
        db.session.commit()
        return True

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password) and user.is_active:
            user.update_last_login()
            return user

        return None

    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """停用用户"""
        user = User.query.get(user_id)
        if not user:
            return False

        user.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def activate_user(user_id: int) -> bool:
        """激活用户"""
        user = User.query.get(user_id)
        if not user:
            return False

        user.is_active = True
        db.session.commit()
        return True

    @staticmethod
    def set_admin(user_id: int) -> bool:
        """设置为管理员"""
        user = User.query.get(user_id)
        if not user:
            return False

        user.role = 'admin'
        db.session.commit()
        return True

    @staticmethod
    def add_favorite(user_id: int, website_id: int) -> bool:
        """添加收藏"""
        # 检查是否已收藏
        if Favorite.is_favorited(user_id, website_id):
            return False

        favorite = Favorite(user_id=user_id, website_id=website_id)
        db.session.add(favorite)

        # 更新网站收藏数
        from app.models.website import Website
        website = Website.query.get(website_id)
        if website:
            website.increment_favorite()

        db.session.commit()
        return True

    @staticmethod
    def remove_favorite(user_id: int, website_id: int) -> bool:
        """取消收藏"""
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            website_id=website_id
        ).first()

        if not favorite:
            return False

        db.session.delete(favorite)

        # 更新网站收藏数
        from app.models.website import Website
        website = Website.query.get(website_id)
        if website:
            website.decrement_favorite()

        db.session.commit()
        return True

    @staticmethod
    def get_user_favorites(user_id: int, page: int = 1, per_page: int = 20) -> Dict:
        """获取用户收藏列表"""
        pagination = Favorite.get_user_favorites(user_id, page, per_page)

        websites = []
        for favorite in pagination.items:
            website = favorite.website
            if website:
                websites.append(website.to_dict())

        return {
            'websites': websites,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }

    @staticmethod
    def get_user_history(user_id: int, page: int = 1, per_page: int = 20) -> Dict:
        """获取用户浏览历史"""
        pagination = ViewHistory.get_user_history(user_id, page, per_page)

        websites = []
        for history in pagination.items:
            website = history.website
            if website:
                website_dict = website.to_dict()
                website_dict['viewed_at'] = history.viewed_at.isoformat()
                websites.append(website_dict)

        return {
            'websites': websites,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }

    @staticmethod
    def get_user_count() -> int:
        """获取用户总数"""
        return User.query.count()

    @staticmethod
    def get_active_user_count() -> int:
        """获取活跃用户数"""
        return User.query.filter_by(is_active=True).count()
