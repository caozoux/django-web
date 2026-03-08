"""
搜索业务逻辑服务
"""
from typing import List, Dict, Optional
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.website import Website
from app.models.category import Category
from app.models.tag import Tag
from app.utils.pagination import Pagination


class SearchService:
    """搜索服务"""

    @staticmethod
    def search_websites(
        keyword: str,
        page: int = 1,
        per_page: int = 20,
        category_id: Optional[int] = None,
        industry: Optional[str] = None,
        color_scheme: Optional[str] = None,
        layout_type: Optional[str] = None,
        order_by: str = 'relevance'
    ) -> Pagination:
        """搜索网站"""
        query = Website.query.filter_by(status='active').options(
            joinedload(Website.category),
            joinedload(Website.tags)
        )

        # 关键词搜索
        if keyword:
            search_term = f'%{keyword}%'
            query = query.filter(or_(
                Website.name.ilike(search_term),
                Website.description.ilike(search_term),
                # 搜索标签
                Website.tags.any(Tag.name.ilike(search_term))
            ))

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

        # 排序
        if order_by == 'relevance' and keyword:
            # 相关性排序（简化版，实际可使用全文检索）
            query = query.order_by(Website.views.desc())
        elif order_by == 'views':
            query = query.order_by(Website.views.desc())
        elif order_by == 'likes':
            query = query.order_by(Website.likes.desc())
        elif order_by == 'favorites':
            query = query.order_by(Website.favorites.desc())
        elif order_by == 'newest':
            query = query.order_by(Website.created_at.desc())
        else:
            query = query.order_by(Website.created_at.desc())

        return Pagination(query, page, per_page)

    @staticmethod
    def search_categories(keyword: str) -> List[Category]:
        """搜索分类"""
        if not keyword:
            return []

        search_term = f'%{keyword}%'
        return Category.query.filter(
            Category.is_active == True,
            or_(
                Category.name.ilike(search_term),
                Category.description.ilike(search_term)
            )
        ).all()

    @staticmethod
    def search_tags(keyword: str, limit: int = 10) -> List[Tag]:
        """搜索标签"""
        if not keyword:
            return []

        search_term = f'%{keyword}%'
        return Tag.query.filter(
            Tag.name.ilike(search_term)
        ).order_by(Tag.usage_count.desc()).limit(limit).all()

    @staticmethod
    def get_filter_options() -> Dict:
        """获取筛选选项"""
        # 获取所有行业
        industries = db.session.query(
            Website.industry
        ).filter(
            Website.status == 'active',
            Website.industry.isnot(None)
        ).distinct().all()
        industries = [i[0] for i in industries if i[0]]

        # 获取所有配色方案
        color_schemes = db.session.query(
            Website.color_scheme
        ).filter(
            Website.status == 'active',
            Website.color_scheme.isnot(None)
        ).distinct().all()
        color_schemes = [c[0] for c in color_schemes if c[0]]

        # 获取所有布局类型
        layout_types = db.session.query(
            Website.layout_type
        ).filter(
            Website.status == 'active',
            Website.layout_type.isnot(None)
        ).distinct().all()
        layout_types = [l[0] for l in layout_types if l[0]]

        return {
            'industries': sorted(industries),
            'color_schemes': sorted(color_schemes),
            'layout_types': sorted(layout_types)
        }

    @staticmethod
    def advanced_search(
        keywords: Optional[List[str]] = None,
        categories: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
        industry: Optional[str] = None,
        color_scheme: Optional[str] = None,
        layout_type: Optional[str] = None,
        min_views: Optional[int] = None,
        max_views: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Pagination:
        """高级搜索"""
        query = Website.query.filter_by(status='active').options(
            joinedload(Website.category),
            joinedload(Website.tags)
        )

        # 关键词搜索（AND逻辑）
        if keywords:
            for keyword in keywords:
                search_term = f'%{keyword}%'
                query = query.filter(or_(
                    Website.name.ilike(search_term),
                    Website.description.ilike(search_term)
                ))

        # 分类筛选（OR逻辑）
        if categories:
            query = query.filter(Website.category_id.in_(categories))

        # 标签筛选（OR逻辑）
        if tags:
            query = query.filter(
                Website.tags.any(Tag.name.in_(tags))
            )

        # 行业筛选
        if industry:
            query = query.filter(Website.industry == industry)

        # 配色方案筛选
        if color_scheme:
            query = query.filter(Website.color_scheme == color_scheme)

        # 布局类型筛选
        if layout_type:
            query = query.filter(Website.layout_type == layout_type)

        # 浏览量范围
        if min_views is not None:
            query = query.filter(Website.views >= min_views)
        if max_views is not None:
            query = query.filter(Website.views <= max_views)

        # 日期范围
        if date_from:
            from datetime import datetime
            try:
                date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Website.created_at >= date_from_dt)
            except ValueError:
                pass

        if date_to:
            from datetime import datetime
            try:
                date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(Website.created_at <= date_to_dt)
            except ValueError:
                pass

        # 默认排序
        query = query.order_by(Website.created_at.desc())

        return Pagination(query, page, per_page)

    @staticmethod
    def get_search_suggestions(keyword: str, limit: int = 5) -> Dict:
        """获取搜索建议"""
        if not keyword or len(keyword) < 2:
            return {'websites': [], 'categories': [], 'tags': []}

        # 网站建议
        websites = SearchService.search_websites(keyword, page=1, per_page=limit)
        website_suggestions = [
            {'id': w.id, 'name': w.name, 'url': w.url}
            for w in websites.items
        ]

        # 分类建议
        categories = SearchService.search_categories(keyword)[:limit]
        category_suggestions = [
            {'id': c.id, 'name': c.name, 'slug': c.slug}
            for c in categories
        ]

        # 标签建议
        tags = SearchService.search_tags(keyword, limit)
        tag_suggestions = [
            {'id': t.id, 'name': t.name, 'slug': t.slug}
            for t in tags
        ]

        return {
            'websites': website_suggestions,
            'categories': category_suggestions,
            'tags': tag_suggestions
        }
