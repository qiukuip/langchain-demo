import asyncio

from langchain_core.documents import Document
from langchain_core.runnables import chain
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

OLLAMA_BASE_URL = "http://localhost:11434/"
OLLAMA_EMBEDDINGS = OllamaEmbeddings(
    model="embeddinggemma-2",
    base_url=OLLAMA_BASE_URL
)
VECTOR_STORE = InMemoryVectorStore(OLLAMA_EMBEDDINGS)


def load_and_split_pdf(file_path: str):
    pypdf = PdfReader(file_path)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    splits = text_splitter.split_documents(
        Document(
            id=i,
            page_content=page.extract_text() or "",
            metadata={"source": file_path, "pages": i}
        )
        for i, page in enumerate(pypdf.pages)
    )
    return splits


def save_vector(splits: list[Document]):
    VECTOR_STORE.add_documents(documents=splits)


def query_embedding(query: str):
    results = VECTOR_STORE.similarity_search(query=query, k=5)
    for result in results:
        print(f"id: {result.id}")
        print(f"page content: {result.page_content}")
        print(f"metadata: {result.metadata}")
        print("=====\n")


async def async_query_embedding(query: str):
    results = await VECTOR_STORE.asimilarity_search(query=query, k=3)
    for result in results:
        print(f"id: {result.id}")
        print(f"page content: {result.page_content}")
        print(f"metadata: {result.metadata}")
        print("=====\n")


def query_embeddings_with_score(query: str):
    results = VECTOR_STORE.similarity_search_with_score(query=query, k=1)
    for result in results:
        doc, score = result
        print(f"id: {doc.id}")
        print(f"page content: {doc.page_content}")
        print(f"score: {score}")
        print(f"=====\n")


def query_by_vector(vector: list[float]):
    results = VECTOR_STORE.similarity_search_by_vector(embedding=vector, k=1)
    for result in results:
        print(f"id: {result.id}")
        print(f"page content: {result.page_content}")
        print(f"metadata: {result.metadata}")
        print("=====\n")


file_path = "./data/nke-10k-2023.pdf"
docs = load_and_split_pdf(file_path)
save_vector(docs)
query_embedding("How many distribution centers does Nike have in the US?")
print("=====\n")
asyncio.run(async_query_embedding("When was Nike incorporated?"))
query_embeddings_with_score(query="What was Nike's revenue in 2023?")

vector = OLLAMA_EMBEDDINGS.embed_query(text="How were Nike's margins compacted in 2023?")
query_by_vector(vector=vector)


@chain
def retriever(query: str) -> list[Document]:
    return VECTOR_STORE.similarity_search(query=query, k=1)


results = retriever.batch(
    [
        "How many distribution centers does Nike have in the US?",
        "When was Nike incorporated?",
    ]
)
for result in results:
    for doc in result:
        print(f"id: {doc.id}")
        print(f"page content: {doc.page_content}")
        print(f"metadata: {doc.metadata}")
        print("=====\n")
    print("======")
    print("======\n")
