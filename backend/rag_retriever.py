import numpy as np

from embedding import create_embedding
from vector_store import create_index, search_index
from sentence_transformers import CrossEncoder
from query_rewriter import rewrite_query
from multi_query import generate_queries
from context_compressor import compress_context
from bm25_retriever import BM25Retriever
from rrf import reciprocal_rank_fusion
from logging_config import logger

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

logger.info("Loading cross-encoder reranker | model=%s", RERANKER_MODEL)

reranker = CrossEncoder(RERANKER_MODEL)

logger.info("Cross-encoder reranker loaded successfully")


class RAGRetriever:
    def __init__(self, chunks: list[dict], index=None):
        self.chunks = chunks

        logger.info(
            "Initializing RAG retriever | chunks=%d | existing_index=%s",
            len(chunks),
            index is not None,
        )

        if index is not None:
            self.index = index

            logger.info("Using existing FAISS index")
        else:
            logger.info("Creating FAISS index | chunks=%d", len(chunks))

            embeddings = [create_embedding(chunk["text"]) for chunk in chunks]

            self.index = create_index(embeddings)  # Semantic search - FAISS

            logger.info("FAISS index created successfully")

        self.bm25 = BM25Retriever(list(chunks))  # Lexical search - BM25

        logger.info("RAG retriever initialized successfully")

    def add_chunks(self, new_chunks: list[dict]):
        if not new_chunks:
            logger.warning("add_chunks called with no new chunks")
            return

        logger.info(
            "Adding chunks to RAG retriever | new_chunks=%d",
            len(new_chunks),
        )

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

        logger.info(
            "Chunks added successfully | total_chunks=%d",
            len(self.chunks),
        )

    def remove_document(self, document_id: str):
        logger.info(
            "Removing document from RAG retriever | document_id=%s",
            document_id,
        )

        remaining_chunks = [
            chunk for chunk in self.chunks if chunk["document_id"] != document_id
        ]

        if len(remaining_chunks) == len(self.chunks):  # means no chunks deleted.
            logger.warning(
                "Document not found in RAG retriever | document_id=%s",
                document_id,
            )
            return False

        self.chunks = remaining_chunks

        if not remaining_chunks:  # means zero chunks in remaining_chunks
            logger.info(
                "No chunks remain after document removal | document_id=%s",
                document_id,
            )
            return True

        logger.info(
            "Rebuilding RAG retriever after document removal | remaining_chunks=%d",
            len(remaining_chunks),
        )

        self.__init__(
            remaining_chunks
        )  # Rebuild entire retriever from remaining chunks

        logger.info(
            "RAG retriever rebuilt successfully | remaining_chunks=%d",
            len(remaining_chunks),
        )

        return True

    def search(
        self,
        query: str,
        top_k: int = 3,
        candidate_k: int = 10,
        rewrite: bool = True,
        multi_query: bool = True,
        document_id: str | None = None,
    ) -> list[dict]:

        # filter chunks of the particular document_id only.
        if document_id is not None:
            allowed_indices = [
                i
                for i, chunk in enumerate(self.chunks)
                if chunk["document_id"] == document_id
            ]
        else:
            allowed_indices = list(range(len(self.chunks)))

        logger.info(
            "RAG search configuration | chunks=%d | allowed_chunks=%d | "
            "top_k=%d | candidate_k=%d | rewrite=%s | multi_query=%s",
            len(self.chunks),
            len(allowed_indices),
            top_k,
            candidate_k,
            rewrite,
            multi_query,
        )

        # 1. Query transformation
        queries = [query]

        if rewrite:
            queries = [rewrite_query(query)]

        if multi_query:
            queries = generate_queries(queries[0])

        queries = list(dict.fromkeys(queries))

        logger.info(
            "Query transformation completed | generated_queries=%d",
            len(queries),
        )

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
                len(self.chunks),
            )

            faiss_indices = [
                index for index in faiss_indices if index in allowed_indices
            ][:candidate_k]

            # ---------- BM25 ----------
            bm25_indices = self.bm25.search(
                query=search_query,
                top_k=candidate_k,
                allowed_indices=allowed_indices,
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

        logger.info(
            "Hybrid retrieval completed | unique_candidates=%d",
            len(candidates),
        )

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

        logger.info(
            "Cross-encoder reranking completed | candidates=%d",
            len(ranked),
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

        logger.info(
            "Context compression completed | results=%d",
            len(results),
        )

        return results
