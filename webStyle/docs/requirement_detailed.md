# WebStyle 网站风格浏览系统 - 详细需求文档

## 1. 项目概述

### 1.1 项目背景
随着互联网的发展，各种网站风格层出不穷。设计师和开发者需要一个便捷的平台来浏览、参考和学习主流网站的视觉风格和设计模式。

### 1.2 项目目标
构建一个网站风格浏览和参考平台，提供：
- 主流网站风格的分类展示
- 网站样式的快照/截图
- 风格趋势分析和可视化
- 设计灵感和参考资源

### 1.3 目标用户
- **UI/UX设计师**：寻找设计灵感和参考
- **前端开发者**：学习不同风格的实现方式
- **产品经理**：了解行业设计趋势
- **创业者**：为自己的网站寻找合适风格

---

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 网站风格分类浏览
- **风格分类体系**：
  - 扁平化设计
  - 卡片式设计
  - 渐变色设计
  - 暗色模式
  - 玻璃拟态 (Glassmorphism)
  - 新拟态 (Neumorphism)
  - 极简主义
  - 3D立体风格
  - 复古风格
  - 科技感风格
  - 等...

- **分类展示**：
  - 首页展示各大类别的缩略图
  - 点击进入类别详情页，展示该类别的网站列表
  - 支持多级分类（如：扁平化 > 商业/社交/工具）

#### 2.1.2 网站详情展示
- **快照展示**：
  - 首页快照截图
  - 支持放大预览
  - 多页面快照（首页、列表页、详情页等）

- **网站信息**：
  - 网站名称
  - 网站链接（可跳转）
  - 风格标签
  - 设计元素说明（配色方案、字体、布局特点）
  - 收藏量、浏览量

- **相似推荐**：
  - 基于风格的相似网站推荐
  - 基于设计元素的相似推荐

#### 2.1.3 搜索与筛选
- **关键词搜索**：搜索网站名称、风格标签、设计元素
- **多维筛选**：
  - 按风格分类筛选
  - 按行业类型筛选（电商、社交、工具、资讯等）
  - 按配色方案筛选（冷色调、暖色调、黑白等）
  - 按布局方式筛选（居中、左右分栏、全屏等）

#### 2.1.4 数据可视化
- **风格趋势分析**：
  - 各风格的流行趋势图（使用ECharts折线图）
  - 季度/年度风格热度变化

- **风格占比分析**：
  - 饼图展示各风格的占比
  - 行业与风格的交叉分析（热力图）

- **网站数据统计**：
  - TOP榜单（最受欢迎网站）
  - 新增网站趋势图

#### 2.1.5 用户交互功能
- **收藏功能**：用户可收藏喜欢的网站
- **点赞/评论**：对网站风格进行评价
- **标签系统**：支持用户自定义标签
- **个人中心**：
  - 我的收藏
  - 浏览历史
  - 个人设置

### 2.2 管理功能

#### 2.2.1 网站管理
- **网站录入**：
  - 手动录入网站信息
  - 批量导入（Excel/CSV）
  - URL抓取自动截图（集成Puppeteer/Selenium）

- **网站编辑**：修改网站信息、标签、风格分类
- **网站审核**：管理员审核用户提交的网站
- **网站上下线**：控制网站的展示状态

#### 2.2.2 分类管理
- **分类CRUD**：创建、编辑、删除风格分类
- **分类排序**：设置分类的展示顺序
- **分类关联**：维护分类之间的层级关系

#### 2.2.3 用户管理
- **用户列表**：查看注册用户
- **用户状态管理**：启用/禁用用户
- **角色权限管理**：管理员/普通用户

#### 2.2.4 数据统计
- **访问统计**：PV/UV统计
- **热门网站统计**
- **搜索关键词统计**
- **用户行为统计**

---

## 3. 非功能需求

### 3.1 性能需求
- **响应时间**：页面加载时间 < 2秒
- **并发能力**：支持至少1000并发用户
- **图片加载**：使用懒加载和CDN加速
- **缓存策略**：使用Redis缓存热点数据

### 3.2 安全需求
- **数据安全**：
  - 密码加密存储（bcrypt）
  - SQL注入防护
  - XSS防护
  - CSRF防护

