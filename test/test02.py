#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试嵌入向量质量
"""

import chromadb
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import numpy as np

CHROMADB_PATH = r'C:\Users\liangxianguang\Desktop\nwpu\bigmodel\test\chroma'
MODEL_PATH = r'D:\llama index\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2'

def debug_embeddings():
    """调试嵌入向量质量"""
    
    # 初始化嵌入模型
    embeddings = HuggingFaceEmbedding(
        model_name=MODEL_PATH,
        device='cuda'
    )
    
    # 连接ChromaDB
    client = chromadb.PersistentClient(path=CHROMADB_PATH)
    
    # 详细测试不同查询的相似度
    test_queries = [
        "煽动、策划非法集会、游行、示威，不听劝阻的处理？",  # 原始查询
        "煽动、策划非法集会、游行、示威，不听劝阻的",           # 去掉"处理？"
        "煽动策划非法集会游行示威不听劝阻",                   # 去掉标点
        "非法集会游行示威",                                 # 核心关键词
        "策划非法集会",                                     # 简化查询
        "煽动、策划非法集会、游行、示威，不听劝阻的，处十日以上十五日以下拘留", # 完全匹配
    ]
    
    collections_to_test = ['public_security_law', 'laodongfa']
    
    for collection_name in collections_to_test:
        print(f"\n{'='*60}")
        print(f"分析集合: {collection_name}")
        print(f"{'='*60}")
        
        try:
            collection = client.get_collection(name=collection_name)
            
            for query_idx, query in enumerate(test_queries):
                print(f"\n--- 测试查询 {query_idx + 1}: '{query}' ---")
                
                # 获取查询的嵌入向量
                query_embedding = embeddings.get_text_embedding(query)
                
                # 查询相关文档
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=20,
                    include=['documents', 'metadatas', 'distances']
                )
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    title = metadata.get('full_title', '未知')
                    # 只显示第六十六条的结果
                    if '第六十六条' in title:
                        similarity = 1 - distance
                        print(f"  找到第六十六条:")
                        print(f"    距离: {distance:.4f}")
                        print(f"    相似度: {similarity:.4f}")
                        print(f"    文档内容: '{doc}'")
                        
                        # 手动计算余弦相似度
                        doc_embedding = embeddings.get_text_embedding(doc)
                        manual_similarity = np.dot(query_embedding, doc_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                        )
                        print(f"    手动余弦相似度: {manual_similarity:.4f}")
                        
                        # 分析文本差异
                        print(f"    查询长度: {len(query)}, 文档长度: {len(doc)}")
                        print(f"    文本重叠度: {calculate_overlap(query, doc):.2f}%")
                        break
                else:
                    print(f"  未在前3个结果中找到第六十六条")
                    
        except Exception as e:
            print(f"处理 {collection_name} 时出错: {e}")

def calculate_overlap(text1, text2):
    """计算两个文本的重叠度"""
    set1 = set(text1)
    set2 = set(text2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return (intersection / union) * 100 if union > 0 else 0

if __name__ == "__main__":
    debug_embeddings()