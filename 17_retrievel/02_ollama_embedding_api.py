import requests
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings


def get_embedding(text: str):
    url = "http://localhost:11434/api/embed"
    payload = {"model": "embeddinggemma-2", "input": text}
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def get_embedding_ollama(text: str):
    embeddings = OllamaEmbeddings(model="embeddinggemma-2")
    vector = embeddings.embed_query(text)
    return vector


def get_vector_store(vector: Embeddings):
    vector_store = InMemoryVectorStore(vector)
    return vector_store


text = "在 Python 环境中，可以使用 requests 库调用 Ollama 的 Embedding 接口。"
embedding = get_embedding_ollama(text)
print(embedding)
