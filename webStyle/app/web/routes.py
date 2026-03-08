"""
前台路由
"""
from flask import render_template, request, redirect, url_for
from app.web import web_bp
from app.services.website_service import WebsiteService
from app.services.category_service import CategoryService
from app.services.stats_service import StatsService
from app.services.search_service import SearchService


@web_bp.route('/')
def index():
    """首页"""
    # 获取热门网站
    hot_websites = WebsiteService.get_hot_websites(8)

    # 获取最新网站
    recent_websites = WebsiteService.get_recent_websites(8)

    # 获取分类
    categories = CategoryService.get_root_categories()

    # 获取统计概览
    stats = StatsService.get_overview_stats()

    return render_template('web/index.html',
                           hot_websites=hot_websites,
                           recent_websites=recent_websites,
                           categories=categories,
                           stats=stats)


@web_bp.route('/categories')
def categories():
    """分类列表页"""
    all_categories = CategoryService.get_active_categories()
    category_tree = CategoryService.get_category_tree()
    statistics = CategoryService.get_category_statistics()

    return render_template('web/categories.html',
                           categories=all_categories,
                           category_tree=category_tree,
                           statistics=statistics)


@web_bp.route('/categories/<int:id>')
def category_detail(id):
    """分类详情页"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = CategoryService.get_category_with_websites(id, page, per_page)

    if not result:
        return render_template('errors/404.html'), 404

    return render_template('web/category_detail.html',
                           category=result['category'],
                           websites=result['websites'],
                           pagination=result['pagination'])


@web_bp.route('/websites/<int:id>')
def website_detail(id):
    """网站详情页"""
    website = WebsiteService.get_by_id(id)

    if not website:
        return render_template('errors/404.html'), 404

    # 增加浏览量
    website.increment_view()

    # 获取相似网站
    similar_websites = WebsiteService.get_similar_websites(id)

    return render_template('web/website.html',
                           website=website,
                           similar_websites=similar_websites)


@web_bp.route('/search')
def search():
    """搜索页面"""
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    industry = request.args.get('industry')
    color_scheme = request.args.get('color_scheme')
    layout_type = request.args.get('layout_type')
    order_by = request.args.get('order_by', 'relevance')

    pagination = SearchService.search_websites(
        keyword=keyword,
        page=page,
        per_page=per_page,
        category_id=category_id,
        industry=industry,
        color_scheme=color_scheme,
        layout_type=layout_type,
        order_by=order_by
    )

    # 获取筛选选项
    filter_options = SearchService.get_filter_options()

    # 获取分类
    categories = CategoryService.get_active_categories()

    return render_template('web/search.html',
                           keyword=keyword,
                           websites=pagination.items,
                           pagination=pagination.to_dict(),
                           filter_options=filter_options,
                           categories=categories)


@web_bp.route('/analytics')
def analytics():
    """数据分析页面"""
    # 获取统计概览
    overview = StatsService.get_overview_stats()

    # 获取分类分布
    category_distribution = StatsService.get_category_distribution()

    # 获取风格趋势
    trends = StatsService.get_style_trends(30)

    # 获取TOP网站
    top_views = StatsService.get_top_websites(10, 'views')
    top_likes = StatsService.get_top_websites(10, 'likes')
    top_favorites = StatsService.get_top_websites(10, 'favorites')

    return render_template('web/analytics.html',
                           overview=overview,
                           category_distribution=category_distribution,
                           trends=trends,
                           top_views=top_views,
                           top_likes=top_likes,
                           top_favorites=top_favorites)


@web_bp.route('/random')
def random_websites():
    """随机发现页面"""
    websites = WebsiteService.get_random_websites(12)

    return render_template('web/random.html', websites=websites)


@web_bp.route('/about')
def about():
    """关于页面"""
    return render_template('web/about.html')


@web_bp.route('/contact')
def contact():
    """联系页面"""
    return render_template('web/contact.html')
