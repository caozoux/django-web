from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, F, Case, When, Value
from decimal import Decimal
from datetime import datetime
import os
from .models import StockHistory, StockTrendPattern, WAVEDATA_DIR, load_wavedata
from django.db import transaction


def analyze_trend_pattern(close_prices):
    """
    分析涨跌形态
    涨: 3, 平: 1, 跌: 2
    """
    pattern = ""
    for i in range(len(close_prices) - 1):
        if close_prices[i + 1] > close_prices[i]:
            pattern += "3"  # 涨
        elif close_prices[i + 1] == close_prices[i]:
            pattern += "1"  # 平
        else:
            pattern += "2"  # 跌
    return pattern


def generate_trend_patterns(request, days):
    """生成指定天数的涨跌形态数据"""
    if days not in [3, 5]:
        return JsonResponse({'error': '只支持3天或5天的统计'}, status=400)

    # 获取所有股票
    tickers = StockHistory.objects.values('ticker').distinct()

    created_count = 0
    updated_count = 0

    with transaction.atomic():
        for ticker_dict in tickers:
            ticker = ticker_dict['ticker']

            # 获取该股票最近的交易数据，按日期升序排列
            history = StockHistory.objects.filter(
                ticker=ticker
            ).order_by('trade_date')

            # 滑动窗口分析
            data_list = list(history)
            for i in range(len(data_list) - days):
                window = data_list[i:i + days + 1]  # 需要days+1天数据来计算days天的涨跌
                close_prices = [float(d.close_price) for d in window]

                pattern = analyze_trend_pattern(close_prices[:days + 1])

                # 构造详情
                detail = []
                for j in range(days):
                    diff = close_prices[j + 1] - close_prices[j]
                    trend_type = "涨" if diff > 0 else ("平" if diff == 0 else "跌")
                    detail.append({
                        'day': j + 1,
                        'close': close_prices[j],
                        'next_close': close_prices[j + 1],
                        'diff': float(diff),
                        'trend': trend_type,
                        'code': pattern[j]
                    })

                # 创建或更新记录
                pattern_date = window[days].trade_date
                obj, created = StockTrendPattern.objects.update_or_create(
                    ticker=ticker,
                    pattern_date=pattern_date,
                    days=days,
                    defaults={
                        'pattern_type': pattern,
                        'pattern_detail': detail
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

    return JsonResponse({
        'success': True,
        'message': f'成功生成{days}天涨跌形态数据',
        'created': created_count,
        'updated': updated_count
    })


def get_patterns_by_type(request, days, pattern_type):
    """获取指定形态的所有股票"""
    patterns = StockTrendPattern.objects.filter(
        days=days,
        pattern_type=pattern_type
    ).select_related().order_by('-pattern_date')

    data = []
    for p in patterns:
        data.append({
            'ticker': p.ticker,
            'pattern_type': p.pattern_type,
            'pattern_date': p.pattern_date.strftime('%Y-%m-%d'),
            'detail': p.pattern_detail
        })

    return JsonResponse({
        'success': True,
        'days': days,
        'pattern_type': pattern_type,
        'count': len(data),
        'data': data
    })


def get_all_pattern_types(request, days):
    """获取所有形态类型及其统计"""
    if days not in [3, 5]:
        return JsonResponse({'error': '只支持3天或5天的统计'}, status=400)

    patterns = StockTrendPattern.objects.filter(days=days).values(
        'pattern_type'
    ).annotate(
        count=Count('id')
    ).order_by('-count')

    return JsonResponse({
        'success': True,
        'days': days,
        'patterns': list(patterns)
    })


def trend_pattern_visualization(request):
    """涨跌形态可视化页面"""
    return render(request, 'trend_pattern.html')


def trend_pattern_data(request):
    """获取可视化页面数据 - 从JSON文件读取"""
    date_str = request.GET.get('date')

    # 从JSON文件加载波浪数据
    wavedata = load_wavedata(date_str)

    if not wavedata:
        return JsonResponse({
            'success': False,
            'error': '未找到波浪数据文件'
        })

    # 转换为前端需要的格式
    pattern_data = []
    for pattern_type, tickers in wavedata.items():
        # 统计涨跌平数量
        up_count = pattern_type.count('3')
        down_count = pattern_type.count('2')
        flat_count = pattern_type.count('1')

        pattern_data.append({
            'pattern_type': pattern_type,
            'count': len(tickers),
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count
        })

    # 按数量排序
    pattern_data.sort(key=lambda x: x['count'], reverse=True)

    return JsonResponse({
        'success': True,
        'date': date_str or datetime.now().strftime('%Y-%m-%d'),
        'patterns': pattern_data,
        'total_stocks': sum(len(v) for v in wavedata.values())
    })


def get_pattern_tickers(request, pattern_type):
    """获取指定形态的股票代码列表"""
    date_str = request.GET.get('date')

    wavedata = load_wavedata(date_str)

    if not wavedata:
        return JsonResponse({
            'success': False,
            'error': '未找到波浪数据文件'
        })

    tickers = wavedata.get(pattern_type, [])

    return JsonResponse({
        'success': True,
        'pattern_type': pattern_type,
        'date': date_str or datetime.now().strftime('%Y-%m-%d'),
        'count': len(tickers),
        'tickers': tickers
    })


def get_available_dates(request):
    """获取可用的波浪数据日期列表"""
    try:
        files = os.listdir(WAVEDATA_DIR)
        # 提取日期部分 (YYYY-MM-DD.json)
        dates = sorted([f.replace('.json', '') for f in files if f.endswith('.json')])

        return JsonResponse({
            'success': True,
            'dates': dates,
            'latest': dates[-1] if dates else None
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def pattern_chart_page(request, pattern_type):
    """形态图表页面"""
    date_str = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))

    return render(request, 'pattern_chart.html', {
        'pattern_type': pattern_type,
        'date': date_str
    })


def get_pattern_chart_data(request, pattern_type):
    """获取指定形态的股票收盘价数据"""
    date_str = request.GET.get('date')
    wavedata = load_wavedata(date_str)

    if not wavedata:
        return JsonResponse({
            'success': False,
            'error': '未找到波浪数据文件'
        })

    tickers_data = wavedata.get(pattern_type, [])

    # 从对象数组中提取股票代码列表
    tickers = [item['ticker'] for item in tickers_data]

    # 限制股票数量，避免图表过于拥挤
    max_tickers = 50
    selected_tickers = tickers[:max_tickers]

    # 获取每个股票的收盘价数据
    chart_data = {}

    for ticker in selected_tickers:
        history = StockHistory.objects.filter(
            ticker=ticker
        ).order_by('trade_date')

        dates = [h.trade_date.strftime('%Y-%m-%d') for h in history]
        closes = [float(h.close_price) for h in history]

        chart_data[ticker] = {
            'dates': dates,
            'closes': closes
        }

    return JsonResponse({
        'success': True,
        'pattern_type': pattern_type,
        'date': date_str or datetime.now().strftime('%Y-%m-%d'),
        'total_tickers': len(tickers),
        'displayed_tickers': len(selected_tickers),
        'data': chart_data
    })


def strategy_watch_page(request):
    """策略观察页面"""
    return render(request, 'strategy_watch.html')


def get_stock_price_data(request, ticker):
    """获取指定股票的价格数据（用于策略观察）"""
    try:
        # 获取该股票最近的交易数据
        history = StockHistory.objects.filter(
            ticker=ticker
        ).order_by('trade_date')[:1000]  # 最多返回1000天数据

        if not history.exists():
            return JsonResponse({
                'success': False,
                'error': f'未找到股票 {ticker} 的数据'
            })

        data_list = list(history)

        # 构建返回数据
        dates = [h.trade_date.strftime('%Y-%m-%d') for h in data_list]
        opens = [float(h.open_price) for h in data_list]
        highs = [float(h.high_price) for h in data_list]
        lows = [float(h.low_price) for h in data_list]
        closes = [float(h.close_price) for h in data_list]
        volumes = [float(h.volume) for h in data_list]

        # 获取 MA 数据
        ma1 = [float(h.ma_1) if h.ma_1 is not None else None for h in data_list]
        ma2 = [float(h.ma_2) if h.ma_2 is not None else None for h in data_list]
        ma3 = [float(h.ma_3) if h.ma_3 is not None else None for h in data_list]

        # 计算涨跌颜色（根据收盘价）
        colors = []
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                colors.append('#ef232a')  # 涨 - 红色
            elif closes[i] < closes[i-1]:
                colors.append('#14b143')  # 跌 - 绿色
            else:
                colors.append('#909399')  # 平 - 灰色

        # 第一天没有涨跌比较，用灰色
        colors.insert(0, '#909399')

        # 计算涨跌幅（百分比）
        changes = [None]  # 第一天没有涨跌幅
        for i in range(1, len(closes)):
            change = ((closes[i] - closes[i-1]) / closes[i-1]) * 100
            changes.append(change)

        return JsonResponse({
            'success': True,
            'ticker': ticker,
            'data': {
                'dates': dates,
                'open': opens,
                'high': highs,
                'low': lows,
                'close': closes,
                'volume': volumes,
                'colors': colors,
                'ma1': ma1,
                'ma2': ma2,
                'ma3': ma3,
                'changes': changes
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

