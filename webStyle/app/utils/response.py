"""
统一响应格式
"""
from typing import Any, Dict, Optional
from flask import jsonify


def success_response(data: Any = None, message: str = 'Success', status_code: int = 200):
    """
    成功响应

    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码

    Returns:
        Flask响应对象
    """
    response = {
        'success': True,
        'message': message
    }

    if data is not None:
        response['data'] = data

    return jsonify(response), status_code


def error_response(message: str = 'Error', status_code: int = 400, errors: Optional[Dict] = None):
    """
    错误响应

    Args:
        message: 错误消息
        status_code: HTTP状态码
        errors: 详细错误信息

    Returns:
        Flask响应对象
    """
    response = {
        'success': False,
        'message': message
    }

    if errors:
        response['errors'] = errors

    return jsonify(response), status_code


def paginate_response(items: list, pagination_info: Dict, message: str = 'Success'):
    """
    分页响应

    Args:
        items: 数据项列表
        pagination_info: 分页信息
        message: 响应消息

    Returns:
        Flask响应对象
    """
    return success_response({
        'items': items,
        'pagination': pagination_info
    }, message)


def created_response(data: Any = None, message: str = 'Created successfully'):
    """创建成功响应（201）"""
    return success_response(data, message, 201)


def no_content_response():
    """无内容响应（204）"""
    return '', 204


def not_found_response(message: str = 'Resource not found'):
    """未找到响应（404）"""
    return error_response(message, 404)


def unauthorized_response(message: str = 'Unauthorized'):
    """未授权响应（401）"""
    return error_response(message, 401)


def forbidden_response(message: str = 'Forbidden'):
    """禁止访问响应（403）"""
    return error_response(message, 403)


def validation_error_response(errors: Dict, message: str = 'Validation error'):
    """验证错误响应（422）"""
    return error_response(message, 422, errors)


def server_error_response(message: str = 'Internal server error'):
    """服务器错误响应（500）"""
    return error_response(message, 500)
