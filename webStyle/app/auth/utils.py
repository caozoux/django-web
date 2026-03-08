"""
认证工具函数
"""
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token


def hash_password(password: str) -> str:
    """生成密码哈希"""
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """验证密码"""
    return check_password_hash(password_hash, password)


def generate_tokens(user_id: int) -> dict:
    """生成访问令牌和刷新令牌"""
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def is_valid_password(password: str) -> tuple:
    """
    验证密码强度

    Returns:
        (is_valid, error_message)
    """
    if len(password) < 6:
        return False, 'Password must be at least 6 characters'

    if len(password) > 128:
        return False, 'Password is too long'

    return True, None


def is_valid_username(username: str) -> tuple:
    """
    验证用户名

    Returns:
        (is_valid, error_message)
    """
    if len(username) < 3:
        return False, 'Username must be at least 3 characters'

    if len(username) > 50:
        return False, 'Username must be less than 50 characters'

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, 'Username can only contain letters, numbers and underscores'

    return True, None


def is_valid_email(email: str) -> tuple:
    """
    验证邮箱格式

    Returns:
        (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, 'Invalid email format'

    if len(email) > 100:
        return False, 'Email is too long'

    return True, None
