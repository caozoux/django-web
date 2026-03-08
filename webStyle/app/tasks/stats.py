"""
统计任务
"""
from datetime import datetime, timedelta
from celery import shared_task

from app.extensions import db, celery
from app.models.website import Website
from app.models.user import User
from app.models.favorite import Favorite
from app.models.view_history import ViewHistory
from app.services.stats_service import StatsService


@celery.task(name='update_stats')
def update_stats_task():
    """
    更新统计任务
    定期运行，更新缓存中的统计数据
    """
    # 清除统计缓存，强制重新计算
    StatsService.clear_stats_cache()

    # 预热缓存
    StatsService.get_overview_stats()
    StatsService.get_category_distribution()
    StatsService.get_style_trends()

    return {
        'status': 'SUCCESS',
        'updated_at': datetime.utcnow().isoformat()
    }


@celery.task(name='calculate_daily_stats')
def calculate_daily_stats_task():
    """
    计算每日统计任务
    每天凌晨运行，计算前一天的统计数据
    """
    from sqlalchemy import func

    yesterday = datetime.utcnow().date() - timedelta(days=1)
    day_start = datetime.combine(yesterday, datetime.min.time())
    day_end = datetime.combine(yesterday, datetime.max.time())

    # 新增网站数
    new_websites = Website.query.filter(
        Website.created_at >= day_start,
        Website.created_at <= day_end
    ).count()

    # 新增用户数
    new_users = User.query.filter(
        User.created_at >= day_start,
        User.created_at <= day_end
    ).count()

    # 新增收藏数
    new_favorites = Favorite.query.filter(
        Favorite.created_at >= day_start,
        Favorite.created_at <= day_end
    ).count()

    # 总浏览量
    total_views = db.session.query(
        func.sum(Website.views)
    ).filter(
        Website.updated_at >= day_start,
        Website.updated_at <= day_end
    ).scalar() or 0

    stats = {
        'date': yesterday.isoformat(),
        'new_websites': new_websites,
        'new_users': new_users,
        'new_favorites': new_favorites,
        'total_views': total_views
    }

    # 可以将统计数据存入数据库或发送通知
    return stats


@celery.task(name='cleanup_old_history')
def cleanup_old_history_task(days: int = 90):
    """
    清理旧浏览历史任务

    Args:
        days: 保留天数
    """
    cleaned = ViewHistory.clear_old_history(days)

    return {
        'status': 'SUCCESS',
        'cleaned_count': cleaned
    }


@celery.task(name='update_website_counts')
def update_website_counts_task():
    """
    更新网站统计数任务
    定期校正网站的浏览量、点赞数、收藏数
    """
    from sqlalchemy import func

    # 更新收藏数
    websites = Website.query.all()

    for website in websites:
        # 计算实际收藏数
        actual_favorites = Favorite.query.filter_by(
            website_id=website.id
        ).count()

        # 如果不一致则更新
        if website.favorites != actual_favorites:
            website.favorites = actual_favorites

    db.session.commit()

    return {
        'status': 'SUCCESS',
        'updated_count': len(websites)
    }


@celery.task(name='generate_weekly_report')
def generate_weekly_report_task():
    """
    生成周报任务
    每周一运行，生成上周的统计报告
    """
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday() + 7)  # 上周一
    week_end = week_start + timedelta(days=6)  # 上周日

    start_dt = datetime.combine(week_start, datetime.min.time())
    end_dt = datetime.combine(week_end, datetime.max.time())

    # 周新增网站
    weekly_new_websites = Website.query.filter(
        Website.created_at >= start_dt,
        Website.created_at <= end_dt
    ).count()

    # 周新增用户
    weekly_new_users = User.query.filter(
        User.created_at >= start_dt,
        User.created_at <= end_dt
    ).count()

    # 周活跃网站（有浏览记录）
    weekly_active_websites = db.session.query(
        func.count(func.distinct(ViewHistory.website_id))
    ).filter(
        ViewHistory.viewed_at >= start_dt,
        ViewHistory.viewed_at <= end_dt
    ).scalar() or 0

    # 周总浏览量
    weekly_views = db.session.query(
        func.sum(Website.views)
    ).filter(
        Website.updated_at >= start_dt,
        Website.updated_at <= end_dt
    ).scalar() or 0

    report = {
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'new_websites': weekly_new_websites,
        'new_users': weekly_new_users,
        'active_websites': weekly_active_websites,
        'total_views': weekly_views
    }

    # 可以将报告发送邮件或存储
    return report
