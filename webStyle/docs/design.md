# WebStyle 系统架构设计文档

## 1. 架构概览

### 1.1 架构风格
采用 **分层架构 + 模块化设计**，结合 **前后端分离** 的思想。

### 1.2 整体架构图

```mermaid
graph TB
    subgraph "客户端层"
        PC[PC浏览器]
        Mobile[移动端]
        Admin[管理后台]
    end

    subgraph "接入层"
        Nginx[Nginx<br/>反向代理 + 静态资源]
    end

    subgraph "应用层 - Flask"
        Web[Web Blueprint<br/>前台页面]
        API[API Blueprint<br/>RESTful接口]
        AdminPanel[Admin Blueprint<br/>管理后台]
        Auth[Auth Blueprint<br/>认证授权]
    end

    subgraph "服务层"
        WebsiteService[网站服务]
        CategoryService[分类服务]
        UserService[用户服务]
        StatsService[统计服务]
        ScreenshotService[截图服务]
    end

    subgraph "数据访问层"
        ORM[SQLAlchemy ORM]
        Cache[Redis缓存]
        Queue[Celery任务队列]
    end

    subgraph "存储层"
        PG[(PostgreSQL<br/>主数据库)]
        Redis[(Redis<br/>缓存+会话)]
        FileStorage[文件存储<br/>本地/S3]
    end

    subgraph "外部服务"
        Puppeteer[Puppeteer<br/>网页截图]
        CDN[CDN<br/>图片加速]
    end

    PC --> Nginx
    Mobile --> Nginx
    Admin --> Nginx
    Nginx --> Web
    Nginx --> API
    Nginx --> AdminPanel

    Web --> WebsiteService
    Web --> CategoryService
    Web --> StatsService

    API --> Auth
    API --> WebsiteService
    API --> CategoryService
    API --> UserService

    AdminPanel --> WebsiteService
    AdminPanel --> CategoryService
    AdminPanel --> UserService

    ScreenshotService --> Puppeteer

    WebsiteService --> ORM
    CategoryService --> ORM
    UserService --> ORM
    StatsService --> ORM

    WebsiteService --> Cache
    CategoryService --> Cache
    StatsService --> Cache

    ScreenshotService --> Queue

    ORM --> PG
    Cache --> Redis
    Queue --> Redis
    FileStorage --> CDN
```

---

## 2. 模块设计

### 2.1 模块划分

```
webstyle/
├── app/                          # Flask应用主目录
│   ├── __init__.py               # 应用工厂
│   ├── config.py                # 配置管理
│   ├── extensions.py             # 扩展初始化
│   │
│   ├── models/                  # 数据模型层
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型
│   │   ├── website.py           # 网站模型
│   │   ├── category.py          # 分类模型
│   │   ├── tag.py               # 标签模型
│   │   └── base.py              # 基础模型
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── website_service.py   # 网站业务逻辑
│   │   ├── category_service.py  # 分类业务逻辑
│   │   ├── user_service.py      # 用户业务逻辑
│   │   ├── stats_service.py     # 统计业务逻辑
│   │   └── screenshot_service.py # 截图业务逻辑
│   │
│   ├── api/                     # RESTful API层
│   │   ├── __init__.py
│   │   ├── website.py           # 网站API
│   │   ├── category.py          # 分类API
│   │   ├── user.py              # 用户API
│   │   └── stats.py             # 统计API
│   │
│   ├── web/                     # 前台页面蓝图
│   │   ├── __init__.py
│   │   ├── routes.py            # 路由定义
│   │   └── forms.py             # 表单定义
│   │
│   ├── admin/                   # 管理后台蓝图
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   │
│   ├── auth/                    # 认证授权模块
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── utils.py             # JWT、密码加密等工具
│   │
│   ├── utils/                   # 工具类
│   │   ├── __init__.py
│   │   ├── validators.py        # 数据验证
│   │   ├── decorators.py        # 装饰器
│   │   ├── pagination.py        # 分页工具
│   │   └── helpers.py           # 辅助函数
│   │
│   ├── tasks/                   # Celery异步任务
│   │   ├── __init__.py
│   │   ├── screenshot.py        # 截图任务
│   │   └── stats.py             # 统计任务
│   │
│   ├── static/                  # 静态资源
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── uploads/
│   │
│   └── templates/               # Jinja2模板
│       ├── base.html            # 基础模板
│       ├── web/                 # 前台模板
│       │   ├── index.html
│       │   ├── categories.html
│       │   ├── website.html
│       │   └── analytics.html
│       └── admin/               # 管理后台模板
│           ├── dashboard.html
│           ├── websites.html
│           └── categories.html
│
├── tests/                       # 测试目录
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── migrations/                  # 数据库迁移
├── scripts/                     # 脚本目录
│   ├── init_db.py
│   └── seed_data.py
│
├── requirements.txt             # Python依赖
├── config.example.py            # 配置示例
├── docker-compose.yml           # Docker编排
├── Dockerfile                   # Docker镜像
├── nginx.conf                   # Nginx配置
└── run.py                       # 应用入口
```

