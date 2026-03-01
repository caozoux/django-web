# 基于Django的量化交易策略系统设计文档

## 1. 项目概述

### 1.1 项目目标
设计并实现一个基于Django框架的量化交易策略系统，利用现有的 `stock_data.stock_history` 表进行技术分析、策略回测和信号生成。

### 1.2 数据库信息
- **数据库**: stock_data
- **用户名**: stock
- **密码**: w123456W!
- **核心表**: stock_history

## 2. 数据库表结构分析

### 2.1 stock_history 表结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键，自增 |
| ticker | varchar(10) | 股票代码 |
| trade_date | date | 交易日期 |
| open_price | decimal(10,4) | 开盘价 |
| high_price | decimal(10,4) | 最高价 |
| low_price | decimal(10,4) | 最低价 |
| close_price | decimal(10,4) | 收盘价 |
| volume | decimal(15,2) | 成交量 |
| change_price | decimal(10,6) | 涨跌幅 |
| ma_1 | decimal(10,4) | 移动平均线1 |
| ma_2 | decimal(10,4) | 移动平均线2 |
| ma_3 | decimal(10,4) | 移动平均线3 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.2 索引设计
- PRIMARY KEY: `id`
- UNIQUE KEY: `unique_stock_date` (ticker, trade_date)
- INDEX: `idx_ticker`, `idx_trade_date`, `idx_ticker_date`

## 3. 系统架构设计

### 3.1 技术栈
- **后端框架**: Django 4.x / 5.x
- **数据库**: MySQL 8.0+
- **数据处理**: pandas, numpy
- **技术指标计算**: talib (技术分析库)
- **任务队列**: Celery + Redis (异步任务)
- **可视化**: Django REST Framework (API)

### 3.2 系统模块划分

```
stock_trading_system/
├── config/                    # 配置模块
│   ├── __init__.py
│   ├── settings.py           # Django设置
│   ├── urls.py               # URL路由
│   └── wsgi.py
├── stock/                     # 股票数据应用
│   ├── __init__.py
│   ├── models.py             # 数据模型
│   ├── views.py              # 视图
│   ├── urls.py               # 路由
│   ├── serializers.py        # 序列化器
│   └── tasks.py              # Celery任务
├── strategy/                  # 策略应用
│   ├── __init__.py
│   ├── models.py             # 策略模型
│   ├── backtest.py           # 回测引擎
│   ├── signals.py            # 信号生成
│   ├── indicators.py         # 技术指标计算
│   └── views.py              # 策略管理视图
├── trading/                   # 交易应用
│   ├── __init__.py
│   ├── models.py             # 订单、持仓模型
│   ├── portfolio.py          # 组合管理
│   └── risk.py               # 风险管理
└── utils/                     # 工具模块
    ├── __init__.py
    ├── data_fetcher.py       # 数据获取
    └── db_utils.py           # 数据库工具
```

## 4. 核心功能设计

### 4.1 数据模型设计 (models.py)

```python
from django.db import models
from django.db import connections

# 方案1: 使用原生数据库映射(直接操作现有表)
class StockHistory(models.Model):
    """股票历史数据模型 - 映射到现有表"""
    ticker = models.CharField(max_length=10, db_column='ticker')
    trade_date = models.DateField(db_column='trade_date')
    open_price = models.DecimalField(max_digits=10, decimal_places=4, db_column='open_price')
    high_price = models.DecimalField(max_digits=10, decimal_places=4, db_column='high_price')
    low_price = models.DecimalField(max_digits=10, decimal_places=4, db_column='low_price')
    close_price = models.DecimalField(max_digits=10, decimal_places=4, db_column='close_price')
    volume = models.DecimalField(max_digits=15, decimal_places=2, db_column='volume')
    change_price = models.DecimalField(max_digits=10, decimal_places=6, db_column='change_price', null=True)
    ma_1 = models.DecimalField(max_digits=10, decimal_places=4, db_column='ma_1', null=True)
    ma_2 = models.DecimalField(max_digits=10, decimal_places=4, db_column='ma_2', null=True)
    ma_3 = models.DecimalField(max_digits=10, decimal_places=4, db_column='ma_3', null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        managed = False  # 不让Django管理表结构
        db_table = 'stock_history'
        verbose_name = '股票历史数据'
        verbose_name_plural = '股票历史数据'
        ordering = ['-trade_date']

# 方案2: 新增策略相关表
class TradingStrategy(models.Model):
    """交易策略配置"""
    name = models.CharField(max_length=100, verbose_name='策略名称')
    description = models.TextField(verbose_name='策略描述')
    strategy_type = models.CharField(max_length=50, choices=[
        ('MA', '均线策略'),
        ('MACD', 'MACD策略'),
        ('RSI', 'RSI策略'),
        ('BOLL', '布林带策略'),
        ('MOMENTUM', '动量策略'),
        ('CUSTOM', '自定义策略'),
    ], default='MA')
    parameters = models.JSONField(verbose_name='策略参数')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '交易策略'
        verbose_name_plural = '交易策略'

class BacktestResult(models.Model):
    """回测结果"""
    strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE, related_name='backtests')
    ticker = models.CharField(max_length=10, verbose_name='股票代码')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    total_return = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='总收益率')
    annual_return = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='年化收益率')
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='最大回撤')
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='夏普比率')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='胜率')
    total_trades = models.IntegerField(verbose_name='总交易次数')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '回测结果'
        verbose_name_plural = '回测结果'

class TradingSignal(models.Model):
    """交易信号"""
    SIGNAL_CHOICES = [
        ('BUY', '买入'),
        ('SELL', '卖出'),
        ('HOLD', '持有'),
    ]
    ticker = models.CharField(max_length=10, verbose_name='股票代码')
    signal_type = models.CharField(max_length=10, choices=SIGNAL_CHOICES)
    signal_date = models.DateField(verbose_name='信号日期')
    price = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='信号价格')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='置信度(%)')
    strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE, related_name='signals')
    is_executed = models.BooleanField(default=False, verbose_name='是否执行')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '交易信号'
        verbose_name_plural = '交易信号'
        ordering = ['-signal_date']
```

