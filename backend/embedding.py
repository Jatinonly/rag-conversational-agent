from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # a bi-encoder 

model = SentenceTransformer(EMBEDDING_MODEL)


def create_embedding(text: str) -> list[float]:
    vector = model.encode(text)

    return vector.tolist()
