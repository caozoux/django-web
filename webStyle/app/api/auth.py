"""
认证API
"""
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from app.services.user_service import UserService
from app.utils.response import success_response, error_response
from app.utils.validators import validate_email, validate_password

auth_api = Blueprint('auth_api', __name__)


@auth_api.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # 验证必填字段
    if not username or not email or not password:
        return error_response('Missing required fields', 400)

    # 验证用户名长度
    if len(username) < 3 or len(username) > 50:
        return error_response('Username must be between 3 and 50 characters', 400)

    # 验证邮箱格式
    if not validate_email(email):
        return error_response('Invalid email format', 400)

    # 验证密码强度
    if not validate_password(password):
        return error_response('Password must be at least 6 characters', 400)

    # 检查用户名是否已存在
    if UserService.get_by_username(username):
        return error_response('Username already exists', 400)

    # 检查邮箱是否已存在
    if UserService.get_by_email(email):
        return error_response('Email already exists', 400)

    # 创建用户
    user = UserService.create_user({
        'username': username,
        'email': email,
        'password': password
    })

    # 生成token
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return success_response({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }, status_code=201)


@auth_api.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return error_response('Missing username or password', 400)

    # 验证用户
    user = UserService.authenticate(username, password)

    if not user:
        return error_response('Invalid username or password', 401)

    if not user.is_active:
        return error_response('Account is deactivated', 401)

    # 生成token
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return success_response({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@auth_api.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新token"""
    user_id = get_jwt_identity()
    user = UserService.get_by_id(user_id)

    if not user or not user.is_active:
        return error_response('User not found or inactive', 401)

    access_token = create_access_token(identity=user_id)

    return success_response({
        'access_token': access_token
    })


@auth_api.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    user = UserService.get_by_id(user_id)

    if not user:
        return error_response('User not found', 404)

    return success_response(user.to_dict())


@auth_api.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """登出（客户端清除token）"""
    return success_response({'message': 'Successfully logged out'})


@auth_api.route('/check-username', methods=['POST'])
def check_username():
    """检查用户名是否可用"""
    data = request.get_json()
    username = data.get('username', '').strip()

    if not username:
        return error_response('Username is required', 400)

    exists = UserService.get_by_username(username) is not None

    return success_response({
        'available': not exists,
        'username': username
    })


@auth_api.route('/check-email', methods=['POST'])
def check_email():
    """检查邮箱是否可用"""
    data = request.get_json()
    email = data.get('email', '').strip()

    if not email:
        return error_response('Email is required', 400)

    if not validate_email(email):
        return error_response('Invalid email format', 400)

    exists = UserService.get_by_email(email) is not None

    return success_response({
        'available': not exists,
        'email': email
    })
