from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='../frontend/dist')
CORS(app)

# API 路由示例
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'})


# 前端路由 - 生产环境时服务 React 构建文件
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    dist_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(dist_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
