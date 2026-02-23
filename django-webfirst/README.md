# Django 文件管理系统

基于 Django 框架开发的文件上传下载管理系统，集成 ECharts 数据可视化功能。

## 功能特性

- 文件上传 - 支持各种文件类型上传，自动检测重复文件
- 文件下载 - 记录下载次数，支持断点续传
- 文件删除 - 删除文件及数据库记录
- 数据可视化 - ECharts 图表展示文件统计信息
  - 文件类型分布饼图
  - 热门下载排行柱状图
  - 实时统计卡片（文件数、总大小、下载次数、类型数）
- Django 管理后台 - 方便的后台管理界面

## 技术栈

- 后端: Django 3.2.12
- 数据库: SQLite
- 前端: HTML5 + CSS3 + JavaScript
- 图表库: ECharts 5.4.3

## 项目结构

```
django-webfirst/
├── config/                  # Django项目配置目录
│   ├── settings.py          # 项目设置文件
│   ├── urls.py              # 主路由配置
│   └── wsgi.py              # WSGI配置
├── filemanager/             # 文件管理应用
│   ├── models.py            # 数据模型
│   ├── views.py             # 视图函数
│   ├── urls.py              # 应用路由
│   └── admin.py             # 管理后台配置
├── templates/               # 模板文件
│   └── filemanager/
│       └── index.html       # 主页面（含ECharts）
├── media/                   # 媒体文件目录
│   └── files/               # 上传文件存储位置
├── static/                  # 静态文件目录
│   ├── css/                 # CSS文件
│   └── js/                  # JavaScript文件
├── manage.py                # Django管理脚本
├── db.sqlite3               # SQLite数据库文件
└── README.md                # 项目文档
```

## 安装步骤

### 1. 环境要求

- Python 3.6+
- Django 3.2.12

### 2. 安装依赖

```bash
pip install django==3.2.12
```

### 3. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建超级用户（可选）

如果需要使用Django管理后台：

```bash
python manage.py createsuperuser
```

按照提示输入用户名、邮箱和密码。

## 使用说明

### 启动开发服务器

```bash
python manage.py runserver
```

默认运行在 `http://127.0.0.1:8000/`

如需指定端口：

```bash
python manage.py runserver 0.0.0.0:8000
```

### 访问应用

- 主页面: http://127.0.0.1:8000/
- 管理后台: http://127.0.0.1:8000/admin/

## 数据模型

### UploadedFile 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| file | FileField | 文件路径 |
| filename | CharField | 文件名 |
| file_size | BigIntegerField | 文件大小（字节） |
| file_type | CharField | 文件MIME类型 |
| upload_time | DateTimeField | 上传时间 |
| download_count | IntegerField | 下载次数 |

## API接口

### 1. 文件列表页面

```
GET /
```

### 2. 上传文件

```
POST /upload/
Content-Type: multipart/form-data

参数:
- file: 上传的文件
```

### 3. 下载文件

```
GET /download/<file_id>/
```

### 4. 删除文件

```
GET /delete/<file_id>/
```

### 5. 获取统计数据

```
GET /api/stats/
```

返回JSON格式数据：

```json
{
  "typeDistribution": [
    {"name": "pdf", "value": 5},
    {"name": "jpg", "value": 3}
  ],
  "topDownloaded": [
    {"name": "document.pdf", "value": 10},
    {"name": "image.jpg", "value": 5}
  ],
  "totalFiles": 8,
  "totalSize": 1048576,
  "totalDownloads": 15
}
```

## 前端功能

### 统计卡片

实时显示：
- 总文件数
- 总存储大小
- 总下载次数
- 文件类型数量

### 文件类型分布图

使用 ECharts 饼图展示不同文件类型的分布情况。

### 热门下载排行

使用 ECharts 柱状图展示下载量最高的10个文件。

### 文件列表

展示所有上传文件的详细信息，支持下载和删除操作。

## 配置说明

### 修改上传文件大小限制

在 `config/settings.py` 中添加：

```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

### 修改允许上传的文件类型

在 `filemanager/views.py` 的 `upload_file` 函数中添加文件类型验证。

### 修改存储路径

在 `config/settings.py` 中修改：

```python
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

## 部署建议

### 生产环境配置

1. 修改 `DEBUG = False`
2. 设置 `ALLOWED_HOSTS`
3. 使用 PostgreSQL 或 MySQL 替代 SQLite
4. 配置静态文件服务（Nginx）
5. 使用 Gunicorn 或 uWSGI 作为应用服务器

### 收集静态文件

```bash
python manage.py collectstatic
```

## 常见问题

### Q: 上传文件失败

A: 检查 `media/` 目录是否有写入权限。

### Q: ECharts 图表不显示

A: 检查网络连接，ECharts 是通过 CDN 加载的。

### Q: 文件下载中文乱码

A: 已在代码中处理，如仍有问题请检查浏览器编码设置。

## 许可证

MIT License

## 作者

Created with Claude Code
