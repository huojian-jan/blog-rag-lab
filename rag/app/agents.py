from config import (
    DATA_DIR,
    CHROMA_DIR,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OPENAI_EMBED_MODEL,
)

Settings.llm = OpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    api_base=OPENAI_BASE_URL,
    temperature=0.1,
)

Settings.embed_model = OpenAIEmbedding(
    model=OPENAI_EMBED_MODEL,
    api_key=OPENAI_API_KEY,
    api_base=OPENAI_BASE_URL,
)