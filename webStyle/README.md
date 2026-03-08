# WebStyle - 网站风格浏览系统

一个基于 Flask 的网站风格浏览和参考平台，提供主流网站风格分类、快照展示和数据分析功能。

## 项目简介

WebStyle 帮助设计师和开发者：
- 🎨 浏览和发现主流网站设计风格
- 📸 查看网站样式快照和截图
- 📊 分析设计趋势和流行风格
- ⭐ 收藏和管理设计灵感
- 🔍 搜索和筛选特定风格的网站

## 技术栈

### 后端
- **Web框架**: Flask 3.x
- **数据库**: PostgreSQL 15 + Redis 7
- **ORM**: SQLAlchemy
- **任务队列**: Celery + Redis
- **爬虫/截图**: Puppeteer
- **认证**: Flask-JWT-Extended

### 前端
- **基础**: HTML5 + CSS3 + Vanilla JavaScript
- **图表**: ECharts 5.x
- **UI框架**: Bootstrap 5
- **构建**: Webpack 5

### 运维
- **容器**: Docker + Docker Compose
- **Web服务器**: Nginx
- **应用服务器**: Gunicorn
- **监控**: Flower (Celery Monitor)

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+ (仅开发环境)
- Docker & Docker Compose (生产环境)
- PostgreSQL 15+
- Redis 7+

### 开发环境启动

#### 1. 克隆项目

```bash
git clone <repository-url>
cd webStyle
```

#### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
cp config.example.py config.py
# 编辑 config.py，设置数据库连接等配置
```

#### 5. 初始化数据库

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 填充初始数据
python scripts/seed_data.py
```

#### 6. 启动服务

```bash
# 启动Flask应用
flask run

# 启动Celery Worker（新终端）
celery -A app.celery worker -l info

# 启动Celery Beat（可选，用于定时任务）
celery -A app.celery beat -l info
```

#### 7. 访问应用

- 前台：http://localhost:5000
- API文档：http://localhost:5000/api/docs
- Celery监控：http://localhost:5555

### Docker 部署

#### 快速启动

```bash
docker-compose up -d
```

#### 查看日志

```bash
docker-compose logs -f
```

#### 停止服务

```bash
docker-compose down
```

## 项目结构

```
webStyle/
├── app/                    # Flask应用主目录
│   ├── __init__.py         # 应用工厂
│   ├── config.py          # 配置管理
│   ├── extensions.py      # 扩展初始化
│   │
│   ├── models/            # 数据模型
│   │   ├── user.py
│   │   ├── website.py
│   │   ├── category.py
│   │   └── tag.py
│   │
│   ├── services/          # 业务逻辑层
│   │   ├── website_service.py
│   │   ├── category_service.py
│   │   └── stats_service.py
│   │
│   ├── api/               # RESTful API
│   │   ├── website.py
│   │   ├── category.py
│   │   └── stats.py
│   │
│   ├── web/               # 前台页面
│   ├── admin/             # 管理后台
│   ├── auth/              # 认证授权
│   │
│   ├── tasks/             # Celery异步任务
│   │   └── screenshot.py
│   │
│   ├── utils/             # 工具类
│   ├── static/            # 静态资源
│   └── templates/         # Jinja2模板
│
├── tests/                 # 测试代码
├── migrations/            # 数据库迁移
├── scripts/               # 脚本工具
├── docs/                  # 文档
│   ├── requirement.md          # 需求文档
│   ├── requirement_detailed.md # 详细需求
│   └── design.md              # 架构设计
│
├── requirements.txt       # Python依赖
├── docker-compose.yml     # Docker编排
├── Dockerfile             # Docker镜像
├── nginx.conf             # Nginx配置
└── README.md              # 本文件
```

## 核心功能

### 1. 网站浏览
- 📁 风格分类浏览（扁平化、卡片式、暗色模式等）
- 🖼️ 网站快照展示
- 🔍 搜索和筛选
- 🔄 相似推荐

