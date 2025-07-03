#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试知识库 API 的简单脚本
"""

import requests
import json
import time

def test_knowledge_api():
    """测试知识库 API"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试知识库检索 API")
    print("="*50)
    
    # 1. 健康检查
    print("1. 检查服务状态...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务正常运行")
            print(f"📊 服务状态: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 服务异常: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务: {e}")
        print("请确保知识库 API 服务已启动（python api/knowledge_api.py）")
        return
    
    print("\n" + "="*50)
    
    # 2. 测试知识库检索
    print("2. 测试知识库检索...")
    test_queries = [
        "劳动合同的相关规定是什么？",
        "工作时间有什么限制？",
        "劳动者的权利有哪些？",
        "用人单位的义务包括什么？"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 测试查询 {i}: {query}")
        
        try:
            # 发送检索请求
            payload = {
                "query": query,
                "top_k": 3,
                "max_length": 1000
            }
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/retrieve", 
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 检索成功 (耗时: {end_time - start_time:.2f}s)")
                print(f"📚 找到 {result['total']} 条相关文档:")
                
                for j, doc in enumerate(result['documents'], 1):
                    print(f"\n   📄 文档 {j}:")
                    print(f"   标题: {doc.get('title', '未知')}")
                    print(f"   来源: {doc.get('source', '未知')}")
                    print(f"   内容: {doc['content'][:100]}...")
                    if doc.get('score'):
                        print(f"   相似度: {doc['score']:.3f}")
            else:
                print(f"❌ 检索失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
    
    print("\n" + "="*50)
    print("🎉 测试完成！")
    
    # 3. 显示使用建议
    print("\n💡 使用建议:")
    print("1. 启动前端服务: npm run dev")
    print("2. 在前端设置中启用'知识库检索'")
    print("3. 开始与 AI 对话，所有回答将基于知识库内容")

if __name__ == "__main__":
    test_knowledge_api()
