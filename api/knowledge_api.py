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
import logging
import json
import asyncio
from pathlib import Path
from fastapi.responses import StreamingResponse
import chromadb
import torch
import json
import asyncio

# 添加项目根目录到 Python 路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

try:
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.core import StorageContext, VectorStoreIndex, Settings
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.huggingface import HuggingFaceLLM
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
COLLECTION_NAME = 'laodongfa'
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'
LLM_PATH = r'C:\Users\liangxianguang\Desktop\model\deepseek-ai\DeepSeek-R1-Distill-Qwen-1___5B'

# 相似度阈值配置
SIMILARITY_THRESHOLD = 0.65  # 相似度阈值，低于此值将被过滤（提高到0.65更严格）
MIN_RELEVANT_NODES = 1       # 最少相关节点数，少于此数量将启用LLM兜底

# 如果模型路径不存在，使用在线模型
if not Path(MODEL_PATH).exists():
    MODEL_PATH = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    logger.warning("本地embedding模型路径不存在，将使用在线模型")

# 检查本地 LLM 路径
USE_LOCAL_LLM = Path(LLM_PATH).exists()
if not USE_LOCAL_LLM:
    logger.warning("本地LLM路径不存在，将禁用LLM功能")

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

# 请求和响应模型
class RetrieveRequest(BaseModel):
    query: str = Field(..., description="查询问题")
    top_k: int = Field(default=5, ge=1, le=20, description="返回文档数量")
    max_length: int = Field(default=3000, ge=100, le=10000, description="最大内容长度")

class DocumentResult(BaseModel):
    content: str = Field(..., description="文档内容")
    source: str = Field(..., description="文档来源")
    title: Optional[str] = Field(None, description="文档标题")
    score: Optional[float] = Field(None, description="相似度分数")

class RetrieveResponse(BaseModel):
    documents: List[DocumentResult] = Field(..., description="检索到的文档列表")
    total: int = Field(..., description="总文档数量")
    query: str = Field(..., description="原始查询")

# 全局变量
query_engine = None
vector_store = None
retriever = None 

