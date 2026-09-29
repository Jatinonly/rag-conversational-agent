from llm import generate_answer


def generate_queries(question: str, num_queries: int = 3) -> list[str]:
    prompt = f"""
Generate {num_queries} different search queries for the user's question.

Each query should:
- preserve the original meaning
- use different wording
- be useful for semantic document retrieval
- not answer the question

Return only the queries, one per line.

User question:
{question}

Search queries:
"""

    response = generate_answer(prompt)

    queries = [
        line.strip("- ").strip() for line in response.splitlines() if line.strip()
    ]

    return queries[:num_queries]
