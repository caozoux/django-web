from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebStyle</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        html, body {
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        body {
            display: flex;
            flex-direction: column;
            background: #fafafa;
        }

        /* 顶部导航栏 */
        .navbar {
            display: flex;
            align-items: center;
            background: #fff;
            padding: 0 32px;
            height: 64px;
            border-bottom: 1px solid #eee;
        }
        .navbar-brand {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1a1a1a;
            letter-spacing: -0.5px;
        }
        .navbar-menu {
            display: flex;
            align-items: center;
            margin-left: 48px;
            gap: 8px;
        }
        .navbar-item {
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 6px;
            font-size: 0.9rem;
            color: #666;
            transition: all 0.2s ease;
        }
        .navbar-item:hover {
            color: #1a1a1a;
            background: #f5f5f5;
        }
        .navbar-item.active {
            color: #0066ff;
            background: rgba(0, 102, 255, 0.08);
        }
        .navbar-spacer {
            flex: 1;
        }
        .navbar-action {
            padding: 8px 20px;
            background: #1a1a1a;
            color: #fff;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .navbar-action:hover {
            background: #333;
            transform: translateY(-1px);
        }

        /* 主内容区域 */
        .main {
            flex: 1;
            display: flex;
            padding: 32px;
            overflow: auto;
        }
        .content-card {
            flex: 1;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 48px;
        }
        .content-empty {
            text-align: center;
        }
        .content-empty-icon {
            width: 64px;
            height: 64px;
            margin: 0 auto 24px;
            background: #f5f5f5;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .content-empty-icon svg {
            width: 28px;
            height: 28px;
            stroke: #bbb;
        }
        .content-empty h3 {
            font-size: 1.125rem;
            font-weight: 500;
            color: #1a1a1a;
            margin-bottom: 8px;
        }
        .content-empty p {
            font-size: 0.9rem;
            color: #999;
        }

        /* 底部状态栏 */
        .footer {
            display: flex;
            align-items: center;
            padding: 0 32px;
            height: 40px;
            font-size: 0.8rem;
            color: #999;
        }
        .footer-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .footer-dot {
            width: 6px;
            height: 6px;
            background: #22c55e;
            border-radius: 50%;
        }
        .footer-spacer {
            flex: 1;
        }
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="navbar">
        <div class="navbar-brand">WebStyle</div>
        <div class="navbar-menu">
            <div class="navbar-item active">功能1</div>
            <div class="navbar-item">功能2</div>
            <div class="navbar-item">功能3</div>
        </div>
        <div class="navbar-spacer"></div>
        <div class="navbar-action">设置</div>
    </nav>

    <!-- 主内容区域 -->
    <main class="main">
        <div class="content-card">
            <div class="content-empty">
                <div class="content-empty-icon">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"/>
                    </svg>
                </div>
                <h3>显示区域</h3>
                <p>这里放置主要内容</p>
            </div>
        </div>
    </main>

    <!-- 底部状态栏 -->
    <footer class="footer">
        <div class="footer-item">
            <span class="footer-dot"></span>
            <span>就绪</span>
        </div>
        <div class="footer-spacer"></div>
        <span>v1.0.0</span>
    </footer>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
