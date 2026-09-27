from embedding import create_embedding
from vector_store import create_index, search_index

chunks = [
    {
        "text": "JWT tokens are used to authenticate users and authorize API requests.",
        "page": 1,
    },
    {
        "text": "Python lists can contain multiple values and can be modified after creation.",
        "page": 2,
    },
    {
        "text": "A database index improves the speed of database queries.",
        "page": 3,
    },
]


chunk_embeddings = [create_embedding(chunk["text"]) for chunk in chunks]

index = create_index(chunk_embeddings)

query = "How does authentication using JWT work?"

query_embedding = create_embedding(query)

distances, indices = search_index(
    index,
    query_embedding,
    top_k=2,
)

print("Query:", query)
print()  # prints  blank line


for distance, index_position in zip(distances, indices):
    chunk = chunks[index_position]

    print("Distance:", distance)
    print("Page:", chunk["page"])
    print("Text:", chunk["text"])
    print()