### 2. 数据分析
- 📈 风格趋势图（ECharts折线图）
- 🥧 风格占比图（ECharts饼图）
- 🏆 TOP榜单（浏览量/点赞/收藏）
- 📊 行业与风格交叉分析

### 3. 用户功能
- 👤 用户注册/登录
- ⭐ 收藏网站
- 👍 点赞网站
- 💬 评论（可选）
- 📜 浏览历史

### 4. 管理后台
- 📝 网站管理（增删改查）
- 🏷️ 分类管理
- 👥 用户管理
- 📉 数据统计
- 🖼️ 截图任务管理

## API文档

### 获取网站列表

```http
GET /api/websites?page=1&per_page=20&category_id=1
```

**响应示例：**

```json
{
  "data": [
    {
      "id": 1,
      "name": "示例网站",
      "url": "https://example.com",
      "description": "这是一个示例网站",
      "screenshots": [
        {"url": "/uploads/screenshot1.jpg", "type": "homepage"}
      ],
      "category_name": "扁平化",
      "views": 1000
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

### 获取统计数据

```http
GET /api/stats/trends?days=30
```

**响应示例：**

```json
{
  "dates": ["2024-01-01", "2024-01-02", ...],
  "series": [
    {
      "name": "扁平化",
      "data": [10, 15, 20, ...]
    },
    {
      "name": "卡片式",
      "data": [5, 8, 12, ...]
    }
  ]
}
```

更多API文档请访问：`/api/docs`

## 开发指南

### 添加新的API端点

1. 在 `app/api/` 创建或编辑文件
2. 定义蓝图和路由
3. 在 `app/__init__.py` 注册蓝图

```python
# app/api/example.py
from flask import Blueprint, jsonify

example_bp = Blueprint('example', __name__, url_prefix='/api/example')

@example_bp.route('', methods=['GET'])
def list_examples():
    return jsonify({'data': []})
```

### 添加新的页面

1. 在 `app/templates/web/` 创建模板
2. 在 `app/web/routes.py` 添加路由

```python
# app/web/routes.py
from flask import render_template

@web_bp.route('/example')
def example_page():
    return render_template('web/example.html')
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_website.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 数据库迁移

```bash
# 生成迁移脚本
flask db migrate -m "描述变更"

# 应用迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

## 性能优化

### 缓存策略

```python
from app.extensions import cache

# 装饰器缓存
@cache.cached(timeout=3600, key_prefix='category_list')
def get_categories():
    return Category.query.all()

# 手动缓存
def get_website(id):
    key = f'website:{id}'
    data = cache.get(key)
    if not data:
        data = Website.query.get(id)
        cache.set(key, data, timeout=1800)
    return data
```

### 数据库优化

```python
# 使用 join 避免N+1查询
websites = Website.query.options(
    joinedload(Website.category)
).all()

# 批量插入
db.session.bulk_insert_mappings(Website, websites_data)
db.session.commit()
```

## 部署

### 环境变量配置

```bash
# config.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://webstyle:webstyle123@localhost:5432/webstyle'
    )
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
```

### Nginx配置

```nginx
upstream flask_app {
    server flask:5000;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /var/www/static;
        expires 30d;
    }
}
```

## 监控

### Celery监控

访问 Flower：http://localhost:5555

### 应用日志

```bash
# 查看实时日志
tail -f logs/webstyle.log

# 查看错误日志
tail -f logs/error.log
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 联系方式

- 项目地址：https://github.com/yourusername/webStyle
- 问题反馈：https://github.com/yourusername/webStyle/issues
- 邮箱：your.email@example.com

## 致谢

- Flask 框架：https://flask.palletsprojects.com/
- ECharts：https://echarts.apache.org/
- Bootstrap：https://getbootstrap.com/

## 更新日志

### v1.0.0 (2024-03)
- 初始版本发布
- 实现核心功能：网站浏览、分类展示、数据分析
- 完成管理后台基础功能
- Docker部署支持
