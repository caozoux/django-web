# WebStyle

一个基于 React + Flask 的现代化 Web 应用，支持流程图编辑功能。

## 项目结构

```
webStyle/
├── backend/               # Flask 后端
│   ├── app.py            # Flask 应用入口
│   └── requirements.txt  # Python 依赖
├── frontend/             # React 前端
│   ├── src/
│   │   ├── components/
│   │   │   └── FlowDiagram.jsx  # React Flow 流程图组件
│   │   ├── App.jsx       # 主应用组件
│   │   ├── App.css       # 应用样式
│   │   ├── main.jsx      # 入口文件
│   │   └── index.css     # 全局样式
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 快速开始

### 后端 (Flask)

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python app.py
```

后端运行在 http://localhost:5000

### 前端 (React)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:3000

## 生产构建

```bash
# 构建前端
cd frontend
npm run build

# 启动 Flask 服务（会自动服务构建后的前端文件）
cd ../backend
python app.py
```

## 技术栈

### 前端
- React 18
- React Flow - 流程图库
- Vite - 构建工具

### 后端
- Flask - Python Web 框架
- Flask-CORS - 跨域支持

## 功能特性

- 流程图编辑器（基于 React Flow）
- 节点拖拽、连线
- 缩略图导航
- 背景网格
- 响应式布局
- 简洁现代的 UI 设计