- **访问控制**：
  - 管理后台需登录认证
  - 敏感操作二次确认

### 3.3 可扩展性
- **模块化设计**：前后端分离，便于扩展
- **插件化架构**：支持自定义风格分类和数据源
- **API设计**：预留RESTful API接口

### 3.4 兼容性
- **浏览器兼容**：Chrome/Firefox/Safari/Edge最新两个版本
- **响应式设计**：支持PC、平板、手机

---

## 4. 技术架构

### 4.1 技术栈

#### 后端技术栈
- **Web框架**：Flask 3.x
- **数据库**：
  - 主库：PostgreSQL（存储结构化数据）
  - 缓存：Redis（缓存、会话）
  - 图数据库（可选）：Neo4j（风格关联分析）
- **ORM**：SQLAlchemy
- **爬虫/截图**：
  - Puppeteer（网页截图）
  - BeautifulSoup（网页解析）
- **任务队列**：Celery + Redis（异步任务）
- **API文档**：Flask-RESTX/Swagger

#### 前端技术栈
- **基础框架**：HTML5 + CSS3 + Vanilla JavaScript
- **图表库**：ECharts 5.x
- **UI框架**：Bootstrap 5 / TailwindCSS
- **图片处理**：Lightbox（图片预览）
- **构建工具**：Webpack / Vite
- **版本管理**：ES Modules

#### 运维技术栈
- **Web服务器**：Nginx
- **应用服务器**：Gunicorn/uWSGI
- **容器化**：Docker + Docker Compose
- **反向代理**：Nginx
- **日志管理**：Logrotate + ELK Stack（可选）
- **监控**：Prometheus + Grafana（可选）

### 4.2 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ PC浏览器 │  │平板浏览器│  │手机浏览器│  │ 管理后台 │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
┌───────┼─────────────┼─────────────┼─────────────┼──────────┐
│       │    Nginx (反向代理 + 静态资源)               │          │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
┌───────┴─────────────┴─────────────┴─────────────┴──────────┐
│                      Flask应用层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 蓝图: 首页│  │蓝图: 网站│  │蓝图: API │  │蓝图: 管理│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────────────────────────────────────────┘
        │             │             │             │
┌───────┴─────────────┴─────────────┴─────────────┴──────────┐
│                      数据访问层                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │SQLAlchemy│  │  Redis   │  │  Celery  │  │S3/MinIO  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
┌───────┴─────────────┴─────────────┴─────────────┴──────────┐
│                      数据存储层                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │PostgreSQL│  │   Redis  │  │ 文件存储 │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└───────────────────────────────────────────────────────────┘
```

---

## 5. 数据模型设计

### 5.1 核心实体

#### Website（网站）
```python
{
    id: int,
    name: str,              # 网站名称
    url: str,               # 网站链接
    description: text,      # 网站描述
    screenshots: json,      # 截图列表 [{'url': '', 'type': 'homepage'}]
    category_id: int,       # 主分类ID
    tags: list[str],        # 标签列表
    industry: str,          # 行业类型
    color_scheme: str,      # 配色方案
    layout_type: str,       # 布局类型
    views: int,             # 浏览量
    likes: int,             # 点赞数
    favorites: int,         # 收藏数
    status: str,            # 状态：active/inactive/pending
    created_by: int,        # 创建者ID
    created_at: datetime,
    updated_at: datetime
}
```

#### Category（分类）
```python
{
    id: int,
    name: str,              # 分类名称
    slug: str,              # URL友好标识
    description: text,      # 分类描述
    icon: str,              # 图标
    parent_id: int,         # 父分类ID
    sort_order: int,        # 排序
    is_active: bool,        # 是否启用
    created_at: datetime
}
```

#### User（用户）
```python
{
    id: int,
    username: str,
    email: str,
    password_hash: str,
    avatar: str,
    role: str,              # user/admin
    is_active: bool,
    created_at: datetime,
    last_login: datetime
}
```

#### Favorite（收藏）
```python
{
    id: int,
    user_id: int,
    website_id: int,
    created_at: datetime
}
```

#### Tag（标签）
```python
{
    id: int,
    name: str,
    slug: str,
    usage_count: int
}
```

### 5.2 数据库表结构（简化版）

```sql
-- 分类表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(255),
    parent_id INTEGER REFERENCES categories(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 网站表
CREATE TABLE websites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    url VARCHAR(500) NOT NULL,
    description TEXT,
    screenshots JSONB DEFAULT '[]',
    category_id INTEGER REFERENCES categories(id),
    industry VARCHAR(50),
    color_scheme VARCHAR(50),
    layout_type VARCHAR(50),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    favorites INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 标签表
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 0
);

