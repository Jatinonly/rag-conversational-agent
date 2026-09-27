from embedding import create_embedding
from vector_store import create_index, search_index


class RAGRetriever:
    def __init__(self, chunks: list[dict]):  #self refers to current object i.e. created 
        self.chunks = chunks

        embeddings = [create_embedding(chunk["text"]) for chunk in chunks]

        self.index = create_index(embeddings)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        query_embedding = create_embedding(query)

        distances, indices = search_index(
            self.index,
            query_embedding,
            top_k,
        )

        results = []

        for distance, index_position in zip(distances, indices):
            chunk = self.chunks[index_position]

            results.append(
                {
                    "text": chunk["text"],
                    "page": chunk["page"],
                    "distance": float(distance),
                }
            )

        return results
