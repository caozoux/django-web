"""
分页工具
"""
from typing import List, Any, Dict
from math import ceil


class Pagination:
    """分页类"""

    def __init__(self, query, page: int = 1, per_page: int = 20):
        """
        初始化分页

        Args:
            query: SQLAlchemy查询对象
            page: 当前页码
            per_page: 每页数量
        """
        self.page = max(1, page)
        self.per_page = min(max(1, per_page), 100)  # 最大100条
        self.total = query.count()
        self.pages = ceil(self.total / self.per_page) if self.total > 0 else 1

        # 计算偏移量
        offset = (self.page - 1) * self.per_page

        # 获取数据
        self.items: List[Any] = query.offset(offset).limit(self.per_page).all()

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1

    @property
    def next_num(self) -> int:
        """下一页页码"""
        return self.page + 1 if self.has_next else self.page

    @property
    def prev_num(self) -> int:
        """上一页页码"""
        return self.page - 1 if self.has_prev else self.page

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'page': self.page,
            'per_page': self.per_page,
            'total': self.total,
            'pages': self.pages,
            'has_next': self.has_next,
            'has_prev': self.has_prev,
            'next_num': self.next_num,
            'prev_num': self.prev_num
        }

    def iter_pages(self, left_edge: int = 2, left_current: int = 2,
                   right_current: int = 2, right_edge: int = 2):
        """
        生成页码迭代器（用于分页导航）

        Args:
            left_edge: 左边缘显示的页数
            left_current: 当前页左边显示的页数
            right_current: 当前页右边显示的页数
            right_edge: 右边缘显示的页数
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge or
                (num >= self.page - left_current and num <= self.page + right_current) or
                    num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def paginate(query, page: int = 1, per_page: int = 20, serializer=None) -> Dict:
    """
    分页辅助函数

    Args:
        query: SQLAlchemy查询对象
        page: 当前页码
        per_page: 每页数量
        serializer: 序列化函数

    Returns:
        分页结果字典
    """
    pagination = Pagination(query, page, per_page)

    items = pagination.items
    if serializer:
        items = [serializer(item) for item in items]

    return {
        'items': items,
        'pagination': pagination.to_dict()
    }
