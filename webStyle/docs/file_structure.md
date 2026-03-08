# 项目目录结构说明

本文档详细说明 WebStyle 项目的目录结构和文件用途。

## 完整目录树

```
webStyle/
├── app/                                    # Flask 应用主目录
│   ├── __init__.py                         # 应用工厂，初始化 Flask 应用
│   ├── config.py                           # 配置管理（开发/测试/生产环境）
│   ├── extensions.py                       # 扩展初始化（数据库、缓存、Celery等）
│   │
│   ├── models/                             # 数据模型层（SQLAlchemy ORM）
│   │   ├── __init__.py                    # 模型包，导出所有模型
│   │   ├── base.py                        # 基础模型类（提供通用字段和方法）
│   │   ├── user.py                        # 用户模型（账号、权限等）
│   │   ├── website.py                     # 网站模型（网站信息、截图等）
│   │   ├── category.py                    # 分类模型（风格分类）
│   │   ├── tag.py                         # 标签模型
│   │   ├── favorite.py                    # 收藏模型
│   │   └── view_history.py                # 浏览历史模型
│   │
│   ├── services/                           # 业务逻辑层（Service Layer）
│   │   ├── __init__.py
│   │   ├── website_service.py             # 网站业务逻辑
│   │   ├── category_service.py            # 分类业务逻辑
│   │   ├── user_service.py                # 用户业务逻辑
│   │   ├── stats_service.py               # 统计业务逻辑
│   │   ├── screenshot_service.py          # 截图业务逻辑
│   │   └── search_service.py              # 搜索业务逻辑
│   │
│   ├── api/                                # RESTful API 层
│   │   ├── __init__.py
│   │   ├── website.py                     # 网站相关API
│   │   ├── category.py                    # 分类相关API
│   │   ├── user.py                        # 用户相关API
│   │   ├── auth.py                        # 认证相关API
│   │   └── stats.py                       # 统计相关API
│   │
│   ├── web/                                # 前台页面蓝图
│   │   ├── __init__.py                    # 蓝图初始化
│   │   ├── routes.py                      # 路由定义
│   │   └── forms.py                       # 表单定义（如果需要）
│   │
│   ├── admin/                              # 管理后台蓝图
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   │
│   ├── auth/                               # 认证授权模块
│   │   ├── __init__.py
│   │   ├── routes.py                      # 登录/注册路由
│   │   └── utils.py                       # JWT工具、密码加密等
│   │
│   ├── tasks/                              # Celery 异步任务
│   │   ├── __init__.py
│   │   ├── screenshot.py                  # 截图任务（Puppeteer）
│   │   ├── stats.py                       # 统计计算任务
│   │   └── email.py                       # 邮件发送任务（可选）
│   │
│   ├── utils/                              # 工具类和辅助函数
│   │   ├── __init__.py
│   │   ├── validators.py                  # 数据验证器
│   │   ├── decorators.py                  # 装饰器（权限、缓存等）
│   │   ├── pagination.py                 # 分页工具
│   │   ├── helpers.py                     # 辅助函数
│   │   └── response.py                    # 统一响应格式
│   │
│   ├── static/                             # 静态资源目录
│   │   ├── css/
│   │   │   ├── main.css                   # 主样式文件
│   │   │   └── analytics.css              # 数据分析页样式
│   │   ├── js/
│   │   │   ├── main.js                    # 主JS文件
│   │   │   ├── charts.js                  # ECharts配置
│   │   │   └── lazyload.js                # 图片懒加载
│   │   ├── images/
│   │   │   ├── logo.png                   # 网站Logo
│   │   │   └── default-avatar.png         # 默认头像
│   │   └── uploads/                       # 上传文件目录
│   │       ├── screenshots/               # 网站截图
│   │       ├── avatars/                   # 用户头像
│   │       └── others/                    # 其他文件
│   │
│   ├── templates/                          # Jinja2 模板目录
│   │   ├── base.html                      # 基础模板
│   │   ├── errors/                        # 错误页面
│   │   │   ├── 404.html
│   │   │   ├── 500.html
│   │   │   └── 403.html
│   │   │
│   │   ├── web/                           # 前台页面模板
│   │   │   ├── index.html                 # 首页
│   │   │   ├── categories.html            # 分类列表页
│   │   │   ├── category_detail.html      # 分类详情页
│   │   │   ├── website.html               # 网站详情页
│   │   │   ├── search.html                # 搜索结果页
│   │   │   ├── analytics.html             # 数据分析页
│   │   │   └── user/                      # 用户中心
│   │   │       ├── profile.html
│   │   │       ├── favorites.html
│   │   │       └── history.html
│   │   │
│   │   ├── admin/                         # 管理后台模板
│   │   │   ├── layout.html                # 后台布局
│   │   │   ├── dashboard.html             # 仪表盘
│   │   │   ├── websites/                  # 网站管理
│   │   │   │   ├── list.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   ├── categories/                # 分类管理
│   │   │   │   ├── list.html
│   │   │   │   └── form.html
│   │   │   ├── users/                     # 用户管理
│   │   │   │   └── list.html
│   │   │   └── stats/                     # 统计分析
│   │   │       └── overview.html
│   │   │
│   │   └── auth/                          # 认证页面
│   │       ├── login.html
│   │       ├── register.html
│   │       └── forgot_password.html
│   │
│   └── celery.py                           # Celery 配置和初始化
│
├── tests/                                   # 测试目录
│   ├── __init__.py
│   ├── conftest.py                         # Pytest 配置和Fixture
│   ├── unit/                               # 单元测试
│   │   ├── __init__.py
│   │   ├── test_models.py                 # 模型测试
│   │   ├── test_services.py               # 服务层测试
│   │   └── test_utils.py                  # 工具类测试
│   ├── integration/                        # 集成测试
│   │   ├── __init__.py
│   │   ├── test_api.py                    # API测试
│   │   └── test_routes.py                 # 路由测试
│   └── e2e/                                # 端到端测试
│       └── test_user_flow.py
│
├── migrations/                              # 数据库迁移文件（Alembic）
│   ├── versions/                           # 迁移版本文件
│   │   ├── 001_initial.py                 # 初始迁移
│   │   └── 002_add_tags.py                # 添加标签功能
│   ├── env.py                              # Alembic环境配置
│   ├── script.py.mako                      # 迁移脚本模板
│   └── README                              # 迁移说明
│
├── scripts/                                 # 脚本工具目录
│   ├── init_db.py                          # 初始化数据库
│   ├── seed_data.py                        # 填充测试数据
│   ├── create_admin.py                     # 创建管理员账号
│   ├── cleanup_cache.py                    # 清理缓存
│   └── backup_db.py                        # 数据库备份
│
├── docs/                                    # 文档目录
│   ├── requirement.md                      # 原始需求文档
│   ├── requirement_detailed.md             # 详细需求文档
│   ├── design.md                           # 架构设计文档
│   ├── roadmap.md                          # 项目路线图
│   ├── api.md                              # API文档（可选，使用Swagger）
│   └── deployment.md                       # 部署文档
│
├── logs/                                    # 日志目录
│   ├── webstyle.log                        # 应用日志
│   ├── error.log                           # 错误日志
│   ├── access.log                          # 访问日志
│   └── celery.log                          # Celery日志
│
├── .git/                                    # Git版本控制
│
├── .github/                                 # GitHub配置
│   ├── workflows/                          # GitHub Actions工作流
│   │   ├── test.yml                        # 测试工作流
│   │   └── deploy.yml                      # 部署工作流
│   └── ISSUE_TEMPLATE/                     # Issue模板
│
├── .claude/                                 # Claude AI配置
│   └── settings.local.json
│
├── .gitignore                               # Git忽略文件配置
├── .env.example                             # 环境变量示例
├── .dockerignore                            # Docker忽略文件配置
├── Dockerfile                               # Docker镜像构建文件
├── docker-compose.yml                       # Docker编排文件
├── docker-compose.prod.yml                  # 生产环境Docker编排
├── docker-compose.dev.yml                   # 开发环境Docker编排
│
├── requirements.txt                         # Python依赖
│   # 包含所有生产环境依赖
│   # Flask==3.0.0
│   # SQLAlchemy==2.0.0
│   # ...
│
├── requirements-dev.txt                     # 开发环境依赖
│   # pytest==7.4.0
│   # black==23.0.0
│   # flake8==6.0.0
│   # ...
│
├── config.example.py                        # 配置文件示例
├── nginx.conf                               # Nginx配置文件
├── gunicorn.conf.py                         # Gunicorn配置
├── run.py                                   # 应用启动入口
├── wsgi.py                                  # WSGI入口（用于生产）
│
├── webpack.config.js                        # Webpack配置（可选）
├── package.json                             # Node.js依赖（可选）
└── README.md                                # 项目说明文档
```

