"""检索器模块"""
from typing import List, Optional
from dataclasses import dataclass

from langchain_core.documents import Document

from rag.vector_store import VectorStore


@dataclass
class RetrievalResult:
    """检索结果"""
    document: Document
    score: Optional[float] = None


class Retriever:
    """检索器类"""

    def __init__(self, vector_store: VectorStore):
        """
        初始化检索器

        Args:
            vector_store: 向量存储实例
        """
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[dict] = None,
    ) -> List[RetrievalResult]:
        """
        检索相关文档

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_dict: 过滤条件

        Returns:
            检索结果列表
        """
        documents = self.vector_store.similarity_search(
            query,
            k=top_k,
            filter_dict=filter_dict,
        )
        return [RetrievalResult(doc) for doc in documents]

    def retrieve_with_scores(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[dict] = None,
    ) -> List[RetrievalResult]:
        """
        检索相关文档（带相似度分数）

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_dict: 过滤条件

        Returns:
            带分数的检索结果列表
        """
        results = self.vector_store.similarity_search_with_score(
            query,
            k=top_k,
            filter_dict=filter_dict,
        )
        return [RetrievalResult(doc, score) for doc, score in results]

    def retrieve_with_mmr(
        self,
        query: str,
        top_k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
    ) -> List[RetrievalResult]:
        """
        使用 MMR 算法检索（保证结果多样性）

        Args:
            query: 查询文本
            top_k: 返回结果数量
            fetch_k: 初始检索数量
            lambda_mult: 多样性参数（0-1，越大越关注相关性）

        Returns:
            检索结果列表
        """
        documents = self.vector_store.max_marginal_relevance_search(
            query,
            k=top_k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
        )
        return [RetrievalResult(doc) for doc in documents]

    def format_context(
        self,
        results: List[RetrievalResult],
        include_scores: bool = False,
    ) -> str:
        """
        将检索结果格式化为上下文字符串

        Args:
            results: 检索结果列表
            include_scores: 是否包含相似度分数

        Returns:
            格式化后的上下文
        """
        contexts = []
        for i, result in enumerate(results, 1):
            text = result.document.page_content
            if include_scores and result.score is not None:
                contexts.append(f"[{i}] (相似度: {result.score:.3f})\n{text}")
            else:
                contexts.append(f"[{i}]\n{text}")
        return "\n\n---\n\n".join(contexts)


class RAGChain:
    """RAG 链（检索 + 生成）"""

    def __init__(
        self,
        retriever: Retriever,
        llm,
        prompt_template=None,
    ):
        """
        初始化 RAG 链

        Args:
            retriever: 检索器
            llm: LLM 实例
            prompt_template: Prompt 模板
        """
        self.retriever = retriever
        self.llm = llm
        self.prompt_template = prompt_template

    def query(
        self,
        question: str,
        top_k: int = 5,
        return_context: bool = False,
    ) -> dict:
        """
        执行 RAG 查询

        Args:
            question: 问题
            top_k: 检索文档数量
            return_context: 是否返回检索上下文

        Returns:
            包含 answer 和可选 context 的字典
        """
        # 检索相关文档
        results = self.retriever.retrieve(question, top_k=top_k)
        context = self.retriever.format_context(results)

        # 构建 Prompt
        if self.prompt_template:
            prompt = self.prompt_template.format(
                context=context,
                question=question,
            )
        else:
            prompt = f"基于以下上下文回答问题：\n\n上下文：\n{context}\n\n问题：{question}\n\n回答："

        # 生成回答
        response = self.llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)

        result = {"answer": answer}
        if return_context:
            result["context"] = context
            result["sources"] = [r.document.metadata for r in results]

        return result


def create_retriever(vector_store: VectorStore) -> Retriever:
    """
    创建检索器

    Args:
        vector_store: 向量存储实例

    Returns:
        Retriever 实例
    """
    return Retriever(vector_store)
