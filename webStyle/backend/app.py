from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import subprocess
import json

app = Flask(__name__, static_folder='../frontend/dist')
CORS(app)

# API 路由示例
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'})


# AI 分析 API
@app.route('/api/ai-analyze', methods=['POST'])
def ai_analyze():
    try:
        data = request.get_json()
        requirements = data.get('requirements', '')

        if not requirements:
            return jsonify({'error': '需求内容不能为空'}), 400

        # 构建 prompt
        prompt = f"帮我分析一下需求: {requirements}, 告诉我哪些你不清楚，需要继续补充一下什么"

        # 执行 Docker 命令调用 AI Agent
        cmd = [
            'sudo', 'docker', 'run', '-i', '--rm',
            '-e', f'GLM_API_KEY={os.environ.get("GLM_API_KEY", "")}',
            'ai-agent', '-m', 'invoke', '-p', prompt
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2分钟超时
        )

        if result.returncode != 0:
            return jsonify({
                'error': 'AI 分析失败',
                'details': result.stderr
            }), 500

        return jsonify({
            'success': True,
            'analysis': result.stdout
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'AI 分析超时，请稍后重试'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
