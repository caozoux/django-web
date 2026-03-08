"""
管理后台API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.website_service import WebsiteService
from app.services.category_service import CategoryService
from app.services.stats_service import StatsService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required

admin_api = Blueprint('admin_api', __name__)


# ==================== 网站管理 ====================

@admin_api.route('/websites', methods=['GET'])
@jwt_required()
@admin_required
def list_websites():
    """获取网站列表（包含所有状态）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword')

    pagination = WebsiteService.get_websites_paginated(
        page=page,
        per_page=per_page,
        status=status,
        category_id=category_id,
        keyword=keyword
    )

    return success_response({
        'data': [w.to_detail_dict() for w in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@admin_api.route('/websites', methods=['POST'])
@jwt_required()
@admin_required
def create_website():
    """创建网站"""
    user_id = get_jwt_identity()
    data = request.get_json()

    # 设置创建者
    data['created_by'] = user_id

    # 验证必填字段
    if not data.get('name') or not data.get('url') or not data.get('category_id'):
        return error_response('Missing required fields', 400)

    website = WebsiteService.create_website(data)
    return success_response(website.to_detail_dict(), status_code=201)


@admin_api.route('/websites/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_website(id):
    """更新网站"""
    data = request.get_json()
    website = WebsiteService.update_website(id, data)

    if not website:
        return error_response('Website not found', 404)

    return success_response(website.to_detail_dict())


@admin_api.route('/websites/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_website(id):
    """删除网站"""
    hard = request.args.get('hard', 'false').lower() == 'true'

    if hard:
        success = WebsiteService.hard_delete_website(id)
    else:
        success = WebsiteService.delete_website(id)

    if not success:
        return error_response('Website not found', 404)

    return success_response({'message': 'Website deleted'})


@admin_api.route('/websites/<int:id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_website(id):
    """审核通过网站"""
    from app.models.website import Website
    website = Website.query.get(id)
    if not website:
        return error_response('Website not found', 404)

    website.status = 'active'
    website.save()

    return success_response(website.to_detail_dict())


@admin_api.route('/websites/<int:id>/reject', methods=['POST'])
@jwt_required()
@admin_required
def reject_website(id):
    """拒绝网站"""
    from app.models.website import Website
    website = Website.query.get(id)
    if not website:
        return error_response('Website not found', 404)

    website.status = 'inactive'
    website.save()

    return success_response(website.to_detail_dict())


# ==================== 分类管理 ====================

@admin_api.route('/categories', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    """创建分类"""
    data = request.get_json()

    if not data.get('name') or not data.get('slug'):
        return error_response('Missing required fields', 400)

    # 检查slug是否已存在
    if CategoryService.get_by_slug(data['slug']):
        return error_response('Slug already exists', 400)

    category = CategoryService.create_category(data)
    return success_response(category.to_dict(), status_code=201)


@admin_api.route('/categories/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(id):
    """更新分类"""
    data = request.get_json()
    category = CategoryService.update_category(id, data)

    if not category:
        return error_response('Category not found', 404)

    return success_response(category.to_dict())


@admin_api.route('/categories/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(id):
    """删除分类"""
    success = CategoryService.delete_category(id)

    if not success:
        return error_response('Cannot delete category (has children or websites)', 400)

    return success_response({'message': 'Category deleted'})


@admin_api.route('/categories/<int:id>/toggle', methods=['POST'])
@jwt_required()
@admin_required
def toggle_category(id):
    """切换分类状态"""
    from app.models.category import Category
    category = Category.query.get(id)
    if not category:
        return error_response('Category not found', 404)

    category.is_active = not category.is_active
    category.save()

    return success_response(category.to_dict())


# ==================== 统计信息 ====================

@admin_api.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_stats():
    """获取管理后台统计"""
    overview = StatsService.get_overview_stats()
    category_distribution = StatsService.get_category_distribution()
    growth = StatsService.get_website_growth_trend(30)

    return success_response({
        'overview': overview,
        'category_distribution': category_distribution,
        'growth': growth
    })
