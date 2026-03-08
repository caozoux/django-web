"""
认证路由
"""
from flask import render_template, redirect, url_for, flash, request
from flask_jwt_extended import create_access_token
from app.auth import auth_bp
from app.services.user_service import UserService
from app.utils.validators import validate_email


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter username and password', 'error')
            return render_template('auth/login.html')

        user = UserService.authenticate(username, password)

        if not user:
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Account is deactivated', 'error')
            return render_template('auth/login.html')

        # 创建token
        access_token = create_access_token(identity=user.id)

        # 设置cookie或重定向
        response = redirect(url_for('web.index'))
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')

        return response

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # 验证
        if not username or not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('auth/register.html')

        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('auth/register.html')

        # 检查用户名是否存在
        if UserService.get_by_username(username):
            flash('Username already exists', 'error')
            return render_template('auth/register.html')

        # 检查邮箱是否存在
        if UserService.get_by_email(email):
            flash('Email already exists', 'error')
            return render_template('auth/register.html')

        # 创建用户
        user = UserService.create_user({
            'username': username,
            'email': email,
            'password': password
        })

        flash('Registration successful, please login', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """登出"""
    response = redirect(url_for('web.index'))
    response.delete_cookie('access_token')
    return response


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码页面"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash('Please enter your email', 'error')
            return render_template('auth/forgot_password.html')

        user = UserService.get_by_email(email)

        # 不透露用户是否存在
        flash('If the email exists, a password reset link has been sent', 'info')
        return render_template('auth/forgot_password.html')

    return render_template('auth/forgot_password.html')
