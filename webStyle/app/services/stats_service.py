"""
统计业务逻辑服务
"""
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db, cache
from app.models.website import Website
from app.models.category import Category
from app.models.user import User
from app.models.favorite import Favorite


class StatsService:
    """统计服务"""

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='stats_overview')
    def get_overview_stats() -> Dict:
        """获取概览统计"""
        return {
            'total_websites': Website.query.count(),
            'active_websites': Website.query.filter_by(status='active').count(),
            'pending_websites': Website.query.filter_by(status='pending').count(),
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_categories': Category.query.filter_by(is_active=True).count(),
            'total_favorites': Favorite.query.count(),
            'total_views': db.session.query(func.sum(Website.views)).scalar() or 0,
            'total_likes': db.session.query(func.sum(Website.likes)).scalar() or 0,
        }

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='stats_category_distribution')
    def get_category_distribution() -> List[Dict]:
        """获取分类分布"""
        result = db.session.query(
            Category.id,
            Category.name,
            func.count(Website.id).label('count')
        ).outerjoin(
            Website, and_(Category.id == Website.category_id, Website.status == 'active')
        ).filter(
            Category.is_active == True
        ).group_by(
            Category.id, Category.name
        ).order_by(
            func.count(Website.id).desc()
        ).all()

        return [
            {'id': r[0], 'category': r[1], 'count': r[2]}
            for r in result
        ]

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='stats_style_trends')
    def get_style_trends(days: int = 30) -> Dict:
        """获取风格趋势"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        result = db.session.query(
            func.date(Website.created_at).label('date'),
            Category.name.label('category'),
            func.count(Website.id).label('count')
        ).join(
            Category
        ).filter(
            Website.created_at >= start_date,
            Website.status == 'active'
        ).group_by(
            func.date(Website.created_at),
            Category.name
        ).order_by(
            func.date(Website.created_at)
        ).all()

        # 转换为ECharts数据格式
        dates = sorted(list(set([str(r[0]) for r in result])))
        categories = list(set([r[1] for r in result]))

        series_data = []
        for category in categories:
            category_data = {
                'name': category,
                'data': []
            }
            for date in dates:
                count = next((r[2] for r in result if str(r[0]) == date and r[1] == category), 0)
                category_data['data'].append(count)
            series_data.append(category_data)

        return {
            'dates': dates,
            'series': series_data
        }

    @staticmethod
    def get_top_websites(limit: int = 10, metric: str = 'views') -> List[Dict]:
        """获取TOP网站"""
        query = Website.query.filter_by(status='active')

        if metric == 'views':
            query = query.order_by(Website.views.desc())
        elif metric == 'likes':
            query = query.order_by(Website.likes.desc())
        elif metric == 'favorites':
            query = query.order_by(Website.favorites.desc())
        else:
            query = query.order_by(Website.views.desc())

        websites = query.limit(limit).all()

        return [
            {
                'id': w.id,
                'name': w.name,
                'url': w.url,
                'value': getattr(w, metric),
                'category_name': w.category.name if w.category else None
            }
            for w in websites
        ]

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='stats_industry_distribution')
    def get_industry_distribution() -> List[Dict]:
        """获取行业分布"""
        result = db.session.query(
            Website.industry,
            func.count(Website.id).label('count')
        ).filter(
            Website.status == 'active',
            Website.industry.isnot(None)
        ).group_by(
            Website.industry
        ).order_by(
            func.count(Website.id).desc()
        ).all()

        return [
            {'industry': r[0], 'count': r[1]}
            for r in result
        ]

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='stats_color_distribution')
    def get_color_scheme_distribution() -> List[Dict]:
        """获取配色方案分布"""
        result = db.session.query(
            Website.color_scheme,
            func.count(Website.id).label('count')
        ).filter(
            Website.status == 'active',
            Website.color_scheme.isnot(None)
        ).group_by(
            Website.color_scheme
        ).order_by(
            func.count(Website.id).desc()
        ).all()

        return [
            {'color_scheme': r[0], 'count': r[1]}
            for r in result
        ]

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='stats_layout_distribution')
    def get_layout_distribution() -> List[Dict]:
        """获取布局类型分布"""
        result = db.session.query(
            Website.layout_type,
            func.count(Website.id).label('count')
        ).filter(
            Website.status == 'active',
            Website.layout_type.isnot(None)
        ).group_by(
            Website.layout_type
        ).order_by(
            func.count(Website.id).desc()
        ).all()

        return [
            {'layout_type': r[0], 'count': r[1]}
            for r in result
        ]

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='stats_growth_trend')
    def get_website_growth_trend(days: int = 30) -> Dict:
        """获取网站增长趋势"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        result = db.session.query(
            func.date(Website.created_at).label('date'),
            func.count(Website.id).label('count')
        ).filter(
            Website.created_at >= start_date
        ).group_by(
            func.date(Website.created_at)
        ).order_by(
            func.date(Website.created_at)
        ).all()

        return {
            'dates': [str(r[0]) for r in result],
            'counts': [r[1] for r in result]
        }

    @staticmethod
    def clear_stats_cache():
        """清除统计缓存"""
        keys = [
            'stats_overview',
            'stats_category_distribution',
            'stats_style_trends',
            'stats_industry_distribution',
            'stats_color_distribution',
            'stats_layout_distribution',
            'stats_growth_trend'
        ]
        for key in keys:
            cache.delete(key)
