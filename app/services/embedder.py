import os
from openai import OpenAI

_client: OpenAI | None = None
_MODEL = "text-embedding-3-small"


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def embed_text(text: str) -> list[float]:
    response = _get_client().embeddings.create(model=_MODEL, input=text)
    return response.data[0].embedding


def embed_batch(texts: list[str]) -> list[list[float]]:
    response = _get_client().embeddings.create(model=_MODEL, input=texts)
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
