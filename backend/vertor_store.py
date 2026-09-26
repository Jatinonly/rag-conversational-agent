import faiss
import numpy as np


def create_index(embeddings: list[list[float]]):
    vectors = np.array(embeddings, dtype="float32")

    dimension = vectors.shape[1]   #384 in our case

    index = faiss.IndexFlatL2(dimension)  #Create an empty "object" or "FAISS search index" dimension=(say)384

    index.add(vectors)

    return index
