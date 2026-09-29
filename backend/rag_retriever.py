from embedding import create_embedding
from vector_store import create_index, search_index
from sentence_transformers import CrossEncoder
from query_rewriter import rewrite_query
from multi_query import generate_queries
from context_compressor import compress_context

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
        rewrite: bool = True,
        multi_query: bool = True,
    ) -> list[dict]:

        queries = [query]

        if rewrite:
            queries = [rewrite_query(query)]

        if multi_query:
            queries = generate_queries(queries[0])

        queries = list(dict.fromkeys(queries))  # removes duplicate query from queries

        unique_candidates = {}

        for search_query in queries:  # finding candidates from multiple queries
            query_embedding = create_embedding(search_query)

            distances, indices = search_index(
                self.index,
                query_embedding,
                candidate_k,
            )

            for distance, index_position in zip(distances, indices):
                if max_distance is not None and distance > max_distance:
                    continue

                chunk = self.chunks[index_position]

                if index_position not in unique_candidates:
                    unique_candidates[index_position] = {
                        "text": chunk["text"],
                        "page": chunk["page"],
                        "filename": chunk["filename"],
                        "distance": float(distance),
                    }
                elif (
                    distance < unique_candidates[index_position]["distance"]
                ):  # Because say a query q1 can have distance 2 with the chunk and the other query q2 can have distance 1.5 with the same chunk, so we need the shorter distance because chunk is still the same.
                    unique_candidates[index_position]["distance"] = float(distance)

        candidates = list(unique_candidates.values())

        # From here starts the cross-encoder part:
        pairs = [
            [query, candidate["text"]] for candidate in candidates
        ]  # we do not use multiple queries in cross-encoder because we only want to find best chunks using the users query only.

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
                    "text": compress_context(question=query, text=candidate["text"]),  #compress the chunks text before sending results
                    "page": candidate["page"],
                    "filename": candidate["filename"],
                    "distance": candidate["distance"],
                    "rerank_score": float(score),
                }
            )

        return results
