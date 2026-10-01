import faiss
import numpy as np


def create_index(embeddings: list[list[float]]):

    # we convert because FAISS expects vectors in NumPy array.
    vectors = np.array(embeddings, dtype="float32")

    dimension = vectors.shape[1]   #384 in our case

    index = faiss.IndexFlatL2(dimension)
    # Creates an empty "object" or "FAISS search index" with dimension = 384
    # because the embedding model we used i.e. "all-MiniLM-L6-v2" creates
    # each embeddings vector with 384 values init. like- [-0.12,0.23, 0.56, -0.31, .... till 384 values]

    index.add(vectors)

    return index


# semantic searching/retrieval:
def search_index(
    index,
    query_embedding: list[float],
    top_k: int = 2,
):
    query_vector = np.array(
        [query_embedding],
        dtype="float32",
    )

    distances, indices = index.search(
        query_vector,
        top_k,
    )

    return distances[0], indices[0]


def save_index(index, path: str):
    faiss.write_index(index, path)


def load_index(path: str):
    return faiss.read_index(path)
