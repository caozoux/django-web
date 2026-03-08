"""
网站业务逻辑服务
"""
from typing import List, Dict, Optional
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from app.extensions import db, cache
from app.models.website import Website
from app.models.category import Category
from app.models.tag import Tag
from app.utils.pagination import Pagination


class WebsiteService:
    """网站业务逻辑服务"""

    @staticmethod
    def get_websites_paginated(
        page: int = 1,
        per_page: int = 20,
        category_id: Optional[int] = None,
        industry: Optional[str] = None,
        color_scheme: Optional[str] = None,
        layout_type: Optional[str] = None,
        keyword: Optional[str] = None,
        status: str = 'active',
        order_by: str = 'created_at',
        order_desc: bool = True
    ) -> Pagination:
        """分页获取网站列表"""
        query = Website.query.options(joinedload(Website.category))

        # 状态筛选
        if status:
            query = query.filter(Website.status == status)

        # 分类筛选
        if category_id:
            query = query.filter(Website.category_id == category_id)

        # 行业筛选
        if industry:
            query = query.filter(Website.industry == industry)

        # 配色方案筛选
        if color_scheme:
            query = query.filter(Website.color_scheme == color_scheme)

        # 布局类型筛选
        if layout_type:
            query = query.filter(Website.layout_type == layout_type)

        # 关键词搜索
        if keyword:
            search_term = f'%{keyword}%'
            query = query.filter(or_(
                Website.name.ilike(search_term),
                Website.description.ilike(search_term)
            ))

        # 排序
        order_column = getattr(Website, order_by, Website.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return Pagination(query, page, per_page)

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='website_hot')
    def get_hot_websites(limit: int = 10) -> List[Website]:
        """获取热门网站"""
        return Website.query.filter_by(status='active')\
            .options(joinedload(Website.category))\
            .order_by(Website.views.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='website_recent')
    def get_recent_websites(limit: int = 10) -> List[Website]:
        """获取最新网站"""
        return Website.query.filter_by(status='active')\
            .options(joinedload(Website.category))\
            .order_by(Website.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def get_by_id(website_id: int) -> Optional[Website]:
        """根据ID获取网站"""
        return Website.query.options(
            joinedload(Website.category),
            joinedload(Website.tags),
            joinedload(Website.creator)
        ).get(website_id)

    @staticmethod
    def get_similar_websites(website_id: int, limit: int = 6) -> List[Website]:
        """获取相似网站（基于同一分类）"""
        website = Website.query.get(website_id)
        if not website:
            return []

        return Website.query.filter(
            Website.category_id == website.category_id,
            Website.id != website_id,
            Website.status == 'active'
        ).options(joinedload(Website.category))\
         .order_by(Website.views.desc())\
         .limit(limit)\
         .all()

    @staticmethod
    def create_website(data: Dict) -> Website:
        """创建网站"""
        tags_data = data.pop('tags', [])

        website = Website(**data)
        db.session.add(website)

        # 处理标签
        if tags_data:
            for tag_name in tags_data:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    # 创建新标签
                    import slugify
                    tag = Tag(name=tag_name, slug=slugify.slugify(tag_name))
                    db.session.add(tag)
                website.tags.append(tag)
                tag.increment_usage()

        db.session.commit()

        # 清除缓存
        cache.delete('website_hot')
        cache.delete('website_recent')

        return website

    @staticmethod
    def update_website(website_id: int, data: Dict) -> Optional[Website]:
        """更新网站"""
        website = Website.query.get(website_id)
        if not website:
            return None

        tags_data = data.pop('tags', None)

        for key, value in data.items():
            if hasattr(website, key):
                setattr(website, key, value)

        # 处理标签更新
        if tags_data is not None:
            # 移除旧标签
            for tag in website.tags:
                tag.decrement_usage()
            website.tags = []

            # 添加新标签
            for tag_name in tags_data:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    import slugify
                    tag = Tag(name=tag_name, slug=slugify.slugify(tag_name))
                    db.session.add(tag)
                website.tags.append(tag)
                tag.increment_usage()

        db.session.commit()

        # 清除缓存
        cache.delete('website_hot')
        cache.delete('website_recent')

        return website

    @staticmethod
    def delete_website(website_id: int) -> bool:
        """删除网站（软删除）"""
        website = Website.query.get(website_id)
        if not website:
            return False

        website.status = 'inactive'
        db.session.commit()

        # 清除缓存
        cache.delete('website_hot')
        cache.delete('website_recent')

        return True

    @staticmethod
    def hard_delete_website(website_id: int) -> bool:
        """永久删除网站"""
        website = Website.query.get(website_id)
        if not website:
            return False

        # 移除标签关联
        for tag in website.tags:
            tag.decrement_usage()

        db.session.delete(website)
        db.session.commit()

        # 清除缓存
        cache.delete('website_hot')
        cache.delete('website_recent')

        return True

    @staticmethod
    def get_random_websites(limit: int = 6) -> List[Website]:
        """随机获取网站"""
        from sqlalchemy.sql.expression import func
        return Website.query.filter_by(status='active')\
            .options(joinedload(Website.category))\
            .order_by(func.random())\
            .limit(limit)\
            .all()

    @staticmethod
    def get_website_count_by_category() -> Dict[int, int]:
        """获取各分类的网站数量"""
        result = db.session.query(
            Website.category_id,
            db.func.count(Website.id)
        ).filter(
            Website.status == 'active'
        ).group_by(
            Website.category_id
        ).all()

        return {row[0]: row[1] for row in result}
