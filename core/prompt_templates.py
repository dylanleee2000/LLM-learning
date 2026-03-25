"""Prompt 模板库"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_qa_prompt() -> ChatPromptTemplate:
    """通用问答 Prompt"""
    template = """你是一个有用的 AI 助手。请回答用户的问题。

用户问题: {question}

请提供清晰、准确的回答:"""

    return ChatPromptTemplate.from_template(template)


def get_rag_prompt() -> ChatPromptTemplate:
    """RAG 问答 Prompt"""
    template = """基于以下上下文信息回答问题。如果上下文中没有相关信息，请说明无法回答。

上下文:
{context}

问题: {question}

请基于上下文提供准确、简洁的回答:"""

    return ChatPromptTemplate.from_template(template)


def get_agent_system_prompt(tools_description: str = "") -> str:
    """Agent 系统提示词"""
    base_prompt = """你是一个智能助手，可以使用工具帮助用户完成任务。

可用工具:
{tools}

请遵循以下规则:
1. 分析用户请求，判断是否需要使用工具
2. 如果需要工具，使用正确的格式调用
3. 如果不需要工具，直接回答
4. 保持回答简洁、准确

当前对话:
"""
    return base_prompt.format(tools=tools_description)


def get_code_review_prompt() -> ChatPromptTemplate:
    """代码审查 Prompt"""
    template = """请审查以下代码，检查潜在问题和改进建议。

代码:
```python
{code}
```

请从以下方面分析:
1. 代码质量和可读性
2. 潜在的错误或漏洞
3. 性能优化建议
4. 最佳实践遵循情况

审查意见:"""

    return ChatPromptTemplate.from_template(template)


def get_summarize_prompt() -> ChatPromptTemplate:
    """文本总结 Prompt"""
    template = """请对以下文本进行总结。

文本:
{text}

要求:
- 提取关键信息
- 保持简洁
- 使用 bullet points

总结:"""

    return ChatPromptTemplate.from_template(template)


def get_chat_with_history_prompt() -> ChatPromptTemplate:
    """带历史记录的聊天 Prompt"""
    return ChatPromptTemplate.from_messages([
        ("system", "你是一个有用的 AI 助手。请基于对话历史回答用户问题。"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])


def get_test_generation_prompt() -> ChatPromptTemplate:
    """测试用例生成 Prompt"""
    template = """请为以下代码生成测试用例。

代码:
```python
{code}
```

要求:
1. 使用 pytest 框架
2. 覆盖正常情况和边界情况
3. 每个测试用例包含清晰的注释
4. 使用有意义的测试函数名

生成的测试代码:"""

    return ChatPromptTemplate.from_template(template)