---

## 3. 核心模块详细设计

### 3.1 数据模型层 (Models)

#### 3.1.1 基础模型 (base.py)
```python
from datetime import datetime
from app.extensions import db

class BaseModel(db.Model):
    """基础模型，提供通用字段和方法"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """保存到数据库"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """从数据库删除"""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

#### 3.1.2 用户模型 (user.py)
```python
from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # user, admin
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    # 关系
    favorites = db.relationship('Favorite', back_populates='user', lazy='dynamic')
    view_history = db.relationship('ViewHistory', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """是否管理员"""
        return self.role == 'admin'
```

#### 3.1.3 分类模型 (category.py)
```python
from .base import BaseModel

class Category(BaseModel):
    __tablename__ = 'categories'

    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    # 自引用关系
    parent = db.relationship('Category', remote_side=[id], backref='children')
    websites = db.relationship('Website', back_populates='category', lazy='dynamic')

    @property
    def website_count(self):
        """网站数量"""
        return self.websites.filter_by(status='active').count()

    def get_path(self):
        """获取分类路径"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return ' > '.join(reversed(path))
```

#### 3.1.4 网站模型 (website.py)
```python
from .base import BaseModel

class Website(BaseModel):
    __tablename__ = 'websites'

    name = db.Column(db.String(200), nullable=False, index=True)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    screenshots = db.Column(db.JSON, default=list)  # [{'url': '', 'type': 'homepage', 'width': 1920, 'height': 1080}]
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    industry = db.Column(db.String(50))
    color_scheme = db.Column(db.String(50))  # cold, warm, neutral, dark
    layout_type = db.Column(db.String(50))   # centered, split, fullscreen
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    favorites = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, active, inactive
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关系
    category = db.relationship('Category', back_populates='websites')
    tags = db.relationship('Tag', secondary='website_tags', backref='websites')
    creator = db.relationship('User', backref='websites')
    favorites_list = db.relationship('Favorite', back_populates='website', lazy='dynamic')

    def increment_view(self):
        """增加浏览量"""
        self.views += 1
        db.session.commit()

    def get_main_screenshot(self):
        """获取主截图"""
        return self.screenshots[0] if self.screenshots else None

    def to_detail_dict(self):
        """转换为详情字典"""
        data = self.to_dict()
        data['category_name'] = self.category.name
        data['tag_names'] = [tag.name for tag in self.tags]
        data['main_screenshot'] = self.get_main_screenshot()
        return data
```

#### 3.1.5 标签模型 (tag.py)
```python
from .base import BaseModel

class Tag(BaseModel):
    __tablename__ = 'tags'

    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    usage_count = db.Column(db.Integer, default=0)
```

#### 3.1.6 收藏模型 (favorite.py)
```python
from .base import BaseModel

class Favorite(BaseModel):
    __tablename__ = 'favorites'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)

    # 关系
    user = db.relationship('User', back_populates='favorites')
    website = db.relationship('Website', back_populates='favorites_list')

    __table_args__ = (db.UniqueConstraint('user_id', 'website_id', name='unique_user_website'),)
```

---

### 3.2 服务层 (Services)

#### 3.2.1 网站服务 (website_service.py)
```python
from typing import List, Dict, Optional
from sqlalchemy import or_
from app.models.website import Website
from app.models.category import Category
from app.extensions import cache
from app.utils.pagination import Pagination

class WebsiteService:
    """网站业务逻辑服务"""

    @staticmethod
    def get_websites_paginated(page: int = 1, per_page: int = 20,
                              category_id: Optional[int] = None,
                              industry: Optional[str] = None,
                              color_scheme: Optional[str] = None,
                              keyword: Optional[str] = None) -> Pagination:
        """分页获取网站列表"""
        query = Website.query.filter_by(status='active')

        # 筛选条件
        if category_id:
            query = query.filter_by(category_id=category_id)
        if industry:
            query = query.filter_by(industry=industry)
        if color_scheme:
            query = query.filter_by(color_scheme=color_scheme)
        if keyword:
            query = query.filter(or_(
                Website.name.ilike(f'%{keyword}%'),
                Website.description.ilike(f'%{keyword}%')
            ))

        # 排序：最新在前
        query = query.order_by(Website.created_at.desc())

        return Pagination(query, page, per_page)

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='website_hot')
    def get_hot_websites(limit: int = 10) -> List[Website]:
        """获取热门网站"""
        return Website.query.filter_by(status='active')\
            .order_by(Website.views.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='website_recent')
    def get_recent_websites(limit: int = 10) -> List[Website]:
        """获取最新网站"""
        return Website.query.filter_by(status='active')\
            .order_by(Website.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def get_similar_websites(website_id: int, limit: int = 6) -> List[Website]:
        """获取相似网站（基于同一分类）"""
        website = Website.query.get_or_404(website_id)
        return Website.query.filter(
            Website.category_id == website.category_id,
            Website.id != website_id,
            Website.status == 'active'
        ).limit(limit).all()

    @staticmethod
    def search_websites(keyword: str, page: int = 1, per_page: int = 20) -> Pagination:
        """搜索网站"""
        query = Website.query.filter(
            Website.status == 'active',
            or_(
                Website.name.ilike(f'%{keyword}%'),
                Website.description.ilike(f'%{keyword}%')
            )
        )
        return Pagination(query, page, per_page)

    @staticmethod
    def create_website(data: Dict) -> Website:
        """创建网站"""
        website = Website(**data)
        website.save()
        # 清除缓存
        cache.delete('website_hot')
        cache.delete('website_recent')
        return website

    @staticmethod
    def update_website(website_id: int, data: Dict) -> Website:
        """更新网站"""
        website = Website.query.get_or_404(website_id)
        for key, value in data.items():
            setattr(website, key, value)
        website.save()
        return website

    @staticmethod
    def delete_website(website_id: int):
        """删除网站（软删除）"""
        website = Website.query.get_or_404(website_id)
        website.status = 'inactive'
        website.save()
```

#### 3.2.2 截图服务 (screenshot_service.py)
```python
import asyncio
from typing import List, Dict
from app.tasks.screenshot import capture_screenshot
from app.extensions import celery

class ScreenshotService:
    """截图服务"""

    @staticmethod
    def capture_website_screenshots(url: str, website_id: int) -> Dict:
        """触发网站截图任务"""
        task = capture_screenshot.delay(url, website_id)
        return {
            'task_id': task.id,
            'status': 'pending'
        }

    @staticmethod
    def get_screenshot_status(task_id: str) -> Dict:
        """获取截图任务状态"""
        from app.extensions import celery
        result = celery.AsyncResult(task_id)
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None
        }

    @staticmethod
    def batch_capture(urls: List[str], website_ids: List[int]) -> List[Dict]:
        """批量截图"""
        tasks = []
        for url, website_id in zip(urls, website_ids):
            task = capture_screenshot.delay(url, website_id)
            tasks.append({
                'url': url,
                'website_id': website_id,
                'task_id': task.id
            })
        return tasks
```

#### 3.2.3 统计服务 (stats_service.py)
```python
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.website import Website
from app.models.category import Category
from app.models.user import User
from app.models.favorite import Favorite
from app.extensions import cache

class StatsService:
    """统计服务"""

    @staticmethod
    @cache.cached(timeout=1800, key_prefix='stats_overview')
    def get_overview_stats() -> Dict:
        """获取概览统计"""
        return {
            'total_websites': Website.query.count(),
            'active_websites': Website.query.filter_by(status='active').count(),
            'total_users': User.query.count(),
            'total_categories': Category.query.filter_by(is_active=True).count(),
            'total_favorites': Favorite.query.count()
        }

    @staticmethod
    def get_category_distribution() -> List[Dict]:
        """获取分类分布"""
        result = db.session.query(
            Category.name,
            func.count(Website.id).label('count')
        ).outerjoin(Website)\
         .filter(Category.is_active == True)\
         .group_by(Category.id, Category.name)\
         .order_by(func.count(Website.id).desc())\
         .all()

        return [{'category': name, 'count': count} for name, count in result]

    @staticmethod
    def get_style_trends(days: int = 30) -> List[Dict]:
        """获取风格趋势"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        result = db.session.query(
            func.date(Website.created_at).label('date'),
            Category.name.label('category'),
            func.count(Website.id).label('count')
        ).join(Category)\
         .filter(Website.created_at >= start_date)\
         .group_by(func.date(Website.created_at), Category.name)\
         .order_by(func.date(Website.created_at))\
         .all()

        # 转换为ECharts数据格式
        dates = sorted(list(set([r[0] for r in result])))
        categories = list(set([r[1] for r in result]))

        series_data = []
        for category in categories:
            category_data = {
                'name': category,
                'data': []
            }
            for date in dates:
                count = next((r[2] for r in result if r[0] == date and r[1] == category), 0)
                category_data['data'].append(count)
            series_data.append(category_data)

        return {
            'dates': [str(d) for d in dates],
            'series': series_data
        }

    @staticmethod
    def get_top_websites(limit: int = 10, metric: str = 'views') -> List[Dict]:
        """获取TOP网站"""
        query = Website.query.filter_by(status='active')
        if metric == 'views':
            query = query.order_by(Website.views.desc())
        elif metric == 'likes':
            query = query.order_by(Website.likes.desc())
        elif metric == 'favorites':
            query = query.order_by(Website.favorites.desc())

        websites = query.limit(limit).all()
        return [{'id': w.id, 'name': w.name, 'url': w.url, 'value': getattr(w, metric)} for w in websites]
