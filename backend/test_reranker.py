from bm25_retriever import BM25Retriever

chunks = [
    {
        "text": "Running economy describes how efficiently a person uses oxygen while running at a given speed.",
        "page": 1,
        "filename": "running.pdf",
    },
    {
        "text": "Sleep and nutrition are important for recovery after demanding exercise.",
        "page": 2,
        "filename": "running.pdf",
    },
    {
        "text": "Interval training alternates faster running with easier recovery periods.",
        "page": 3,
        "filename": "running.pdf",
    },
]

retriever = BM25Retriever(chunks)

results = retriever.search(
    "What is running economy?",
    top_k=2,
)

for result in results:
    print(result)
