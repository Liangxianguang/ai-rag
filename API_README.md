# 知识库检索 + 智能回答系统

这是一个基于 Vue.js + FastAPI + LlamaIndex + ChromaDB 的知识库检索和智能回答系统。

## 系统架构

```
前端 (Vue.js) → 知识库检索 API (FastAPI) → ChromaDB → LLM 回答
```

## 功能特点

- ✅ **知识库检索优先**: AI 回答严格基于检索到的知识库内容
- ✅ **信息来源标注**: 每个回答都会显示信息来源
- ✅ **多轮对话支持**: 保持对话上下文
- ✅ **本地部署**: 支持本地 Ollama 模型和远程 API
- ✅ **实时流式回答**: 支持打字机效果
- ✅ **知识库可视化**: 显示检索状态和结果

## 快速开始

### 1. 安装依赖

#### 前端依赖
```bash
npm install
```

#### 后端依赖
```bash
pip install -r api/requirements.txt
```

### 2. 准备知识库

确保您已经按照 `test/save_vector.py` 脚本建立了 ChromaDB 知识库：

```bash
cd test
python save_vector.py
```

### 3. 启动服务

#### 启动知识库 API 服务
```bash
python api/start_api.py
```
或者直接运行：
```bash
python api/knowledge_api.py
```

API 服务将在 http://localhost:8000 启动。

#### 启动前端服务
```bash
npm run dev
```

前端服务将在 http://localhost:3000 启动。

### 4. 配置 LLM

在前端设置中选择：
- **本地模型**: 使用 Ollama（需要先安装和启动 Ollama）
- **远程模型**: 使用在线 API 服务

## API 接口

### 知识库检索 API

**POST** `/api/knowledge/retrieve`

请求体：
```json
{
  "query": "用户问题",
  "top_k": 5,
  "max_length": 3000
}
```

响应：
```json
{
  "documents": [
    {
      "content": "文档内容",
      "source": "文档来源",
      "title": "文档标题",
      "score": 0.95
    }
  ],
  "total": 5,
  "query": "用户问题"
}
```

### 健康检查

**GET** `/api/knowledge/health`

## 配置说明

### 前端配置

在前端界面的设置中可以配置：

- **知识库检索开关**: 是否启用知识库检索
- **知识库 API 地址**: 默认 `/api/knowledge`
- **最大上下文长度**: 控制检索内容的总长度
- **检索文档数量**: 控制返回的文档数量
- **LLM 配置**: 模型选择、参数调整等

### 后端配置

修改 `api/knowledge_api.py` 中的配置：

```python
# ChromaDB 路径
CHROMADB_PATH = "path/to/your/chromadb"

# 集合名称
COLLECTION_NAME = 'your_collection_name'

# 嵌入模型路径
MODEL_PATH = "path/to/embedding/model"
```

## 工作流程

1. **用户提问** → 前端接收用户输入
2. **知识库检索** → 调用 FastAPI 检索相关文档
3. **构建提示词** → 将检索结果作为 context 传递给 LLM
4. **生成回答** → LLM 基于 context 生成回答
5. **显示结果** → 前端展示回答和信息来源

## 技术栈

### 前端
- **Vue.js 3**: 响应式框架
- **Element Plus**: UI 组件库
- **Vite**: 构建工具
- **Axios**: HTTP 客户端

### 后端
- **FastAPI**: API 框架
- **LlamaIndex**: RAG 框架
- **ChromaDB**: 向量数据库
- **HuggingFace**: 嵌入模型

### AI/ML
- **Sentence Transformers**: 文本嵌入
- **Ollama**: 本地 LLM 服务
- **PyTorch**: 深度学习框架

## 故障排除

### 常见问题

1. **知识库检索失败**
   - 检查 ChromaDB 路径是否正确
   - 确认集合名称是否存在
   - 检查嵌入模型是否加载成功

2. **API 服务启动失败**
   - 检查端口 8000 是否被占用
   - 确认依赖是否完整安装
   - 查看控制台错误信息

3. **前端连接失败**
   - 检查 Vite 代理配置
   - 确认 API 服务是否正常运行
   - 查看浏览器网络面板

### 日志查看

- **API 服务日志**: 控制台输出
- **前端日志**: 浏览器开发者工具
- **ChromaDB 日志**: ChromaDB 数据目录

## 扩展功能

### 添加新的知识库

1. 准备数据文件（JSON 格式）
2. 修改 `test/save_vector.py` 脚本
3. 运行脚本建立向量索引
4. 更新 API 配置

### 集成其他 LLM

修改前端的 LLM 调用逻辑，支持更多模型接口。

### 优化检索算法

在 `api/knowledge_api.py` 中调整检索参数和重排序逻辑。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
