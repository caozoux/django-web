"""
标签模型
"""
from app.extensions import db
from app.models.base import BaseModel


class Tag(BaseModel):
    """标签模型"""
    __tablename__ = 'tags'

    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    usage_count = db.Column(db.Integer, default=0)

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        db.session.commit()

    def decrement_usage(self):
        """减少使用次数"""
        if self.usage_count > 0:
            self.usage_count -= 1
            db.session.commit()

    @staticmethod
    def get_by_slug(slug):
        """根据slug获取标签"""
        return Tag.query.filter_by(slug=slug).first()

    @staticmethod
    def get_popular_tags(limit=20):
        """获取热门标签"""
        return Tag.query.order_by(Tag.usage_count.desc()).limit(limit).all()

    def __repr__(self):
        return f'<Tag {self.name}>'


class WebsiteTag(db.Model):
    """网站标签关联表"""
    __tablename__ = 'website_tags'

    website_id = db.Column(db.Integer, db.ForeignKey('websites.id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return f'<WebsiteTag website={self.website_id} tag={self.tag_id}>'
