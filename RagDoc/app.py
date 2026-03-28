"""
RAG 知识库浏览查询 Web 应用 - Flask 后端
"""

import os
# 设置离线模式，使用本地缓存的模型，不尝试联网
os.environ['HF_HUB_OFFLINE'] = '1'

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app)

# 配置
DATA_DIR = 'data'
DOCS_DIR = os.path.join(DATA_DIR, 'docs')
INDEX_FILE = os.path.join(DATA_DIR, 'faiss.index')
METADATA_FILE = os.path.join(DATA_DIR, 'metadata.json')

# 确保数据目录存在
os.makedirs(DOCS_DIR, exist_ok=True)

# 全局变量
encoder = None
index = None
metadata = {}


def init_encoder():
    """初始化文本编码器"""
    global encoder
    if encoder is None:
        print("Loading sentence transformer model...")
        encoder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    return encoder


def init_faiss():
    """初始化 FAISS 索引"""
    global index, metadata
    
    # 尝试加载现有索引
    if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
        print("Loading existing FAISS index...")
        index = faiss.read_index(INDEX_FILE)
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"Loaded {index.ntotal} documents from index")
    else:
        print("Creating new FAISS index...")
        # 创建基于余弦相似度的索引（L2 归一化）
        index = faiss.IndexFlatL2(384)  # MiniLM-L12 的维度是 384
        metadata = {}
        save_index()


