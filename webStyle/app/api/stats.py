"""
统计API
"""
from flask import Blueprint, request

from app.services.stats_service import StatsService
from app.utils.response import success_response

stats_api = Blueprint('stats_api', __name__)


@stats_api.route('/overview', methods=['GET'])
def get_overview():
    """获取概览统计"""
    stats = StatsService.get_overview_stats()
    return success_response(stats)


@stats_api.route('/categories/distribution', methods=['GET'])
def get_category_distribution():
    """获取分类分布"""
    data = StatsService.get_category_distribution()
    return success_response(data)


@stats_api.route('/trends', methods=['GET'])
def get_trends():
    """获取风格趋势"""
    days = request.args.get('days', 30, type=int)
    data = StatsService.get_style_trends(days)
    return success_response(data)


@stats_api.route('/top', methods=['GET'])
def get_top():
    """获取TOP网站"""
    limit = request.args.get('limit', 10, type=int)
    metric = request.args.get('metric', 'views')

    if metric not in ['views', 'likes', 'favorites']:
        metric = 'views'

    data = StatsService.get_top_websites(limit, metric)
    return success_response(data)


@stats_api.route('/industry/distribution', methods=['GET'])
def get_industry_distribution():
    """获取行业分布"""
    data = StatsService.get_industry_distribution()
    return success_response(data)


@stats_api.route('/color/distribution', methods=['GET'])
def get_color_distribution():
    """获取配色方案分布"""
    data = StatsService.get_color_scheme_distribution()
    return success_response(data)


@stats_api.route('/layout/distribution', methods=['GET'])
def get_layout_distribution():
    """获取布局类型分布"""
    data = StatsService.get_layout_distribution()
    return success_response(data)


@stats_api.route('/growth', methods=['GET'])
def get_growth():
    """获取网站增长趋势"""
    days = request.args.get('days', 30, type=int)
    data = StatsService.get_website_growth_trend(days)
    return success_response(data)
