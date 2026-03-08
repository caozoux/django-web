#!/usr/bin/env python3
"""
数据库初始化脚本（使用SQLite）
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Category, Website, Tag, Favorite, ViewHistory


def init_db():
    """初始化数据库"""
    # 使用开发配置（SQLite）
    app = create_app('development')

    with app.app_context():
        # 创建所有表
        print('Creating database tables...')
        db.create_all()
        print('Database tables created successfully.')

        # 检查是否有数据
        if User.query.count() == 0:
            print('Creating admin user...')
            admin = User(
                username='admin',
                email='admin@webstyle.com',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin / admin123')

        print('Database initialization completed.')


if __name__ == '__main__':
    init_db()
