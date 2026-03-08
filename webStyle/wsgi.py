"""
WSGI入口文件 - 用于生产环境部署（Gunicorn/uWSGI）
"""
import os
from app import create_app

# 生产环境配置
config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
