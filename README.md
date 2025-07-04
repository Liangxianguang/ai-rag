# AI RAG 智能知识库问答系统

基于 Vue 3 + FastAPI + LlamaIndex + ChromaDB 的全栈智能知识库检索与问答系统。

## 🌟 功能特性

### 后端 API 服务
- 🔍 **智能检索**: 基于语义相似度的文档检索，支持相似度阈值过滤
- 📚 **多知识库**: 支持多个知识库集合的动态切换和管理
- 🎯 **精准检索**: 可配置检索数量、内容长度、相似度阈值等参数
- 🔧 **灵活部署**: 支持本地嵌入模型和在线模型的灵活配置

### 前端聊天界面  
- 🤖 **智能对话**: 结合知识库的上下文感知AI问答
- � **多会话管理**: 支持创建、切换、删除多个对话会话
- 📱 **现代化UI**: 基于 Element Plus 的响应式聊天界面
- ⚡ **流式响应**: 支持实时流式输出，提升用户体验
- 📎 **文件上传**: 支持图片、文本、PDF、Word等多种文件类型
- 😊 **表情支持**: 内置表情选择器，支持消息表情互动
- 🔧 **灵活配置**: 支持本地模型(Ollama)和远程API的切换

### 系统管理
- 🎛️ **模型管理**: 自动发现Ollama本地模型，支持远程API配置
- 📊 **设置持久化**: 用户设置和对话历史本地存储
- 🔄 **健康监控**: 完善的健康检查和状态监控接口

## 📁 项目结构

```
bigmodel/
├── api/                           # 后端 FastAPI 服务
│   ├── knowledge_api.py          # 知识库检索 API 主服务
│   ├── requirements.txt          # Python 依赖包
│   └── test_similarity.py        # 相似度测试工具
├── src/                          # 前端 Vue 3 应用
│   ├── components/               # 可复用组件
│   │   ├── ChatInput.vue        # 聊天输入组件（支持文件上传、表情）
│   │   ├── ChatMessages.vue     # 消息展示组件（流式、点赞、复制）
│   │   ├── ChatSidebar.vue      # 会话侧边栏
│   │   └── SettingsDialog.vue   # 设置对话框
│   ├── composables/             # 组合式 API
│   │   ├── useChat.js          # 聊天状态管理
│   │   ├── useSettings.js      # 设置管理
│   │   └── useMessageSender.js # 消息发送逻辑
│   ├── services/               # 服务层
│   │   └── knowledgeService.js # 知识库与AI服务调用
│   ├── utils/                  # 工具函数
│   │   └── helpers.js          # 文件处理、文本工具等
│   └── views/                  # 页面组件
│       └── Chat.vue            # 主聊天页面
├── test/                        # 测试和数据管理
│   ├── data/                   # 原始数据文件
│   │   ├── 劳动法.json         # 劳动法条文数据
│   │   ├── 治安管理处罚法.json  # 治安管理法规数据
│   │   └── jinxiandaishi_event.json
│   ├── chroma/                 # ChromaDB 向量数据库
│   ├── get_data.py             # 数据抓取脚本
│   ├── save_vector.py          # 向量化存储脚本
│   ├── test01.py - test05.py   # 各种测试脚本
│   └── test_api.py             # API 测试脚本
├── public/                      # 静态资源
├── package.json                # 前端依赖配置
├── vite.config.js              # Vite 构建配置
└── README.md                   # 项目文档
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- CUDA 支持的GPU（可选，用于加速推理）

### 后端安装与配置

1. **安装Python依赖**
```bash
cd api
pip install -r requirements.txt
```

2. **配置知识库路径**
在 `api/knowledge_api.py` 中修改以下配置：

```python
# ChromaDB 数据路径
CHROMADB_PATH = str(project_root / "test" / "chroma")

# 嵌入模型路径（本地或在线）
MODEL_PATH = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
```

3. **构建知识库（可选）**
```bash
cd test
# 运行数据处理脚本构建知识库
python test05.py  # 处理治安管理处罚法
python test01.py  # 处理劳动法
```

### 前端安装与配置

1. **安装Node.js依赖**
```bash
npm install
# 或
yarn install
```

2. **配置代理（开发环境）**
在 `vite.config.js` 中已配置API代理，默认将 `/api` 请求转发到 `http://localhost:8000`

### 运行服务

1. **启动后端API服务**
```bash
cd api
python knowledge_api.py
```
服务将在 `http://localhost:8000` 启动

2. **启动前端开发服务器**
```bash
npm run dev
# 或
yarn dev
```
前端将在 `http://localhost:3000` 启动

3. **生产环境部署**
```bash
npm run build
npm run preview
```

## 📚 API 接口文档

### 健康检查
- `GET /` - 基础健康检查
- `GET /health` - 详细状态信息，包括模型加载状态、CUDA可用性等

### 知识库管理
- `GET /collections` - 列出所有可用的知识库集合

### 知识库检索
- `POST /retrieve` - 检索相关文档

**请求参数:**
```json
{
  "query": "劳动合同期限",
  "collection_name": "laodongfa",
  "top_k": 5,
  "max_length": 3000,
  "similarity_threshold": 0.65
}
```

