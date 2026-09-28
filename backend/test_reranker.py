from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(MODEL_NAME)


query = "What are the benefits of running?"

chunks = [
    "Running is an aerobic physical activity that can improve cardiovascular fitness and endurance.",
    "Docker is a platform used to package applications and their dependencies into containers.",
    "PostgreSQL is an open-source relational database management system.",
]


pairs = [[query, chunk] for chunk in chunks]

scores = reranker.predict(pairs)


for chunk, score in zip(chunks, scores):
    print("Score:", score)
    print("Chunk:", chunk)
    print()
