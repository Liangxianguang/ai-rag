# 严格按照 test01.py 老方法实现的最终版
import os
import json
from pathlib import Path
import logging
import chromadb
from llama_index.core.schema import TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import torch

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 路径配置
current_dir = Path(__file__).parent
project_root = current_dir.parent
CHROMADB_PATH = str(project_root / "test" / "chroma")
DATA_PATH = str(project_root / "test" / "data")
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'

def init_model():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"使用设备: {device} 加载 Embedding 模型...")
    Settings.embed_model = HuggingFaceEmbedding(model_name=MODEL_PATH, device=device)
    os.makedirs(CHROMADB_PATH, exist_ok=True)
    db = chromadb.PersistentClient(path=CHROMADB_PATH)
    return db

def load_data(data_path):
    files = list(Path(data_path).glob('*.json'))
    all_data = []
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.append({
                    'content': data,
                    'metadata': {'source': file.name, 'stem': file.stem}
                })
        except Exception as e:
            logger.warning(f"加载文件 {file} 失败: {e}")
    return all_data

def create_nodes(all_data):
    nodes = []
    for file in all_data:
        law_dict = file["content"]
        source_file = file["metadata"]["source"]
        for key, value in law_dict.items():
            if not value or len(value.strip()) < 5:
                continue
            node_id = f"{source_file}_{key}"
            parts = key.split(' ', 1)
            law_name = parts[0] if len(parts) > 0 else "未知法律"
            article = parts[1] if len(parts) > 1 else "未知条款"
            node = TextNode(
                id=node_id,
                text=value,
                metadata={
                    "law_name": law_name,
                    "article": article,
                    "full_title": key,
                    "source_file": source_file,
                    "content_type": "legal_article"
                }
            )
            nodes.append(node)
    return nodes

def save_to_chroma(nodes, collection_name):
    db = chromadb.PersistentClient(path=CHROMADB_PATH)
    # 删除已存在集合
    try:
        existing_collections = [c.name for c in db.list_collections()]
        if collection_name in existing_collections:
            logger.warning(f"删除已存在的集合: {collection_name}")
            db.delete_collection(name=collection_name)
    except Exception as e:
        logger.error(f"删除集合 {collection_name} 失败: {e}")

    # 创建集合（严格指定余弦距离）
    chroma_collection = db.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    storage_context.docstore.add_documents(nodes)
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True
    )
    logger.info(f"集合 {collection_name} 构建完成，节点数: {len(nodes)}")

def main():
    db = init_model()
    all_data = load_data(DATA_PATH)
    if not all_data:
        logger.warning(f"在 {DATA_PATH} 目录下未找到任何 .json 文件。")
        return
    for file in all_data:
        file_stem = file["metadata"]["stem"].replace(' ', '')
        if '劳动法' in file_stem:
            collection_name = 'labor_law'
        elif '治安管理处罚法' in file_stem:
            collection_name = 'public_security_law'
        else:
            import re
            safe_name = re.sub(r'[^a-zA-Z]', '', file_stem)
            if not safe_name:
                logger.warning(f"无法为文件 {file_stem} 生成有效的集合名称，已跳过。")
                continue
            collection_name = safe_name.lower() + "_law"
        nodes = create_nodes([file])
        if not nodes:
            logger.warning(f"未能从 {file_stem} 创建任何文档节点，跳过。")
            continue
        save_to_chroma(nodes, collection_name)

if __name__ == "__main__":
    main()