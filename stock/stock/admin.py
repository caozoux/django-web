from django.contrib import admin
from .models import StockHistory, StockTrendPattern


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
    list_filter = ['trade_date', 'ticker']
    search_fields = ['ticker']
    date_hierarchy = 'trade_date'


@admin.register(StockTrendPattern)
class StockTrendPatternAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'pattern_type', 'days', 'pattern_date', 'created_at']
    list_filter = ['days', 'pattern_type', 'pattern_date']
    search_fields = ['ticker', 'pattern_type']
    date_hierarchy = 'pattern_date'

