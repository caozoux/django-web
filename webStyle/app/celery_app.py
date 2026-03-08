"""
Celery应用配置
"""
from celery import Celery

celery = Celery(
    'webstyle',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# 配置
celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    task_soft_time_limit=25 * 60,  # 25分钟软超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 自动发现任务
celery.autodiscover_tasks(['app.tasks'])
