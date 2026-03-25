## ADDED Requirements

### Requirement: LLM initialization module
core/llm_init.py SHALL 提供统一接口初始化不同 LLM：
- OpenAI (gpt-4, gpt-3.5-turbo)
- 通义千问 (qwen系列)
- Ollama (本地模型)

#### Scenario: Initialize OpenAI model
- **WHEN** 调用 get_llm("openai", model="gpt-4")
- **THEN** 返回配置好的 ChatOpenAI 实例

#### Scenario: Initialize Qwen model
- **WHEN** 调用 get_llm("qwen", model="qwen-turbo")
- **THEN** 返回配置好的 ChatTongyi 实例

#### Scenario: Initialize Ollama model
- **WHEN** 调用 get_llm("ollama", model="llama2")
- **THEN** 返回配置好的 ChatOllama 实例

### Requirement: Prompt templates library
core/prompt_templates.py SHALL 提供常用 Prompt 模板：
- 通用问答模板
- RAG 问答模板
- Agent 系统提示词模板
- 代码审查模板

#### Scenario: Get RAG prompt
- **WHEN** 调用 get_rag_prompt()
- **THEN** 返回包含 context 和 question 占位符的 ChatPromptTemplate

#### Scenario: Get agent system prompt
- **WHEN** 调用 get_agent_system_prompt(tools_description)
- **THEN** 返回包含工具描述的系统提示词

### Requirement: Global configuration
core/config.py SHALL 提供：
- 项目根目录路径
- 数据目录路径
- 输出目录路径
- 默认模型配置
- 日志配置

#### Scenario: Get project paths
- **WHEN** 导入 config 模块
- **THEN** 可以使用 config.PROJECT_ROOT, config.DATA_DIR 等路径常量
