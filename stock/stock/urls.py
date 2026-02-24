from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # 涨跌形态相关URL
    path('api/generate-patterns/<int:days>/', views.generate_trend_patterns, name='generate_patterns'),
    path('api/patterns/<int:days>/<str:pattern_type>/', views.get_patterns_by_type, name='patterns_by_type'),
    path('api/pattern-types/<int:days>/', views.get_all_pattern_types, name='pattern_types'),
    path('visualization/', views.trend_pattern_visualization, name='trend_pattern_visualization'),
    path('api/trend-pattern-data/', views.trend_pattern_data, name='trend_pattern_data'),

    # 波浪数据相关URL - 从JSON文件读取
    path('api/pattern-tickers/<str:pattern_type>/', views.get_pattern_tickers, name='pattern_tickers'),
    path('api/available-dates/', views.get_available_dates, name='available_dates'),

    # 形态图表相关URL
    path('chart/<str:pattern_type>/', views.pattern_chart_page, name='pattern_chart_page'),
    path('api/pattern-chart-data/<str:pattern_type>/', views.get_pattern_chart_data, name='pattern_chart_data'),
]
