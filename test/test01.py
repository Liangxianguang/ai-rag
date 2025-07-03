from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import numpy as np
embeddings = HuggingFaceEmbedding(model_name=r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2')
v = embeddings.get_text_embedding('这件已经卖多少')
documents = ['这件衣服是什么价格', '这件衣服多少钱', '今天的天气太热了']
documents_embedding = [ embeddings.get_text_embedding(doc) for doc in documents]
value0 = np.dot(v, documents_embedding[0])
value1 = np.dot(v, documents_embedding[1])
value2 = np.dot(v, documents_embedding[2])
print(value0)
print(value1)
print(value2)