## 核心文件说明

### 应用入口

#### `app/__init__.py`
Flask应用工厂，负责：
- 创建Flask应用实例
- 注册蓝图（web, admin, api等）
- 初始化扩展（数据库、缓存等）
- 配置错误处理
- 注册中间件

```python
def create_app(config_name='development'):
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 初始化扩展
    db.init_app(app)
    # 注册蓝图
    from app.web import web_bp
    app.register_blueprint(web_bp)
    # ...
    return app
```

#### `run.py`
开发环境启动脚本
```python
from app import create_app
app = create_app('development')
app.run(host='0.0.0.0', port=5000, debug=True)
```

### 配置文件

#### `config.py`
环境配置管理
```python
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    # ...

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
```

### 数据模型

每个模型文件对应一个数据库表：
- **继承** `BaseModel` 获得通用字段（id, created_at, updated_at）
- **定义** 表名和字段类型
- **建立** 表之间的关系（Relationships）
- **提供** 业务方法（如：`increment_view()`, `check_password()`）

### 服务层

服务层封装业务逻辑：
- **解耦**：控制器和模型之间的中间层
- **复用**：多个API可以调用同一个服务
- **缓存**：统一管理缓存逻辑
- **事务**：处理复杂的业务事务

示例：
```python
class WebsiteService:
    @staticmethod
    def get_website_detail(id):
        # 查询逻辑
        # 缓存逻辑
        # 权限检查
        # 返回结果
        pass
```

