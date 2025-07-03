#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试流式知识库问答API
"""

import requests
import json
import time

# API 配置
BASE_URL = "http://127.0.0.1:8000"

def test_stream_api():
    """测试流式API功能"""
    
    test_cases = [
        {
            "query": "工作时间的规定",
            "description": "高相关性问题 - 应该找到劳动法相关法条"
        },
        {
            "query": "学医的怎么规划自己学习",
            "description": "低相关性问题 - 应该转入LLM并显示思考过程"
        }
    ]
    
    print("=" * 80)
    print("测试流式知识库问答API")
    print("=" * 80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【测试 {i}】{case['description']}")
        print(f"问题：{case['query']}")
        print("-" * 60)
        
        try:
            # 发送流式请求
            response = requests.post(
                f"{BASE_URL}/answer_stream",
                json={
                    "query": case["query"],
                    "top_k": 3,
                    "max_length": 2000
                },
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                print("🔄 开始接收流式响应...")
                
                thinking_content = ""
                answer_content = ""
                sources = []
                method = ""
                
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            
                            if data.get('type') == 'thinking':
                                thinking_content = data.get('content', '')
                                print(f"💭 思考: {thinking_content}")
                                
                            elif data.get('type') == 'answer_start':
                                method = data.get('method', 'unknown')
                                print(f"🤖 开始回答 (方法: {method})")
                                
                            elif data.get('type') == 'answer':
                                content = data.get('content', '')
                                answer_content += content
                                if len(content) > 20:  # 只打印较长的内容块
                                    print(f"📝 内容: {content[:50]}...")
                                
                            elif data.get('type') == 'sources':
                                sources = data.get('sources', [])
                                print(f"📚 来源: {len(sources)} 条")
                                
                            elif data.get('type') == 'done':
                                print("✅ 回答完成")
                                break
                                
                            elif data.get('type') == 'error':
                                print(f"❌ 错误: {data.get('content')}")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON解析错误: {e}")
                            continue
                
                print(f"\n最终结果:")
                print(f"- 处理方法: {method}")
                print(f"- 最后思考: {thinking_content}")
                print(f"- 回答长度: {len(answer_content)} 字符")
                print(f"- 信息来源: {len(sources)} 条")
                
                if sources:
                    print("信息来源详情:")
                    for j, source in enumerate(sources[:3], 1):
                        title = source.get('title', '未知') if isinstance(source, dict) else str(source)
                        print(f"  {j}. {title}")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 60)
        time.sleep(1)  # 间隔1秒

if __name__ == "__main__":
    # 首先检查API是否正常运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 知识库API运行正常")
            health_data = response.json()
            print(f"服务状态: {health_data.get('status')}")
            print(f"LLM状态: {'启用' if health_data.get('llm_enabled') else '禁用'}")
            
            # 运行流式测试
            test_stream_api()
            
        else:
            print(f"❌ 知识库API运行异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 无法连接到知识库API: {e}")
        print("请确保知识库API服务正在运行")