```

---

### 3.3 API层

#### 3.3.1 网站API (api/website.py)
```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app.services.website_service import WebsiteService
from app.services.screenshot_service import ScreenshotService

website_bp = Blueprint('website', __name__, url_prefix='/api/websites')

@website_bp.route('', methods=['GET'])
def list_websites():
    """获取网站列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    industry = request.args.get('industry')
    color_scheme = request.args.get('color_scheme')
    keyword = request.args.get('keyword')

    pagination = WebsiteService.get_websites_paginated(
        page=page,
        per_page=per_page,
        category_id=category_id,
        industry=industry,
        color_scheme=color_scheme,
        keyword=keyword
    )

    return jsonify({
        'data': [w.to_detail_dict() for w in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })

@website_bp.route('/<int:id>', methods=['GET'])
def get_website(id):
    """获取网站详情"""
    website = WebsiteService.get_by_id(id)
    website.increment_view()
    return jsonify(website.to_detail_dict())

@website_bp.route('/<int:id>/similar', methods=['GET'])
def get_similar(id):
    """获取相似网站"""
    websites = WebsiteService.get_similar_websites(id)
    return jsonify([w.to_detail_dict() for w in websites])

@website_bp.route('/<int:id>/screenshot', methods=['POST'])
@jwt_required()
def capture_screenshot(id):
    """触发截图任务"""
    website = WebsiteService.get_by_id(id)
    result = ScreenshotService.capture_website_screenshots(website.url, id)
    return jsonify(result)

@website_bp.route('/hot', methods=['GET'])
def get_hot():
    """获取热门网站"""
    websites = WebsiteService.get_hot_websites(limit=10)
    return jsonify([w.to_detail_dict() for w in websites])

@website_bp.route('/recent', methods=['GET'])
def get_recent():
    """获取最新网站"""
    websites = WebsiteService.get_recent_websites(limit=10)
    return jsonify([w.to_detail_dict() for w in websites])

@website_bp.route('/search', methods=['GET'])
def search():
    """搜索网站"""
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = WebsiteService.search_websites(keyword, page, per_page)
    return jsonify({
        'data': [w.to_detail_dict() for w in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })
```

#### 3.3.2 统计API (api/stats.py)
```python
from flask import Blueprint, jsonify
from app.services.stats_service import StatsService

stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')

@stats_bp.route('/overview', methods=['GET'])
def get_overview():
    """获取概览统计"""
    stats = StatsService.get_overview_stats()
    return jsonify(stats)

@stats_bp.route('/categories/distribution', methods=['GET'])
def get_category_distribution():
    """获取分类分布"""
    data = StatsService.get_category_distribution()
    return jsonify(data)

@stats_bp.route('/trends', methods=['GET'])
def get_trends():
    """获取风格趋势"""
    days = request.args.get('days', 30, type=int)
    data = StatsService.get_style_trends(days)
    return jsonify(data)

@stats_bp.route('/top', methods=['GET'])
def get_top():
    """获取TOP网站"""
    limit = request.args.get('limit', 10, type=int)
    metric = request.args.get('metric', 'views')
    data = StatsService.get_top_websites(limit, metric)
    return jsonify(data)
```

---

### 3.4 前端集成 (ECharts)

#### 3.4.1 数据分析页面模板
```html
<!-- templates/web/analytics.html -->
{% extends 'base.html' %}

{% block title %}数据分析 - WebStyle{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>网站风格数据分析</h2>

    <!-- 统计卡片 -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">网站总数</h5>
                    <h2 id="total-websites">-</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">活跃网站</h5>
                    <h2 id="active-websites">-</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">用户总数</h5>
                    <h2 id="total-users">-</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">收藏总数</h5>
                    <h2 id="total-favorites">-</h2>
                </div>
            </div>
        </div>
    </div>

    <!-- 图表区域 -->
    <div class="row">
        <!-- 风格趋势图 -->
        <div class="col-md-8 mb-4">
            <div class="card">
                <div class="card-header">
                    <h5>风格流行趋势</h5>
                </div>
                <div class="card-body">
                    <div id="trend-chart" style="height: 400px;"></div>
                </div>
            </div>
        </div>

        <!-- 分类占比图 -->
        <div class="col-md-4 mb-4">
            <div class="card">
                <div class="card-header">
                    <h5>风格分类占比</h5>
                </div>
                <div class="card-body">
                    <div id="pie-chart" style="height: 400px;"></div>
                </div>
            </div>
        </div>

        <!-- TOP榜单 -->
        <div class="col-md-12">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>热门网站 TOP 10</h5>
                    <select id="top-metric" class="form-select" style="width: 150px;">
                        <option value="views">浏览量</option>
                        <option value="likes">点赞数</option>
                        <option value="favorites">收藏数</option>
                    </select>
                </div>
                <div class="card-body">
                    <div id="bar-chart" style="height: 400px;"></div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
    // 初始化图表
    const trendChart = echarts.init(document.getElementById('trend-chart'));
    const pieChart = echarts.init(document.getElementById('pie-chart'));
    const barChart = echarts.init(document.getElementById('bar-chart'));

    // 加载概览统计
    async function loadOverview() {
        const response = await fetch('/api/stats/overview');
        const data = await response.json();
        document.getElementById('total-websites').textContent = data.total_websites;
        document.getElementById('active-websites').textContent = data.active_websites;
        document.getElementById('total-users').textContent = data.total_users;
        document.getElementById('total-favorites').textContent = data.total_favorites;
    }

    // 加载趋势图
    async function loadTrendChart() {
        const response = await fetch('/api/stats/trends?days=30');
        const data = await response.json();

        const option = {
            title: { text: '近30天风格趋势' },
            tooltip: { trigger: 'axis' },
            legend: { data: data.series.map(s => s.name) },
            xAxis: { type: 'category', data: data.dates },
            yAxis: { type: 'value' },
            series: data.series.map(s => ({
                name: s.name,
                type: 'line',
                data: s.data,
                smooth: true
            }))
        };
        trendChart.setOption(option);
    }

    // 加载饼图
    async function loadPieChart() {
        const response = await fetch('/api/stats/categories/distribution');
        const data = await response.json();

        const option = {
            tooltip: { trigger: 'item' },
            legend: { orient: 'vertical', left: 'left' },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
                data: data.map(d => ({ value: d.count, name: d.category }))
            }]
        };
        pieChart.setOption(option);
    }

    // 加载TOP榜单
    async function loadTopChart(metric = 'views') {
        const response = await fetch(`/api/stats/top?limit=10&metric=${metric}`);
        const data = await response.json();

        const option = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            xAxis: {
                type: 'value'
            },
            yAxis: {
                type: 'category',
                data: data.map(d => d.name)
            },
            series: [{
                type: 'bar',
                data: data.map(d => d.value),
                itemStyle: { color: '#5470c6' }
            }]
        };
        barChart.setOption(option);
    }

    // 初始化
    loadOverview();
    loadTrendChart();
    loadPieChart();
    loadTopChart();

    // 监听指标变化
    document.getElementById('top-metric').addEventListener('change', function() {
        loadTopChart(this.value);
    });

    // 响应式调整
    window.addEventListener('resize', () => {
        trendChart.resize();
        pieChart.resize();
        barChart.resize();
    });
</script>
{% endblock %}
```

---

## 4. 数据库设计

### 4.1 ER图

```mermaid
erDiagram
    USER ||--o{ WEBSITE : creates
    USER ||--o{ FAVORITE : has
    USER ||--o{ VIEW_HISTORY : has

    CATEGORY ||--o{ WEBSITE : contains
    CATEGORY ||--o{ CATEGORY : has_subcategories

    WEBSITE ||--o{ FAVORITE : is_favorited
    WEBSITE ||--o{ VIEW_HISTORY : is_viewed
    WEBSITE }o--o{ TAG : has

    TAG ||--o{ WEBSITE : tags

    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        string avatar
        string role
        boolean is_active
        datetime last_login
    }

    CATEGORY {
        int id PK
        string name
        string slug UK
        text description
        string icon
        int parent_id FK
        int sort_order
        boolean is_active
    }

    WEBSITE {
        int id PK
        string name
        string url
        text description
        json screenshots
        int category_id FK
        string industry
        string color_scheme
        string layout_type
        int views
        int likes
        int favorites
        string status
        int created_by FK
    }

    TAG {
        int id PK
        string name UK
        string slug UK
        int usage_count
    }

    FAVORITE {
        int id PK
        int user_id FK
        int website_id FK
    }

    VIEW_HISTORY {
        int id PK
        int user_id FK
        int website_id FK
    }
```

---

## 5. 部署架构

### 5.1 部署架构图

```mermaid
graph TB
    User[用户]

    subgraph "负载均衡"
        LB[Nginx LB]
    end

    subgraph "Web服务器集群"
        Web1[Flask App 1]
        Web2[Flask App 2]
        Web3[Flask App 3]
    end

    subgraph "Worker集群"
        Worker1[Celery Worker 1<br/>截图任务]
        Worker2[Celery Worker 2<br/>统计任务]
    end

    subgraph "存储层"
        RedisCluster[Redis Cluster<br/>缓存+队列]
        PGMaster[PostgreSQL Master]
        PGSlave[PostgreSQL Slave<br/>读写分离]
        MinIO[MinIO<br/>对象存储]
    end

    subgraph "CDN"
        CDN[CDN<br/>图片加速]
    end

    User --> LB
    LB --> Web1
    LB --> Web2
    LB --> Web3

    Web1 --> RedisCluster
    Web2 --> RedisCluster
    Web3 --> RedisCluster

    Web1 --> PGMaster
    Web2 --> PGMaster
    Web3 --> PGMaster

    Worker1 --> RedisCluster
    Worker2 --> RedisCluster

    Worker1 --> MinIO
    MinIO --> CDN
    Web1 --> CDN
    Web2 --> CDN
    Web3 --> CDN

    PGMaster --> PGSlave
```

### 5.2 Docker Compose配置

```yaml
version: '3.8'

services:
  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./app/static:/var/www/static
    depends_on:
      - flask
    networks:
      - webstyle_network

  # Flask 应用
  flask:
    build: .
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://webstyle:webstyle123@pg-master:5432/webstyle
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - pg-master
      - redis
    networks:
      - webstyle_network

  # Celery Worker
  celery-worker:
    build: .
    command: celery -A app.celery worker -l info --concurrency=2
    environment:
      - DATABASE_URL=postgresql://webstyle:webstyle123@pg-master:5432/webstyle
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - pg-master
      - minio
    networks:
      - webstyle_network

  # PostgreSQL 主库
  pg-master:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=webstyle
      - POSTGRES_USER=webstyle
      - POSTGRES_PASSWORD=webstyle123
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=replicator123
    volumes:
      - pg_master_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - webstyle_network

  # PostgreSQL 从库
  pg-slave:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=webstyle
      - POSTGRES_USER=webstyle
      - POSTGRES_PASSWORD=webstyle123
      - PGUSER=webstyle
    command: >
      bash -c "
      until pg_isready -h pg-master; do sleep 1; done &&
      rm -rf /var/lib/postgresql/data/* &&
      pg_basebackup -h pg-master -D /var/lib/postgresql/data -U replicator -P &&
      echo 'standby_mode = on' >> /var/lib/postgresql/data/recovery.conf &&
      echo 'primary_conninfo = host=pg-master port=5432 user=replicator password=replicator123' >> /var/lib/postgresql/data/recovery.conf &&
      postgres"
    networks:
      - webstyle_network

  # Redis
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - webstyle_network

  # MinIO 对象存储
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin123
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    networks:
      - webstyle_network

  # Flower (Celery监控)
  flower:
    build: .
    command: celery -A app.celery flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - webstyle_network

volumes:
  pg_master_data:
  redis_data:
  minio_data:

networks:
  webstyle_network:
    driver: bridge
```

---

## 6. 安全设计

### 6.1 安全措施

| 安全领域 | 措施 |
|---------|------|
| **认证授权** | JWT Token + 密码bcrypt加密 |
| **SQL注入防护** | SQLAlchemy ORM参数化查询 |
| **XSS防护** | Jinja2自动转义 + Content Security Policy |
| **CSRF防护** | Flask-WTF CSRF Token |
| **HTTPS** | Let's Encrypt SSL证书 |
| **限流** | Flask-Limiter API限流 |
| **文件上传** | 类型验证 + 大小限制 + 病毒扫描 |
| **敏感数据** | 环境变量存储，不提交到代码库 |

### 6.2 权限设计

```python
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models.user import User

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin():
            return jsonify({'error': 'Admin permission required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """登录权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

