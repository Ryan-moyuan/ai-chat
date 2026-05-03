"""RAG 引擎 - 文档索引与语义检索"""
import os

# 延迟导入 chromadb，避免打包问题
_chroma_client = None
CHROMA_PERSIST_DIR = None


def _get_collection():
    global _chroma_client, CHROMA_PERSIST_DIR
    if _chroma_client is None:
        import chromadb
        from config_loader import CHROMA_DIR
        CHROMA_PERSIST_DIR = os.path.join(CHROMA_DIR, "store")
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _chroma_client.get_or_create_collection("knowledge_base")


def load_document(file_path):
    """
    加载文档到知识库
    支持: .txt, .pdf, .docx
    返回: 分块数量
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raise ImportError("请安装 pypdf: pip install pypdf")
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

    # 分块
    chunk_size = 500
    overlap = 50
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)

    if not chunks:
        return 0

    # 存储
    collection = _get_collection()
    doc_id = os.path.basename(file_path)
    # 删除旧文档（如果存在）
    try:
        collection.delete(where={"source": doc_id})
    except Exception:
        pass

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": doc_id, "chunk_idx": i} for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas,
    )

    return len(chunks)


def delete_document(filename):
    """从知识库中删除文档"""
    collection = _get_collection()
    try:
        collection.delete(where={"source": filename})
    except Exception:
        pass


def list_documents():
    """列出知识库中所有文档"""
    collection = _get_collection()
    results = collection.get(include=["metadatas"], limit=10000)

    docs = {}
    for meta in results.get("metadatas", []):
        source = meta.get("source", "unknown")
        if source not in docs:
            docs[source] = 0
        docs[source] += 1

    return docs


def retrieve(query, top_k=None):
    """
    检索与 query 最相关的文档片段
    返回: 检索到的文本拼接结果
    """
    config = load_config()
    if top_k is None:
        top_k = config.get("rag_top_k", 3)

    collection = _get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas"],
    )

    if not results.get("documents"):
        return ""

    # 拼接检索结果
    context_parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context_parts.append(f"[来源: {meta['source']}]\n{doc}")

    return "\n\n---\n\n".join(context_parts)
