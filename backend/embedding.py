from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # a bi-encoder 

model = SentenceTransformer(EMBEDDING_MODEL)


def create_embedding(text: str) -> list[float]:
    return create_embeddings([text])[0]


# For batch embedding, thus accepts list[chunks text]
def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    vectors = model.encode(texts)
    return vectors.tolist()
