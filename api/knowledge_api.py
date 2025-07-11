#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库检索 API 服务
提供基于 LlamaIndex + ChromaDB 的知识库检索功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 跻径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

try:
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.core import StorageContext, VectorStoreIndex, Settings
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core.llms import MockLLM # 修正导入路径
    import chromadb
    import torch
except ImportError as e:
    print(f"请安装必要的依赖: {e}")
    print("pip install llama-index chromadb sentence-transformers torch")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置路径 - 请根据实际情况修改
CHROMADB_PATH = str(project_root / "test" / "chroma")
# 移除固定的 COLLECTION_NAME
# COLLECTION_NAME = 'laodongfa'
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'

# 如果模型路径不存在，使用在线模型
if not Path(MODEL_PATH).exists():
    MODEL_PATH = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    logger.warning("本地模型路径不存在，将使用在线模型")

app = FastAPI(
    title="知识库检索 API",
    description="基于 LlamaIndex + ChromaDB 的知识库检索服务",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic 模型定义 ---
class RetrieveRequest(BaseModel):
    query: str = Field(..., description="查询问题")
    collection_name: str = Field(..., description="要查询的知识库集合名称")
    top_k: int = Field(default=5, ge=1, le=20, description="返回文档数量")
    max_length: int = Field(default=3000, ge=100, le=10000, description="最大内容长度")
    similarity_threshold: float = Field(default=0.65, ge=0, le=1, description="相似度阈值，只返回高于此分数的文档")

class DocumentResult(BaseModel):
    content: str = Field(..., description="文档内容")
    source: str = Field(..., description="文档来源")
    title: Optional[str] = Field(None, description="文档标题")
    score: Optional[float] = Field(None, description="相似度分数")

class RetrieveResponse(BaseModel):
    documents: List[DocumentResult] = Field(..., description="检索到的文档列表")
    total: int = Field(..., description="总文档数量")
    query: str = Field(..., description="原始查询")

# --- 全局变量和初始化 ---
# 移除全局 index，改为在请求时动态创建
# index = None
chroma_client = None

def init_knowledge_base():
    """初始化知识库组件，主要是 embedding 模型和 chroma 客户端"""
    global chroma_client
    
    try:
        logger.info("正在初始化知识库组件...")
        
        if not Path(CHROMADB_PATH).exists():
            raise FileNotFoundError(f"ChromaDB 路径不存在: {CHROMADB_PATH}")
        
        # 1. 显式禁用 LLM 功能，只做检索
        Settings.llm = MockLLM()
        Settings.chunk_size = 512

        # 2. 初始化 embedding 模型
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"使用设备: {device} 加载 Embedding 模型...")
        
        embeddings = HuggingFaceEmbedding(model_name=MODEL_PATH, device=device)
        Settings.embed_model = embeddings
        logger.info("Embedding 模型加载成功")
        
        # 3. 初始化 ChromaDB 客户端
        chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
        
        logger.info("知识库组件初始化完成")
        
    except Exception as e:
        logger.error(f"知识库组件初始化失败: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化知识库"""
    init_knowledge_base()

@app.get("/")
async def root():
    """健康检查接口"""
    return {
        "service": "知识库检索 API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """详细健康检查"""
    global chroma_client
    
    status = {
        "service": "knowledge_api",
        "status": "healthy" if chroma_client is not None else "unhealthy",
        "chromadb_client": "initialized" if chroma_client is not None else "not_initialized",
        "chromadb_path": CHROMADB_PATH,
        "model_path": MODEL_PATH,
        "cuda_available": torch.cuda.is_available()
    }
    
    if chroma_client is None:
        raise HTTPException(status_code=503, detail="知识库未初始化")
    
    return status

@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_knowledge(request: RetrieveRequest):
    """检索知识库内容"""
    global chroma_client
    
    if chroma_client is None:
        raise HTTPException(status_code=503, detail="知识库未初始化 (Chroma Client is None)")
    
    try:
        logger.info(f"收到对集合 '{request.collection_name}' 的检索请求: '{request.query}' (top_k={request.top_k})")
        
        # 动态加载集合并创建索引
        try:
            chroma_collection = chroma_client.get_collection(name=request.collection_name)
            logger.info(f"成功加载集合: {request.collection_name}")
        except Exception as e:
            logger.error(f"加载集合 '{request.collection_name}' 失败: {e}")
            raise HTTPException(status_code=404, detail=f"知识库集合 '{request.collection_name}' 不存在或加载失败")

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        # 直接从 index 创建一个配置好 top_k 的 retriever
        retriever = index.as_retriever(similarity_top_k=request.top_k)
        
        # 执行检索
        nodes = retriever.retrieve(request.query)

        documents = []
        total_length = 0
        if nodes:
            for node in nodes:
                score = node.get_score() if hasattr(node, 'get_score') else 0.0
                
                # 根据阈值过滤文档
                if score < request.similarity_threshold:
                    continue

                content = node.get_content()
                if total_length + len(content) > request.max_length and len(documents) > 0:
                    break
                
                metadata = node.metadata or {}
                doc_result = DocumentResult(
                    content=content,
                    source=metadata.get('source_file', '未知来源'),
                    title=metadata.get('full_title', metadata.get('article', '未知标题')),
                    score=score
                )
                documents.append(doc_result)
                total_length += len(content)

        logger.info(f"检索完成，返回 {len(documents)} 条满足阈值 (>{request.similarity_threshold}) 的文档")
        return RetrieveResponse(
            documents=documents,
            total=len(documents),
            query=request.query
        )
    except Exception as e:
        logger.error(f"检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

@app.get("/collections")
async def list_collections():
    """列出所有可用的集合"""
    global chroma_client
    if chroma_client is None:
        raise HTTPException(status_code=503, detail="知识库未初始化 (Chroma Client is None)")
        
    try:
        collections = chroma_client.list_collections()
        # 将返回的 Collection 对象转换为字典列表
        return [{"name": c.name, "id": str(c.id), "metadata": c.metadata} for c in collections]
    except Exception as e:
        logger.error(f"列出集合失败: {e}")
        raise HTTPException(status_code=500, detail=f"列出集合失败: {str(e)}")

if __name__ == "__main__":
    # 引入 uvicorn 和必要的库
    import uvicorn
    import logging
    
    logger.info("启动知识库检索 API 服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
