"""
分类模型
"""
from app.extensions import db
from app.models.base import BaseModel


class Category(BaseModel):
    """风格分类模型"""
    __tablename__ = 'categories'

    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    # 自引用关系（子分类）
    children = db.relationship(
        'Category',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    # 网站关系
    websites = db.relationship('Website', back_populates='category', lazy='dynamic')

    @property
    def website_count(self):
        """获取该分类下的活跃网站数量"""
        return self.websites.filter_by(status='active').count()

    def get_path(self):
        """获取分类路径（面包屑）"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return ' > '.join(reversed(path))

    def get_all_children(self):
        """获取所有子分类（递归）"""
        children = list(self.children)
        for child in self.children:
            children.extend(child.get_all_children())
        return children

    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['website_count'] = self.website_count
        data['parent_name'] = self.parent.name if self.parent else None
        return data

    @staticmethod
    def get_by_slug(slug):
        """根据slug获取分类"""
        return Category.query.filter_by(slug=slug).first()

    @staticmethod
    def get_root_categories():
        """获取顶级分类"""
        return Category.query.filter_by(parent_id=None, is_active=True).order_by(Category.sort_order).all()

    @staticmethod
    def get_active_categories():
        """获取所有活跃分类"""
        return Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()

    def __repr__(self):
        return f'<Category {self.name}>'
