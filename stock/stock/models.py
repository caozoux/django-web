import json
import os
from datetime import datetime
from django.db import models
from django.core.cache import cache


WAVEDATA_DIR = '/data/stock/wavedata/'


def get_wavedata_path(date_str=None):
    """
    获取指定日期的波浪数据文件路径

    Args:
        date_str: 日期字符串，格式为 YYYY-MM-DD，默认为当天

    Returns:
        JSON文件路径，如果文件不存在则返回None
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    file_path = os.path.join(WAVEDATA_DIR, f'{date_str}.json')

    if os.path.exists(file_path):
        return file_path
    return None


def load_wavedata(date_str=None):
    """
    从JSON文件加载波浪数据

    Args:
        date_str: 日期字符串，格式为 YYYY-MM-DD，默认为当天

    Returns:
        波浪数据字典，键为形态类型（如"111"），值为股票代码列表
        如果文件不存在则返回空字典
    """
    file_path = get_wavedata_path(date_str)

    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading wavedata from {file_path}: {e}")
    return {}


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
        unique_together = (('ticker', 'trade_date'),)

    def __str__(self):
        return f"{self.ticker} - {self.trade_date}"
