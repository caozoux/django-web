from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.db import connection
from datetime import datetime, timedelta, date
from decimal import Decimal


@require_http_methods(["GET"])
def daily_market_summary(request):
    """每日市场涨跌统计"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # 如果没有提供日期，默认查询最近30天
    if not end_date:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if not start_date:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    with connection.cursor() as cursor:
        # 计算每日涨跌情况
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
        daily_stats = []
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            # 转换Decimal为float
            for key, value in data.items():
                if isinstance(value, Decimal):
                    data[key] = float(value)
                elif isinstance(value, date):
                    data[key] = str(value)
            daily_stats.append(data)

    return JsonResponse({'data': daily_stats})


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

    # 默认查询最近一个月
    if not end_date:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if not start_date:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    with connection.cursor() as cursor:
        # 计算每个股票在指定日期范围内的涨跌幅
        cursor.execute("""
            WITH stock_range AS (
                SELECT ticker,
                       MAX(CASE WHEN trade_date >= %s THEN trade_date END) as start_day,
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
            ),
            stock_data AS (
                SELECT pr.ticker,
                       pr.start_price,
                       pr.end_price,
                       ((pr.end_price - pr.start_price) / pr.start_price * 100) as change_percent,
                       (SELECT SUM(sh.volume) FROM stock_history sh
                        WHERE sh.ticker = pr.ticker AND sh.trade_date BETWEEN %s AND %s) as total_volume
                FROM price_range pr
            )
            SELECT * FROM stock_data
            WHERE (%s IS NULL OR change_percent >= %s)
              AND (%s IS NULL OR change_percent <= %s)
              AND (%s IS NULL OR total_volume >= %s)
            ORDER BY change_percent DESC
            LIMIT %s OFFSET %s
        """, [start_date, end_date, start_date, end_date,
              min_change, min_change, max_change, max_change,
              min_volume, min_volume, page_size, (page - 1) * page_size])

        columns = [col[0] for col in cursor.description]
        stocks = []
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            # 转换Decimal为float
            for key, value in data.items():
                if isinstance(value, Decimal):
                    data[key] = float(value)
                elif value is None:
                    data[key] = 0.0
            stocks.append(data)

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


@require_http_methods(["GET"])
def get_stock_kline(request, ticker):
    """获取股票K线数据"""
    period = request.GET.get('period', 'daily')  # daily, weekly, monthly
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # 默认查询最近一年
    if not end_date:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if not start_date:
        start_date = end_date - timedelta(days=365)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

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
                GROUP BY YEAR(trade_date), WEEK(trade_date, 5), DATE(DATE_SUB(trade_date, INTERVAL WEEKDAY(trade_date) DAY))
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
        data = []
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            # 转换Decimal为float
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)
                elif isinstance(value, date):
                    item[key] = str(value)
            data.append(item)

    return JsonResponse({'data': data})


@require_http_methods(["GET"])
def stock_list(request):
    """获取股票列表"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT ticker
            FROM stock_history
            ORDER BY ticker
        """)
        stocks = [row[0] for row in cursor.fetchall()]

    return JsonResponse({'stocks': stocks})


@require_http_methods(["GET"])
def stock_detail(request, ticker):
    """获取股票详情（用于曲线选股的迷你图表）"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not end_date:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if not start_date:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT trade_date, close_price
            FROM stock_history
            WHERE ticker = %s
              AND trade_date BETWEEN %s AND %s
            ORDER BY trade_date
        """, [ticker, start_date, end_date])

        data = [{'date': str(row[0]), 'price': float(row[1])} for row in cursor.fetchall()]

    return JsonResponse({'data': data})


def index(request):
    """首页模板"""
    return render(request, 'index.html')