---

## 7. 性能优化策略

### 7.1 缓存策略

```python
from app.extensions import cache

# 装饰器缓存
@cache.cached(timeout=3600, key_prefix='category_list')
def get_all_categories():
    return Category.query.filter_by(is_active=True).all()

# 函数缓存
@cache.memoize(timeout=1800)
def get_website_detail(website_id):
    return Website.query.get(website_id)

# 删除缓存
@website_bp.route('/<int:id>', methods=['PUT'])
def update_website(id):
    website = WebsiteService.update_website(id, request.json)
    cache.delete_memoized(get_website_detail, id)
    return jsonify(website.to_dict())
```

### 7.2 数据库优化

- **索引优化**：为常用查询字段添加索引
  ```python
  # User模型
  username = db.Column(db.String(50), index=True)
  email = db.Column(db.String(100), index=True)

  # Website模型
  name = db.Column(db.String(200), index=True)
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), index=True)
  status = db.Column(db.String(20), index=True)
  ```

- **查询优化**：使用eager loading避免N+1查询
  ```python
  # 不好的方式
  websites = Website.query.all()
  for w in websites:
      print(w.category.name)  # N+1查询

  # 好的方式
  websites = Website.query.options(joinedload(Website.category)).all()
  ```

### 7.3 前端优化

