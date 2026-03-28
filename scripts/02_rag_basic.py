"""
示例 2: RAG Basic
RAG (检索增强生成) 基础示例，演示完整的 RAG 流程
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_init import get_llm
from core.config import check_api_key
from rag.chunker import chunk_text
from rag.vector_store import create_vector_store
from rag.retriever import create_retriever, RAGChain
from core.prompt_templates import get_rag_prompt


def create_sample_documents():
    """创建示例文档"""
    docs = [
        """Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。
        它以简洁、易读的语法著称，使用缩进来表示代码块。
        Python 支持多种编程范式，包括面向对象、函数式和过程式编程。""",

        """LangChain 是一个用于构建基于大语言模型应用的框架。
        它提供了组件化的方式，帮助开发者轻松构建复杂的 LLM 应用。
        主要功能包括：Prompt 管理、链式调用、数据增强生成、Agent 等。""",

        """RAG (Retrieval-Augmented Generation) 是一种结合检索和生成的技术。
        它首先从知识库中检索相关信息，然后将这些信息作为上下文提供给 LLM 生成回答。
        RAG 可以有效减少幻觉，提高回答的准确性和可解释性。""",

        """向量数据库是专门用于存储和检索向量数据的数据库。
        它将文本转换为高维向量（embedding），通过向量相似度搜索找到相关内容。
        常用的向量数据库包括 FAISS、Chroma、Pinecone、Weaviate 等。""",

        """Embedding 是将文本、图像等数据转换为数值向量的技术。
        语义相似的文本在向量空间中距离较近。
        常用的文本 Embedding 模型有 OpenAI Ada、BGE、M3E 等。""",
    ]
    return docs


def main():
    print("=" * 60)
    print("🔍 RAG Basic - 检索增强生成示例")
    print("=" * 60)

    # 检查 API Key
    provider = "qwen"
    if not check_api_key(provider):
        print(f"\n⚠️  未配置 {provider} 的 API Key")
        print("尝试使用 Ollama...")
        provider = "ollama"

    try:
        # 步骤 1: 准备文档
        print("\n📄 步骤 1: 准备示例文档")
        raw_docs = create_sample_documents()
        print(f"   创建了 {len(raw_docs)} 篇示例文档")

        # 步骤 2: 文档分块
        print("\n✂️  步骤 2: 文档分块")
        all_chunks = []
        for i, doc in enumerate(raw_docs):
            chunks = chunk_text(doc, chunk_size=200, chunk_overlap=20)
            all_chunks.extend(chunks)
            print(f"   文档 {i+1}: 分成 {len(chunks)} 块")
        print(f"   总计: {len(all_chunks)} 个文本块")

        # 步骤 3: 创建向量存储
        print("\n🗄️  步骤 3: 创建向量存储")
        print("   初始化 FAISS 向量库 (首次运行会下载 embedding 模型)...")
        vector_store = create_vector_store(collection_name="demo")

        # 添加文档
        from langchain_core.documents import Document
        documents = [Document(page_content=chunk) for chunk in all_chunks]
        vector_store.add_documents(documents)
        print(f"   ✓ 已存储 {len(documents)} 个文档向量")

        # 步骤 4: 创建检索器
        print("\n🔎 步骤 4: 创建检索器")
        retriever = create_retriever(vector_store)

        # 步骤 5: 测试检索
        print("\n🧪 步骤 5: 测试检索")
        test_queries = [
            "什么是 Python？",
            "RAG 技术是什么？",
        ]

        for query in test_queries:
            print(f"\n   查询: {query}")
            results = retriever.retrieve_with_scores(query, top_k=2)
            for i, result in enumerate(results, 1):
                print(f"   [{i}] 相似度: {result.score:.3f}")
                print(f"       {result.document.page_content[:80]}...")

        # 步骤 6: RAG 问答
        print("\n" + "-" * 60)
        print("🤖 步骤 6: RAG 问答演示")
        print("-" * 60)

        # 初始化 LLM
        llm = get_llm(provider=provider, temperature=0.7)

        # 创建 RAG 链
        rag_prompt = get_rag_prompt()
        rag_chain = RAGChain(retriever, llm, rag_prompt)

        questions = [
            "Python 是谁创建的？它有什么特点？",
            "RAG 和传统的 LLM 生成有什么区别？",
            "什么是 embedding，它有什么作用？",
        ]

        for question in questions:
            print(f"\n❓ 问题: {question}")
            print("\n⏳ 检索并生成回答...")

            result = rag_chain.query(question, top_k=3, return_context=True)

            print(f"\n💡 回答:\n{result['answer']}")
            print(f"\n📚 参考来源:")
            for i, source in enumerate(result['sources'][:2], 1):
                print(f"   [{i}] {source}")
            print("-" * 60)

        # 清理
        print("\n🧹 清理向量存储...")
        vector_store.clear()

        print("\n" + "=" * 60)
        print("✅ RAG 示例运行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
