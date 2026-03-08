# Gunicorn 配置文件

# 绑定地址
bind = "0.0.0.0:5000"

# 工作进程数 (建议: (2 x CPU核心数) + 1)
workers = 4

# 每个工作进程的线程数
threads = 2

# 工作模式
worker_class = "gthread"

# 超时时间
timeout = 60

# 最大请求数（之后重启worker）
max_requests = 1000
max_requests_jitter = 50

# 守护进程
daemon = False

# PID文件
pidfile = "/tmp/gunicorn.pid"

# 日志
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 保持连接
keepalive = 5

# 预加载应用
preload_app = True

# 优雅重启超时
graceful_timeout = 30
