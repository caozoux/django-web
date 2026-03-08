"""
用户API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required

user_api = Blueprint('user_api', __name__)


@user_api.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = UserService.get_by_id(user_id)

    if not user:
        return error_response('User not found', 404)

    return success_response(user.to_dict())


@user_api.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新当前用户信息"""
    user_id = get_jwt_identity()
    data = request.get_json()

    user = UserService.update_user(user_id, data)
    if not user:
        return error_response('User not found', 404)

    return success_response(user.to_dict())


@user_api.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    user_id = get_jwt_identity()
    data = request.get_json()

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return error_response('Missing required fields', 400)

    if len(new_password) < 6:
        return error_response('Password must be at least 6 characters', 400)

    success = UserService.change_password(user_id, old_password, new_password)
    if not success:
        return error_response('Invalid old password', 400)

    return success_response({'message': 'Password changed successfully'})


@user_api.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    """获取收藏列表"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = UserService.get_user_favorites(user_id, page, per_page)
    return success_response(result)


@user_api.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """获取浏览历史"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    result = UserService.get_user_history(user_id, page, per_page)
    return success_response(result)


# 管理接口
@user_api.route('', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """获取用户列表（管理员）"""
    from app.models.user import User
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)

    return success_response({
        'data': [u.to_dict() for u in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@user_api.route('/<int:id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(id):
    """获取用户详情（管理员）"""
    user = UserService.get_by_id(id)
    if not user:
        return error_response('User not found', 404)

    return success_response(user.to_dict(include_sensitive=True))


@user_api.route('/<int:id>/deactivate', methods=['POST'])
@jwt_required()
@admin_required
def deactivate_user(id):
    """停用用户（管理员）"""
    success = UserService.deactivate_user(id)
    if not success:
        return error_response('Failed to deactivate user', 400)

    return success_response({'message': 'User deactivated'})


@user_api.route('/<int:id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_user(id):
    """激活用户（管理员）"""
    success = UserService.activate_user(id)
    if not success:
        return error_response('Failed to activate user', 400)

    return success_response({'message': 'User activated'})


@user_api.route('/<int:id>/admin', methods=['POST'])
@jwt_required()
@admin_required
def set_admin(id):
    """设置管理员（管理员）"""
    success = UserService.set_admin(id)
    if not success:
        return error_response('Failed to set admin', 400)

    return success_response({'message': 'Admin role set'})
