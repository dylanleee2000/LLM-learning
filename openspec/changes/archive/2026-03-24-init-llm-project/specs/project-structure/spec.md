## ADDED Requirements

### Requirement: Project directory structure
项目 SHALL 创建以下目录结构：
- .env - 环境变量配置文件（API Key 等）
- .gitignore - Git 忽略文件
- requirements.txt - Python 依赖
- README.md - 项目说明
- scripts/ - 测试脚本目录
- core/ - 核心模块目录
- rag/ - RAG 相关代码目录
- agents/ - Agent 框架目录
- data/docs/ - 本地文档存储
- outputs/ - 生成结果输出

#### Scenario: Directory initialization
- **WHEN** 执行项目初始化
- **THEN** 所有目录和文件按结构创建

### Requirement: Environment configuration
.env 文件 SHALL 支持配置：
- OPENAI_API_KEY
- DASHSCOPE_API_KEY（通义千问）
- LANGCHAIN_API_KEY（可选）
- LANGCHAIN_TRACING_V2（可选）

#### Scenario: Environment loading
- **WHEN** 加载 core/config.py
- **THEN** 自动从 .env 读取环境变量

### Requirement: Git ignore rules
.gitignore SHALL 忽略：
- .env 文件
- __pycache__/ 目录
- *.pyc 文件
- outputs/ 目录内容
- data/ 目录中的大文件

#### Scenario: Git status check
- **WHEN** 执行 git status
- **THEN** 敏感文件和临时文件不被追踪