-- 网站标签关联表
CREATE TABLE website_tags (
    website_id INTEGER REFERENCES websites(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (website_id, tag_id)
);

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 收藏表
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    website_id INTEGER REFERENCES websites(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, website_id)
);

-- 浏览历史
CREATE TABLE view_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    website_id INTEGER REFERENCES websites(id) ON DELETE CASCADE,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. 核心业务流程

### 6.1 网站浏览流程
```
用户访问首页
    ↓
查看分类列表
    ↓
选择分类
    ↓
查看该分类下的网站列表
    ↓
点击某个网站
    ↓
查看网站详情（截图、描述、标签）
    ↓
可选操作：收藏/点赞/评论
```

### 6.2 网站录入流程
```
管理员登录后台
    ↓
点击"新增网站"
    ↓
填写网站信息（URL、名称、分类等）
    ↓
系统自动抓取网页截图（Puppeteer）
    ↓
补充其他信息（描述、标签等）
    ↓
提交审核/直接发布
    ↓
网站在前台展示
```

### 6.3 数据分析流程
```
用户访问数据分析页面
    ↓
选择分析维度（时间范围、风格类型等）
    ↓
后端查询统计数据
    ↓
返回JSON数据
    ↓
前端ECharts渲染图表
    ↓
交互式查看趋势和占比
```

---

## 7. API接口设计

### 7.1 前台接口

#### 网站相关
```
GET  /api/categories           # 获取分类列表
GET  /api/categories/{id}      # 获取分类详情
GET  /api/websites             # 获取网站列表（支持分页、筛选）
GET  /api/websites/{id}        # 获取网站详情
GET  /api/websites/random      # 随机推荐网站
GET  /api/websites/similar/{id} # 相似网站推荐
GET  /api/websites/search      # 搜索网站
```

#### 用户相关
```
POST /api/auth/register        # 用户注册
POST /api/auth/login           # 用户登录
POST /api/auth/logout          # 用户登出
GET  /api/user/profile         # 获取用户信息
PUT  /api/user/profile         # 更新用户信息
```

#### 收藏相关
```
POST /api/favorites            # 添加收藏
DELETE /api/favorites/{id}     # 取消收藏
GET  /api/favorites            # 获取收藏列表
```

#### 统计相关
```
GET  /api/stats/trends         # 获取风格趋势
GET  /api/stats/distribution   # 获取风格分布
GET  /api/stats/top            # 获取TOP榜单
```

### 7.2 管理后台接口

```
GET    /api/admin/websites         # 网站管理列表
POST   /api/admin/websites         # 创建网站
PUT    /api/admin/websites/{id}    # 更新网站
DELETE /api/admin/websites/{id}    # 删除网站
POST   /api/admin/websites/{id}/screenshot  # 重新截图

GET    /api/admin/categories        # 分类管理
POST   /api/admin/categories        # 创建分类
PUT    /api/admin/categories/{id}   # 更新分类
DELETE /api/admin/categories/{id}   # 删除分类

GET    /api/admin/users             # 用户管理
PUT    /api/admin/users/{id}        # 更新用户状态

GET    /api/admin/stats             # 管理后台统计数据
```

---

## 8. 页面设计

### 8.1 前台页面结构

#### 首页 (/)
- 顶部导航栏
- Hero区域：展示平台介绍和热门分类
- 分类快捷入口
- 热门网站推荐
- 最新添加网站
- 页脚

#### 分类列表页 (/categories)
- 分类卡片网格
- 每个分类显示：图标、名称、网站数量、缩略图

#### 分类详情页 (/categories/{slug})
- 分类信息（名称、描述）
- 网站列表（支持筛选、排序）
- 分页