def init_knowledge_base():
    """初始化知识库"""
    global query_engine, vector_store, retriever
    
    try:
        logger.info("正在初始化知识库...")
        
        # 初始化 embedding 模型
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"使用设备: {device}")
        
        embeddings = HuggingFaceEmbedding(
            model_name=MODEL_PATH,
            device=device
        )
        Settings.embed_model = embeddings
        
        # 初始化本地 LLM（如果可用）
        if USE_LOCAL_LLM:
            logger.info("正在加载本地 LLM...")
            try:
                llm = HuggingFaceLLM(
                    model_name=LLM_PATH,
                    tokenizer_name=LLM_PATH,
                    model_kwargs={
                        'trust_remote_code': True,
                        'torch_dtype': torch.float16,
                        'load_in_8bit': True,
                        'low_cpu_mem_usage': True
                    },
                    tokenizer_kwargs={'trust_remote_code': True},
                    device_map='auto'
                )
                Settings.llm = llm
                logger.info("本地 LLM 初始化完成")
            except Exception as e:
                logger.warning(f"本地 LLM 加载失败: {e}，将禁用 LLM")
                Settings.llm = None
        else:
            logger.info("未找到本地 LLM，禁用 LLM 功能")
            Settings.llm = None
        
        # 检查 ChromaDB 是否存在
        if not Path(CHROMADB_PATH).exists():
            raise FileNotFoundError(f"ChromaDB 路径不存在: {CHROMADB_PATH}")
        
        # 创建 ChromaDB 客户端
        chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
        
        # 获取集合
        try:
            chroma_collection = chroma_client.get_collection(name=COLLECTION_NAME)
            logger.info(f"成功加载集合: {COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"无法加载集合 {COLLECTION_NAME}: {e}")
            raise
        
        # 创建向量存储
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        # 创建索引和查询引擎
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        
        # 根据是否有 LLM 选择不同的查询模式
        if Settings.llm is not None:
            query_engine = index.as_query_engine(
                similarity_top_k=10,  # 内部检索更多文档
                response_mode="compact"  # 使用 LLM 生成简洁回答
            )
            retriever = index.as_retriever(similarity_top_k=10)
            logger.info("知识库初始化完成（带 LLM 功能）")
        else:
            # 使用检索器而不是查询引擎（因为禁用了LLM）
            retriever = index.as_retriever(
                similarity_top_k=10  # 内部检索更多文档
            )
            query_engine = None
            logger.info("知识库初始化完成（仅检索功能）")
        
    except Exception as e:
        logger.error(f"知识库初始化失败: {e}")
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
    global query_engine, vector_store, retriever
    
    status = {
        "service": "knowledge_api",
        "status": "healthy" if (query_engine is not None or retriever is not None) else "unhealthy",
        "vector_store": "initialized" if vector_store is not None else "not_initialized",
        "query_engine": "initialized" if query_engine is not None else "not_initialized",
        "retriever": "initialized" if retriever is not None else "not_initialized",
        "llm_enabled": Settings.llm is not None,
        "chromadb_path": CHROMADB_PATH,
        "collection_name": COLLECTION_NAME,
        "model_path": MODEL_PATH,
        "cuda_available": torch.cuda.is_available()
    }
    
    if not query_engine and not retriever:
        raise HTTPException(status_code=503, detail="知识库未初始化")
    
    return status

@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_knowledge(request: RetrieveRequest):
    """检索知识库内容"""
    global query_engine, retriever
    
    if not query_engine and not retriever:
        raise HTTPException(status_code=503, detail="知识库未初始化")
    
    try:
        logger.info(f"收到检索请求: {request.query}")
        
        # 优先使用检索器，然后是查询引擎
        if retriever:
            source_nodes = retriever.retrieve(request.query)
        elif hasattr(query_engine, 'query'):
            # 这是查询引擎（带LLM）
            response = query_engine.query(request.query)
            source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else []
        else:
            # 这是检索器（仅检索）
            source_nodes = query_engine.retrieve(request.query)
        
        # 处理检索结果，应用相似度过滤
        documents = []
        total_length = 0
        
        if source_nodes:
            # 先过滤低相似度的节点
            filtered_nodes = []
            for node in source_nodes:
                score = getattr(node, 'score', 0.0)
                if score >= SIMILARITY_THRESHOLD:
                    filtered_nodes.append(node)
            
            logger.info(f"检索到 {len(source_nodes)} 条结果，相似度过滤后剩余 {len(filtered_nodes)} 条")
            
            for i, node in enumerate(filtered_nodes[:request.top_k]):
                # 获取文档内容
                content = node.node.text if hasattr(node, 'node') else node.text
                
                # 检查内容长度限制
                if total_length + len(content) > request.max_length:
                    # 截断内容
                    remaining_length = request.max_length - total_length
                    if remaining_length > 100:  # 至少保留100字符
                        content = content[:remaining_length] + "..."
                    else:
                        break
                
                # 获取元数据
                metadata = (node.node.metadata if hasattr(node, 'node') else node.metadata) or {}
                
                # 构建文档结果
                doc_result = DocumentResult(
                    content=content,
                    source=metadata.get('source_file', '未知来源'),
                    title=metadata.get('full_title', metadata.get('article', '未知标题')),
                    score=node.score if hasattr(node, 'score') else None
                )
                
                documents.append(doc_result)
                total_length += len(content)
                
                # 如果达到长度限制，停止添加
                if total_length >= request.max_length:
                    break
        
        logger.info(f"检索完成，返回 {len(documents)} 条文档")
        
        return RetrieveResponse(
            documents=documents,
            total=len(documents),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

@app.post("/answer")
async def answer_question(request: RetrieveRequest):
    """基于知识库内容回答问题"""
    global retriever, query_engine
    
    if not retriever and not query_engine:
        raise HTTPException(status_code=500, detail="知识库未初始化")
    
    try:
        logger.info(f"回答问题: {request.query}")
        
        # 第一步：优先使用检索器检索知识库内容
        if retriever:
            nodes = retriever.retrieve(request.query)
        elif query_engine and hasattr(query_engine, 'retrieve'):
            # 备用：如果query_engine是检索器
            nodes = query_engine.retrieve(request.query)
        else:
            # 如果只有LLM查询引擎，先获取其检索结果
            response = query_engine.query(request.query)
            nodes = getattr(response, 'source_nodes', [])
        
        # 第二步：检查是否从知识库找到了相关内容，并应用相似度阈值过滤
        if nodes and len(nodes) > 0:
            # 过滤低相似度的节点
            filtered_nodes = []
            for node in nodes:
                score = getattr(node, 'score', 0.0)
                logger.info(f"节点相似度: {score}, 阈值: {SIMILARITY_THRESHOLD}")
                if score >= SIMILARITY_THRESHOLD:
                    filtered_nodes.append(node)
                    logger.info(f"节点通过过滤: {score} >= {SIMILARITY_THRESHOLD}")
                else:
                    logger.info(f"节点被过滤: {score} < {SIMILARITY_THRESHOLD}")
            
            logger.info(f"原始检索到 {len(nodes)} 条结果，相似度阈值过滤后剩余 {len(filtered_nodes)} 条")
            
            # 检查过滤后是否还有足够的相关内容
            if len(filtered_nodes) >= MIN_RELEVANT_NODES:
                # 知识库有相关内容，直接基于检索结果组装详细答案（不使用LLM）
                logger.info(f"知识库找到 {len(filtered_nodes)} 条高相关性内容，直接基于法条回答")
            
                context_parts = []
                sources = []
                
                for i, node in enumerate(filtered_nodes[:request.top_k], 1):
                    # 正确获取元数据和内容
                    if hasattr(node, 'node'):
                        metadata = getattr(node.node, 'metadata', {})
                        content = node.node.text
                    else:
                        metadata = getattr(node, 'metadata', {})
                        content = node.text
                    
                    title = metadata.get('full_title', metadata.get('article', f'相关条文{i}'))
                    source_file = metadata.get('source_file', '劳动法.json')
                    score = getattr(node, 'score', None)
                    
                    # 格式化每条法条内容（纯文本格式，无Markdown）
                    formatted_content = f"{title}\n{content}"
                    if score:
                        formatted_content += f"\n（相似度：{score:.4f}）"
                    
                    context_parts.append(formatted_content)
                    
                    sources.append({
                        "title": title,
                        "source": source_file,
                        "score": score
                    })
                
                # 基于知识库内容构建简洁的纯文本回答
                answer_parts = [
                    "【基于知识库数据】",
                    f"\n根据您的问题「{request.query}」，在劳动法知识库中找到以下相关法律条文：\n"
                ]
                
                # 添加每条法条的完整内容（纯文本格式）
                for i, part in enumerate(context_parts, 1):
                    answer_parts.append(f"{i}. {part}\n")
                
                # 添加简洁的数据来源说明
                answer_parts.append(f"\n数据来源说明：")
                answer_parts.append("以上内容来自劳动法知识库，为法律条文原文，具有法律权威性。")
                answer_parts.append("如需具体的法律适用建议，请结合实际情况咨询专业法律顾问。")
                
                answer = "\n".join(answer_parts)
                
                return {
                    "answer": answer,
                    "sources": sources,
                    "method": "knowledge_base_direct"
                }
            else:
                # 相似度过滤后没有足够的相关内容，转入LLM处理
                logger.info(f"知识库检索结果相似度不足（阈值: {SIMILARITY_THRESHOLD}），转入LLM智能回答")
        else:
            logger.info("知识库未检索到任何内容，转入LLM智能回答")
        
        # 第三步：知识库没有相关内容或相似度不足，使用LLM智能回答（如果可用）
        if Settings.llm is not None:
            try:
                logger.info("使用LLM智能回答")
                
                # 构建包含清晰思考过程的提示词
                general_prompt = f"""
用户问题：{request.query}

请按照以下格式回答，确保思考过程和回答内容完全分离：

<think>
嗯，用户的问题是"{request.query}"。让我仔细分析一下：

1. 问题分析：这个问题涉及什么主题或领域？
2. 背景考虑：可能需要考虑哪些相关因素？
3. 回答策略：如何提供最有帮助的信息？
4. 注意事项：需要特别提醒用户什么？

由于在专业知识库中没有找到直接相关的内容，我需要基于通用知识来回答这个问题，并明确标注信息来源。
</think>

【知识库未找到相关法律条文】

知识库检索结果：在劳动法知识库中未找到与「{request.query}」直接匹配的法律条文。

【AI智能生成回答（非知识库数据）】

[请在这里提供详细、有用的回答，要求：
1. 明确说明这是基于通用知识的回答
2. 提供具体的指导和建议  
3. 如果涉及法律问题，建议咨询专业法律顾问
4. 用专业但易懂的语言表达
5. 回答要有条理、完整]

重要提示：
- 以上回答为AI智能生成，非知识库权威法条
- 不具备法律效力，仅供参考
- 如需权威法律依据，请咨询专业法律顾问
- 建议查阅最新的官方法律法规原文
"""
                
                from llama_index.core.llms import ChatMessage
                messages = [ChatMessage(role="user", content=general_prompt)]
                response = Settings.llm.chat(messages)
                llm_answer = str(response).strip()
                
                return {
                    "answer": llm_answer,  # 直接返回包含think标签的完整回答
                    "sources": [],
                    "method": "llm_fallback"
                }
            
            except Exception as e:
                logger.error(f"LLM智能回答失败: {e}")
        
        # 最后的备用方案：都没有时的回答
        return {
            "answer": f"""【知识库未找到相关内容，AI服务不可用】

知识库检索结果：在劳动法知识库中未找到与「{request.query}」相关的法律条文。

AI智能服务状态：当前不可用，无法提供智能生成回答。

建议您：
1. 尝试使用不同的关键词重新提问
2. 咨询专业的法律顾问
3. 查阅相关的法律法规原文
4. 在官方法律数据库中搜索

提示：本系统优先基于权威法律条文回答，确保信息的准确性和可靠性。""",
            "sources": [],
            "method": "no_result"
        }
            
    except Exception as e:
        logger.error(f"回答问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"回答问题失败: {str(e)}")

@app.post("/answer_stream")
async def answer_question_stream(request: RetrieveRequest):
    """基于知识库内容回答问题（流式响应）"""
    global retriever, query_engine
    
    if not retriever and not query_engine:
        raise HTTPException(status_code=500, detail="知识库未初始化")
    
    async def generate_response():
        try:
            logger.info(f"流式回答问题: {request.query}")
            
            # 先发送检索状态
            yield f"data: {json.dumps({'type': 'thinking', 'content': '正在搜索知识库...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)
            
            # 第一步：检索知识库内容
            if retriever:
                nodes = retriever.retrieve(request.query)
            elif query_engine and hasattr(query_engine, 'retrieve'):
                nodes = query_engine.retrieve(request.query)
            else:
                response = query_engine.query(request.query)
                nodes = getattr(response, 'source_nodes', [])
            
            # 发送检索结果状态
            yield f"data: {json.dumps({'type': 'thinking', 'content': f'检索到 {len(nodes)} 条结果，正在过滤...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)
            
            # 第二步：应用相似度过滤
            if nodes and len(nodes) > 0:
                filtered_nodes = []
                for node in nodes:
                    score = getattr(node, 'score', 0.0)
                    if score >= SIMILARITY_THRESHOLD:
                        filtered_nodes.append(node)
                
                logger.info(f"过滤后剩余 {len(filtered_nodes)} 条相关内容")
                
                if len(filtered_nodes) >= MIN_RELEVANT_NODES:
                    # 知识库有相关内容
                    yield f"data: {json.dumps({'type': 'thinking', 'content': f'找到 {len(filtered_nodes)} 条高相关性法条，正在整理答案...'}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.2)
                    
                    # 构建知识库回答
                    sources = []
                    context_parts = []
                    
                    for i, node in enumerate(filtered_nodes[:request.top_k], 1):
                        if hasattr(node, 'node'):
                            metadata = getattr(node.node, 'metadata', {})
                            content = node.node.text
                        else:
                            metadata = getattr(node, 'metadata', {})
                            content = node.text
                        
                        title = metadata.get('full_title', metadata.get('article', f'相关条文{i}'))
                        source_file = metadata.get('source_file', '劳动法.json')
                        score = getattr(node, 'score', None)
                        
                        formatted_content = f"{title}\n{content}"
                        if score:
                            formatted_content += f"\n（相似度：{score:.4f}）"
                        
                        context_parts.append(formatted_content)
                        sources.append({
                            "title": title,
                            "source": source_file,
                            "score": score
                        })
                    
                    # 流式发送答案
                    yield f"data: {json.dumps({'type': 'answer_start', 'method': 'knowledge_base_direct'}, ensure_ascii=False)}\n\n"
                    
                    answer_parts = [
                        "【基于知识库数据】",
                        f"\n根据您的问题「{request.query}」，在劳动法知识库中找到以下相关法律条文：\n"
                    ]
                    
                    for part in answer_parts:
                        yield f"data: {json.dumps({'type': 'answer', 'content': part}, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.05)
                    
                    for i, part in enumerate(context_parts, 1):
                        content = f"{i}. {part}\n"
                        yield f"data: {json.dumps({'type': 'answer', 'content': content}, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.1)
                    
                    final_parts = [
                        f"\n数据来源说明：",
                        "以上内容来自劳动法知识库，为法律条文原文，具有法律权威性。",
                        "如需具体的法律适用建议，请结合实际情况咨询专业法律顾问。"
                    ]
                    
                    for part in final_parts:
                        yield f"data: {json.dumps({'type': 'answer', 'content': part + '\n'}, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.05)
                    
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                    return
            
            # 没有找到相关内容，使用LLM
            yield f"data: {json.dumps({'type': 'thinking', 'content': '知识库中未找到相关内容，正在启用AI智能分析...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.2)
            
            if Settings.llm is not None:
                # 第一阶段：显示LLM思考过程
                thinking_parts = [
                    f"嗯，用户的问题是「{request.query}」。",
                    "让我分析一下这个问题的含义和可能涉及的方面。",
                    "这个问题可能涉及多个层面，我需要仔细考虑如何提供最有帮助的回答。",
                    "由于在专业知识库中没有找到直接相关的内容，我需要基于通用知识来回答。",
                    "我会确保提供准确、有用的信息，并明确标注这是AI生成的内容。"
                ]
                
                # 逐步显示思考过程
                for part in thinking_parts:
                    yield f"data: {json.dumps({'type': 'thinking', 'content': part}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.5)  # 稍微慢一点，让用户看清思考过程
                
                # 思考完成，开始生成回答
                yield f"data: {json.dumps({'type': 'thinking', 'content': '思考完成，正在生成回答...'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.3)
                
                # 第二阶段：开始回答
                yield f"data: {json.dumps({'type': 'answer_start', 'method': 'llm_fallback'}, ensure_ascii=False)}\n\n"
                
                # 构建LLM提示（不包含思考过程，只要纯粹的回答）
                general_prompt = f"""
用户问题：{request.query}

请直接回答用户的问题，不要包含思考过程。要求：
1. 明确说明这是基于通用知识的回答，不是基于专业法律文件
2. 如果涉及法律问题，建议用户咨询专业法律顾问  
3. 提供有用的指导和建议
4. 用专业但易懂的语言表达
5. 回答要完整、有条理

请直接开始回答，不要使用"好的"、"我来回答"等开场白。
"""
                
                from llama_index.core.llms import ChatMessage
                messages = [ChatMessage(role="user", content=general_prompt)]
                response = Settings.llm.chat(messages)
                llm_answer = str(response).strip()
                
                # 第三阶段：流式发送回答内容
                # 先发送固定的标题部分
                header = "【知识库未找到相关法律条文】\n\n知识库检索结果：在劳动法知识库中未找到与「{request.query}」直接匹配的法律条文。\n\n"
                yield f"data: {json.dumps({'type': 'answer', 'content': header}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
                
                content_header = "【AI智能生成回答（非知识库数据）】\n\n"
                yield f"data: {json.dumps({'type': 'answer', 'content': content_header}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
                
                # 逐字符发送AI回答内容
                for char in llm_answer:
                    yield f"data: {json.dumps({'type': 'answer', 'content': char}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.02)  # 打字机效果
                
                # 发送重要提示
                footer = "\n\n重要提示：\n- 以上回答为AI智能生成，非知识库权威法条\n- 不具备法律效力，仅供参考\n- 如需权威法律依据，请咨询专业法律顾问\n- 建议查阅最新的官方法律法规原文"
                yield f"data: {json.dumps({'type': 'answer', 'content': footer}, ensure_ascii=False)}\n\n"
            
            else:
                # 没有LLM时的备用回答
                fallback_answer = f"""【知识库未找到相关内容，AI服务不可用】

知识库检索结果：在劳动法知识库中未找到与「{request.query}」相关的法律条文。

建议您：
1. 尝试使用不同的关键词重新提问
2. 咨询专业的法律顾问
3. 查阅相关的法律法规原文"""
                
                yield f"data: {json.dumps({'type': 'answer', 'content': fallback_answer}, ensure_ascii=False)}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"流式回答失败: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': f'回答失败: {str(e)}'}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/collections")
async def list_collections():
    """列出所有可用的集合"""
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
        collections = chroma_client.list_collections()
        
        return {
            "collections": [
                {
                    "name": col.name,
                    "count": col.count(),
                    "metadata": col.metadata
                }
                for col in collections
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取集合列表失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动知识库检索 API 服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
