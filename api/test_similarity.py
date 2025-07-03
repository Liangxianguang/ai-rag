#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 /retrieve 接口的相似度阈值过滤效果
"""

import requests
import json

# API 配置
BASE_URL = "http://127.0.0.1:8000"
SIMILARITY_THRESHOLD = 0.65

def test_similarity_filtering():
    """直接测试 /retrieve 接口的相似度阈值过滤功能"""
    
    # 测试用例：不同相关性的问题
    test_cases = [
        {
            "query": "工作时间的规定",
            "should_find_docs": True,
            "description": "高相关性问题 - 应该从知识库找到答案"
        },
        {
            "query": "学医的怎么规划自己学习",
            "should_find_docs": False,
            "description": "低相关性问题 - 不应找到答案，应由前端调用LLM"
        },
        {
            "query": "如何做好吃的火锅",
            "should_find_docs": False,
            "description": "完全无关问题 - 不应找到答案，应由前端调用LLM"
        },
        {
            "query": "劳动合同终止的条件",
            "should_find_docs": True,
            "description": "高相关性问题 - 应该从知识库找到答案"
        },
        {
            "query": "怎么学习编程",
            "should_find_docs": False,
            "description": "无关问题 - 不应找到答案，应由前端调用LLM"
        }
    ]
    
    print("=" * 80)
    print(f"开始测试 /retrieve 接口的相似度阈值过滤功能 (阈值: {SIMILARITY_THRESHOLD})")
    print("=" * 80)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【测试 {i}】{case['description']}")
        print(f"问题：'{case['query']}'")
        expected_behavior = "返回文档" if case['should_find_docs'] else "返回空列表"
        print(f"预期行为：{expected_behavior}")
        print("-" * 60)
        
        try:
            # 发送请求到 /retrieve 接口
            response = requests.post(
                f"{BASE_URL}/retrieve",
                json={
                    "query": case["query"],
                    "top_k": 3,
                    "similarity_threshold": SIMILARITY_THRESHOLD
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("documents", [])
                num_docs = len(documents)
                
                print(f"实际返回文档数量：{num_docs}")
                
                # 检查是否符合预期
                test_passed = (num_docs > 0) if case['should_find_docs'] else (num_docs == 0)

                if test_passed:
                    print("✅ 行为符合预期")
                    success_count += 1
                    
                    if num_docs > 0:
                        print(f"找到 {num_docs} 条相关法条:")
                        for j, doc in enumerate(documents, 1):
                            score = doc.get('score', 0)
                            print(f"  文档{j}: {doc.get('title', '未知')} (相似度: {score:.4f})")
                            if score < SIMILARITY_THRESHOLD:
                                print(f"    ❌ 警告: 返回了低于阈值的文档！")
                                # This case should fail if a below-threshold doc is returned.
                                success_count -=1 
                                break
                    else:
                        print("正确地没有返回任何文档，前端将转而调用LLM。")
                        
                else:
                    print(f"❌ 行为不符合预期 - 期望: '{expected_behavior}', 实际返回了 {num_docs} 个文档")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            print("请确保后端服务 (knowledge_api.py) 正在运行，并且可以从这里访问。")
    
    print("\n" + "=" * 80)
    print(f"测试完成：{success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！相似度阈值过滤在 /retrieve 接口上工作正常！")
    else:
        print(f"⚠️ 有 {total_count - success_count} 个测试未通过，请检查后端逻辑。")


if __name__ == "__main__":
    # 首先检查API是否可达
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 知识库API服务可达，准备开始测试...")
            # 运行测试
            test_similarity_filtering()
        else:
            print(f"❌ 知识库API服务返回异常状态: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到知识库API: {e}")
        print(f"请确保知识库API服务 (knowledge_api.py) 正在 http://127.0.0.1:8000 运行。")
