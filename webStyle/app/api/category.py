"""
分类API
"""
from flask import Blueprint, request, jsonify

from app.services.category_service import CategoryService
from app.utils.response import success_response, error_response

category_api = Blueprint('category_api', __name__)


@category_api.route('', methods=['GET'])
def list_categories():
    """获取分类列表"""
    categories = CategoryService.get_active_categories()
    return success_response([c.to_dict() for c in categories])


@category_api.route('/root', methods=['GET'])
def get_root_categories():
    """获取顶级分类"""
    categories = CategoryService.get_root_categories()
    return success_response([c.to_dict() for c in categories])


@category_api.route('/tree', methods=['GET'])
def get_category_tree():
    """获取分类树"""
    tree = CategoryService.get_category_tree()
    return success_response(tree)


@category_api.route('/statistics', methods=['GET'])
def get_statistics():
    """获取分类统计"""
    stats = CategoryService.get_category_statistics()
    return success_response(stats)


@category_api.route('/<int:id>', methods=['GET'])
def get_category(id):
    """获取分类详情"""
    category = CategoryService.get_by_id(id)
    if not category:
        return error_response('Category not found', 404)

    return success_response(category.to_dict())


@category_api.route('/<int:id>/websites', methods=['GET'])
def get_category_websites(id):
    """获取分类下的网站"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = CategoryService.get_category_with_websites(id, page, per_page)
    if not result:
        return error_response('Category not found', 404)

    return success_response({
        'category': result['category'].to_dict(),
        'websites': [w.to_dict() for w in result['websites']],
        'pagination': result['pagination']
    })


@category_api.route('/slug/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    """根据slug获取分类"""
    category = CategoryService.get_by_slug(slug)
    if not category:
        return error_response('Category not found', 404)

    return success_response(category.to_dict())
