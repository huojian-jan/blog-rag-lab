import chromadb

from llama_index.core import Settings, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

from config import (
    CHROMA_DIR,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OPENAI_MODEL_API_KEY,
    OPENAI_EMBED_MODEL,
    OPENAI_EMBED_API_KEY,
)

SYSTEM_PROMPT = """
你是一个基于个人博客知识库的问答助手。
请严格根据检索到的资料回答问题，不要编造。
如果资料不足以支持结论，请明确说：“我无法从现有博客内容中确认这个问题”。
回答尽量清晰、准确、简洁。
"""


def build_query_engine():
    if not OPENAI_MODEL:
        raise ValueError("OPENAI_MODEL 未设置，请检查 .env 文件")

    if not OPENAI_MODEL_API_KEY:
        raise ValueError("OPENAI_MODEL_API_KEY 未设置，请检查 .env 文件")

    if not OPENAI_EMBED_MODEL:
        raise ValueError("OPENAI_EMBED_MODEL 未设置，请检查 .env 文件")

    if not OPENAI_EMBED_API_KEY:
        raise ValueError("OPENAI_EMBED_API_KEY 未设置，请检查 .env 文件")

    print(f"LLM model: {OPENAI_MODEL}")
    print(f"Embedding model: {OPENAI_EMBED_MODEL}")

    Settings.llm = OpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_MODEL_API_KEY,
        api_base=OPENAI_BASE_URL,
        temperature=0.1,
        system_prompt=SYSTEM_PROMPT,
    )

    Settings.embed_model = OpenAIEmbedding(
        model=OPENAI_EMBED_MODEL,
        api_key=OPENAI_EMBED_API_KEY,
        api_base=OPENAI_BASE_URL,
    )

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma_client.get_collection("blog_rag")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )

    query_engine = index.as_query_engine(
        similarity_top_k=4,
        response_mode="compact",
    )
    return query_engine


def print_sources(response):
    print("\n" + "=" * 80)
    print("参考片段")
    print("=" * 80)

    source_nodes = getattr(response, "source_nodes", [])
    if not source_nodes:
        print("没有返回参考片段。")
        return

    for i, node in enumerate(source_nodes, start=1):
        metadata = node.node.metadata or {}
        file_name = metadata.get("file_name", "未知文件")
        score = getattr(node, "score", None)
        text = node.node.get_text().strip().replace("\n", " ")

        print(f"\n[{i}] 文件: {file_name}")
        if score is not None:
            print(f"相似度分数: {score:.4f}")
        print(f"片段: {text[:300]}...")


def main():
    query_engine = build_query_engine()

    print("\nBlog RAG 已启动，输入 quit 退出。\n")

    while True:
        question = input("请输入问题> ").strip()

        if question.lower() in {"quit", "exit", "q"}:
            print("已退出。")
            break

        if not question:
            continue

        print("\n" + "=" * 80)
        print("用户问题")
        print("=" * 80)
        print(question)

        response = query_engine.query(question)

        print("\n" + "=" * 80)
        print("回答")
        print("=" * 80)
        print(str(response))

        print_sources(response)
        print()


if __name__ == "__main__":
    main()