**响应格式:**
```json
{
  "documents": [
    {
      "content": "文档内容",
      "source": "文档来源",
      "title": "文档标题",
      "score": 0.85
    }
  ],
  "total": 5,
  "query": "劳动合同期限"
}
```

## 🎛️ 前端功能配置

### 模型配置
- **本地模型**: 支持Ollama本地部署的模型，可自动发现可用模型
- **远程模型**: 支持SiliconFlow等API服务，需配置API Key
- **参数调节**: 支持温度、最大长度等参数的实时调节

### 知识库配置
- **多知识库**: 支持在不同知识库间切换（劳动法、治安管理法等）
- **检索参数**: 可配置检索数量、相似度阈值、最大内容长度
- **API地址**: 支持自定义知识库API地址

### 聊天功能
- **多会话**: 支持创建、切换、删除多个独立对话
- **消息操作**: 支持复制、点赞、重新生成回答
- **文件上传**: 支持多种格式文件的上传和处理
- **表情互动**: 内置丰富的表情选择器

## 💡 使用示例

### 1. Python API调用
```python
import requests

# 检索文档
response = requests.post('http://localhost:8000/retrieve', json={
    'query': '试用期最长多久？',
    'collection_name': 'laodongfa',
    'top_k': 3,
    'similarity_threshold': 0.7
})

print(response.json())

# 列出所有知识库
collections = requests.get('http://localhost:8000/collections')
print(collections.json())
```

### 2. 前端集成
```javascript
import { KnowledgeService } from '@/services/knowledgeService'

const knowledgeService = new KnowledgeService()

// 发送消息
const response = await knowledgeService.sendMessage(
  messages,
  currentMessage,
  settings,
  onChunk  // 流式响应回调
)
```

### 3. 知识库构建
```python
# 使用测试脚本构建新的知识库
cd test
python test05.py  # 构建治安管理处罚法知识库
```

## 🔧 高级配置

### 1. 自定义嵌入模型
```python
# 在 knowledge_api.py 中修改
MODEL_PATH = 'your-custom-model-path'
# 支持本地路径或HuggingFace模型名称
```

### 2. CORS配置
```python
# 在 knowledge_api.py 中修改允许的前端地址
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "your-frontend-url"],
    # ...
)
```

### 3. 数据库路径配置
```python
# 自定义ChromaDB存储路径
CHROMADB_PATH = "/path/to/your/chroma/data"
```

## 🛠️ 技术栈

### 后端技术
- **FastAPI**: 现代高性能Web框架，提供自动API文档生成
- **LlamaIndex**: 强大的RAG框架，支持多种数据源和检索策略
- **ChromaDB**: 高性能向量数据库，支持相似度搜索
- **HuggingFace Transformers**: 预训练模型加载和推理
- **Sentence Transformers**: 专业的句子嵌入模型
- **PyTorch**: 深度学习框架，支持GPU加速

### 前端技术
- **Vue 3**: 渐进式JavaScript框架，采用Composition API
- **Element Plus**: 基于Vue 3的桌面端组件库
- **Pinia**: Vue 3官方状态管理库
- **Vue Router 4**: Vue 3官方路由管理器
- **Vite**: 快速的前端构建工具
- **Axios**: HTTP客户端，用于API调用

### 开发工具
- **Vite Plugin Vue**: Vue单文件组件支持
- **Auto Import**: 自动导入API和组件
- **Vue DevTools**: Vue开发者工具支持

## 📊 性能特性

- **流式响应**: 前后端支持Server-Sent Events实时推送
- **GPU加速**: 支持CUDA加速的模型推理
- **内存优化**: 智能的模型加载和缓存机制
- **并发处理**: FastAPI异步处理多个请求
- **响应式UI**: Element Plus响应式组件适配多设备

## 🔒 安全特性

- **CORS配置**: 严格的跨域资源共享策略
- **输入验证**: Pydantic模型自动验证API输入
- **错误处理**: 完善的异常捕获和错误提示
- **API限流**: 可配置的请求频率限制

## 📖 数据支持

### 当前知识库
- **劳动法**: 完整的劳动法条文和解释
- **治安管理处罚法**: 治安管理相关法规
- **晋贤大事**: 历史事件数据

### 支持的数据格式
- **JSON**: 结构化法条数据
- **文本文件**: 纯文本文档
- **PDF**: 通过文件上传功能支持
- **Word文档**: 支持.docx格式
- **图片**: 支持OCR文字提取（需配置）

## 🚀 部署建议

### 开发环境
- 本地开发推荐使用热重载模式
- 前后端分离部署便于调试
- 建议使用代码编辑器的API自动补全

### 生产环境
- 使用Nginx作为反向代理
- 配置HTTPS加密传输
- 使用Docker容器化部署
- 配置日志轮转和监控

## 🤝 贡献指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue到GitHub仓库
- 发送邮件到项目维护者

## 🙏 致谢

感谢以下开源项目的支持：
- [LlamaIndex](https://github.com/jerryjliu/llama_index) - 强大的RAG框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库