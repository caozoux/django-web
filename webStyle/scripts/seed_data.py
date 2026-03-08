#!/usr/bin/env python3
"""
填充测试数据脚本
"""
import os
import sys
import random
import re

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Category, Website, Tag


def slugify(text):
    """简单的 slug 生成函数"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text)
    text = text.strip('-')
    return text


# 初始分类数据
CATEGORIES = [
    {'name': '扁平化设计', 'slug': 'flat-design', 'icon': 'square', 'description': '简洁、干净的扁平化设计风格'},
    {'name': '卡片式设计', 'slug': 'card-design', 'icon': 'grid', 'description': '使用卡片展示内容的布局方式'},
    {'name': '渐变色设计', 'slug': 'gradient-design', 'icon': 'palette', 'description': '使用渐变色彩的视觉效果'},
    {'name': '暗色模式', 'slug': 'dark-mode', 'icon': 'moon', 'description': '深色主题的界面设计'},
    {'name': '玻璃拟态', 'slug': 'glassmorphism', 'icon': 'diamond', 'description': '半透明磨砂玻璃效果'},
    {'name': '新拟态', 'slug': 'neumorphism', 'icon': 'circle', 'description': '柔和的立体浮雕效果'},
    {'name': '极简主义', 'slug': 'minimalism', 'icon': 'minus', 'description': '简约、留白的设计风格'},
    {'name': '3D立体风格', 'slug': '3d-style', 'icon': 'box', 'description': '三维立体的视觉效果'},
    {'name': '复古风格', 'slug': 'retro-style', 'icon': 'clock-history', 'description': '怀旧复古的设计元素'},
    {'name': '科技感风格', 'slug': 'tech-style', 'icon': 'cpu', 'description': '未来科技感的界面设计'},
]

# 示例网站数据
WEBSITES = [
    {'name': 'Apple', 'url': 'https://www.apple.com', 'category': '极简主义'},
    {'name': 'Stripe', 'url': 'https://stripe.com', 'category': '渐变色设计'},
    {'name': 'Linear', 'url': 'https://linear.app', 'category': '暗色模式'},
    {'name': 'Notion', 'url': 'https://www.notion.so', 'category': '极简主义'},
    {'name': 'Figma', 'url': 'https://www.figma.com', 'category': '扁平化设计'},
    {'name': 'Dribbble', 'url': 'https://dribbble.com', 'category': '卡片式设计'},
    {'name': 'Behance', 'url': 'https://www.behance.net', 'category': '卡片式设计'},
    {'name': 'GitHub', 'url': 'https://github.com', 'category': '扁平化设计'},
    {'name': 'Vercel', 'url': 'https://vercel.com', 'category': '暗色模式'},
    {'name': 'Spotify', 'url': 'https://www.spotify.com', 'category': '暗色模式'},
    {'name': 'Airbnb', 'url': 'https://www.airbnb.com', 'category': '卡片式设计'},
    {'name': 'Netflix', 'url': 'https://www.netflix.com', 'category': '暗色模式'},
]

# 标签数据
TAGS = ['responsive', 'animation', 'interactive', 'clean', 'modern', 'creative', 'enterprise', 'ecommerce', 'social', 'tools']


def run_seed():
    """填充数据"""
    app = create_app('development')

    with app.app_context():
        # 创建分类
        print('Creating categories...')
        category_map = {}
        for cat_data in CATEGORIES:
            existing = Category.query.filter_by(slug=cat_data['slug']).first()
            if not existing:
                category = Category(**cat_data, is_active=True)
                db.session.add(category)
                category_map[cat_data['name']] = category
            else:
                category_map[cat_data['name']] = existing
        db.session.commit()
        print(f'Created {len(category_map)} categories.')

        # 创建标签
        print('Creating tags...')
        tag_map = {}
        for tag_name in TAGS:
            existing = Tag.query.filter_by(name=tag_name).first()
            if not existing:
                tag = Tag(name=tag_name, slug=slugify(tag_name))
                db.session.add(tag)
                tag_map[tag_name] = tag
            else:
                tag_map[tag_name] = existing
        db.session.commit()
        print(f'Created {len(tag_map)} tags.')

        # 创建网站
        print('Creating websites...')
        admin = User.query.filter_by(username='admin').first()
        for web_data in WEBSITES:
            existing = Website.query.filter_by(url=web_data['url']).first()
            if not existing:
                category = category_map.get(web_data['category'])
                if category:
                    website = Website(
                        name=web_data['name'],
                        url=web_data['url'],
                        description=f'{web_data["name"]} official website',
                        category_id=category.id,
                        status='active',
                        views=random.randint(100, 10000),
                        likes=random.randint(10, 1000),
                        favorites=random.randint(5, 500),
                        created_by=admin.id if admin else None
                    )
                    # 添加随机标签
                    for _ in range(random.randint(2, 4)):
                        tag_name = random.choice(TAGS)
                        if tag_name in tag_map:
                            website.tags.append(tag_map[tag_name])

                    db.session.add(website)
        db.session.commit()
        print(f'Created {len(WEBSITES)} websites.')

        print('Data seeding completed.')
        print('\nSummary:')
        print(f'  Categories: {Category.query.count()}')
        print(f'  Tags: {Tag.query.count()}')
        print(f'  Websites: {Website.query.count()}')
        print(f'  Admin: admin / admin123')


if __name__ == '__main__':
    run_seed()
