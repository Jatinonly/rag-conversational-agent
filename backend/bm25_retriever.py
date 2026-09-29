from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks

        tokenized_chunks = [
            chunk["text"].lower().split() for chunk in chunks
        ]  # Tokenzied Chunk looks liks: [ ["Running", "improves", ...chunk1], ["Swimming", "helps", ...chunk2], ...]

        self.bm25 = BM25Okapi(tokenized_chunks)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(
            tokenized_query
        )  # gives scores to every "tokenized chunk", Looks like: [4.5, 0.8, 1.2] where each score is score of tokenzied chunk

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )

        results = []

        for index in ranked_indices[:top_k]:
            results.append(
                {
                    "text": self.chunks[index]["text"],
                    "page": self.chunks[index]["page"],
                    "filename": self.chunks[index]["filename"],
                    "bm25_score": float(scores[index]),
                }
            )

        return results