#### 网站详情页 (/websites/{id})
- 网站截图画廊
- 网站基本信息
- 设计元素分析
- 相似网站推荐
- 评论区
- 收藏/点赞按钮

#### 数据分析页 (/analytics)
- 风格趋势图（折线图）
- 风格占比图（饼图）
- 行业风格热力图
- TOP榜单

#### 搜索结果页 (/search)
- 搜索框
- 筛选条件
- 结果列表
- 分页

#### 用户中心 (/user)
- 个人资料
- 我的收藏
- 浏览历史
- 设置

### 8.2 管理后台页面结构

#### 登录页 (/admin/login)

#### 仪表盘 (/admin)
- 数据概览（网站总数、用户总数、今日新增等）
- 待审核网站
- 热门网站排行
- 最近活动

#### 网站管理 (/admin/websites)
- 网站列表（支持搜索、筛选）
- 新增/编辑/删除网站
- 批量操作
- 批量导入

#### 分类管理 (/admin/categories)
- 分类树形结构
- 拖拽排序
- 新增/编辑/删除分类

#### 用户管理 (/admin/users)
- 用户列表
- 用户状态管理

#### 统计分析 (/admin/stats)
- 详细的数据统计图表

---

## 9. 部署方案

### 9.1 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 启动开发服务器
flask run --host=0.0.0.0 --port=5000
```

### 9.2 生产环境（Docker部署）
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/var/www/static
    depends_on:
      - flask

  flask:
    build: .
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/webstyle
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A app.celery worker -l info
    depends_on:
      - redis
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=webstyle
      - POSTGRES_USER=webstyle
      - POSTGRES_PASSWORD=webstyle123
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 10. 项目里程碑

### 阶段一：MVP开发（4周）
- Week 1: 项目搭建、数据库设计、基础框架
- Week 2: 网站展示功能（分类、列表、详情）
- Week 3: 用户系统（注册、登录、收藏）
- Week 4: 管理后台基础功能

### 阶段二：核心功能完善（3周）
- Week 5: 搜索与筛选
- Week 6: 数据可视化（ECharts集成）
- Week 7: 网站截图功能

### 阶段三：优化与上线（2周）
- Week 8: 性能优化、测试
- Week 9: 部署上线、文档完善

---

## 11. 风险与挑战

### 11.1 技术风险
- **截图稳定性**：不同网站的兼容性问题，需要降级方案
- **图片存储**：大量截图的存储和CDN优化
- **性能优化**：图片懒加载、数据库查询优化

### 11.2 内容风险
- **版权问题**：网站截图的版权风险
- **内容质量**：需要建立内容审核机制

### 11.3 业务风险
- **数据来源**：如何获取持续的高质量网站数据
- **用户增长**：如何吸引用户使用

---

## 12. 后续扩展方向

- **AI分析**：使用AI自动分析网站风格特征
- **设计工具集成**：提供设计资源下载
- **社区功能**：用户提交、评论、评分
- **移动端APP**：开发移动应用
- **国际化**：多语言支持
- **商业化**：付费高级功能、设计服务对接

---

## 13. 技术选型理由

### 13.1 为什么选择Flask？
- **轻量灵活**：适合中小型项目，学习曲线平缓
- **扩展性强**：丰富的插件生态
- **开发效率高**：快速原型开发
- **社区活跃**：问题解决方案丰富

### 13.2 为什么选择PostgreSQL？
- **支持JSONB**：方便存储截图列表等灵活数据
- **全文检索**：内置全文搜索功能
- **成熟稳定**：企业级数据库

### 13.3 为什么选择ECharts？
- **功能强大**：支持丰富的图表类型
- **性能优秀**：大数据量渲染流畅
- **文档完善**：中英文文档齐全
- **免费开源**：无商业授权问题

---

## 附录

### A. 参考资料
- Flask官方文档：https://flask.palletsprojects.com/
- ECharts官方文档：https://echarts.apache.org/
- Puppeteer文档：https://pptr.dev/

### B. 数据初始化脚本
- 初始分类数据
- 示例网站数据
- 测试用户数据

### C. 配置文件模板
- Flask配置
- Nginx配置
- Docker Compose配置
