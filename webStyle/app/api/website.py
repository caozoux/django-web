"""
网站API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity

from app.services.website_service import WebsiteService
from app.services.screenshot_service import ScreenshotService
from app.utils.response import success_response, error_response

website_api = Blueprint('website_api', __name__)


@website_api.route('', methods=['GET'])
def list_websites():
    """获取网站列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    industry = request.args.get('industry')
    color_scheme = request.args.get('color_scheme')
    layout_type = request.args.get('layout_type')
    keyword = request.args.get('keyword')
    order_by = request.args.get('order_by', 'created_at')

    pagination = WebsiteService.get_websites_paginated(
        page=page,
        per_page=per_page,
        category_id=category_id,
        industry=industry,
        color_scheme=color_scheme,
        layout_type=layout_type,
        keyword=keyword,
        order_by=order_by
    )

    return success_response({
        'data': [w.to_dict() for w in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@website_api.route('/<int:id>', methods=['GET'])
def get_website(id):
    """获取网站详情"""
    website = WebsiteService.get_by_id(id)
    if not website:
        return error_response('Website not found', 404)

    # 增加浏览量
    website.increment_view()

    return success_response(website.to_detail_dict())


@website_api.route('/<int:id>/similar', methods=['GET'])
def get_similar(id):
    """获取相似网站"""
    websites = WebsiteService.get_similar_websites(id)
    return success_response([w.to_dict() for w in websites])


@website_api.route('/hot', methods=['GET'])
def get_hot():
    """获取热门网站"""
    limit = request.args.get('limit', 10, type=int)
    websites = WebsiteService.get_hot_websites(limit)
    return success_response([w.to_dict() for w in websites])


@website_api.route('/recent', methods=['GET'])
def get_recent():
    """获取最新网站"""
    limit = request.args.get('limit', 10, type=int)
    websites = WebsiteService.get_recent_websites(limit)
    return success_response([w.to_dict() for w in websites])


@website_api.route('/random', methods=['GET'])
def get_random():
    """随机获取网站"""
    limit = request.args.get('limit', 6, type=int)
    websites = WebsiteService.get_random_websites(limit)
    return success_response([w.to_dict() for w in websites])


@website_api.route('/<int:id>/screenshot', methods=['POST'])
@jwt_required()
def capture_screenshot(id):
    """触发截图任务"""
    website = WebsiteService.get_by_id(id)
    if not website:
        return error_response('Website not found', 404)

    result = ScreenshotService.capture_website_screenshots(website.url, id)
    return success_response(result)


@website_api.route('/<int:id>/screenshot/status/<task_id>', methods=['GET'])
@jwt_required()
def get_screenshot_status(id, task_id):
    """获取截图任务状态"""
    result = ScreenshotService.get_screenshot_status(task_id)
    return success_response(result)


@website_api.route('/<int:id>/screenshot/upload', methods=['POST'])
@jwt_required()
def upload_screenshot(id):
    """手动上传截图"""
    if 'file' not in request.files:
        return error_response('No file provided', 400)

    file = request.files['file']
    screenshot_type = request.form.get('type', 'homepage')

    result = ScreenshotService.upload_screenshot(id, file, screenshot_type)

    if 'error' in result:
        return error_response(result['error'], 400)

    return success_response(result)


@website_api.route('/search', methods=['GET'])
def search():
    """搜索网站"""
    from app.services.search_service import SearchService

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

    return success_response({
        'data': [w.to_dict() for w in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@website_api.route('/search/suggestions', methods=['GET'])
def search_suggestions():
    """获取搜索建议"""
    from app.services.search_service import SearchService

    keyword = request.args.get('keyword', '')
    limit = request.args.get('limit', 5, type=int)

    suggestions = SearchService.get_search_suggestions(keyword, limit)
    return success_response(suggestions)


@website_api.route('/filter-options', methods=['GET'])
def get_filter_options():
    """获取筛选选项"""
    from app.services.search_service import SearchService

    options = SearchService.get_filter_options()
    return success_response(options)
