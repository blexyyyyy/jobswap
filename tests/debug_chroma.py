#!/usr/bin/env python3
"""Debug the ChromaDB retrieval issue."""

import os

import chromadb

# Create a test collection
chroma_dir = "chroma_store"
os.makedirs(chroma_dir, exist_ok=True)

client = chromadb.PersistentClient(path=chroma_dir)
collection = client.get_or_create_collection(name="test_embeddings")

# Add a test embedding
test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 154  # 770 dims
collection.add(
    ids=["1"],
    embeddings=[test_embedding],
    metadatas=[{"name": "Test"}]
)

print("Added embedding with ID '1'")

# Try to retrieve it
result = collection.get(ids=["1"])
print(f"\nRaw result from get():")
print(f"  Keys: {result.keys()}")
print(f"  IDs: {result.get('ids')}")
print(f"  Embeddings type: {type(result.get('embeddings'))}")
print(f"  Embeddings value: {result.get('embeddings')}")

if result.get('embeddings'):
    print(f"\n  First embedding type: {type(result['embeddings'][0])}")
    print(f"  First embedding length: {len(result['embeddings'][0])}")
    print(f"  First 5 values: {result['embeddings'][0][:5]}")
    print(f"  First 5 values: {result['embeddings'][0][:5]}")
