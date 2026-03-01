# 自定义曲线图功能说明

## 功能概述

新增的自定义曲线图功能允许用户使用 Python 从数据库获取股票数据，计算自定义技术指标，然后在前端图表中显示。

## 文件说明

### 1. 后端 API (`stock/views.py`)
- `get_custom_chart_data()`: 接收 POST 请求，返回自定义图表数据

### 2. 前端页面 (`stock/templates/strategy_watch.html`)
- 新增"自定义曲线图"区域
- 包含 Python 代码示例展示
- 支持通过输入股票代码加载自定义指标

### 3. Python 示例脚本 (`custom_chart_example.py`)
- 演示如何从数据库获取数据
- 提供多种技术指标计算函数
- 自动发送数据到前端 API

## 使用方法

### 方法一：使用 Python 脚本（推荐）

```bash
# 1. 运行示例脚本
python custom_chart_example.py

# 2. 脚本会自动：
#    - 从数据库获取股票数据
#    - 计算技术指标（SMA, EMA, MACD 等）
#    - 发送到前端 API

# 3. 在页面中查看结果
访问 http://localhost:8000/stock/strategy/
```

### 方法二：手动调用 API

```python
import requests
from stock.models import StockHistory

# 1. 获取数据
ticker = '600000'
history = StockHistory.objects.filter(
    ticker=ticker
).order_by('trade_date')[:200]

data_list = list(history)
dates = [h.trade_date.strftime('%Y-%m-%d') for h in data_list]
close_prices = [float(h.close_price) for h in data_list]

# 2. 自定义计算（示例：SMA）
def calculate_sma(data, period=20):
    sma = []
    for i in range(len(data)):
        if i < period - 1:
            sma.append(None)
        else:
            avg = sum(data[i-period+1:i+1]) / period
            sma.append(avg)
    return sma

sma20 = calculate_sma(close_prices, 20)

# 3. 发送到 API
url = 'http://localhost:8000/stock/api/custom-chart-data/'
payload = {
    'dates': dates,
    'series': [
        {
            'name': '收盘价',
            'data': close_prices,
            'type': 'line',
            'color': '#667eea'
        },
        {
            'name': '自定义SMA20',
            'data': sma20,
            'type': 'line',
            'color': '#ff6b6b',
            'smooth': True
        }
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

### 方法三：在页面中直接加载

在策略观察页面底部的"自定义曲线图"区域：
1. 输入股票代码
2. 点击"加载自定义曲线"按钮
3. 系统会自动计算并显示 SMA20 和 SMA50

## 数据格式说明

API 接收的 JSON 格式：

```json
{
    "dates": ["2024-01-01", "2024-01-02", ...],
    "series": [
        {
            "name": "系列名称",
            "data": [10.5, 10.8, ...],
            "type": "line|bar",
            "color": "#667eea",
            "smooth": true,
            "showSymbol": false
        }
    ]
}
```

系列配置参数：
- `name`: 系列名称
- `data`: 数据数组
- `type`: 图表类型（line, bar, scatter 等）
- `color`: 颜色（可选）
- `smooth`: 是否平滑（仅 line 类型）
- `showSymbol`: 是否显示数据点（仅 line 类型）

## 技术指标函数说明

### calculate_sma(data, period)
计算简单移动平均（SMA）

参数：
- `data`: 价格数据列表
- `period`: 周期（默认20）

### calculate_ema(data, period)
计算指数移动平均（EMA）

参数：
- `data`: 价格数据列表
- `period`: 周期（默认20）

### calculate_bollinger_bands(data, period, std_dev)
计算布林带（需要 numpy）

参数：
- `data`: 价格数据列表
- `period`: 周期（默认20）
- `std_dev`: 标准差倍数（默认2）

返回：上轨、中轨、下轨

### calculate_rsi(data, period)
计算相对强弱指标（RSI）

参数：
- `data`: 价格数据列表
- `period`: 周期（默认14）

返回：RSI 数值（0-100）

## 常见问题

### Q: 如何修改计算逻辑？
A: 修改 `custom_chart_example.py` 中的函数，或编写自己的 Python 脚本

### Q: 如何添加新的技术指标？
A: 在脚本中定义新函数，然后在 `generate_custom_chart_data()` 中调用

### Q: 数据没有显示怎么办？
A: 检查浏览器控制台，确认 API 请求是否成功

### Q: 如何自定义颜色和样式？
A: 在发送的 `series` 数据中添加 `color`、`smooth` 等参数
