"""
辅助函数
"""
import re
import os
import uuid
import random
import string
from datetime import datetime
from typing import Optional, List


def slugify(text: str) -> str:
    """
    将文本转换为slug格式

    Args:
        text: 原始文本

    Returns:
        slug格式的字符串
    """
    # 转小写
    text = text.lower()

    # 替换空格为连字符
    text = re.sub(r'\s+', '-', text)

    # 移除非字母数字字符
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff-]', '', text)

    # 移除多余的连字符
    text = re.sub(r'-+', '-', text)

    # 移除首尾连字符
    text = text.strip('-')

    return text


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def generate_random_string(length: int = 16) -> str:
    """生成随机字符串"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())


def format_datetime(dt: datetime, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """格式化日期时间"""
    if not dt:
        return ''
    return dt.strftime(fmt)


def format_date(dt: datetime) -> str:
    """格式化日期"""
    return format_datetime(dt, '%Y-%m-%d')


def time_ago(dt: datetime) -> str:
    """
        将日期时间转换为"多久以前"的格式

    Args:
        dt: 日期时间对象

    Returns:
        人性化的时间描述
    """
    if not dt:
        return ''

    now = datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f'{weeks} week{"s" if weeks > 1 else ""} ago'
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f'{months} month{"s" if months > 1 else ""} ago'
    else:
        years = int(seconds / 31536000)
        return f'{years} year{"s" if years > 1 else ""} ago'


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """截断文本"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def ensure_directory(path: str) -> str:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
    return path


def humanize_number(num: int) -> str:
    """将数字转换为人性化格式（如：1.2K, 3.5M）"""
    if num is None:
        return '0'

    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000:
            if num == int(num):
                return f'{int(num)}{unit}'
            return f'{num:.1f}{unit}'
        num /= 1000

    return f'{num:.1f}P'


def chunks(lst: List, n: int):
    """将列表分割成指定大小的块"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def deep_merge(dict1: dict, dict2: dict) -> dict:
    """深度合并两个字典"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
