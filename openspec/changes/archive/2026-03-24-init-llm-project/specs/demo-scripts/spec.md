## ADDED Requirements

### Requirement: Hello LLM script
scripts/01_hello_llm.py SHALL 演示：
- 加载环境变量
- 初始化 LLM
- 进行简单对话

#### Scenario: Run hello script
- **WHEN** 运行 python scripts/01_hello_llm.py
- **THEN** 输出 LLM 对 "你好，请介绍一下自己" 的回复

### Requirement: RAG basic script
scripts/02_rag_basic.py SHALL 演示：
- 加载文档
- 创建向量存储
- 执行 RAG 检索和问答

#### Scenario: Run RAG demo
- **WHEN** 运行 python scripts/02_rag_basic.py
- **THEN** 演示完整的 RAG 流程，包括文档加载、索引、检索、生成

### Requirement: LangGraph agent script
scripts/03_langgraph_agent.py SHALL 演示：
- 创建简单 Agent
- 注册工具
- 执行多步任务

#### Scenario: Run agent demo
- **WHEN** 运行 python scripts/03_langgraph_agent.py
- **THEN** Agent 完成一个需要工具调用的任务

### Requirement: Auto test script
scripts/04_auto_test.py SHALL 演示：
- 使用 LLM 生成测试用例
- 执行代码测试
- 输出测试报告

#### Scenario: Run auto test demo
- **WHEN** 运行 python scripts/04_auto_test.py
- **THEN** 生成并展示自动化测试示例
