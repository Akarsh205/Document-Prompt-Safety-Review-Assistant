
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class RAGEngine:

    def __init__(self):
        # Load the sentence embedding model
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.index = None
        self.chunks = []

    def create_vector_store(self, chunks):
        """Convert chunks into embeddings and store in FAISS."""

        if not chunks:
            raise ValueError("No document chunks provided")

        self.chunks = chunks

        # Generate embeddings
        embeddings = self.model.encode(
            chunks,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        # Create FAISS similarity index
        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        # Add embeddings to FAISS
        self.index.add(embeddings)

        return len(chunks)

    def retrieve(self, query, top_k=5):
        """Retrieve the most relevant document chunks."""

        if self.index is None:
            raise ValueError("Vector store has not been created")

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        # Search for similar passages
        k = min(top_k, len(self.chunks))

        scores, indices = self.index.search(
            query_embedding,
            k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            results.append({
                "text": self.chunks[idx],
                "similarity": float(score),
                "chunk_id": int(idx)
            })

        return results