- **图片懒加载**：使用Intersection Observer API
- **CDN加速**：静态资源通过CDN分发
- **代码分割**：按需加载JavaScript模块
- **Gzip压缩**：Nginx启用gzip

---

## 8. 监控与日志

### 8.1 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """配置日志"""
    if not app.debug:
        # 文件日志
        file_handler = RotatingFileHandler(
            'logs/webstyle.log',
            maxBytes=1024 * 1024 * 100,  # 100MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # 错误日志
        error_handler = RotatingFileHandler(
            'logs/error.log',
            maxBytes=1024 * 1024 * 100,
            backupCount=10
        )
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        error_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('WebStyle startup')
```

### 8.2 监控指标

- **应用指标**：响应时间、错误率、请求量
- **系统指标**：CPU、内存、磁盘、网络
- **业务指标**：PV/UV、注册量、收藏量
- **Celery监控**：任务队列长度、执行时间、失败率

---

## 9. 测试策略

### 9.1 测试金字塔

```
        /\
       /E2E\       端到端测试 (10%)
      /------\
     /  集成  \    集成测试 (30%)
    /----------\
   /    单元     \  单元测试 (60%)
  /--------------\
```

### 9.2 单元测试示例

```python
import pytest
from app.services.website_service import WebsiteService
from app.models.website import Website
from app import create_app, db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_websites_paginated(app):
    """测试分页获取网站"""
    with app.app_context():
        # 创建测试数据
        for i in range(25):
            Website(name=f'Website {i}', url=f'http://example{i}.com',
                    category_id=1, status='active').save()

        # 测试
        pagination = WebsiteService.get_websites_paginated(page=1, per_page=20)
        assert len(pagination.items) == 20
        assert pagination.total == 25
        assert pagination.pages == 2
```

---

## 10. 技术风险评估

| 风险项 | 风险等级 | 缓解措施 |
|--------|---------|---------|
| 截图失败率高 | 高 | 重试机制 + 手动上传备用 |
| 图片存储成本 | 中 | 使用对象存储 + CDN + 图片压缩 |
| 并发性能 | 中 | 缓存 + 数据库读写分离 + 负载均衡 |
| 数据版权 | 低 | 添加免责声明 + 用户协议 |
| 数据库迁移 | 低 | 使用Alembic管理迁移 |

---

## 11. 项目交付清单

### 11.1 代码交付
- [ ] 完整的Flask应用代码
- [ ] 数据库迁移脚本
- [ ] 初始化数据脚本
- [ ] Docker部署文件

### 11.2 文档交付
- [ ] API文档（Swagger）
- [ ] 部署文档
- [ ] 运维手册
- [ ] 用户手册

### 11.3 测试交付
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试
- [ ] 性能测试报告

---

## 12. 总结

本设计文档详细阐述了WebStyle网站风格浏览系统的架构设计，包括：

1. **分层架构**：清晰的MVC分层，职责分明
2. **模块化设计**：易于扩展和维护
3. **高性能**：多级缓存 + 读写分离 + CDN
4. **高可用**：集群部署 + 负载均衡
5. **易部署**：Docker容器化部署
6. **数据可视化**：ECharts实现丰富的数据分析图表

项目可以按照MVP -> 核心功能 -> 优化上线的节奏逐步推进，确保每个阶段都有可交付的成果。
