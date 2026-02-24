from django.urls import path
from . import views

urlpatterns = [
    # API路由
    path('api/market/daily-summary', views.daily_market_summary, name='daily_summary'),
    path('api/stocks/screener', views.stock_screener, name='stock_screener'),
    path('api/stocks/<str:ticker>/kline', views.get_stock_kline, name='stock_kline'),
    path('api/stocks/list', views.stock_list, name='stock_list'),
    path('api/stocks/<str:ticker>/detail', views.stock_detail, name='stock_detail'),

    # 页面路由
    path('', views.index, name='index'),
]
