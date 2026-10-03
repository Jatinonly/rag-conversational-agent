import json

from main import retriever
from prompt import build_rag_prompt
from llm import generate_answer

with open("eval/answer_questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)


for item in questions:
    retrieved_chunks = retriever.search(
        query=item["question"],
        top_k=3,
        candidate_k=10,
        rewrite=False,
        multi_query=False,
        document_id=item["document_id"],
    )

    prompt = build_rag_prompt(
        question=item["question"],
        retrieved_chunks=retrieved_chunks,
        history=[],
    )

    answer = generate_answer(prompt)

    print("\nQuestion:", item["question"])
    print("Expected:", item["expected_answer"])
    print("Generated:", answer)
