"""示例 Skill - 演示如何创建和使用工具"""
from datetime import datetime
from typing import List

from langchain_core.tools import Tool


def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式，如 "1 + 2 * 3"
    """
    try:
        # 安全计算：只允许基本运算符
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含非法字符"
        
        result = eval(expression)
        return f"结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


def search_knowledge(query: str) -> str:
    """
    搜索知识库（示例实现）
    
    Args:
        query: 搜索关键词
    """
    # 这是一个示例，实际使用时应连接真实的知识库
    knowledge_base = {
        "python": "Python 是一种高级编程语言，以简洁易读著称。",
        "langchain": "LangChain 是一个用于构建 LLM 应用的框架。",
        "rag": "RAG (Retrieval-Augmented Generation) 是一种结合检索和生成的技术。",
        "agent": "Agent 是可以自主决策和执行任务的智能体。",
    }
    
    query_lower = query.lower()
    results = []
    
    for key, value in knowledge_base.items():
        if query_lower in key or query_lower in value.lower():
            results.append(f"{key}: {value}")
    
    if results:
        return "\n".join(results)
    return f"未找到与 '{query}' 相关的信息"


def get_tools() -> List[Tool]:
    """
    获取该 skill 提供的所有工具
    
    Returns:
        工具列表
    """
    return [
        Tool(
            name="get_current_time",
            func=lambda x: get_current_time(),
            description="获取当前日期和时间，不需要参数",
        ),
        Tool(
            name="calculate",
            func=calculate,
            description="计算数学表达式，输入如 '1 + 2 * 3'",
        ),
        Tool(
            name="search_knowledge",
            func=search_knowledge,
            description="搜索知识库，输入关键词如 'python' 或 'rag'",
        ),
    ]


# 如果直接运行此文件，演示工具使用
if __name__ == "__main__":
    print("=== 示例 Skill 演示 ===")
    
    tools = get_tools()
    print(f"\n可用工具: {[t.name for t in tools]}")
    
    print(f"\n1. 当前时间: {get_current_time()}")
    print(f"2. 计算 2 + 3 * 4: {calculate('2 + 3 * 4')}")
    print(f"3. 搜索 'python': {search_knowledge('python')}")
