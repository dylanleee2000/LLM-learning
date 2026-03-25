"""文本分块模块"""
from typing import List, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separator: str = "\n"
) -> List[str]:
    """
    将文本分块

    Args:
        text: 输入文本
        chunk_size: 每块大小（字符数）
        chunk_overlap: 块间重叠大小
        separator: 分隔符

    Returns:
        分块后的文本列表
    """
    splitter = CharacterTextSplitter(
        separator=separator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_text(text)


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    将文档列表分块

    Args:
        documents: 文档列表
        chunk_size: 每块大小
        chunk_overlap: 块间重叠大小

    Returns:
        分块后的文档列表
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "。", "，", " ", ""],
    )
    return splitter.split_documents(documents)


def load_text_file(file_path: str) -> List[Document]:
    """
    加载文本文件

    Args:
        file_path: 文件路径

    Returns:
        文档列表
    """
    from langchain_community.document_loaders import TextLoader

    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()


def load_pdf_file(file_path: str) -> List[Document]:
    """
    加载 PDF 文件

    Args:
        file_path: 文件路径

    Returns:
        文档列表
    """
    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader(file_path)
    return loader.load()


def load_markdown_file(file_path: str) -> List[Document]:
    """
    加载 Markdown 文件

    Args:
        file_path: 文件路径

    Returns:
        文档列表
    """
    from langchain_community.document_loaders import UnstructuredMarkdownLoader

    loader = UnstructuredMarkdownLoader(file_path)
    return loader.load()


def load_and_chunk_file(
    file_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    加载文件并分块

    Args:
        file_path: 文件路径
        chunk_size: 每块大小
        chunk_overlap: 块间重叠大小

    Returns:
        分块后的文档列表
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    # 根据文件类型选择加载器
    if suffix == ".pdf":
        documents = load_pdf_file(file_path)
    elif suffix in [".md", ".markdown"]:
        documents = load_markdown_file(file_path)
    elif suffix in [".txt", ".py", ".json", ".yaml", ".yml"]:
        documents = load_text_file(file_path)
    else:
        # 默认使用文本加载器
        documents = load_text_file(file_path)

    # 分块
    return chunk_documents(documents, chunk_size, chunk_overlap)


def load_directory(
    directory: str,
    glob_pattern: str = "**/*",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    加载目录中的所有文件并分块

    Args:
        directory: 目录路径
        glob_pattern: 文件匹配模式
        chunk_size: 每块大小
        chunk_overlap: 块间重叠大小

    Returns:
        分块后的文档列表
    """
    from langchain_community.document_loaders import DirectoryLoader

    loader = DirectoryLoader(
        directory,
        glob=glob_pattern,
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    documents = loader.load()
    return chunk_documents(documents, chunk_size, chunk_overlap)
