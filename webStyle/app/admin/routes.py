"""
管理后台路由
"""
from flask import render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.admin import admin_bp
from app.services.website_service import WebsiteService
from app.services.category_service import CategoryService
from app.services.stats_service import StatsService
from app.services.user_service import UserService
from app.models.user import User


def admin_required_context():
    """检查管理员权限的上下文"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    user = User.query.get(user_id)
    if not user or not user.is_admin():
        return None
    return user


@admin_bp.route('/')
@jwt_required()
def dashboard():
    """管理后台首页"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    # 获取统计数据
    stats = StatsService.get_overview_stats()

    # 获取待审核网站
    pending_websites = WebsiteService.get_websites_paginated(
        status='pending',
        per_page=10
    )

    # 获取最新网站
    recent_websites = WebsiteService.get_recent_websites(5)

    # 获取分类分布
    category_distribution = StatsService.get_category_distribution()

    return render_template('admin/dashboard.html',
                           user=user,
                           stats=stats,
                           pending_websites=pending_websites.items,
                           recent_websites=recent_websites,
                           category_distribution=category_distribution)


@admin_bp.route('/websites')
@jwt_required()
def websites():
    """网站管理列表"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword')

    pagination = WebsiteService.get_websites_paginated(
        page=page,
        per_page=per_page,
        status=status,
        category_id=category_id,
        keyword=keyword
    )

    categories = CategoryService.get_active_categories()

    return render_template('admin/websites/list.html',
                           user=user,
                           websites=pagination.items,
                           pagination=pagination.to_dict(),
                           categories=categories,
                           filters={'status': status, 'category_id': category_id, 'keyword': keyword})


@admin_bp.route('/websites/create', methods=['GET', 'POST'])
@jwt_required()
def create_website():
    """创建网站"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'url': request.form.get('url'),
            'description': request.form.get('description'),
            'category_id': request.form.get('category_id', type=int),
            'industry': request.form.get('industry'),
            'color_scheme': request.form.get('color_scheme'),
            'layout_type': request.form.get('layout_type'),
            'status': request.form.get('status', 'active'),
            'created_by': user.id
        }

        if not data['name'] or not data['url'] or not data['category_id']:
            flash('Please fill in required fields', 'error')
        else:
            website = WebsiteService.create_website(data)
            flash('Website created successfully', 'success')
            return redirect(url_for('admin.edit_website', id=website.id))

    categories = CategoryService.get_active_categories()
    return render_template('admin/websites/create.html',
                           user=user,
                           categories=categories)


@admin_bp.route('/websites/<int:id>/edit', methods=['GET', 'POST'])
@jwt_required()
def edit_website(id):
    """编辑网站"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    website = WebsiteService.get_by_id(id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('admin.websites'))

    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'url': request.form.get('url'),
            'description': request.form.get('description'),
            'category_id': request.form.get('category_id', type=int),
            'industry': request.form.get('industry'),
            'color_scheme': request.form.get('color_scheme'),
            'layout_type': request.form.get('layout_type'),
            'status': request.form.get('status')
        }

        WebsiteService.update_website(id, data)
        flash('Website updated successfully', 'success')
        return redirect(url_for('admin.edit_website', id=id))

    categories = CategoryService.get_active_categories()
    return render_template('admin/websites/edit.html',
                           user=user,
                           website=website,
                           categories=categories)


@admin_bp.route('/websites/<int:id>/delete', methods=['POST'])
@jwt_required()
def delete_website(id):
    """删除网站"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    success = WebsiteService.delete_website(id)
    if success:
        flash('Website deleted', 'success')
    else:
        flash('Failed to delete website', 'error')

    return redirect(url_for('admin.websites'))


@admin_bp.route('/categories')
@jwt_required()
def categories():
    """分类管理列表"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    all_categories = CategoryService.get_all_categories()
    category_tree = CategoryService.get_category_tree()

    return render_template('admin/categories/list.html',
                           user=user,
                           categories=all_categories,
                           category_tree=category_tree)


@admin_bp.route('/categories/create', methods=['GET', 'POST'])
@jwt_required()
def create_category():
    """创建分类"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'slug': request.form.get('slug'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon'),
            'parent_id': request.form.get('parent_id', type=int),
            'sort_order': request.form.get('sort_order', 0, type=int),
            'is_active': request.form.get('is_active') == 'on'
        }

        if not data['name'] or not data['slug']:
            flash('Please fill in required fields', 'error')
        elif CategoryService.get_by_slug(data['slug']):
            flash('Slug already exists', 'error')
        else:
            CategoryService.create_category(data)
            flash('Category created successfully', 'success')
            return redirect(url_for('admin.categories'))

    parent_categories = CategoryService.get_root_categories()
    return render_template('admin/categories/create.html',
                           user=user,
                           parent_categories=parent_categories)


@admin_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@jwt_required()
def edit_category(id):
    """编辑分类"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    category = CategoryService.get_by_id(id)
    if not category:
        flash('Category not found', 'error')
        return redirect(url_for('admin.categories'))

    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'slug': request.form.get('slug'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon'),
            'parent_id': request.form.get('parent_id', type=int),
            'sort_order': request.form.get('sort_order', 0, type=int),
            'is_active': request.form.get('is_active') == 'on'
        }

        CategoryService.update_category(id, data)
        flash('Category updated successfully', 'success')
        return redirect(url_for('admin.edit_category', id=id))

    parent_categories = CategoryService.get_root_categories()
    return render_template('admin/categories/edit.html',
                           user=user,
                           category=category,
                           parent_categories=parent_categories)


@admin_bp.route('/categories/<int:id>/delete', methods=['POST'])
@jwt_required()
def delete_category(id):
    """删除分类"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    success = CategoryService.delete_category(id)
    if success:
        flash('Category deleted', 'success')
    else:
        flash('Cannot delete category (has children or websites)', 'error')

    return redirect(url_for('admin.categories'))


@admin_bp.route('/users')
@jwt_required()
def users():
    """用户管理列表"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/users/list.html',
                           user=user,
                           users=pagination.items,
                           pagination={
                               'page': page,
                               'pages': pagination.pages,
                               'total': pagination.total
                           })


@admin_bp.route('/stats')
@jwt_required()
def stats():
    """统计分析页面"""
    user = admin_required_context()
    if not user:
        return redirect(url_for('auth.login'))

    overview = StatsService.get_overview_stats()
    category_distribution = StatsService.get_category_distribution()
    industry_distribution = StatsService.get_industry_distribution()
    color_distribution = StatsService.get_color_scheme_distribution()
    layout_distribution = StatsService.get_layout_distribution()
    growth = StatsService.get_website_growth_trend(30)

    return render_template('admin/stats/overview.html',
                           user=user,
                           overview=overview,
                           category_distribution=category_distribution,
                           industry_distribution=industry_distribution,
                           color_distribution=color_distribution,
                           layout_distribution=layout_distribution,
                           growth=growth)
