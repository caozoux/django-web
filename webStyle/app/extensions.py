"""
Flask扩展初始化
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from celery import Celery
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 数据库
db = SQLAlchemy()

# 数据库迁移
migrate = Migrate()

# 缓存
cache = Cache()

# JWT认证
jwt = JWTManager()

# Celery
celery = Celery()

# 限流器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['200/hour']
)
