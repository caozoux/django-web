"""
装饰器
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models.user import User


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_admin():
            return jsonify({
                'error': 'Forbidden',
                'message': 'Admin permission required'
            }), 403

        return f(*args, **kwargs)
    return decorated_function


def active_user_required(f):
    """活跃用户权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_active:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Active user required'
            }), 403

        return f(*args, **kwargs)
    return decorated_function


def cache_key_prefix(prefix):
    """缓存键前缀装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            from app.extensions import cache

            # 生成缓存键
            cache_key = f"{prefix}:{request.path}:{str(request.args)}"

            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result

            # 执行函数
            result = f(*args, **kwargs)

            # 存入缓存
            cache.set(cache_key, result)

            return result
        return decorated_function
    return decorator


def validate_json(*required_fields):
    """验证JSON请求体装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request

            if not request.is_json:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Content-Type must be application/json'
                }), 400

            data = request.get_json()

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': 'Bad Request',
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit(limit='200/hour'):
    """限流装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_limiter import Limiter
            from flask_limiter.util import get_remote_address
            from flask import current_app

            limiter = current_app.extensions.get('limiter')
            if limiter:
                return limiter.limit(limit)(f)(*args, **kwargs)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
