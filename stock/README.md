# 股票量化交易可视化系统

## 项目简介

这是一个基于 Django + Vue3 + ECharts 的股票量化交易可视化系统，实现了以下核心功能：
- **股票曲线选股** - 以可视化方式展示股票价格曲线，支持筛选和点击查看详情
- **每日个股涨跌个数统计** - 统计并可视化每日上涨/下跌/平盘的股票数量
- **单股日线/周线/月线查看** - 支持切换周期查看股票K线图和指标

## 技术栈

### 后端
- Django 5.2.11
- Django REST Framework
- PyMySQL (MySQL数据库连接)
- MySQL 8.0+

### 前端
- Vue 3
- Vite 7
- ECharts 5
- Axios
- Element Plus

## 项目结构

```
stock/
├── stockproj/              # Django项目配置
│   ├── settings.py        # 项目设置（数据库配置等）
│   ├── urls.py          # 主路由配置
│   └── templates/       # 模板文件
├── stock/                # 股票数据应用
│   └── models.py        # StockHistory模型
├── visualization/        # 可视化数据应用
│   ├── views.py         # API视图函数
│   └── urls.py         # 路由配置
├── frontend/             # Vue前端项目
│   ├── src/
│   │   ├── api/        # API客户端
│   │   ├── components/  # Vue组件
│   │   └── views/      # 页面组件
│   └── dist/           # 构建输出
└── venv/               # Python虚拟环境
```

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- MySQL 8.0+

### 数据库配置

项目使用现有的 `stock_data` 数据库，连接信息已在 `stockproj/settings.py` 中配置：
- 数据库名: stock_data
- 用户名: stock
- 密码: w123456W!

### 后端启动

```bash
# 进入项目目录
cd /home/zc/github/django-web/stock

# 激活虚拟环境
source venv/bin/activate

# 运行Django服务器
python manage.py runserver 0.0.0.0:8000
```

### 前端开发（可选）

如果需要开发前端组件：

```bash
cd frontend

# 安装依赖（如果还没安装）
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器会运行在 `http://localhost:5173`，并自动代理API请求到Django后端。

### 生产构建

```bash
cd frontend
npm run build
```

构建后的文件会输出到 `frontend/dist/` 目录，Django会自动服务这些静态文件。

### 访问系统

启动Django服务器后，访问：
- 主页: http://localhost:8000/
- API端点: http://localhost:8000/api/*

## API接口

### 每日市场涨跌统计
```
GET /api/market/daily-summary
参数:
  - start_date: 开始日期 (YYYY-MM-DD)
  - end_date: 结束日期 (YYYY-MM-DD)
```

### 股票选股
```
GET /api/stocks/screener
参数:
  - start_date: 开始日期
  - end_date: 结束日期
  - min_change: 最小涨跌幅（可选）
  - max_change: 最大涨跌幅（可选）
  - min_volume: 最小成交量（可选）
  - page: 页码（默认1）
  - page_size: 每页数量（默认50）
```

### 股票K线数据
```
GET /api/stocks/{ticker}/kline
参数:
  - period: 周期 (daily/weekly/monthly，默认daily)
  - start_date: 开始日期
  - end_date: 结束日期
```

### 股票列表
```
GET /api/stocks/list
```

### 股票详情（曲线图数据）
```
GET /api/stocks/{ticker}/detail
参数:
  - start_date: 开始日期
  - end_date: 结束日期
```

## 功能说明

### 1. 股票曲线选股页面

- 展示多只股票的迷你价格曲线图
- 支持按日期范围、涨跌幅筛选
- 点击股票卡片查看详细K线图
- 分页浏览所有股票

### 2. 每日涨跌统计页面

- 显示最近交易日的涨跌统计卡片
- 涨跌趋势柱状图（支持缩放）
- 涨跌分布饼图
- 可选择任意日期范围查看

### 3. 股票详情页面

- 展示单个股票的完整K线图
- 支持日线/周线/月线切换
- K线图包含：
  - 蜡烛图（开盘/收盘/最高/最低价）
  - MA5/MA10/MA20移动平均线
  - 成交量柱状图
- 支持图表缩放和平移
- 显示最新价格、涨跌幅、成交量等信息

## 常见问题

### Django服务器无法启动
确保MySQL服务正在运行，并且数据库连接信息正确。

### 静态文件无法加载
如果修改了前端代码，需要重新构建：
```bash
cd frontend
npm run build
```

### API返回500错误
检查Django日志：
```bash
tail -f /tmp/django.log
```

## 开发说明

### 添加新的API端点

1. 在 `visualization/views.py` 中添加视图函数
2. 在 `visualization/urls.py` 中注册路由
3. 无需修改主路由配置，`visualization/urls.py` 已被包含

### 修改数据库模型

由于 `stock_history` 表是现有的，我们使用了 `managed = False` 来避免Django修改表结构。如需添加新表，创建新的模型类即可。

## 许可

此项目仅供学习和研究使用。
