from llm import generate_answer


def rewrite_conversation_query(
    question: str,
    history: list[dict],
) -> str:
    recent_history = history[-6:]  # Only sending the last 6 chat history instead of sending complete convo histroy.

    history_text = "\n".join(
        f"{message['role']}: {message['content']}" for message in recent_history
    )

    prompt = f"""
Rewrite the user's latest question into a standalone search query.

Use the conversation history to resolve references such as:
- it
- they
- that
- this
- the previous topic

Preserve the user's original meaning.
Do not answer the question.
Do not add information that is not supported by the conversation.

Conversation history:
{history_text}

Latest question:
{question}

Standalone search query:
"""

    return generate_answer(prompt).strip()
