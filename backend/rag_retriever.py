import numpy as np

from embedding import create_embedding
from vector_store import create_index, search_index
from sentence_transformers import CrossEncoder
from query_rewriter import rewrite_query
from multi_query import generate_queries
from context_compressor import compress_context
from bm25_retriever import BM25Retriever
from rrf import reciprocal_rank_fusion

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(RERANKER_MODEL)


class RAGRetriever:
    def __init__(self, chunks: list[dict], index=None):
        self.chunks = chunks

        if index is not None:
            self.index = index
        else:
            embeddings = [create_embedding(chunk["text"]) for chunk in chunks]

            self.index = create_index(embeddings)  # Semantic search - FAISS

        self.bm25 = BM25Retriever(list(chunks))  # Lexical search - BM25
        

    def add_chunks(self, new_chunks: list[dict]):
        if not new_chunks:
            return

        # 1. Create embeddings for the new chunks
        new_embeddings = [create_embedding(chunk["text"]) for chunk in new_chunks]

        # 2. Add new vectors to the existing FAISS index
        vectors = np.array(
            new_embeddings,
            dtype="float32",
        )

        self.index.add(vectors)

        # 3. Add new chunks to BM25
        self.bm25.add_chunks(new_chunks)

        # 4. Keeps chunk metadata in same order as FAISS
        self.chunks.extend(new_chunks)

    def remove_document(self, document_id: str):
        remaining_chunks = [
            chunk 
            for chunk in self.chunks
            if chunk["document_id"] != document_id
        ]

        if len(remaining_chunks) == len(self.chunks):  # means no chunks deleted.
            return False

        self.chunks = remaining_chunks
        if not remaining_chunks:  # means zero chunks in remaining_chunks
            return True

        self.__init__(
            remaining_chunks
        )  # Rebuild entire retriever from remaining chunks
        return True

    def search(
        self,
        query: str,
        top_k: int = 3,
        candidate_k: int = 10,
        rewrite: bool = True,
        multi_query: bool = True,
    ) -> list[dict]:

        # 1. Query transformation

        queries = [query]

        if rewrite:
            queries = [rewrite_query(query)]

        if multi_query:
            queries = generate_queries(queries[0])

        queries = list(dict.fromkeys(queries))

        # 2. Hybrid retrieval + RRF

        # Store unique chunks across ALL generated queries.
        # Key = chunk index
        all_candidates = {}

        for search_query in queries:

            # ---------- FAISS ----------
            query_embedding = create_embedding(search_query)

            faiss_distances, faiss_indices = search_index(
                self.index,
                query_embedding,
                candidate_k,
            )

            faiss_indices = list(faiss_indices)

            # ---------- BM25 ----------
            bm25_indices = self.bm25.search(
                query=search_query,
                top_k=candidate_k,
            )

            # ---------- RRF ----------
            hybrid_scores = reciprocal_rank_fusion(
                [
                    faiss_indices,
                    bm25_indices,
                ]
            )

            hybrid_ranked = sorted(
                hybrid_scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )

            # ---------- Collect "UNIQUE" candidates ----------
            for index_position, rrf_score in hybrid_ranked[:candidate_k]:

                chunk = self.chunks[index_position]

                # First time we see this chunk
                if index_position not in all_candidates:

                    all_candidates[index_position] = {
                        "text": chunk["text"],
                        "page": chunk["page"],
                        "filename": chunk["filename"],
                        "document_id": chunk["document_id"],
                        "rrf_score": float(rrf_score),
                        "query_hits": 1,  # Number of queries who gave this chunk as a candidate.
                    }

                # Same chunk found by another generated query.
                # Keep the better RRF score.
                else:
                    all_candidates[index_position]["query_hits"] += 1

                    if rrf_score > all_candidates[index_position]["rrf_score"]:
                        all_candidates[index_position]["rrf_score"] = float(rrf_score)

        # Convert dictionary back into list
        candidates = list(all_candidates.values())

        # 3. Cross-encoder reranking

        pairs = [
            [query, candidate["text"]] for candidate in candidates
        ]  # we do not use multiple queries in cross-encoder because we only want to find best chunks using the users query only.

        scores = reranker.predict(pairs)

        ranked = sorted(
            zip(scores, candidates),
            key=lambda item: item[0],
            reverse=True,
        )

        # 4. Contextual compression

        results = []

        for score, candidate in ranked[:top_k]:

            results.append(
                {
                    "text": compress_context(
                        question=query,
                        text=candidate["text"],
                    ),
                    "page": candidate["page"],
                    "filename": candidate["filename"],
                    "document_id": candidate["document_id"],
                    "rrf_score": candidate["rrf_score"],
                    "rerank_score": float(score),
                    "query_hits": candidate["query_hits"],
                }
            )

        return results
