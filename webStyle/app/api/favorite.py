"""
收藏API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.utils.response import success_response, error_response

favorite_api = Blueprint('favorite_api', __name__)


@favorite_api.route('', methods=['GET'])
@jwt_required()
def list_favorites():
    """获取收藏列表"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = UserService.get_user_favorites(user_id, page, per_page)
    return success_response(result)


@favorite_api.route('', methods=['POST'])
@jwt_required()
def add_favorite():
    """添加收藏"""
    user_id = get_jwt_identity()
    data = request.get_json()

    website_id = data.get('website_id')
    if not website_id:
        return error_response('Website ID is required', 400)

    success = UserService.add_favorite(user_id, website_id)

    if not success:
        return error_response('Already favorited or website not found', 400)

    return success_response({'message': 'Added to favorites'})


@favorite_api.route('/<int:website_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(website_id):
    """取消收藏"""
    user_id = get_jwt_identity()

    success = UserService.remove_favorite(user_id, website_id)

    if not success:
        return error_response('Favorite not found', 404)

    return success_response({'message': 'Removed from favorites'})


@favorite_api.route('/check/<int:website_id>', methods=['GET'])
@jwt_required()
def check_favorite(website_id):
    """检查是否已收藏"""
    from app.models.favorite import Favorite
    user_id = get_jwt_identity()

    is_favorited = Favorite.is_favorited(user_id, website_id)

    return success_response({'is_favorited': is_favorited})
