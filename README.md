# AI RAG 知识库检索系统

基于 LlamaIndex + ChromaDB 的智能知识库检索 API 服务。

## 功能特性

- 🔍 **智能检索**: 基于语义相似度的文档检索
- 🤖 **AI 问答**: 结合本地 LLM 的智能问答
- 📊 **流式响应**: 支持实时流式输出
- 🎯 **相似度过滤**: 可配置的相似度阈值
- 🔧 **灵活配置**: 支持本地和在线模型

## 项目结构

```
bigmodel/
├── api/
│   └── knowledge_api.py    # FastAPI 知识库检索服务
├── test/
│   └── chroma/            # ChromaDB 数据存储
├── requirements.txt       # Python 依赖
└── README.md
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

在 `api/knowledge_api.py` 中修改以下配置：

```python
# ChromaDB 数据路径
CHROMADB_PATH = str(project_root / "test" / "chroma")

# 集合名称
COLLECTION_NAME = 'laodongfa'

# 嵌入模型路径（本地或在线）
MODEL_PATH = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

# 本地 LLM 路径（可选）
LLM_PATH = 'path/to/your/local/llm'
```

## 运行服务

```bash
cd api
python knowledge_api.py
```

服务将在 `http://localhost:8000` 启动。

## API 接口

### 健康检查
- `GET /` - 基础健康检查
- `GET /health` - 详细状态信息

### 知识库检索
- `POST /retrieve` - 检索相关文档
- `POST /answer` - 基于知识库回答问题
- `POST /answer_stream` - 流式问答

### 集合管理
- `GET /collections` - 列出所有集合

## 使用示例

```python
import requests

# 检索文档
response = requests.post('http://localhost:8000/retrieve', json={
    'query': '劳动合同期限',
    'top_k': 5
})

# 问答
response = requests.post('http://localhost:8000/answer', json={
    'query': '试用期最长多久？'
})
```

## 技术栈

- **FastAPI**: Web 框架
- **LlamaIndex**: RAG 框架
- **ChromaDB**: 向量数据库
- **HuggingFace**: 模型加载
- **PyTorch**: 深度学习框架

## 许可证

MIT License