### 4.2 技术指标模块 (indicators.py)

```python
import pandas as pd
import numpy as np

class TechnicalIndicators:
    """技术指标计算类"""

    @staticmethod
    def calculate_ma(data: pd.Series, period: int) -> pd.Series:
        """计算移动平均线"""
        return data.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均线"""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_macd(close: pd.Series, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI相对强弱指标"""
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_bollinger_bands(close: pd.Series, period: int = 20, std_dev: int = 2):
        """计算布林带"""
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        return upper_band, sma, lower_band

    @staticmethod
    def calculate_kdj(high: pd.Series, low: pd.Series, close: pd.Series, n=9, m1=3, m2=3):
        """计算KDJ指标"""
        low_n = low.rolling(window=n).min()
        high_n = high.rolling(window=n).max()
        rsv = (close - low_n) / (high_n - low_n) * 100
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        return k, d, j
```

### 4.3 策略实现 (signals.py)

```python
from .indicators import TechnicalIndicators
import pandas as pd

class MAStrategy:
    """双均线策略"""

    def __init__(self, short_period=5, long_period=20):
        self.short_period = short_period
        self.long_period = long_period
        self.indicators = TechnicalIndicators()

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        data = data.copy()
        data['ma_short'] = self.indicators.calculate_ma(data['close_price'], self.short_period)
        data['ma_long'] = self.indicators.calculate_ma(data['close_price'], self.long_period)

        # 金叉买入，死叉卖出
        data['ma_diff'] = data['ma_short'] - data['ma_long']
        data['signal'] = 'HOLD'
        data.loc[data['ma_diff'] > 0, 'signal'] = 'BUY'
        data.loc[data['ma_diff'] < 0, 'signal'] = 'SELL'

        # 检测金叉和死叉
        data['golden_cross'] = (data['ma_diff'] > 0) & (data['ma_diff'].shift(1) <= 0)
        data['death_cross'] = (data['ma_diff'] < 0) & (data['ma_diff'].shift(1) >= 0)

        return data

class MACDStrategy:
    """MACD策略"""

    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.indicators = TechnicalIndicators()

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        data = data.copy()
        macd, signal_line, histogram = self.indicators.calculate_macd(
            data['close_price'], self.fast, self.slow, self.signal
        )
        data['macd'] = macd
        data['macd_signal'] = signal_line
        data['macd_histogram'] = histogram

        data['signal'] = 'HOLD'
        data.loc[histogram > 0, 'signal'] = 'BUY'
        data.loc[histogram < 0, 'signal'] = 'SELL'

        return data

class RSIStrategy:
    """RSI策略"""

    def __init__(self, period=14, oversold=30, overbought=70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.indicators = TechnicalIndicators()

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        data = data.copy()
        data['rsi'] = self.indicators.calculate_rsi(data['close_price'], self.period)

        data['signal'] = 'HOLD'
        data.loc[data['rsi'] < self.oversold, 'signal'] = 'BUY'
        data.loc[data['rsi'] > self.overbought, 'signal'] = 'SELL'

        return data
```

### 4.4 回测引擎 (backtest.py)

