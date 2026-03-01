"""
自定义曲线图数据处理示例

这个脚本演示如何：
1. 从 MySQL 数据库获取股票数据
2. 计算自定义技术指标
3. 发送处理后的数据到前端图表 API
"""

import os
import django
import requests

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockproj.settings')
django.setup()

from stock.models import StockHistory


def calculate_sma(data, period=20):
    """
    计算简单移动平均 (SMA)

    Args:
        data: 价格数据列表
        period: 周期（默认20日）

    Returns:
        SMA 数据列表
    """
    sma = []
    for i in range(len(data)):
        if i < period - 1:
            sma.append(None)
        else:
            avg = sum(data[i - period + 1: i + 1]) / period
            sma.append(avg)
    return sma


def calculate_ema(data, period=20):
    """
    计算指数移动平均 (EMA)

    Args:
        data: 价格数据列表
        period: 周期（默认20日）

    Returns:
        EMA 数据列表
    """
    ema = []
    multiplier = 2 / (period + 1)

    # 第一天的EMA等于当天价格
    ema.append(data[0])

    # 计算后续的EMA
    for i in range(1, len(data)):
        ema_value = (data[i] - ema[i - 1]) * multiplier + ema[i - 1]
        ema.append(ema_value)

    return ema


def calculate_bollinger_bands(data, period=20, std_dev=2):
    """
    计算布林带

    Args:
        data: 价格数据列表
        period: 周期（默认20日）
        std_dev: 标准差倍数（默认2）

    Returns:
        上轨、中轨、下轨数据
    """
    import numpy as np

    sma = calculate_sma(data, period)
    upper_band = []
    lower_band = []

    for i in range(len(data)):
        if sma[i] is None or i < period - 1:
            upper_band.append(None)
            lower_band.append(None)
        else:
            # 计算标准差
            std = np.std(data[i - period + 1: i + 1])
            upper_band.append(sma[i] + std * std_dev)
            lower_band.append(sma[i] - std * std_dev)

    return upper_band, sma, lower_band


def calculate_rsi(data, period=14):
    """
    计算相对强弱指标 (RSI)

    Args:
        data: 价格数据列表
        period: 周期（默认14日）

    Returns:
        RSI 数据列表
    """
    rsi = []

    for i in range(len(data)):
        if i < period:
            rsi.append(None)
        else:
            gains = []
            losses = []

            for j in range(i - period + 1, i + 1):
                change = data[j] - data[j - 1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period

            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi_value = 100 - (100 / (1 + rs))
                rsi.append(rsi_value)

    return rsi


def generate_custom_chart_data(ticker, days=200):
    """
    生成自定义曲线图数据

    Args:
        ticker: 股票代码
        days: 获取天数（默认200天）

    Returns:
        用于前端图表的数据字典
    """
    # 1. 从数据库获取股票数据
    history = StockHistory.objects.filter(
        ticker=ticker
    ).order_by('trade_date')[:days]

    if not history.exists():
        print(f"未找到股票 {ticker} 的数据")
        return None

    data_list = list(history)

    # 2. 提取基础数据
    dates = [h.trade_date.strftime('%Y-%m-%d') for h in data_list]
    close_prices = [float(h.close_price) for h in data_list]
    high_prices = [float(h.high_price) for h in data_list]
    low_prices = [float(h.low_price) for h in data_list]
    volumes = [float(h.volume) for h in data_list]

    # 3. 计算自定义指标
    print(f"正在计算技术指标...")

    # SMA 指标
    sma5 = calculate_sma(close_prices, 5)
    sma10 = calculate_sma(close_prices, 10)
    sma20 = calculate_sma(close_prices, 20)
    sma50 = calculate_sma(close_prices, 50)

    # EMA 指标
    ema12 = calculate_ema(close_prices, 12)
    ema26 = calculate_ema(close_prices, 26)

    # 计算 MACD
    macd_line = []
    signal_line = []
    macd_histogram = []

    for i in range(len(close_prices)):
        if ema12[i] and ema26[i]:
            macd = ema12[i] - ema26[i]
            macd_line.append(macd)
        else:
            macd_line.append(None)

    # Signal线是MACD的9日EMA
    macd_values = [v for v in macd_line if v is not None]
    signal_values = calculate_ema(macd_values, 9)

    signal_idx = 0
    for i in range(len(close_prices)):
        if macd_line[i] is not None:
            signal_line.append(signal_values[signal_idx])
            signal_idx += 1
        else:
            signal_line.append(None)

    # MACD柱状图
    for i in range(len(close_prices)):
        if macd_line[i] and signal_line[i]:
            macd_histogram.append(macd_line[i] - signal_line[i])
        else:
            macd_histogram.append(None)

    # 4. 构建返回数据
    chart_data = {
        'dates': dates,
        'series': [
            # 基础价格数据
            {
                'name': '收盘价',
                'data': close_prices,
                'type': 'line',
                'color': '#667eea',
                'smooth': True,
                'showSymbol': False
            },
            # SMA 均线
            {
                'name': 'SMA5',
                'data': sma5,
                'type': 'line',
                'color': '#f59e0b',
                'smooth': True,
                'showSymbol': False
            },
            {
                'name': 'SMA10',
                'data': sma10,
                'type': 'line',
                'color': '#06b6d4',
                'smooth': True,
                'showSymbol': False
            },
            {
                'name': 'SMA20',
                'data': sma20,
                'type': 'line',
                'color': '#ff6b6b',
                'smooth': True,
                'showSymbol': False
            },
            {
                'name': 'SMA50',
                'data': sma50,
                'type': 'line',
                'color': '#8b5cf6',
                'smooth': True,
                'showSymbol': False
            },
            # MACD 指标
            {
                'name': 'MACD',
                'data': macd_line,
                'type': 'line',
                'color': '#ef232a',
                'smooth': True,
                'showSymbol': False
            },
            {
                'name': 'Signal',
                'data': signal_line,
                'type': 'line',
                'color': '#14b143',
                'smooth': True,
                'showSymbol': False
            },
            {
                'name': 'MACD柱状图',
                'data': macd_histogram,
                'type': 'bar',
                'color': '#909399',
                'showSymbol': False
            }
        ]
    }

    return chart_data


def send_to_api(chart_data):
    """
    发送数据到自定义曲线图 API

    Args:
        chart_data: 图表数据字典
    """
    api_url = 'http://localhost:8000/stock/api/custom-chart-data/'

    try:
        response = requests.post(api_url, json=chart_data, timeout=30)
        result = response.json()

        if result.get('success'):
            print("数据发送成功！")
            print(f"包含 {len(chart_data['series'])} 个系列")
            print(f"日期范围: {chart_data['dates'][0]} 到 {chart_data['dates'][-1]}")
        else:
            print(f"发送失败: {result.get('error')}")

    except Exception as e:
        print(f"发送数据时出错: {e}")


if __name__ == '__main__':
    # 使用示例
    ticker = '600000'  # 股票代码
    days = 200  # 获取天数

    print(f"开始处理股票 {ticker} 的数据...")
    print(f"获取最近 {days} 天数据\n")

    # 生成图表数据
    chart_data = generate_custom_chart_data(ticker, days)

    if chart_data:
        print("\n生成的指标:")
        for series in chart_data['series']:
            print(f"  - {series['name']}: {sum(1 for v in series['data'] if v is not None)} 个有效数据点")

        print(f"\n发送到 API...")
        send_to_api(chart_data)
    else:
        print("处理失败！")
