"""LLM 统一初始化模块"""
from typing import Optional
from langchain_core.language_models import BaseChatModel

from core.config import (
    OPENAI_API_KEY,
    DASHSCOPE_API_KEY,
    OLLAMA_BASE_URL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_QWEN_MODEL,
    DEFAULT_OLLAMA_MODEL,
)


def get_llm(
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> BaseChatModel:
    """
    获取 LLM 实例

    Args:
        provider: 模型提供商 (openai, qwen, ollama)
        model: 模型名称，默认使用各提供商的默认模型
        temperature: 温度参数
        **kwargs: 其他参数

    Returns:
        BaseChatModel: LangChain 聊天模型实例
    """
    provider = provider.lower()

    if provider == "openai":
        return _get_openai_llm(model or DEFAULT_OPENAI_MODEL, temperature, **kwargs)
    elif provider in ["qwen", "dashscope"]:
        return _get_qwen_llm(model or DEFAULT_QWEN_MODEL, temperature, **kwargs)
    elif provider == "ollama":
        return _get_ollama_llm(model or DEFAULT_OLLAMA_MODEL, temperature, **kwargs)
    else:
        raise ValueError(f"不支持的 provider: {provider}")


def _get_openai_llm(model: str, temperature: float, **kwargs) -> BaseChatModel:
    """初始化 OpenAI LLM"""
    if not OPENAI_API_KEY:
        raise ValueError("未配置 OPENAI_API_KEY，请在 .env 文件中设置")

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=OPENAI_API_KEY,
        **kwargs
    )


def _get_qwen_llm(model: str, temperature: float, **kwargs) -> BaseChatModel:
    """初始化通义千问 LLM"""
    if not DASHSCOPE_API_KEY:
        raise ValueError("未配置 DASHSCOPE_API_KEY，请在 .env 文件中设置")

    from langchain_community.chat_models import ChatTongyi

    return ChatTongyi(
        model=model,
        temperature=temperature,
        dashscope_api_key=DASHSCOPE_API_KEY,
        **kwargs
    )


def _get_ollama_llm(model: str, temperature: float, **kwargs) -> BaseChatModel:
    """初始化 Ollama 本地 LLM"""
    from langchain_community.chat_models import ChatOllama

    return ChatOllama(
        model=model,
        temperature=temperature,
        base_url=OLLAMA_BASE_URL,
        **kwargs
    )


def get_embedding_model(model_name: Optional[str] = None):
    """
    获取 Embedding 模型

    Args:
        model_name: 模型名称，默认使用 config 中的配置

    Returns:
        Embeddings: LangChain Embedding 实例
    """
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from core.config import DEFAULT_EMBEDDING_MODEL

    model_name = model_name or DEFAULT_EMBEDDING_MODEL

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
