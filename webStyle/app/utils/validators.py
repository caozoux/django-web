"""
数据验证器
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> bool:
    """验证密码强度（至少6位）"""
    if not password:
        return False

    return len(password) >= 6


def validate_strong_password(password: str) -> tuple[bool, Optional[str]]:
    """
    验证强密码
    要求：至少8位，包含大小写字母和数字
    返回：(是否有效, 错误信息)
    """
    if not password:
        return False, 'Password is required'

    if len(password) < 8:
        return False, 'Password must be at least 8 characters'

    if not re.search(r'[a-z]', password):
        return False, 'Password must contain lowercase letters'

    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain uppercase letters'

    if not re.search(r'\d', password):
        return False, 'Password must contain numbers'

    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    验证用户名
    要求：3-50位，只允许字母、数字、下划线
    """
    if not username:
        return False, 'Username is required'

    if len(username) < 3:
        return False, 'Username must be at least 3 characters'

    if len(username) > 50:
        return False, 'Username must be less than 50 characters'

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, 'Username can only contain letters, numbers and underscores'

    return True, None


def validate_url(url: str) -> bool:
    """验证URL格式"""
    if not url:
        return False

    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def validate_slug(slug: str) -> bool:
    """验证slug格式（只允许小写字母、数字、连字符）"""
    if not slug:
        return False

    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """清理字符串（去除首尾空格，限制长度）"""
    if not text:
        return ''

    text = text.strip()

    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text


def validate_hex_color(color: str) -> bool:
    """验证十六进制颜色值"""
    if not color:
        return False

    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    return bool(re.match(pattern, color))


def is_positive_integer(value) -> bool:
    """检查是否为正整数"""
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False


def is_valid_page(value, max_page: int = 10000) -> int:
    """验证并返回有效的页码"""
    try:
        page = int(value)
        if page < 1:
            return 1
        if page > max_page:
            return max_page
        return page
    except (ValueError, TypeError):
        return 1
