
from rag_engine import RAGEngine

# Sample document chunks
chunks = [
    "Company policy requires employees to protect confidential information.",
    "All passwords must be stored securely.",
    "Employees must follow company security policies.",
    "The company provides annual employee training.",
    "Confidential customer information must not be disclosed."
]

# Initialize RAG
rag = RAGEngine()

# Create vector database
total = rag.create_vector_store(chunks)

print("RAG Engine Test")
print("--------------------")
print("Stored chunks:", total)

# Search for relevant passages
query = "Identify instructions related to confidential data exposure"

results = rag.retrieve(query, top_k=3)

print("\nRetrieved Passages:")

for result in results:
    print("\nChunk ID:", result["chunk_id"])
    print("Similarity:", round(result["similarity"], 3))
    print("Text:", result["text"])
