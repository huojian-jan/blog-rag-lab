import chromadb

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding

from config import (
    DATA_DIR,
    CHROMA_DIR,
    OPENAI_BASE_URL,
    OPENAI_EMBED_MODEL,
    OPENAI_EMBED_API_KEY,
)
from url_loader import load_documents_from_urls

COLLECTION_NAME = "blog_rag"


def main():
    if not OPENAI_EMBED_API_KEY:
        raise ValueError("OPENAI_EMBED_API_KEY 未设置，请检查 .env 文件")

    if not OPENAI_EMBED_MODEL:
        raise ValueError("OPENAI_EMBED_MODEL 未设置，请检查 .env 文件")

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"数据目录不存在: {DATA_DIR}")

    print("Embedding model:", OPENAI_EMBED_MODEL)

    Settings.embed_model = OpenAIEmbedding(
        model=OPENAI_EMBED_MODEL,
        api_key=OPENAI_EMBED_API_KEY,
        api_base=OPENAI_BASE_URL,
    )

    Settings.text_splitter = SentenceSplitter(
        chunk_size=500,
        chunk_overlap=80,
    )

    documents = load_documents_from_urls(DATA_DIR)

    if not documents:
        raise ValueError("没有读取到文档，请检查 data/ 目录下是否有可访问的博客链接")

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
        print(f"已清理旧索引集合: {COLLECTION_NAME}")
    except Exception:
        pass

    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    print(f"索引构建完成，共加载 {len(documents)} 个网页。")
    print(f"索引目录: {CHROMA_DIR}")


if __name__ == "__main__":
    main()
