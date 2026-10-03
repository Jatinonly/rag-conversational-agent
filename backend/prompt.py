def build_rag_prompt(
    question: str,
    retrieved_chunks: list[dict],
    history: list[dict],
) -> str:

    recent_history = history[-6:]
    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in recent_history
    )

    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(f"[Page {chunk['page']}]\n{chunk['text']}")

    context = "\n\n".join(context_parts)

    return f"""
You are a helpful document question-answering assistant.

Answer the user's question using only the provided document context.

If the answer is not present in the context, say:
"I couldn't find the answer in the document."

Recent conversation:
{history_text}

Document context:
{context}

Question:
{question}

Answer:
"""
