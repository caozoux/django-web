from django.db import models


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
