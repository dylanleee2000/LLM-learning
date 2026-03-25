## Why

当前目录为空，需要一个结构化的 LLM 学习项目框架来组织日常 Python 脚本学习。通过建立清晰的目录结构和可复用的核心模块，可以高效地学习和实验 LLM 相关技术（RAG、Agent、Prompt 工程等）。

## What Changes

- 创建项目基础配置文件（.env、.gitignore、requirements.txt、README.md）
- 创建 scripts/ 目录存放日常学习脚本
- 创建 core/ 目录存放可复用的核心模块（LLM 初始化、Prompt 模板、配置）
- 创建 rag/ 目录存放 RAG 相关实现（分块、向量存储、检索器）
- 创建 agents/ 目录存放 LangGraph Agent 框架
- 创建 data/ 和 outputs/ 目录用于数据存储和结果输出

## Capabilities

### New Capabilities
- `project-structure`: 项目目录结构初始化
- `core-modules`: 核心模块（LLM 初始化、Prompt 模板、配置）
- `rag-modules`: RAG 模块（分块、向量存储、检索器）
- `agent-framework`: Agent 框架（基础 Agent、技能系统）
- `demo-scripts`: 示例脚本（Hello LLM、RAG 基础、LangGraph Agent、自动化测试）

### Modified Capabilities
- 无

## Impact

- 新增 Python 依赖（langchain、langgraph、openai 等）
- 需要配置 API Key 环境变量
- 建立代码组织规范，便于后续扩展