### API层

RESTful API定义：
- **路由**：定义HTTP方法和URL
- **验证**：请求数据验证
- **调用**：调用服务层
- **响应**：返回JSON响应

### 模板层

Jinja2模板：
- **继承**：继承 `base.html` 获得通用布局
- **块**：定义可替换的区块（`{% block content %}`）
- **变量**：使用 `{{ variable }}` 输出变量
- **过滤器**：使用 `| filter` 处理数据

## 文件命名规范

### Python文件
- 模块文件：小写+下划线 `user_service.py`
- 类文件：大驼峰（每个类一个文件时）`WebsiteService.py`
- 测试文件：`test_*.py`

### 模板文件
- 全小写+下划线 `category_detail.html`
- 复数形式用于列表 `websites.html`
- 单数形式用于详情 `website.html`

### 静态文件
- CSS：小写+连字符 `main.css`, `analytics.css`
- JS：小写+连字符 `charts.js`, `lazyload.js`
- 图片：小写+连字符 `logo.png`, `default-avatar.png`

## 目录组织原则

### 按层次划分
```
models/        # 数据层
services/      # 业务逻辑层
api/           # 接口层
web/           # 表现层（前台）
admin/         # 表现层（后台）
```

### 按功能划分
```
website.py     # 网站相关
category.py    # 分类相关
user.py        # 用户相关
stats.py       # 统计相关
```

### 按类型划分
```
static/css/    # 样式
static/js/     # 脚本
templates/     # 模板
tests/         # 测试
```

## 扩展建议

### 添加新功能模块

1. **创建模型**
   ```bash
   touch app/models/feature.py
   ```

2. **创建服务**
   ```bash
   touch app/services/feature_service.py
   ```

3. **创建API**
   ```bash
   touch app/api/feature.py
   ```

4. **注册蓝图**
   ```python
   # app/__init__.py
   from app.api.feature import feature_bp
   app.register_blueprint(feature_bp)
   ```

### 添加新的蓝图

```bash
# 1. 创建蓝图目录
mkdir -p app/feature

# 2. 创建文件
touch app/feature/__init__.py
touch app/feature/routes.py

# 3. 注册蓝图
```

## 常用命令速查

### 开发环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
flask db init
flask db migrate -m "Initial"
flask db upgrade

# 填充测试数据
python scripts/seed_data.py

# 启动应用
flask run

# 启动Celery
celery -A app.celery worker -l info
```

### 生产环境
```bash
# Docker构建
docker-compose build

# Docker启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_website.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 总结

这个目录结构遵循了Flask的最佳实践：
- ✅ 清晰的分层架构
- ✅ 模块化设计
- ✅ 易于测试
- ✅ 易于扩展
- ✅ 便于维护

通过合理的目录组织，可以使项目代码结构清晰、职责分明，提高开发效率和代码质量。
