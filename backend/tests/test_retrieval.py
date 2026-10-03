from embedding import create_embedding
from vector_store import create_index, search_index


def test_faiss_returns_closest_vector():
    texts = [
        "JWT authentication uses tokens.",
        "PostgreSQL is a relational database.",
        "Docker packages applications into containers.",
    ]

    embeddings = [create_embedding(text) for text in texts]
    index = create_index(embeddings)

    query_embedding = create_embedding("How does JWT authentication work?")

    distances, indices = search_index(
        index,
        query_embedding,
        top_k=1,
    )

    assert indices[0] == 0
