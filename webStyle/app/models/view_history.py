"""
浏览历史模型
"""
from datetime import datetime, timedelta
from app.extensions import db
from app.models.base import BaseModel


class ViewHistory(BaseModel):
    """浏览历史模型"""
    __tablename__ = 'view_history'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id', ondelete='CASCADE'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    user = db.relationship('User', back_populates='view_history')
    website = db.relationship('Website', back_populates='view_history')

    @staticmethod
    def add_history(user_id, website_id):
        """添加浏览历史"""
        # 检查是否已存在
        existing = ViewHistory.query.filter_by(
            user_id=user_id,
            website_id=website_id
        ).first()

        if existing:
            # 更新浏览时间
            existing.viewed_at = datetime.utcnow()
            existing.save()
        else:
            # 创建新记录
            history = ViewHistory(user_id=user_id, website_id=website_id)
            history.save()

    @staticmethod
    def get_user_history(user_id, page=1, per_page=20, days=30):
        """获取用户浏览历史"""
        since = datetime.utcnow() - timedelta(days=days)
        return ViewHistory.query.filter(
            ViewHistory.user_id == user_id,
            ViewHistory.viewed_at >= since
        ).order_by(ViewHistory.viewed_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def clear_old_history(days=90):
        """清理旧历史记录"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        old_records = ViewHistory.query.filter(ViewHistory.viewed_at < cutoff).all()
        for record in old_records:
            record.delete()
        return len(old_records)

    def __repr__(self):
        return f'<ViewHistory user={self.user_id} website={self.website_id}>'
