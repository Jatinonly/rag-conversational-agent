from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self._build_index()

    # The underscore is a Python convention like in _build_index which means:
    # "This is an internal/helper method;
    # callers normally don't call it directly."
    def _build_index(self):

        tokenized_chunks = [
            chunk["text"].lower().split() for chunk in self.chunks
        ]  # Tokenzied Chunk looks like: [ ["Running", "improves", ...chunk1], ["Swimming", "helps", ...chunk2], ...]

        self.bm25 = BM25Okapi(tokenized_chunks)

    def add_chunks(
        self,
        new_chunks: list[dict]
    ):
        self.chunks.extend(new_chunks)
        self._build_index()

    def search(
        self,
        query: str,
        top_k: int = 3,
        allowed_indices: list[int] | None = None,
    ) -> list[int]:

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(
            tokenized_query
        )  # gives scores to every "tokenized chunk", Looks like: [4.5, 0.8, 1.2] where each score is score of tokenzied chunk

        if allowed_indices is None:
            allowed_indices = range(len(scores))

        ranked_indices = sorted(
            allowed_indices,
            key=lambda i: scores[i],
            reverse=True,
        )

        return ranked_indices[:top_k]
