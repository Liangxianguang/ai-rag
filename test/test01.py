from pathlib import Path
from llama_index.core.schema import TextNode
import json
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
DATA_DIR = r'D:\llama index\test\data'
CHROMADB_PATH = r'D:\llama index\test\chroma'
COLLECTION_NAME = 'laodongfa'
PERSIST_DIR = r'D:\llama index\test\persist'
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'

def init_model():
    embeddings = HuggingFaceEmbedding(model_name=MODEL_PATH)
    Settings.embed_model = embeddings
def load_data (path):
    files = list(Path(path).glob('*.json'))
    all_data = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.append({
                'content': data,
                'metadata': { 'source': file.name }
            })
    return all_data
def create_nodes(all_data):
    nodes = []
    for file in all_data:
        law_dict = file["content"]
        source_file = file["metadata"]["source"]
        for key, value in law_dict.items():
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
def save(nodes):
    client = chromadb.PersistentClient(CHROMADB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    storage_context = StorageContext.from_defaults(
        vector_store=ChromaVectorStore(chroma_collection=collection)
    )
    storage_context.docstore.add_documents(nodes)
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True
    )
    storage_context.persist(PERSIST_DIR)
    index.storage_context.persist(PERSIST_DIR)
if __name__ == '__main__':
    init_model()
    all_data = load_data(DATA_DIR)
    nodes = create_nodes(all_data)
    save(nodes)