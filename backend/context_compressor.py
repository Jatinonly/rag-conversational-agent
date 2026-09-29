from llm import generate_answer


def compress_context(question: str, text: str) -> str:
  
  prompt = f"""
Extract only the information from the document text that is relevant
to answering the user's question.

Do not answer the question yourself.
Do not add information.
Preserve important facts and details from the original text.

User question:
{question}

Document text:
{text}

Relevant information:
"""

  return generate_answer(prompt).strip()