def save_index():
    """保存索引和元数据到磁盘"""
    faiss.write_index(index, INDEX_FILE)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def get_document_id(content):
    """根据内容生成文档 ID"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]


def chunk_text(text, max_length=500, overlap=50):
    """将长文本分割成块"""
    if not text:
        return []
    
    chunks = []
    start = 0
    text = text.strip()
    
    while start < len(text):
        end = start + max_length
        
        # 尝试在句子边界处分割
        if end < len(text):
            for sep in ['\n\n', '\n', '。', '！', '？', '.', '!', '?']:
                last_sep = text.rfind(sep, start, end)
                if last_sep > start:
                    end = last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


@app.route('/')
def index_page():
    """主页"""
    return render_template('index.html')


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'document_count': index.ntotal if index else 0,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/categories', methods=['GET'])
def list_categories():
    """列出所有分类"""
    categories = set()
    for doc_id, doc_meta in metadata.items():
        if 'chunk_count' in doc_meta:  # 只统计文档
            cat = doc_meta.get('category', '')
            if cat:
                categories.add(cat)
    return jsonify({
        'categories': sorted(list(categories))
    })


@app.route('/api/import', methods=['POST'])
def import_directory():
    """从目录批量导入文档"""
    data = request.json

    if not data or 'directory' not in data:
        return jsonify({'error': 'Missing required field: directory'}), 400

    directory = os.path.expanduser(data['directory'])
    category = data.get('category', '').strip()

    if not os.path.isdir(directory):
        return jsonify({'error': f'Directory not found: {directory}'}), 400

    # 支持的文件扩展名
    supported_extensions = ['.md', '.txt', '.rst']

    imported = []
    errors = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if not any(file.endswith(ext) for ext in supported_extensions):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if not content.strip():
                    continue

                # 使用相对路径作为标题
                rel_path = os.path.relpath(file_path, directory)
                title = rel_path

                # 生成文档 ID
                doc_id = get_document_id(content)

                # 检查是否已存在
                if doc_id in metadata and 'chunk_count' in metadata[doc_id]:
                    imported.append({
                        'file': rel_path,
                        'status': 'skipped',
                        'reason': 'already exists'
                    })
                    continue

                # 文本分块
                chunks = chunk_text(content)
                if not chunks:
                    continue

                # 保存文件
                file_name = f"{doc_id}.txt"
                save_path = os.path.join(DOCS_DIR, file_name)
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # 编码文本块
                enc = init_encoder()
                embeddings = enc.encode(chunks, convert_to_numpy=True)
                faiss.normalize_L2(embeddings)

                # 添加到索引
                chunk_ids = []
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{i}"
                    chunk_ids.append(chunk_id)
                    metadata[chunk_id] = {
                        'doc_id': doc_id,
                        'chunk_index': i,
                        'content': chunk,
                        'file_path': file_name
                    }

                index.add(embeddings)

                # 保存文档元数据
                now = datetime.now().isoformat()
                metadata[doc_id] = {
                    'title': title,
                    'category': category,
                    'source_path': file_path,
                    'file_path': file_name,
                    'chunk_count': len(chunks),
                    'chunks': chunk_ids,
                    'created_at': now,
                    'updated_at': now
                }

                imported.append({
                    'file': rel_path,
                    'status': 'success',
                    'doc_id': doc_id,
                    'chunk_count': len(chunks)
                })

            except Exception as e:
                errors.append({
                    'file': os.path.relpath(file_path, directory),
                    'error': str(e)
                })

    save_index()

    return jsonify({
        'success': True,
        'imported': imported,
        'errors': errors,
        'total_imported': len([i for i in imported if i['status'] == 'success']),
        'total_skipped': len([i for i in imported if i['status'] == 'skipped']),
        'total_errors': len(errors)
    })


@app.route('/api/documents', methods=['GET'])
def list_documents():
    """列出所有文档"""
    docs = []
    category_filter = request.args.get('category', '')

    for doc_id, doc_meta in metadata.items():
        # 跳过 chunk 元数据
        if 'chunk_count' not in doc_meta:
            continue

        # 分类过滤
        if category_filter and doc_meta.get('category', '') != category_filter:
            continue

        file_path = doc_meta.get('file_path', '')
        docs.append({
            'id': doc_id,
            'title': doc_meta.get('title', doc_id),
            'category': doc_meta.get('category', ''),
            'file_path': file_path,
            'chunk_count': doc_meta.get('chunk_count', 0),
            'created_at': doc_meta.get('created_at', ''),
            'updated_at': doc_meta.get('updated_at', '')
        })
    
    return jsonify({
        'documents': docs,
        'total': len(docs)
    })


@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """获取单个文档详情"""
    if doc_id not in metadata:
        return jsonify({'error': 'Document not found'}), 404
    
    doc_meta = metadata[doc_id]
    file_path = os.path.join(DOCS_DIR, doc_meta['file_path'])
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    return jsonify({
        'id': doc_id,
        'title': doc_meta.get('title', doc_id),
        'category': doc_meta.get('category', ''),
        'content': content,
        'file_path': doc_meta.get('file_path', ''),
        'chunk_count': doc_meta.get('chunk_count', 0),
        'chunks': doc_meta.get('chunks', []),
        'created_at': doc_meta.get('created_at', ''),
        'updated_at': doc_meta.get('updated_at', '')
    })


@app.route('/api/documents', methods=['POST'])
def add_document():
    """添加新文档"""
    data = request.json

    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Missing required fields: title, content'}), 400

    title = data['title'].strip()
    content = data['content'].strip()
    category = data.get('category', '').strip()

    if not title or not content:
        return jsonify({'error': 'Title and content cannot be empty'}), 400
    
    # 生成文档 ID
    doc_id = get_document_id(content)
    
    # 文本分块
    chunks = chunk_text(content)
    
    if not chunks:
        return jsonify({'error': 'No valid chunks generated from content'}), 400
    
    # 保存文件
    file_name = f"{doc_id}.txt"
    file_path = os.path.join(DOCS_DIR, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 编码文本块
    encoder = init_encoder()
    embeddings = encoder.encode(chunks, convert_to_numpy=True)
    
    # 归一化（用于余弦相似度）
    faiss.normalize_L2(embeddings)
    
    # 添加到索引
    chunk_ids = []
    start_idx = index.ntotal
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{i}"
        chunk_ids.append(chunk_id)
        metadata[chunk_id] = {
            'doc_id': doc_id,
            'chunk_index': i,
            'content': chunk,
            'file_path': file_name
        }
    
    index.add(embeddings)
    
    # 保存文档元数据
    now = datetime.now().isoformat()
    metadata[doc_id] = {
        'title': title,
        'category': category,
        'file_path': file_name,
        'chunk_count': len(chunks),
        'chunks': chunk_ids,
        'created_at': now,
        'updated_at': now
    }
    
    save_index()
    
    return jsonify({
        'success': True,
        'document_id': doc_id,
        'title': title,
        'chunk_count': len(chunks)
    }), 201


@app.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """删除文档"""
    if doc_id not in metadata:
        return jsonify({'error': 'Document not found'}), 404
    
    doc_meta = metadata[doc_id]
    chunk_ids = doc_meta.get('chunks', [])
    
    # 删除文件
    file_path = os.path.join(DOCS_DIR, doc_meta['file_path'])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除元数据（注意：实际删除 FAISS 索引中的向量需要重建索引）
    # 这里简化处理：只删除元数据标记为已删除
    for chunk_id in chunk_ids:
        if chunk_id in metadata:
            metadata[chunk_id]['deleted'] = True
    
    del metadata[doc_id]
    save_index()
    
    return jsonify({'success': True})


@app.route('/api/search', methods=['POST'])
def search():
    """语义搜索"""
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing required field: query'}), 400
    
    query = data['query'].strip()
    top_k = min(int(data.get('top_k', 5)), 20)
    
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    if index.ntotal == 0:
        return jsonify({
            'query': query,
            'results': [],
            'total': 0
        })
    
    # 编码查询
    encoder = init_encoder()
    query_embedding = encoder.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    
    # 搜索
    distances, indices = index.search(query_embedding, top_k)
    
    # 收集结果
    results = []
    for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
        if idx < 0 or idx >= index.ntotal:
            continue
        
        # 找到对应的 chunk
        chunk_id = None
        for k, v in metadata.items():
            if v.get('chunk_index') == idx and 'doc_id' in v and not v.get('deleted'):
                chunk_id = k
                break
        
        if not chunk_id:
            continue
        
        chunk_meta = metadata[chunk_id]
        doc_meta = metadata.get(chunk_meta['doc_id'], {})
        
        # 计算相似度分数（L2 距离转相似度）
        similarity = float(1 / (1 + distance))
        
        results.append({
            'rank': i + 1,
            'score': similarity,
            'chunk_id': chunk_id,
            'doc_id': chunk_meta['doc_id'],
            'title': doc_meta.get('title', chunk_meta['doc_id']),
            'category': doc_meta.get('category', ''),
            'content': chunk_meta['content'],
            'chunk_index': chunk_meta['chunk_index']
        })
    
    return jsonify({
        'query': query,
        'results': results,
        'total': len(results)
    })


@app.route('/api/rebuild', methods=['POST'])
def rebuild_index():
    """重建索引（清理已删除的文档）"""
    global index, metadata
    
    # 收集所有未删除的文档和 chunk
    valid_docs = {}
    valid_chunks = {}
    
    for doc_id, doc_meta in metadata.items():
        if 'chunk_count' not in doc_meta:  # 这是 chunk，跳过
            continue
        
        file_path = os.path.join(DOCS_DIR, doc_meta['file_path'])
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunk_text(content)
        if not chunks:
            continue
        
        encoder = init_encoder()
        embeddings = encoder.encode(chunks, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)
        
        chunk_ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            valid_chunks[chunk_id] = {
                'doc_id': doc_id,
                'chunk_index': i,
                'content': chunk,
                'file_path': doc_meta['file_path']
            }
        
        valid_docs[doc_id] = {
            'title': doc_meta['title'],
            'file_path': doc_meta['file_path'],
            'chunk_count': len(chunks),
            'chunks': chunk_ids,
            'created_at': doc_meta['created_at'],
            'updated_at': datetime.now().isoformat()
        }
    
    # 合并所有元数据
    metadata = {**valid_chunks, **valid_docs}
    
    # 重建索引
    new_index = faiss.IndexFlatL2(384)
    if len(valid_chunks) > 0:
        embeddings = np.array([metadata[cid]['content'] for cid in valid_chunks.keys()])
        encoder = init_encoder()
        embeddings = encoder.encode(embeddings, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)
        new_index.add(embeddings)
    
    index = new_index
    save_index()
    
    return jsonify({
        'success': True,
        'document_count': len(valid_docs),
        'chunk_count': len(valid_chunks)
    })


if __name__ == '__main__':
    # 初始化
    init_encoder()
    init_faiss()
    
    # 启动服务器
    app.run(host='0.0.0.0', port=5000, debug=True)
