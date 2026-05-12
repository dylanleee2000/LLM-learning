"""全局配置模块"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = DATA_DIR / "docs"

# 输出目录
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY")
MIMO_API_KEY = os.getenv("MIMO_API_KEY")

# LangSmith 配置
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "llm-learning")

# Ollama 配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 默认模型配置
DEFAULT_MODEL_PROVIDER = "openai"  # 可选: openai, qwen, ollama, mimo
DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
DEFAULT_QWEN_MODEL = "qwen-turbo"
DEFAULT_OLLAMA_MODEL = "llama2"
DEFAULT_MIMO_MODEL = "mimo-v2-pro"

# MiMo API 配置
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")

# 向量存储配置
VECTOR_STORE_PATH = PROJECT_ROOT / ".faiss"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"  # 中文 embedding 模型


def get_api_key(provider: str) -> str:
    """获取指定 provider 的 API Key"""
    keys = {
        # "openai": OPENAI_API_KEY,
        #"qwen": DASHSCOPE_API_KEY,
        # "dashscope": DASHSCOPE_API_KEY,
        # "volcano": VOLCANO_API_KEY,
        "mimo": MIMO_API_KEY,
    }
    return keys.get(provider.lower())


def check_api_key(provider: str) -> bool:
    """检查指定 provider 的 API Key 是否配置"""
    return bool(get_api_key(provider))