```python
import pandas as pd
from django.db import connections
from decimal import Decimal

class BacktestEngine:
    """回测引擎"""

    def __init__(self, initial_capital=100000, commission=0.0003):
        self.initial_capital = initial_capital
        self.commission = commission

    def run_backtest(self, data: pd.DataFrame, signals: pd.DataFrame):
        """执行回测"""
        capital = self.initial_capital
        position = 0  # 持仓数量
        trades = []

        for i in range(len(data)):
            current_price = data.iloc[i]['close_price']
            signal = signals.iloc[i]['signal']

            if signal == 'BUY' and position == 0 and capital > 0:
                # 买入
                shares = int(capital / (current_price * (1 + self.commission)))
                position = shares
                capital = capital - shares * current_price * (1 + self.commission)
                trades.append({
                    'date': data.iloc[i]['trade_date'],
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'capital': capital
                })

            elif signal == 'SELL' and position > 0:
                # 卖出
                capital = capital + position * current_price * (1 - self.commission)
                trades.append({
                    'date': data.iloc[i]['trade_date'],
                    'action': 'SELL',
                    'price': current_price,
                    'shares': position,
                    'capital': capital
                })
                position = 0

        # 计算最终资产
        final_capital = capital
        if position > 0:
            final_capital = capital + position * data.iloc[-1]['close_price']

        # 计算回测指标
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        win_trades = [t for t in trades if t['action'] == 'SELL' and t['capital'] > self.initial_capital]
        win_rate = len(win_trades) / len([t for t in trades if t['action'] == 'SELL']) * 100 if len(trades) > 0 else 0

        return {
            'total_return': total_return,
            'final_capital': final_capital,
            'total_trades': len(trades),
            'win_rate': win_rate,
            'trades': trades
        }
```

### 4.5 视图层设计 (views.py)

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
import pandas as pd

@require_http_methods(["GET"])
def get_stock_history(request, ticker):
    """获取股票历史数据"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM stock_history
            WHERE ticker = %s
            AND trade_date BETWEEN %s AND %s
            ORDER BY trade_date
        """, [ticker, start_date, end_date])
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({'data': data})

@require_http_methods(["POST"])
def run_strategy(request):
    """运行策略"""
    import json
    from .strategy.signals import MAStrategy
    from .strategy.backtest import BacktestEngine

    body = json.loads(request.body)
    ticker = body.get('ticker')
    strategy_type = body.get('strategy_type', 'MA')
    params = body.get('params', {})

    # 获取数据
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM stock_history
            WHERE ticker = %s
            ORDER BY trade_date
        """, [ticker])
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]

    df = pd.DataFrame(data)

    # 运行策略
    if strategy_type == 'MA':
        strategy = MAStrategy(**params)
    elif strategy_type == 'MACD':
        from .strategy.signals import MACDStrategy
        strategy = MACDStrategy(**params)
    else:
        from .strategy.signals import RSIStrategy
        strategy = RSIStrategy(**params)

    signals = strategy.generate_signals(df)
    backtest = BacktestEngine()
    results = backtest.run_backtest(df, signals)

    return JsonResponse({'signals': signals.to_dict('records'), 'results': results})
```

## 5. API接口设计

### 5.1 RESTful API端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stocks/{ticker}/history | 获取股票历史数据 |
| GET | /api/stocks/{ticker}/history/{period} | 获取股票日线/周线/月线数据 |
| GET | /api/stocks/{ticker}/kline | 获取股票K线数据(用于ECharts) |
| GET | /api/stocks/{ticker}/indicators | 获取股票技术指标数据 |
| GET | /api/market/daily-summary | 获取每日市场涨跌统计 |
| GET | /api/stocks/list | 获取股票列表(支持分页) |
| GET | /api/stocks/{ticker}/signals | 获取交易信号 |
| POST | /api/strategies/run | 运行策略回测 |
| GET | /api/strategies | 获取策略列表 |
| POST | /api/strategies | 创建策略 |
| GET | /api/backtests/{id} | 获取回测结果 |

## 6. ECharts可视化设计

### 6.1 前端技术栈
- **框架**: Vue 3 / React (选择其一)
- **图表库**: ECharts 5.x
- **UI组件库**: Element Plus / Ant Design
- **HTTP请求**: Axios
- **构建工具**: Vite

### 6.2 页面结构

```
stock_visualization/
├── src/
│   ├── components/           # 组件
│   │   ├── StockKLine.vue   # K线图组件
│   │   ├── StockChart.vue   # 股票曲线图组件
│   │   ├── StockSelector.vue # 股票选择器
│   │   ├── PeriodSelector.vue # 周期选择器(日/周/月)
│   │   └── DailyStats.vue   # 每日涨跌统计
│   ├── views/
│   │   ├── Dashboard.vue    # 主页
│   │   ├── StockDetail.vue  # 股票详情页
│   │   └── StockScreener.vue # 股票选股页面
│   ├── api/
│   │   └── stock.js         # API接口
│   └── App.vue
└── index.html
```

### 6.3 股票曲线选股功能

#### 6.3.1 功能说明
- 展示所有股票的价格曲线缩略图
- 支持点击曲线查看详细K线图
- 支持按涨跌幅、成交量等条件筛选
- 支持日期范围选择

#### 6.3.2 API设计
```python
# 视图函数
@require_http_methods(["GET"])
def stock_screener(request):
    """股票选股接口"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_change = request.GET.get('min_change')  # 最小涨跌幅
    max_change = request.GET.get('max_change')  # 最大涨跌幅
    min_volume = request.GET.get('min_volume')  # 最小成交量
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))

    with connection.cursor() as cursor:
        # 计算每个股票在指定日期范围内的涨跌幅
        cursor.execute("""
            WITH stock_range AS (
                SELECT ticker,
                       MIN(CASE WHEN trade_date >= %s THEN trade_date END) as start_day,
                       MAX(CASE WHEN trade_date <= %s THEN trade_date END) as end_day
                FROM stock_history
                GROUP BY ticker
            ),
            price_range AS (
                SELECT sr.ticker,
                       (SELECT close_price FROM stock_history sh
                        WHERE sh.ticker = sr.ticker AND sh.trade_date = sr.end_day) as end_price,
                       (SELECT close_price FROM stock_history sh
                        WHERE sh.ticker = sr.ticker AND sh.trade_date = sr.start_day) as start_price
                FROM stock_range sr
                WHERE sr.start_day IS NOT NULL AND sr.end_day IS NOT NULL
            )
            SELECT pr.ticker,
                   pr.start_price,
                   pr.end_price,
                   ((pr.end_price - pr.start_price) / pr.start_price * 100) as change_percent,
                   (SELECT SUM(sh.volume) FROM stock_history sh
                    WHERE sh.ticker = pr.ticker AND sh.trade_date BETWEEN %s AND %s) as total_volume
            FROM price_range pr
            WHERE (%s IS NULL OR pr.change_percent >= %s)
              AND (%s IS NULL OR pr.change_percent <= %s)
              AND (%s IS NULL OR pr.total_volume >= %s)
            ORDER BY pr.change_percent DESC
            LIMIT %s OFFSET %s
        """, [start_date, end_date, start_date, end_date,
              min_change, min_change, max_change, max_change,
              min_volume, min_volume, page_size, (page - 1) * page_size])

        columns = [col[0] for col in cursor.description]
        stocks = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # 获取总数
        cursor.execute("""
            SELECT COUNT(DISTINCT ticker)
            FROM stock_history
            WHERE trade_date BETWEEN %s AND %s
        """, [start_date, end_date])
        total = cursor.fetchone()[0]

    return JsonResponse({
        'stocks': stocks,
        'total': total,
        'page': page,
        'page_size': page_size
    })
