from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
import chromadb
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"Current GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
CHROMADB_PATH = r'D:\llama index\test\chroma'
COLLECTION_NAME = 'laodongfa'
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'
LLM_PATH = r'C:\Users\liangxianguang\Desktop\model\deepseek-ai\DeepSeek-R1-Distill-Qwen-1___5B'

# 初始化本地 LLM (使用 GPU)
llm = HuggingFaceLLM(
    model_name=LLM_PATH,
    tokenizer_name=LLM_PATH,
    model_kwargs={
        'trust_remote_code': True,
        'torch_dtype': torch.float16,  # 使用半精度
        'load_in_8bit': True,  # 8bit 量化
        'low_cpu_mem_usage': True
        # 移除 'device_map': 'auto'
    },
    tokenizer_kwargs={'trust_remote_code': True},
    device_map='auto'  # 在这里单独指定
)
# 初始化 embedding 模型 (使用 GPU)
embeddings = HuggingFaceEmbedding(
    model_name=MODEL_PATH,
    device='cuda'  # 明确指定使用 GPU
)

# 设置全局模型
Settings.llm = llm
Settings.embed_model = embeddings

# 创建本地持久化 ChromaDB 客户端
chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)

# 获取或创建集合
chroma_collection = chroma_client.get_collection(name=COLLECTION_NAME)

# 创建 ChromaVectorStore
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 创建索引和查询引擎
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
query_engine = index.as_query_engine()

# 执行查询
query = "疾人、少数民族人员、退出现役的军人的就业的相关法律是什么？"
response = query_engine.query(query)
print(response)