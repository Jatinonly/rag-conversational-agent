from embedding import create_embedding
from vector_store import create_index, search_index
from sentence_transformers import CrossEncoder

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(RERANKER_MODEL)


class RAGRetriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks

        embeddings = [create_embedding(chunk["text"]) for chunk in chunks]

        self.index = create_index(embeddings)

    def search(
        self,
        query: str,
        top_k: int = 3,
        candidate_k: int = 10,
        max_distance: float | None = None,
    ) -> list[dict]:

        query_embedding = create_embedding(query)

        distances, indices = search_index(
            self.index,
            query_embedding,
            candidate_k,
        )

        candidates = []

        for distance, index_position in zip(distances, indices):
            if max_distance is not None and distance > max_distance:
                continue

            chunk = self.chunks[index_position]

            candidates.append(
                {
                    "text": chunk["text"],
                    "page": chunk["page"],
                    "filename": chunk["filename"],
                    "distance": float(distance),
                }
            )

        # From here starts the cross-encoder part:
        pairs = [[query, candidate["text"]] for candidate in candidates]

        scores = reranker.predict(pairs)

        ranked = sorted(
            zip(scores, candidates),
            key=lambda item: item[0],
            reverse=True,
        )

        results = []

        for score, candidate in ranked[:top_k]:
            results.append(
                {
                    "text": candidate["text"],
                    "page": candidate["page"],
                    "filename": candidate["filename"],
                    "distance": candidate["distance"],
                    "rerank_score": float(score),
                }
            )

        return results