```

#### 6.3.3 前端组件 (StockScreener.vue)
```vue
<template>
  <div class="stock-screener">
    <!-- 筛选条件 -->
    <el-form :inline="true" class="filter-form">
      <el-form-item label="日期范围">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="loadStocks"
        />
      </el-form-item>
      <el-form-item label="涨跌幅">
        <el-input-number v-model="minChange" placeholder="最小" :min="-100" :max="100" />
        <span>-</span>
        <el-input-number v-model="maxChange" placeholder="最大" :min="-100" :max="100" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadStocks">筛选</el-button>
      </el-form-item>
    </el-form>

    <!-- 股票曲线网格 -->
    <el-row :gutter="16" class="stock-grid">
      <el-col
        v-for="stock in stocks"
        :key="stock.ticker"
        :span="6"
        class="stock-item"
        @click="viewStockDetail(stock.ticker)"
      >
        <el-card>
          <div class="stock-header">
            <span class="ticker">{{ stock.ticker }}</span>
            <span :class="['change', stock.change_percent >= 0 ? 'up' : 'down']">
              {{ stock.change_percent.toFixed(2) }}%
            </span>
          </div>
          <div :id="'chart-' + stock.ticker" class="mini-chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="loadStocks"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '@/api/stock'

const dateRange = ref([])
const minChange = ref(null)
const maxChange = ref(null)
const stocks = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadStocks = async () => {
  const { data } = await stockAPI.screener({
    start_date: dateRange.value[0],
    end_date: dateRange.value[1],
    min_change: minChange.value,
    max_change: maxChange.value,
    page: currentPage.value,
    page_size: pageSize.value
  })
  stocks.value = data.stocks
  total.value = data.total

  // 渲染迷你图表
  await nextTick()
  stocks.value.forEach(stock => {
    renderMiniChart(stock.ticker)
  })
}

const renderMiniChart = (ticker) => {
  const chartDom = document.getElementById('chart-' + ticker)
  if (!chartDom) return

  const chart = echarts.init(chartDom)
  // 获取历史数据并渲染曲线
  // ...
}

