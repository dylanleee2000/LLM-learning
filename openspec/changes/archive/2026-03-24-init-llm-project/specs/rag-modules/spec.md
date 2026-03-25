## ADDED Requirements

### Requirement: Text chunking module
rag/chunker.py SHALL 提供文本分块功能：
- 支持按字符数分块
- 支持按 Token 数分块
- 支持重叠分块（overlap）
- 支持多种文档格式（txt, pdf, md）

#### Scenario: Chunk text by characters
- **WHEN** 调用 chunk_text(text, chunk_size=500, overlap=50)
- **THEN** 返回分块后的文本列表，每块约 500 字符，重叠 50 字符

#### Scenario: Load and chunk PDF
- **WHEN** 调用 load_and_chunk_pdf(file_path)
- **THEN** 返回从 PDF 提取并分块后的文档列表

### Requirement: Vector store module
rag/vector_store.py SHALL 提供向量存储功能：
- 使用 ChromaDB 作为后端
- 支持文档添加和删除
- 支持持久化到本地
- 支持多种 embedding 模型

#### Scenario: Create vector store
- **WHEN** 调用 create_vector_store(collection_name, embedding_model)
- **THEN** 返回配置好的 Chroma 向量存储实例

#### Scenario: Add documents
- **WHEN** 调用 vector_store.add_documents(docs)
- **THEN** 文档被向量化并存储

### Requirement: Retriever module
rag/retriever.py SHALL 提供检索功能：
- 相似度搜索
- MMR（最大边际相关性）搜索
- 支持过滤条件
- 返回带分数的结果

#### Scenario: Similarity search
- **WHEN** 调用 retriever.retrieve(query, top_k=5)
- **THEN** 返回与 query 最相关的 top_k 个文档

#### Scenario: MMR search
- **WHEN** 调用 retriever.retrieve_with_mmr(query, top_k=5, fetch_k=20)
- **THEN** 返回多样性优化的 top_k 个文档
