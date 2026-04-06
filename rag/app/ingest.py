import chromadb

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

from config import (
    DATA_DIR,
    CHROMA_DIR,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OPENAI_MODEL_API_KEY,
    OPENAI_EMBED_MODEL,
    OPENAI_EMBED_API_KEY,
)


def main():
    if not OPENAI_MODEL_API_KEY:
        raise ValueError("OPENAI_MODEL_API_KEY 未设置，请检查 .env 文件")

    if not OPENAI_EMBED_API_KEY:
        raise ValueError("OPENAI_EMBED_API_KEY 未设置，请检查 .env 文件")

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"数据目录不存在: {DATA_DIR}")

    print("LLM model:", OPENAI_MODEL)
    print("Embedding model:", OPENAI_EMBED_MODEL)

    Settings.llm = OpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_MODEL_API_KEY,
        api_base=OPENAI_BASE_URL,
        temperature=0.1,
    )

    Settings.embed_model = OpenAIEmbedding(
        model=OPENAI_EMBED_MODEL,
        api_key=OPENAI_EMBED_API_KEY,
        api_base=OPENAI_BASE_URL,
    )

    Settings.text_splitter = SentenceSplitter(
        chunk_size=500,
        chunk_overlap=80,
    )

    reader = SimpleDirectoryReader(
        input_dir=str(DATA_DIR),
        required_exts=[".md", ".txt"],
        recursive=True,
        filename_as_id=True,
    )

    documents = reader.load_data()

    if not documents:
        raise ValueError("没有读取到文档，请检查 data/ 目录下是否有 .md 或 .txt 文件")

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma_client.get_or_create_collection("blog_rag")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    print(f"索引构建完成，共加载 {len(documents)} 篇文档。")
    print(f"索引目录: {CHROMA_DIR}")


if __name__ == "__main__":
    main()