const viewStockDetail = (ticker) => {
  // 跳转到股票详情页
}
</script>
```

### 6.4 每日个股涨跌个数统计

#### 6.4.1 功能说明
- 统计每日上涨、下跌、平盘的股票数量
- 展示涨跌分布饼图
- 展示涨跌趋势柱状图
- 支持选择特定日期查看详情

#### 6.4.2 API设计
```python
@require_http_methods(["GET"])
def daily_market_summary(request):
    """每日市场统计接口"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    with connection.cursor() as cursor:
        # 统计每日涨跌情况
        cursor.execute("""
            SELECT trade_date,
                   COUNT(*) as total_count,
                   SUM(CASE WHEN close_price > open_price THEN 1 ELSE 0 END) as up_count,
                   SUM(CASE WHEN close_price < open_price THEN 1 ELSE 0 END) as down_count,
                   SUM(CASE WHEN close_price = open_price THEN 1 ELSE 0 END) as flat_count,
                   AVG(CASE WHEN close_price > open_price
                       THEN (close_price - open_price) / open_price * 100
                       ELSE NULL END) as avg_up_percent,
                   AVG(CASE WHEN close_price < open_price
                       THEN (close_price - open_price) / open_price * 100
                       ELSE NULL END) as avg_down_percent
            FROM stock_history
            WHERE trade_date BETWEEN %s AND %s
            GROUP BY trade_date
            ORDER BY trade_date
        """, [start_date, end_date])

        columns = [col[0] for col in cursor.description]
        daily_stats = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({'data': daily_stats})
```

#### 6.4.3 前端组件 (DailyStats.vue)
```vue
<template>
  <div class="daily-stats">
    <!-- 日期选择 -->
    <el-form :inline="true">
      <el-form-item label="日期范围">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          @change="loadStats"
        />
      </el-form-item>
    </el-form>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-cards">
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="label">上涨</div>
            <div class="value up">{{ latestStats.up_count }}</div>
            <div class="percent">{{ latestStats.avg_up_percent?.toFixed(2) }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="label">下跌</div>
            <div class="value down">{{ latestStats.down_count }}</div>
            <div class="percent">{{ latestStats.avg_down_percent?.toFixed(2) }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="label">平盘</div>
            <div class="value">{{ latestStats.flat_count }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 涨跌趋势图 -->
    <el-card class="chart-card">
      <div id="trendChart" style="width: 100%; height: 400px;"></div>
    </el-card>

    <!-- 涨跌分布饼图 -->
    <el-card class="chart-card">
      <div id="pieChart" style="width: 100%; height: 400px;"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '@/api/stock'

const dateRange = ref([])
const dailyStats = ref([])
const latestStats = ref({})

const loadStats = async () => {
  const { data } = await stockAPI.dailySummary({
    start_date: dateRange.value[0],
    end_date: dateRange.value[1]
  })
  dailyStats.value = data.data
  latestStats.value = data.data[data.data.length - 1]

  renderTrendChart()
  renderPieChart()
}

const renderTrendChart = () => {
  const chart = echarts.init(document.getElementById('trendChart'))
  const dates = dailyStats.value.map(d => d.trade_date)

  chart.setOption({
    title: { text: '每日涨跌趋势' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['上涨', '下跌', '平盘'] },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value' },
    series: [
      { name: '上涨', type: 'bar', data: dailyStats.value.map(d => d.up_count), itemStyle: { color: '#f56c6c' } },
      { name: '下跌', type: 'bar', data: dailyStats.value.map(d => d.down_count), itemStyle: { color: '#67c23a' } },
      { name: '平盘', type: 'bar', data: dailyStats.value.map(d => d.flat_count), itemStyle: { color: '#909399' } }
    ]
  })
}

const renderPieChart = () => {
  const chart = echarts.init(document.getElementById('pieChart'))
  chart.setOption({
    title: { text: '涨跌分布', left: 'center' },
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: '50%',
      data: [
        { value: latestStats.value.up_count, name: '上涨', itemStyle: { color: '#f56c6c' } },
        { value: latestStats.value.down_count, name: '下跌', itemStyle: { color: '#67c23a' } },
        { value: latestStats.value.flat_count, name: '平盘', itemStyle: { color: '#909399' } }
      ],
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } }
    }]
  })
}
</script>
```

### 6.5 单股日线/周线/月线查看

#### 6.5.1 功能说明
- 支持切换日线、周线、月线周期
- K线图 + 均线叠加
- 成交量柱状图
- 技术指标(MACD、KDJ)展示
- 缩放、平移交互

#### 6.5.2 API设计
```python
@require_http_methods(["GET"])
def get_stock_kline(request, ticker):
    """获取股票K线数据"""
    period = request.GET.get('period', 'daily')  # daily, weekly, monthly
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    with connection.cursor() as cursor:
        if period == 'daily':
            cursor.execute("""
                SELECT trade_date, open_price, high_price, low_price, close_price, volume,
                       ma_1, ma_2, ma_3
                FROM stock_history
                WHERE ticker = %s
                  AND trade_date BETWEEN %s AND %s
                ORDER BY trade_date
            """, [ticker, start_date, end_date])
        elif period == 'weekly':
            cursor.execute("""
                SELECT
                    DATE(DATE_SUB(trade_date, INTERVAL WEEKDAY(trade_date) DAY)) as trade_date,
                    MIN(open_price) as open_price,
                    MAX(high_price) as high_price,
                    MIN(low_price) as low_price,
                    MAX(close_price) as close_price,
                    SUM(volume) as volume
                FROM stock_history
                WHERE ticker = %s
                  AND trade_date BETWEEN %s AND %s
                GROUP BY YEAR(trade_date), WEEK(trade_date)
                ORDER BY trade_date
            """, [ticker, start_date, end_date])
        else:  # monthly
            cursor.execute("""
                SELECT
                    DATE_FORMAT(trade_date, '%Y-%m-01') as trade_date,
                    MIN(open_price) as open_price,
                    MAX(high_price) as high_price,
                    MIN(low_price) as low_price,
                    MAX(close_price) as close_price,
                    SUM(volume) as volume
                FROM stock_history
                WHERE ticker = %s
                  AND trade_date BETWEEN %s AND %s
                GROUP BY YEAR(trade_date), MONTH(trade_date)
                ORDER BY trade_date
            """, [ticker, start_date, end_date])

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({'data': data})
```

#### 6.5.3 前端组件 (StockDetail.vue)
```vue
<template>
  <div class="stock-detail">
    <!-- 股票信息头部 -->
    <div class="stock-header">
      <h2>{{ stockInfo.ticker }}</h2>
      <el-radio-group v-model="period" @change="loadKLineData">
        <el-radio-button label="daily">日线</el-radio-button>
        <el-radio-button label="weekly">周线</el-radio-button>
        <el-radio-button label="monthly">月线</el-radio-button>
      </el-radio-group>
    </div>

    <!-- K线图 -->
    <div id="klineChart" style="width: 100%; height: 600px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '@/api/stock'

const ticker = ref('000002')
const period = ref('daily')
const klineData = ref([])
let klineChart = null

const loadKLineData = async () => {
  const { data } = await stockAPI.getKLine(ticker.value, {
    period: period.value,
    start_date: '2023-01-01',
    end_date: new Date().toISOString().split('T')[0]
  })
  klineData.value = data.data
  renderKLineChart()
}

const renderKLineChart = () => {
  if (klineChart) {
    klineChart.dispose()
  }
  klineChart = echarts.init(document.getElementById('klineChart'))

  const dates = klineData.value.map(d => d.trade_date)
  const data = klineData.value.map(d => [
    d.open_price, d.close_price, d.low_price, d.high_price
  ])
  const volumes = klineData.value.map((d, i) => [
    i, d.volume,
    d.close_price >= d.open_price ? 1 : -1
  ])
  const ma5 = klineData.value.map(d => d.ma_1)
  const ma10 = klineData.value.map(d => d.ma_2)
  const ma20 = klineData.value.map(d => d.ma_3)

  klineChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    axisPointer: {
      link: { xAxisIndex: 'all' },
      label: { backgroundColor: '#777' }
    },
    grid: [
      { left: '10%', right: '8%', height: '50%' },
      { left: '10%', right: '8%', top: '63%', height: '16%' }
    ],
    xAxis: [
      { type: 'category', data: dates, scale: true, boundaryGap: false, gridIndex: 0, axisLabel: { show: false } },
      { type: 'category', data: dates, scale: true, boundaryGap: false, gridIndex: 1, axisLabel: { show: false } }
    ],
    yAxis: [
      { scale: true, gridIndex: 0, splitLine: { show: true, lineStyle: { color: '#999' } } },
      { scale: true, gridIndex: 1, splitLine: { show: false }, axisLabel: { show: false } }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
      { show: true, xAxisIndex: [0, 1], type: 'slider', top: '85%', start: 50, end: 100 }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: data,
        itemStyle: {
          color: '#ef232a',
          color0: '#14b143',
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        }
      },
      { name: 'MA5', type: 'line', data: ma5, smooth: true, lineStyle: { opacity: 0.5 } },
      { name: 'MA10', type: 'line', data: ma10, smooth: true, lineStyle: { opacity: 0.5 } },
      { name: 'MA20', type: 'line', data: ma20, smooth: true, lineStyle: { opacity: 0.5 } },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: function(params) {
            return params.data[2] > 0 ? '#ef232a' : '#14b143'
          }
        }
      }
    ]
  })
}

onMounted(() => {
  loadKLineData()
  window.addEventListener('resize', () => klineChart?.resize())
})
</script>
```

### 6.6 依赖包列表
```
# 后端
django>=4.2
djangorestframework
pandas
numpy
mysqlclient

# 前端
vue@^3.3
echarts@^5.4
element-plus@^2.4
axios
vite
```

## 7. 配置文件 (settings.py)

```python
# Database settings - 连接到现有MySQL数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stock_data',
        'USER': 'stock',
        'PASSWORD': 'w123456W!',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Celery配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# 时区设置
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

# 已安装应用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'stock',
    'strategy',
    'trading',
]
```

## 8. 部署建议

### 8.1 环境要求
- Python 3.9+
- Django 4.2+
- MySQL 8.0+
- Redis 6.0+

### 8.2 依赖包
```
django>=4.2
djangorestframework
pandas
numpy
celery
redis
mysqlclient
ta-lib
```

## 9. 扩展功能建议

### 9.1 数据增强
- 实时行情推送
- 多数据源整合
- 财务数据接入

### 9.2 策略增强
- 机器学习策略
- 量化因子挖掘
- 风险管理模型

### 9.3 交易增强
- 实盘交易接口对接
- 组合优化
- 止损止盈设置

## 10. 开发步骤

1. **环境搭建**: 创建Django项目，配置数据库连接
2. **模型定义**: 创建策略、回测、信号等模型
3. **数据访问**: 实现与现有stock_history表的交互
4. **指标计算**: 实现技术指标计算模块
5. **策略实现**: 实现基础交易策略(双均线、MACD、RSI等)
6. **回测引擎**: 实现回测逻辑和指标计算
7. **API开发**: 开发RESTful API接口
8. **前端开发**: 实现数据可视化和策略管理界面
9. **测试验证**: 使用历史数据验证策略有效性

## 11. 股票涨跌形态分析功能

### 11.1 功能概述
按照3天、5天统计股票的连续涨跌形态，将涨跌编码为数字后进行分类统计和可视化展示。

### 11.2 编码规则
- **涨**: 3
- **平**: 1
- **跌**: 2

例如：
- 333: 连续3天上涨
- 332: 连续2天上涨后下跌
- 222: 连续3天下跌

### 11.3 数据模型

```python
class StockTrendPattern(models.Model):
    """股票涨跌形态模型"""
    pattern_type = models.CharField(max_length=20, verbose_name='形态类型', help_text='如: 333, 332等')
    days = models.IntegerField(verbose_name='统计天数', help_text='3天或5天')
    ticker = models.CharField(max_length=10, verbose_name='股票代码')
    pattern_date = models.DateField(verbose_name='形态结束日期')
    pattern_detail = models.JSONField(verbose_name='形态详情', help_text='存储每日涨跌详情')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        managed = True
        db_table = 'stock_trend_pattern'
        verbose_name = '股票涨跌形态'
        verbose_name_plural = '股票涨跌形态'
        unique_together = (('ticker', 'pattern_date', 'days'),)

    def __str__(self):
        return f"{self.ticker} - {self.pattern_type} ({self.days}天)"
```

### 11.4 视图功能

- **generate_trend_patterns()**: 生成指定天数的涨跌形态数据
  - 遍历所有股票，使用滑动窗口分析
  - 根据收盘价变化判断涨跌（涨=3, 平=1, 跌=2）
  - 创建或更新形态记录

- **get_patterns_by_type()**: 获取指定形态的所有股票
  - 根据天数和形态类型查询
  - 返回该形态下的所有股票列表

- **get_all_pattern_types()**: 获取所有形态类型及其统计
  - 统计每种形态的股票数量
  - 返回按数量排序的结果

- **trend_pattern_visualization()**: 可视化页面
  - 渲染HTML模板
  - 提供交互式界面

- **trend_pattern_data()**: 获取可视化数据
  - 返回形态统计信息
  - 包含每种形态的涨跌次数统计

### 11.5 URL路由

| 路径 | 方法 | 说明 |
|------|------|------|
| `/stock/visualization/` | GET | 可视化页面 |
| `/stock/api/generate-patterns/<days>/` | POST | 生成数据（days=3或5） |
| `/stock/api/patterns/<days>/<pattern_type>/` | GET | 查询特定形态的股票 |
| `/stock/api/trend-pattern-data/` | GET | 获取统计数据 |

### 11.6 可视化界面特性

1. **现代化响应式设计**
   - 渐变色背景和卡片式布局
   - 悬停动画效果
   - 适配各种屏幕尺寸

2. **交互功能**
   - 3天/5天形态切换
   - 一键生成数据
   - 点击形态卡片查看详情
   - 实时加载状态提示

3. **数据展示**
   - 图例说明（涨/平/跌）
   - 形态卡片网格显示
   - 形态详情统计（涨跌平数量）
   - 股票列表表格

4. **颜色编码**
   - 涨（3）: 绿色 (#28a745)
   - 跌（2）: 红色 (#dc3545)
   - 平（1）: 灰色 (#6c757d)

### 11.7 使用方法

1. 启动Django服务：
   ```bash
   python manage.py runserver
   ```

2. 访问可视化页面：
   ```
   http://localhost:8000/stock/visualization/
   ```

3. 操作步骤：
   - 选择统计天数（3天或5天）
   - 点击"生成数据"按钮分析现有股票数据
   - 查看各种形态及其股票数量
   - 点击任意形态卡片查看该形态下的具体股票列表

### 11.8 管理后台

通过Django Admin可以管理涨跌形态数据：
- 查看所有形态记录
- 按形态类型、天数、日期筛选
- 查看详细形态信息

## 12. 波浪数据文件功能

### 12.1 功能概述
从外部 JSON 文件读取股票涨跌形态数据，支持树形展示和图表分析。

### 12.2 数据来源
- **数据目录**: `/data/stock/wavedata/`
- **文件命名**: `YYYY-MM-DD.json` (如: `2026-02-24.json`)
- **数据格式**:
```json
{
    "333": ["000007", "000021", "000519", ...],
    "332": ["000002", "000066", "000609", ...],
    "222": [...]
}
```

### 12.3 编码规则
- **1**: 平盘
- **2**: 下跌
- **3**: 上涨

例如：
- "333": 连续3天上涨
- "332": 连续2天上涨后下跌
- "222": 连续3天下跌

### 12.4 工具函数 (models.py)

```python
WAVEDATA_DIR = '/data/stock/wavedata/'

def get_wavedata_path(date_str=None):
    """获取指定日期的波浪数据文件路径"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join(WAVEDATA_DIR, f'{date_str}.json')
    if os.path.exists(file_path):
        return file_path
    return None

