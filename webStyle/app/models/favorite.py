"""
收藏模型
"""
from app.extensions import db
from app.models.base import BaseModel


class Favorite(BaseModel):
    """收藏模型"""
    __tablename__ = 'favorites'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id', ondelete='CASCADE'), nullable=False)

    # 关系
    user = db.relationship('User', back_populates='favorites')
    website = db.relationship('Website', back_populates='favorites_list')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'website_id', name='unique_user_website_favorite'),
    )

    @staticmethod
    def is_favorited(user_id, website_id):
        """检查是否已收藏"""
        return Favorite.query.filter_by(user_id=user_id, website_id=website_id).first() is not None

    @staticmethod
    def get_user_favorites(user_id, page=1, per_page=20):
        """获取用户收藏列表"""
        return Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def __repr__(self):
        return f'<Favorite user={self.user_id} website={self.website_id}>'
