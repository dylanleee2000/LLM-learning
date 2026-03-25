## ADDED Requirements

### Requirement: Base agent class
agents/base_agent.py SHALL 提供基础 Agent 类：
- 支持 LangGraph StateGraph 构建
- 支持工具（Tools）注册
- 支持记忆（Memory）功能
- 支持流式输出

#### Scenario: Create agent with tools
- **WHEN** 创建 BaseAgent 实例并注册工具
- **THEN** Agent 可以调用工具完成任务

#### Scenario: Run agent
- **WHEN** 调用 agent.run("查询天气")
- **THEN** Agent 执行推理并返回结果

### Requirement: Skills system
agents/skills/ 目录 SHALL 支持：
- 每个 skill 是一个独立 Python 模块
- Skill 包含工具函数和描述
- 支持动态加载 skill

#### Scenario: Load skill
- **WHEN** 从 agents.skills 导入 weather_skill
- **THEN** 可以使用 weather_skill 中的工具函数

#### Scenario: Register skill tools
- **WHEN** 调用 agent.register_skill(weather_skill)
- **THEN** skill 中的所有工具被注册到 Agent
