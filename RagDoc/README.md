# RAG 知识库浏览查询系统

基于 Flask + JavaScript 的语义搜索知识库管理系统。

## 功能特性

- 📄 **文档管理**: 添加、查看、删除文档
- 🔍 **语义搜索**: 基于向量相似度的智能搜索
- 🎯 **文本分块**: 自动将长文档分割成小块进行索引
- 📊 **实时统计**: 显示文档数量、索引状态等信息
- 🔄 **索引重建**: 支持清理已删除文档并重建索引
- 🎨 **现代界面**: 响应式设计，支持移动端

## 技术栈

### 后端
- Flask: Web 框架
- sentence-transformers: 文本向量化
- faiss-cpu: 向量相似度搜索
- Flask-CORS: 跨域支持

### 前端
- 原生 JavaScript
- CSS3 (Flexbox + Grid)
- Fetch API

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

### 3. 访问系统

在浏览器中打开 `http://localhost:5000`

## 使用说明

### 添加文档

1. 点击左侧的 "添加文档" 按钮
2. 输入文档标题和内容
3. 点击 "添加文档" 保存

系统会自动：
- 将文档分割成小块（每个块最多 500 字符）
- 使用 sentence-transformers 生成向量嵌入
- 将向量存储在 FAISS 索引中

### 语义搜索

1. 在搜索框中输入问题或关键词
2. 点击 "搜索" 按钮
3. 系统会返回最相关的文档片段

搜索基于语义相似度，而不是简单的关键词匹配，因此可以找到意思相近的内容。

### 查看文档

点击左侧文档列表中的任意文档，可以查看完整的文档内容和元数据。

### 删除文档

在文档详情页面点击 "删除" 按钮可以删除文档。

### 重建索引

如果删除了大量文档，点击左侧的 "重建索引" 按钮可以清理索引中的无效数据。

## 项目结构

```
RagDoc/
├── app.py              # Flask 后端应用
├── templates/
│   └── index.html      # 前端页面
├── data/               # 数据目录（自动创建）
│   ├── docs/          # 文档存储
│   ├── faiss.index    # FAISS 向量索引
│   └── metadata.json  # 文档元数据
├── requirements.txt   # Python 依赖
└── README.md         # 项目说明
```

## API 接口

### 健康检查
```
GET /api/health
```

### 列出所有文档
```
GET /api/documents
```

### 获取单个文档
```
GET /api/documents/<doc_id>
```

### 添加文档
```
POST /api/documents
Content-Type: application/json

{
  "title": "文档标题",
  "content": "文档内容"
}
```

### 删除文档
```
DELETE /api/documents/<doc_id>
```

### 语义搜索
```
POST /api/search
Content-Type: application/json

{
  "query": "搜索查询",
  "top_k": 5
}
```

### 重建索引
```
POST /api/rebuild
```

## 技术说明

### 文本分块

系统使用以下策略进行文本分块：
- 最大长度：500 字符
- 重叠：50 字符
- 分割点优先选择在句子边界（句号、问号、感叹号等）

### 向量化

使用 `paraphrase-multilingual-MiniLM-L12-v2` 模型，支持多语言文本的向量化。

### 相似度计算

使用 FAISS 的 L2 距离，转换为相似度分数：
```
similarity = 1 / (1 + distance)
```

## 注意事项

1. 首次运行时，模型下载可能需要一些时间（约 200MB）
2. 文档内容会存储在 `data/docs/` 目录下
3. 索引和元数据会自动保存，重启后数据不会丢失
4. 删除文档时，向量索引中的数据会被标记为删除，需要重建索引才能彻底清理

## 扩展建议

- [ ] 添加用户认证和权限管理
- [ ] 支持文件上传（PDF、Word 等）
- [ ] 添加文档分类和标签功能
- [ ] 支持多种相似度计算方法
- [ ] 添加搜索历史记录
- [ ] 支持导出搜索结果

## License

MIT
