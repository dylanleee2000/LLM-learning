# LLM 学习项目

个人 LLM 技术学习与实践的 Python 项目，包含 RAG、Agent、Prompt Engineering 等实验代码。

## 项目结构

```
├── .env                       # 密钥配置（不提交 git）
├── .gitignore                 # 忽略文件
├── requirements.txt           # Python 依赖
├── README.md                  # 项目说明
│
├── scripts/                   # 日常学习脚本
│   ├── 01_hello_llm.py       # 基础 LLM 调用
│   ├── 02_rag_basic.py       # RAG 基础示例
│   ├── 03_langgraph_agent.py # Agent 示例
│   └── 04_auto_test.py       # 自动化测试示例
│
├── core/                      # 可复用核心代码
│   ├── llm_init.py           # LLM 统一初始化
│   ├── prompt_templates.py   # Prompt 模板库
│   └── config.py             # 全局配置
│
├── rag/                       # RAG 相关代码
│   ├── chunker.py            # 文本分块
│   ├── vector_store.py       # 向量存储
│   └── retriever.py          # 检索器
│
├── agents/                    # LangGraph Agent
│   ├── base_agent.py         # 基础 Agent 类
│   └── skills/               # 各种技能
│
├── data/                      # 本地数据
│   └── docs/                 # 文档存储
│
└── outputs/                   # 生成结果
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 3. 运行示例

```bash
python scripts/01_hello_llm.py
```

## 支持的模型

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **通义千问**: qwen-turbo, qwen-plus, qwen-max
- **Ollama**: 本地模型（需自行安装 Ollama）

## 学习路线

1. **基础**: 运行 `01_hello_llm.py` 了解 LLM 调用
2. **RAG**: 运行 `02_rag_basic.py` 学习检索增强生成
3. **Agent**: 运行 `03_langgraph_agent.py` 体验智能体
4. **实战**: 修改示例代码，实现自己的功能

## 注意事项

- 不要将 `.env` 文件提交到 git
- API Key 请妥善保管
- 大文件请放在 `data/` 目录，该目录已被 git 忽略
