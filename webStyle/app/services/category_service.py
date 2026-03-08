"""
分类业务逻辑服务
"""
from typing import List, Dict, Optional
from app.extensions import db, cache
from app.models.category import Category
from app.models.website import Website


class CategoryService:
    """分类业务逻辑服务"""

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='category_all')
    def get_all_categories() -> List[Category]:
        """获取所有分类"""
        return Category.query.order_by(Category.sort_order).all()

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='category_active')
    def get_active_categories() -> List[Category]:
        """获取所有活跃分类"""
        return Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='category_root')
    def get_root_categories() -> List[Category]:
        """获取顶级分类"""
        return Category.query.filter_by(
            parent_id=None,
            is_active=True
        ).order_by(Category.sort_order).all()

    @staticmethod
    def get_by_id(category_id: int) -> Optional[Category]:
        """根据ID获取分类"""
        return Category.query.get(category_id)

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Category]:
        """根据slug获取分类"""
        return Category.query.filter_by(slug=slug).first()

    @staticmethod
    def get_category_with_websites(category_id: int, page: int = 1, per_page: int = 20) -> Optional[Dict]:
        """获取分类及其网站"""
        category = Category.query.get(category_id)
        if not category:
            return None

        websites = Website.query.filter_by(
            category_id=category_id,
            status='active'
        ).order_by(Website.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'category': category,
            'websites': websites.items,
            'pagination': {
                'page': websites.page,
                'pages': websites.pages,
                'total': websites.total,
                'has_next': websites.has_next,
                'has_prev': websites.has_prev
            }
        }

    @staticmethod
    def create_category(data: Dict) -> Category:
        """创建分类"""
        category = Category(**data)
        db.session.add(category)
        db.session.commit()

        # 清除缓存
        cache.delete('category_all')
        cache.delete('category_active')
        cache.delete('category_root')

        return category

    @staticmethod
    def update_category(category_id: int, data: Dict) -> Optional[Category]:
        """更新分类"""
        category = Category.query.get(category_id)
        if not category:
            return None

        for key, value in data.items():
            if hasattr(category, key):
                setattr(category, key, value)

        db.session.commit()

        # 清除缓存
        cache.delete('category_all')
        cache.delete('category_active')
        cache.delete('category_root')

        return category

    @staticmethod
    def delete_category(category_id: int) -> bool:
        """删除分类"""
        category = Category.query.get(category_id)
        if not category:
            return False

        # 检查是否有子分类
        if category.children.count() > 0:
            return False

        # 检查是否有关联网站
        if category.websites.count() > 0:
            return False

        db.session.delete(category)
        db.session.commit()

        # 清除缓存
        cache.delete('category_all')
        cache.delete('category_active')
        cache.delete('category_root')

        return True

    @staticmethod
    def get_category_tree() -> List[Dict]:
        """获取分类树结构"""
        def build_tree(categories, parent_id=None):
            tree = []
            for category in categories:
                if category.parent_id == parent_id:
                    node = category.to_dict()
                    children = build_tree(categories, category.id)
                    if children:
                        node['children'] = children
                    tree.append(node)
            return tree

        categories = CategoryService.get_all_categories()
        return build_tree(categories)

    @staticmethod
    def get_category_statistics() -> List[Dict]:
        """获取分类统计信息"""
        categories = CategoryService.get_active_categories()
        result = []

        for category in categories:
            result.append({
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'website_count': category.website_count,
                'icon': category.icon
            })

        return result