def load_wavedata(date_str=None):
    """从JSON文件加载波浪数据"""
    file_path = get_wavedata_path(date_str)
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading wavedata from {file_path}: {e}")
    return {}
```

### 12.5 API 接口

| 路径 | 方法 | 说明 |
|------|------|------|
| `/stock/api/available-dates/` | GET | 获取可用的数据日期列表 |
| `/stock/api/trend-pattern-data/?date=YYYY-MM-DD` | GET | 获取指定日期的形态统计 |
| `/stock/api/pattern-tickers/<pattern_type>/?date=YYYY-MM-DD` | GET | 获取指定形态的股票代码列表 |
| `/stock/chart/<pattern_type>/` | GET | 形态图表页面 |
| `/stock/api/pattern-chart-data/<pattern_type>/?date=YYYY-MM-DD` | GET | 获取形态图表数据 |

### 12.6 树形展示页面 (trend_pattern.html)

#### 功能特性
1. **树形结构**
   - 每种形态作为树节点
   - 点击展开/折叠查看股票代码
   - 箭头图标指示展开状态 (▶/▼)

2. **形态节点**
   - 彩色标签显示形态（红涨绿跌灰平）
   - 显示该形态的股票数量
   - 显示涨跌平统计详情
   - **📊 查看图表** 按钮跳转到图表页面

3. **股票代码展示**
   - 网格布局显示股票代码
   - 点击股票代码跳转到 [百度股票通](https://gushitong.baidu.com)
   - 跳转格式: `https://gushitong.baidu.com/stock/ab-{ticker}`
   - 分页加载（每页50只，支持"加载更多"）

