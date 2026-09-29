from llm import generate_answer


def rewrite_query(question: str) -> str:
    prompt = f"""
Rewrite the following user question into a concise search query.

Preserve the original meaning.
Do not answer the question.
Do not add information that is not present in the question.

User question:
{question}

Search query:
"""

    return generate_answer(prompt).strip()
