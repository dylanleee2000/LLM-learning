"""向量存储模块"""
import os
from typing import List, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from core.config import VECTOR_STORE_PATH
from core.llm_init import get_embedding_model


class VectorStore:
    """向量存储封装类 (基于 FAISS)"""

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
        self.index_path = self.persist_directory / f"{collection_name}.faiss"

        self.embedding_model = embedding_model or get_embedding_model()
        self._db = None

    @property
    def db(self) -> FAISS:
        """获取 FAISS 实例（懒加载）"""
        if self._db is None:
            if self.index_path.exists():
                # 加载已有的索引
                self._db = FAISS.load_local(
                    str(self.index_path),
                    self.embedding_model,
                    allow_dangerous_deserialization=True,
                )
            else:
                # 创建空索引
                self._db = None
        return self._db

    def _save(self) -> None:
        """保存索引到磁盘"""
        if self._db is not None:
            self._db.save_local(str(self.index_path))

    def add_documents(self, documents: List[Document]) -> None:
        """
        添加文档到向量存储

        Args:
            documents: 文档列表
        """
        if self._db is None:
            # 首次创建索引
            self._db = FAISS.from_documents(documents, self.embedding_model)
        else:
            self._db.add_documents(documents)
        self._save()

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
        if self._db is None:
            # 首次创建索引
            self._db = FAISS.from_texts(texts, self.embedding_model, metadatas=metadatas)
        else:
            self._db.add_texts(texts, metadatas=metadatas)
        self._save()

    def delete(self, ids: List[str]) -> None:
        """
        删除指定 ID 的文档 (FAISS 不直接支持删除，需要重建索引)

        Args:
            ids: 文档 ID 列表
        """
        if self._db is None:
            return
        
        # FAISS 不直接支持按 ID 删除，这里标记为已删除
        # 实际应用中可能需要重建索引
        for doc_id in ids:
            self._db.delete([doc_id])
        self._save()

    def clear(self) -> None:
        """清空集合中的所有文档"""
        self._db = None
        # 删除索引文件
        if self.index_path.exists():
            import shutil
            shutil.rmtree(self.index_path)

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
            filter_dict: 过滤条件 (FAISS 原生不支持过滤，需要后处理)

        Returns:
            相关文档列表
        """
        if self._db is None:
            return []
        
        results = self._db.similarity_search(query, k=k)
        
        # 简单的后处理过滤
        if filter_dict:
            filtered_results = []
            for doc in results:
                match = True
                for key, value in filter_dict.items():
                    if doc.metadata.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_results.append(doc)
            return filtered_results
        
        return results

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
        if self._db is None:
            return []
        
        results = self._db.similarity_search_with_score(query, k=k)
        
        # 简单的后处理过滤
        if filter_dict:
            filtered_results = []
            for doc, score in results:
                match = True
                for key, value in filter_dict.items():
                    if doc.metadata.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_results.append((doc, score))
            return filtered_results
        
        return results

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
        if self._db is None:
            return []
        
        return self._db.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
        )

    def get_collection_stats(self) -> dict:
        """获取集合统计信息"""
        doc_count = 0
        if self._db is not None and hasattr(self._db, 'index'):
            doc_count = self._db.index.ntotal
        return {
            "collection_name": self.collection_name,
            "document_count": doc_count,
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
