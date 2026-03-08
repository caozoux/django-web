"""
网站模型
"""
from app.extensions import db
from app.models.base import BaseModel


class Website(BaseModel):
    """网站模型"""
    __tablename__ = 'websites'

    name = db.Column(db.String(200), nullable=False, index=True)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    screenshots = db.Column(db.JSON, default=list)  # [{'url': '', 'type': 'homepage', 'width': 1920, 'height': 1080}]

    # 分类
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)

    # 筛选属性
    industry = db.Column(db.String(50), index=True)  # 电商、社交、工具、资讯等
    color_scheme = db.Column(db.String(50), index=True)  # cold, warm, neutral, dark
    layout_type = db.Column(db.String(50), index=True)  # centered, split, fullscreen

    # 统计数据
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    favorites = db.Column(db.Integer, default=0)

    # 状态
    status = db.Column(db.String(20), default='pending', index=True)  # pending, active, inactive

    # 创建者
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关系
    category = db.relationship('Category', back_populates='websites')
    tags = db.relationship('Tag', secondary='website_tags', backref=db.backref('websites', lazy='dynamic'))
    creator = db.relationship('User', back_populates='websites')
    favorites_list = db.relationship('Favorite', back_populates='website', lazy='dynamic',
                                     cascade='all, delete-orphan')
    view_history = db.relationship('ViewHistory', back_populates='website', lazy='dynamic',
                                   cascade='all, delete-orphan')

    def increment_view(self):
        """增加浏览量"""
        self.views += 1
        db.session.commit()

    def increment_like(self):
        """增加点赞数"""
        self.likes += 1
        db.session.commit()

    def decrement_like(self):
        """减少点赞数"""
        if self.likes > 0:
            self.likes -= 1
            db.session.commit()

    def increment_favorite(self):
        """增加收藏数"""
        self.favorites += 1
        db.session.commit()

    def decrement_favorite(self):
        """减少收藏数"""
        if self.favorites > 0:
            self.favorites -= 1
            db.session.commit()

    def get_main_screenshot(self):
        """获取主截图"""
        if self.screenshots and len(self.screenshots) > 0:
            return self.screenshots[0]
        return None

    def add_screenshot(self, url, screenshot_type='homepage', width=None, height=None):
        """添加截图"""
        if not self.screenshots:
            self.screenshots = []
        self.screenshots.append({
            'url': url,
            'type': screenshot_type,
            'width': width,
            'height': height
        })

    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['category_name'] = self.category.name if self.category else None
        data['tag_names'] = [tag.name for tag in self.tags]
        data['main_screenshot'] = self.get_main_screenshot()
        return data

    def to_detail_dict(self):
        """转换为详情字典（包含更多信息）"""
        data = self.to_dict()
        data['creator_name'] = self.creator.username if self.creator else None
        return data

    @staticmethod
    def get_active_websites():
        """获取所有活跃网站"""
        return Website.query.filter_by(status='active')

    @staticmethod
    def get_hot_websites(limit=10):
        """获取热门网站"""
        return Website.query.filter_by(status='active').order_by(Website.views.desc()).limit(limit).all()

    @staticmethod
    def get_recent_websites(limit=10):
        """获取最新网站"""
        return Website.query.filter_by(status='active').order_by(Website.created_at.desc()).limit(limit).all()

    def __repr__(self):
        return f'<Website {self.name}>'
