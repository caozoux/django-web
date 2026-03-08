#!/usr/bin/env python3
"""
创建管理员账号脚本
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User


def create_admin(username, email, password):
    """创建管理员账号"""
    app = create_app('development')

    with app.app_context():
        # 检查用户是否存在
        if User.query.filter_by(username=username).first():
            print(f'Error: Username "{username}" already exists.')
            return

        if User.query.filter_by(email=email).first():
            print(f'Error: Email "{email}" already exists.')
            return

        # 创建管理员
        admin = User(
            username=username,
            email=email,
            role='admin',
            is_active=True
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print(f'Admin user created successfully!')
        print(f'Username: {username}')
        print(f'Email: {email}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create admin user')
    parser.add_argument('--username', '-u', required=True, help='Admin username')
    parser.add_argument('--email', '-e', required=True, help='Admin email')
    parser.add_argument('--password', '-p', required=True, help='Admin password')

    args = parser.parse_args()

    create_admin(args.username, args.email, args.password)
