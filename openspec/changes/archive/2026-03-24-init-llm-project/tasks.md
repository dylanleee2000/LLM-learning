## 1. 项目基础配置

- [x] 1.1 创建 .env.example 文件（包含所有需要的 API Key 占位符）
- [x] 1.2 创建 .gitignore 文件（忽略 .env、__pycache__、outputs 等）
- [x] 1.3 创建 requirements.txt（langchain、langgraph、chromadb、openai 等依赖）
- [x] 1.4 创建 README.md（项目说明、安装步骤、使用方法）

## 2. 核心模块实现

- [x] 2.1 创建 core/config.py（项目路径、环境变量加载、日志配置）
- [x] 2.2 创建 core/llm_init.py（OpenAI、通义千问、Ollama 统一初始化接口）
- [x] 2.3 创建 core/prompt_templates.py（RAG、Agent、通用问答 Prompt 模板）

## 3. RAG 模块实现

- [x] 3.1 创建 rag/chunker.py（文本分块、PDF 加载、多种分块策略）
- [x] 3.2 创建 rag/vector_store.py（ChromaDB 封装、文档增删、持久化）
- [x] 3.3 创建 rag/retriever.py（相似度搜索、MMR 搜索、结果排序）

## 4. Agent 框架实现

- [x] 4.1 创建 agents/base_agent.py（LangGraph StateGraph 基础 Agent 类）
- [x] 4.2 创建 agents/skills/__init__.py（skills 包初始化）
- [x] 4.3 创建 agents/skills/example_skill.py（示例 skill，演示工具注册）

## 5. 示例脚本实现

- [x] 5.1 创建 scripts/01_hello_llm.py（基础 LLM 调用示例）
- [x] 5.2 创建 scripts/02_rag_basic.py（RAG 完整流程示例）
- [x] 5.3 创建 scripts/03_langgraph_agent.py（Agent 工具调用示例）
- [x] 5.4 创建 scripts/04_auto_test.py（LLM 生成测试用例示例）

## 6. 目录结构初始化

- [x] 6.1 创建 scripts/ 目录
- [x] 6.2 创建 core/ 目录
- [x] 6.3 创建 rag/ 目录
- [x] 6.4 创建 agents/ 目录
- [x] 6.5 创建 agents/skills/ 目录
- [x] 6.6 创建 data/docs/ 目录
- [x] 6.7 创建 outputs/ 目录
