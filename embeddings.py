"""Pluggable embedding provider. Swap embed() for Cohere, Voyage, a local model, etc.
If you change the model, change DIMENSIONS and re-run embed_levels.py."""
import os

from openai import OpenAI

MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
DIMENSIONS = 1536


def embed(texts):
    client = OpenAI()  # reads OPENAI_API_KEY
    resp = client.embeddings.create(model=MODEL, input=texts)
    return [d.embedding for d in resp.data]
