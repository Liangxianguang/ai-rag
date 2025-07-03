#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证相似度阈值修复效果
"""

import requests
import json

# API 配置
BASE_URL = "http://127.0.0.1:8000"

def test_fixed_similarity_threshold():
    """测试修复后的相似度阈值功能"""
    
    # 测试用例：不同相关性的问题
    test_cases = [
        {
            "query": "工作时间的规定",
            "expected": "knowledge_base_direct",  # 应该找到相关法条
            "description": "高相关性问题 - 劳动法相关"
        },
        {
            "query": "学医的怎么规划自己学习",
            "expected": "llm_fallback",    # 应该转入LLM
            "description": "低相关性问题 - 与劳动法无关"
        },
        {
            "query": "如何做好吃的火锅",
            "expected": "llm_fallback",    # 应该转入LLM
            "description": "完全无关问题 - 与劳动法无关"
        },
        {
            "query": "劳动合同终止的条件",
            "expected": "knowledge_base_direct",  # 应该找到相关法条
            "description": "高相关性问题 - 劳动法相关"
        },
        {
            "query": "怎么学习编程",
            "expected": "llm_fallback",    # 应该转入LLM
            "description": "无关问题 - 与劳动法无关"
        }
    ]
    
    print("=" * 80)
    print("测试修复后的相似度阈值功能 (阈值: 0.65)")
    print("=" * 80)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【测试 {i}】{case['description']}")
        print(f"问题：{case['query']}")
        print(f"预期：{case['expected']}")
        print("-" * 60)
        
        try:
            # 发送请求
            response = requests.post(
                f"{BASE_URL}/answer",
                json={
                    "query": case["query"],
                    "top_k": 3,
                    "max_length": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                method = data.get("method", "unknown")
                answer = data.get("answer", "")
                sources = data.get("sources", [])
                
                print(f"实际结果：{method}")
                
                # 检查是否符合预期
                if case["expected"] == method:
                    print("✅ 符合预期")
                    success_count += 1
                    
                    if method == "knowledge_base_direct":
                        print(f"找到 {len(sources)} 条相关法条")
                        if sources:
                            for j, source in enumerate(sources, 1):
                                score = source.get('score', 0)
                                print(f"  法条{j}: {source.get('title', '未知')} (相似度: {score:.4f})")
                    elif method == "llm_fallback":
                        print("成功转入LLM智能回答")
                        
                else:
                    print(f"❌ 不符合预期 - 期望:{case['expected']}, 实际:{method}")
                
                # 显示答案片段
                answer_preview = answer[:200] + "..." if len(answer) > 200 else answer
                print(f"\n回答预览：\n{answer_preview}")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 80)
    print(f"测试完成：{success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！相似度阈值过滤工作正常！")
    else:
        print(f"⚠️ 有 {total_count - success_count} 个测试未通过，需要进一步调试")

def quick_test():
    """快速测试两个关键用例"""
    print("\n" + "=" * 80)
    print("快速验证关键用例")
    print("=" * 80)
    
    test_queries = [
        ("工作时间规定", "应该使用知识库"),
        ("学医规划", "应该使用LLM")
    ]
    
    for query, expected_behavior in test_queries:
        print(f"\n测试查询: {query} ({expected_behavior})")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{BASE_URL}/answer",
                json={"query": query, "top_k": 3},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                method = data.get("method", "unknown")
                print(f"处理方式: {method}")
                
                if "工作时间" in query and method == "knowledge_base_direct":
                    print("✅ 正确 - 高相关性问题使用知识库")
                elif "学医" in query and method == "llm_fallback":
                    print("✅ 正确 - 低相关性问题转入LLM")
                else:
                    print(f"❌ 可能有问题 - {query} → {method}")
                    
            else:
                print(f"请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"请求异常: {e}")

if __name__ == "__main__":
    # 首先检查API是否正常运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 知识库API运行正常")
            health_data = response.json()
            print(f"服务状态: {health_data.get('status')}")
            print(f"LLM状态: {'启用' if health_data.get('llm_enabled') else '禁用'}")
            
            # 运行测试
            test_fixed_similarity_threshold()
            quick_test()
            
        else:
            print(f"❌ 知识库API运行异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 无法连接到知识库API: {e}")
        print("请确保知识库API服务正在运行")
