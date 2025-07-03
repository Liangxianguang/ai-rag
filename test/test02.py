import chromadb
from sentence_transformers import SentenceTransformer
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'
class SentenceTransformerEmbeddingFunction:
  def __init__(self, model_path: str, device: str = "cpu"):
        self.model = SentenceTransformer(model_path, device=device)
  def __call__(self, input: list[str]) -> list[list[float]]:
        if isinstance(input, str):
            input = [input]
        return self.model.encode(input, convert_to_numpy=True).tolist()
embeddings = SentenceTransformerEmbeddingFunction(model_path=MODEL_PATH)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection(name="test_collection", metadata={"hnsw:space": "cosine"}, embedding_function=embeddings)
collection.add(
    documents=['这件衣服是什么价格', '这件衣服多少钱', '今天的天气太热了'],
    metadatas=[{"source": "tech_doc"}, {"source": "tech_doc2"}, {"source": "tech_doc3"}],
    ids=['doc1', 'doc2', 'doc3']
)
result = collection.query(
    query_texts='这件已经卖多少',
    n_results=3
)
print(result)