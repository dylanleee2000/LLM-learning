"""向量存储模块"""
from typing import List, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain_chroma import Chroma

from core.config import VECTOR_STORE_PATH
from core.llm_init import get_embedding_model


class VectorStore:
    """向量存储封装类"""

    def __init__(
        self,
        collection_name: str = "default",
        persist_directory: Optional[str] = None,
        embedding_model=None,
    ):
        """
        初始化向量存储

        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录
            embedding_model: Embedding 模型
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory or VECTOR_STORE_PATH)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.embedding_model = embedding_model or get_embedding_model()
        self._db = None

    @property
    def db(self) -> Chroma:
        """获取 Chroma 实例（懒加载）"""
        if self._db is None:
            self._db = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
                persist_directory=str(self.persist_directory),
            )
        return self._db

    def add_documents(self, documents: List[Document]) -> None:
        """
        添加文档到向量存储

        Args:
            documents: 文档列表
        """
        self.db.add_documents(documents)

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> None:
        """
        添加文本到向量存储

        Args:
            texts: 文本列表
            metadatas: 元数据列表
        """
        self.db.add_texts(texts, metadatas=metadatas)

    def delete(self, ids: List[str]) -> None:
        """
        删除指定 ID 的文档

        Args:
            ids: 文档 ID 列表
        """
        self.db.delete(ids=ids)

    def clear(self) -> None:
        """清空集合中的所有文档"""
        self.db.delete_collection()
        self._db = None  # 重置，下次访问时重新创建

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[dict] = None,
    ) -> List[Document]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            filter_dict: 过滤条件

        Returns:
            相关文档列表
        """
        return self.db.similarity_search(
            query,
            k=k,
            filter=filter_dict,
        )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[dict] = None,
    ) -> List[tuple]:
        """
        相似度搜索（带分数）

        Args:
            query: 查询文本
            k: 返回结果数量
            filter_dict: 过滤条件

        Returns:
            (文档, 分数) 元组列表
        """
        return self.db.similarity_search_with_score(
            query,
            k=k,
            filter=filter_dict,
        )

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
    ) -> List[Document]:
        """
        MMR（最大边际相关性）搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            fetch_k: 初始检索数量
            lambda_mult: 多样性参数（0-1，越大越关注相关性）

        Returns:
            相关文档列表
        """
        return self.db.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
        )

    def get_collection_stats(self) -> dict:
        """获取集合统计信息"""
        return {
            "collection_name": self.collection_name,
            "document_count": self.db._collection.count(),
            "persist_directory": str(self.persist_directory),
        }


def create_vector_store(
    collection_name: str = "default",
    persist_directory: Optional[str] = None,
    embedding_model=None,
) -> VectorStore:
    """
    创建向量存储实例

    Args:
        collection_name: 集合名称
        persist_directory: 持久化目录
        embedding_model: Embedding 模型

    Returns:
        VectorStore 实例
    """
    return VectorStore(
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding_model=embedding_model,
    )
