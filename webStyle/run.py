#!/usr/bin/env python3
"""
开发服务器启动脚本
"""
import os
from app import create_app

# 从环境变量获取配置名称，默认为development
config_name = os.getenv('FLASK_ENV', 'development')

app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
