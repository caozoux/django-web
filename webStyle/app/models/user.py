"""
用户模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.base import BaseModel


class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # user, admin
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    # 关系
    favorites = db.relationship('Favorite', back_populates='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    view_history = db.relationship('ViewHistory', back_populates='user', lazy='dynamic',
                                   cascade='all, delete-orphan')
    websites = db.relationship('Website', back_populates='creator', lazy='dynamic')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """是否管理员"""
        return self.role == 'admin'

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        self.save()

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = super().to_dict()
        # 移除敏感信息
        if not include_sensitive:
            data.pop('password_hash', None)
        return data

    @staticmethod
    def get_by_username(username):
        """根据用户名获取用户"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        """根据邮箱获取用户"""
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return f'<User {self.username}>'
