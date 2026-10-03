from embedding import create_embedding
from vector_store import create_index
from rag_retriever import RAGRetriever


def test_document_filter():
    chunks = [
        {
            "text": "JWT authentication uses tokens.",
            "page": 1,
            "filename": "auth.pdf",
            "document_id": "auth-doc",
        },
        {
            "text": "Docker uses containers.",
            "page": 1,
            "filename": "docker.pdf",
            "document_id": "docker-doc",
        },
    ]

    embeddings = [create_embedding(chunk["text"]) for chunk in chunks]

    index = create_index(embeddings)
    retriever = RAGRetriever(chunks, index=index)

    results = retriever.search(
        query="How does Docker work?",
        top_k=2,
        candidate_k=2,
        rewrite=False,
        multi_query=False,
        document_id="auth-doc",
    )

    assert all(result["document_id"] == "auth-doc" for result in results)
