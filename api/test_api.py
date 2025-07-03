#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试知识库检索 API
"""

import requests
import json

# API 配置
API_BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print("健康检查结果:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_retrieve(query="劳动者的权利有哪些？"):
    """测试知识库检索接口"""
    try:
        payload = {
            "query": query,
            "top_k": 3,
            "max_length": 1000
        }
        
        response = requests.post(f"{API_BASE_URL}/retrieve", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n检索查询: {query}")
            print(f"找到 {result['total']} 条相关文档:")
            
            for i, doc in enumerate(result['documents'], 1):
                print(f"\n文档 {i}:")
                print(f"标题: {doc['title']}")
                print(f"来源: {doc['source']}")
                print(f"内容: {doc['content'][:200]}...")
                if doc['score']:
                    print(f"相似度: {doc['score']:.4f}")
            
            return True
        else:
            print(f"检索失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"检索测试失败: {e}")
        return False

def test_collections():
    """测试集合列表接口"""
    try:
        response = requests.get(f"{API_BASE_URL}/collections")
        print("\n可用集合:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.status_code == 200
    except Exception as e:
        print(f"集合列表获取失败: {e}")
        return False

def test_answer(query="劳动者的权利有哪些？"):
    """测试知识库问答接口（后端直接生成答案）"""
    try:
        payload = {
            "query": query,
            "top_k": 3,
            "max_length": 1000
        }
        
        response = requests.post(f"{API_BASE_URL}/answer", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n问答查询: {query}")
            print(f"生成方式: {result['method']}")
            print(f"答案:\n{result['answer']}")
            
            if result['sources']:
                print(f"\n信息来源 ({len(result['sources'])} 条):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"{i}. {source['title']} (来源: {source['source']})")
                    if source.get('score'):
                        print(f"   相似度: {source['score']:.4f}")
            
            return True
        else:
            print(f"问答失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"问答测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("知识库检索 API 测试")
    print("=" * 50)
    
    # 测试健康检查
    if test_health():
        print("✓ 健康检查通过")
    else:
        print("✗ 健康检查失败")
        exit(1)
    
    # 测试集合列表
    if test_collections():
        print("✓ 集合列表获取成功")
    else:
        print("✗ 集合列表获取失败")
    
    # 测试检索功能
    test_queries = [
        "劳动者的权利有哪些？",
        "工作时间的规定",
        "劳动合同应该包含什么内容？",
        "女职工保护的相关规定"
    ]
    
    for query in test_queries:
        if test_retrieve(query):
            print(f"✓ 查询 '{query}' 成功")
        else:
            print(f"✗ 查询 '{query}' 失败")
    
    # 测试问答功能
    test_queries_qa = [
        "劳动者的权利有哪些？",
        "工作时间的规定",
        "劳动合同应该包含什么内容？",
        "女职工保护的相关规定"
    ]
    
    for query in test_queries_qa:
        if test_answer(query):
            print(f"✓ 问答 '{query}' 成功")
        else:
            print(f"✗ 问答 '{query}' 失败")
    
    print("\n" + "=" * 50)
    print("测试完成")
