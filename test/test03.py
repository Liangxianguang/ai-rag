from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
import chromadb
import torch
from transformers import BitsAndBytesConfig

print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"Current GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

CHROMADB_PATH = r'C:\Users\liangxianguang\Desktop\nwpu\bigmodel\test\chroma'
COLLECTION_NAME = 'public_security_law'
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'
LLM_PATH = r'C:\Users\liangxianguang\Desktop\model\deepseek-ai\DeepSeek-R1-Distill-Qwen-1___5B'

# 修复：使用新的量化配置
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
)

# 修复：移除冲突的 max_new_tokens 参数
llm = HuggingFaceLLM(
    model_name=LLM_PATH,
    tokenizer_name=LLM_PATH,
    context_window=4096,  # 使用 LlamaIndex 的标准参数
    max_new_tokens=512,   # 使用 LlamaIndex 的标准参数，而不是 generate_kwargs
    model_kwargs={
        'trust_remote_code': True,
        'torch_dtype': torch.float16,
        'quantization_config': quantization_config,
        'low_cpu_mem_usage': True,
    },
    tokenizer_kwargs={'trust_remote_code': True},
    device_map='auto',
    # 简化生成参数，避免冲突
    generate_kwargs={
        'temperature': 0.1,
        'do_sample': True,
        'top_p': 0.9,
        'top_k': 50,
        'repetition_penalty': 1.1,
        # 移除 max_new_tokens 和 pad_token_id
    }
)

# 初始化 embedding 模型 (使用 GPU)
embeddings = HuggingFaceEmbedding(
    model_name=MODEL_PATH,
    device='cuda'
)

# 设置全局模型
Settings.llm = llm
Settings.embed_model = embeddings

# 创建本地持久化 ChromaDB 客户端
chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)

# 检查现有集合
existing_collections = chroma_client.list_collections()
print("现有集合:", [c.name for c in existing_collections])

# 安全获取集合
try:
    chroma_collection = chroma_client.get_collection(name=COLLECTION_NAME)
    print(f"✅ 成功获取集合: {COLLECTION_NAME}")
except chromadb.errors.NotFoundError:
    print(f"❌ 集合 {COLLECTION_NAME} 不存在")
    exit(1)

# 创建 ChromaVectorStore
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 创建索引和查询引擎
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

# 创建查询引擎
query_engine = index.as_query_engine(
    similarity_top_k=3,
    response_mode="compact",
)

# 执行查询
query = "煽动、策划非法集会、游行、示威，不听劝阻的处理？"
print(f"\n🔍 查询: {query}")
print("🤖 正在生成回答...")

try:
    response = query_engine.query(query)
    print(f"\n✅ 回答:\n{response}")
    
    # 显示检索到的源文档（调试用）- 添加分数显示
    print(f"\n📚 相关法条:")
    if hasattr(response, 'source_nodes'):
        for i, node in enumerate(response.source_nodes):
            # 尝试获取相似度分数
            score = getattr(node, 'score', None)
            score_text = f" (分数: {score:.4f})" if score is not None else ""
            
            print(f"  {i+1}. {node.metadata.get('full_title', '未知')}{score_text}")
            print(f"     内容: {node.text[:100]}...")
    else:
        print("  未找到源文档信息")
            
except Exception as e:
    print(f"❌ 查询失败: {e}")
    import traceback
    traceback.print_exc()