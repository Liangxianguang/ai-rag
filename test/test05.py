from pathlib import Path
from llama_index.core.schema import TextNode
import json
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import logging

# --- 配置 ---
# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 路径配置 (与 test01.py 保持一致的结构)
current_dir = Path(__file__).parent
project_root = current_dir.parent
DATA_PATH = str(project_root / "test" / "data")
CHROMADB_PATH = str(project_root / "test" / "chroma")
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'

# 新集合的名称
COLLECTION_NAME = 'public_security_law'
# 要处理的特定JSON文件名
DATA_FILE_NAME = '治安管理处罚法.json'


def init_model():
    """初始化 Embedding 模型"""
    logger.info(f"正在从 '{MODEL_PATH}' 加载模型...")
    # 使用 HuggingFaceEmbedding 并设置到全局 Settings
    embeddings = HuggingFaceEmbedding(model_name=MODEL_PATH, device='cuda')
    Settings.embed_model = embeddings
    logger.info("模型加载完成。")

def load_data(path, filename):
    """加载指定的 JSON 数据文件"""
    file_path = Path(path) / filename
    if not file_path.exists():
        logger.error(f"数据文件未找到: {file_path}")
        return None
    
    logger.info(f"正在从 '{file_path}' 加载数据...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 保持与 test01.py 一致的数据结构
    return {
        'content': data,
        'metadata': { 'source': file_path.name }
    }

def create_nodes(data):
    """根据加载的数据创建 TextNode 列表"""
    if not data:
        return []
    
    nodes = []
    law_dict = data["content"]
    source_file = data["metadata"]["source"]
    
    logger.info(f"正在为 '{source_file}' 中的 {len(law_dict)} 个法条创建节点...")
    
    for key, value in law_dict.items():
        # 创建唯一的节点ID
        node_id = f"{source_file}_{key.replace(' ', '_')}"
        
        # 解析标题
        parts = key.split(' ', 1)
        law_name = parts[0] if len(parts) > 0 else "未知法律"
        article = parts[1] if len(parts) > 1 else "未知条款"
        
        # 创建 TextNode 对象
        node = TextNode(
            id_=node_id,
            text=value,
            metadata={
                "law_name": law_name,
                "article": article,
                "full_title": key,
                "source_file": source_file,
                "content_type": "legal_article" # 与 test01.py 保持一致
            }
        )
        nodes.append(node)
        
    logger.info(f"成功创建 {len(nodes)} 个节点。")
    return nodes

def save_to_chroma(nodes, collection_name):
    """将节点保存到 ChromaDB，严格遵循 test01.py 的方法"""
    if not nodes:
        logger.warning("没有可保存的节点，操作已跳过。")
        return

    logger.info(f"正在连接到 ChromaDB: {CHROMADB_PATH}")
    client = chromadb.PersistentClient(path=CHROMADB_PATH)
    
    logger.info(f"正在获取或创建集合: '{collection_name}' (使用余弦距离)")
    # 关键步骤：使用 get_or_create_collection 并指定余弦距离
    collection = client.get_or_create_collection(
        name=collection_name, 
        metadata={"hnsw:space": "cosine"}
    )
    
    # 创建向量存储
    vector_store = ChromaVectorStore(chroma_collection=collection)
    
    # 创建并配置存储上下文
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 关键步骤：先将文档添加到 docstore
    logger.info("正在将文档添加到 docstore...")
    storage_context.docstore.add_documents(nodes)
    
    # 创建索引
    logger.info("正在构建向量索引...")
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True
    )
    
    logger.info(f"✅ 集合 '{collection_name}' 已成功创建并填充了 {len(nodes)} 个文档。")

if __name__ == '__main__':
    # 1. 初始化模型
    init_model()
    
    # 2. 加载数据
    law_data = load_data(DATA_PATH, DATA_FILE_NAME)
    
    # 3. 创建节点
    if law_data:
        nodes = create_nodes(law_data)
        
        # 4. 保存到 ChromaDB
        save_to_chroma(nodes, COLLECTION_NAME)
    else:
        logger.error("未能加载数据，程序已退出。")