4. **交互功能**
   - 日期选择器切换不同日期数据
   - 全部展开/全部折叠按钮
   - 刷新数据按钮

#### 颜色编码（中国股市习惯）
- **涨 (3)**: 红色 `#dc3545`
- **跌 (2)**: 绿色 `#28a745`
- **平 (1)**: 灰色 `#6c757d`

### 12.7 形态图表页面 (pattern_chart.html)

#### 功能特性
1. **ECharts 多线图**
   - X 轴：交易日期
   - Y 轴：收盘价
   - 每条线：一只股票的价格走势
   - 自动生成不同颜色区分每只股票

2. **图表控制**
   - 缩放拖拽（内置滑块）
   - 图例可点击显示/隐藏单只股票
   - 悬停显示具体价格
   - 默认只显示前10条线，避免混乱

3. **页面信息**
   - 显示形态类型（彩色标签）
   - 显示数据日期
   - 显示总股票数和显示股票数
   - 股票标签可点击切换显示/隐藏

4. **ECharts 加载**
   - 使用 CDN 加载 ECharts 5.4.3
   - 备用 CDN 机制
   - 加载等待和超时检测
   - 友好的错误提示

### 12.8 使用方法

#### 1. 查看形态列表
```
访问: http://localhost:8000/stock/visualization/
```

#### 2. 查看形态图表
```
1. 在形态列表页面点击任意形态的"📊 查看图表"按钮
2. 跳转到: http://localhost:8000/stock/chart/{pattern_type}/
3. 查看该形态下所有股票的价格走势对比
```

#### 3. 查看股票详情
```
1. 在形态列表中展开任意形态
2. 点击股票代码
3. 在新标签页打开: https://gushitong.baidu.com/stock/ab-{ticker}
```

### 12.9 技术说明

#### 文件结构
```
stock/
├── models.py              # 数据模型 + 波浪数据工具函数
├── views.py               # 视图函数
├── urls.py                # URL 路由配置
└── templates/
    ├── trend_pattern.html      # 树形展示页面
    └── pattern_chart.html      # 图表分析页面
```

#### 响应式设计
- 支持桌面和移动端
- 渐变色背景和卡片式布局
- 平滑动画效果
- 悬停交互反馈

---

*文档版本: 2.0*
*创建日期: 2026-02-23*
*更新日期: 2026-02-24*
