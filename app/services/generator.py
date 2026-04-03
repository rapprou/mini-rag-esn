import os
import anthropic

_client: anthropic.Anthropic | None = None
_SYSTEM_PROMPT = (
    "Tu es un assistant qui répond uniquement en te basant sur les documents fournis. "
    "Si la réponse ne se trouve pas dans les documents, dis-le clairement sans inventer d'information."
)


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def generate_answer(question: str, chunks: list[dict]) -> str:
    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

    context = "\n\n".join(
        f"[Document: {chunk.get('document_title', 'Inconnu')}]\n{chunk['content']}"
        for chunk in chunks
    )

    user_message = (
        f"Voici les extraits de documents pertinents :\n\n{context}\n\n"
        f"Question : {question}"
    )

    response = _get_client().messages.create(
        model=model,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return response.content[0].text
