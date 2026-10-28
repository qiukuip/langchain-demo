import pypdf
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

OLLAMA_BASE_URL = "http://localhost:11434/"
OLLAMA_EMBEDDINGS = OllamaEmbeddings(
    model="embeddinggemma-2",
    base_url=OLLAMA_BASE_URL
)
VECTOR_STORE = InMemoryVectorStore(OLLAMA_EMBEDDINGS)


def load_pdf_pages(file_path: str) -> list[Document]:
    reader = pypdf.PdfReader(file_path)
    return [
        Document(
            id=i,
            page_content=page.extract_text() or "",
            metadata={"source": file_path, "page": i},
        )
        for i, page in enumerate(reader.pages)
    ]


def recursive_character_text_split(file_path: str) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    reader = pypdf.PdfReader(file_path)
    all_splits = text_splitter.split_documents(
        Document(
            id="1",
            page_content=page.extract_text() or "",
            metadata={"source": file_path, "page": i},
        )
        for i, page in enumerate(reader.pages)
    )
    return all_splits


def save_embeddings(all_splits: list[Document]):
    document_ids = VECTOR_STORE.add_documents(documents=all_splits)
    print(f"Document count: {len(document_ids)}")


file_path = "./data/nke-10k-2023.pdf"
docs = recursive_character_text_split(file_path)
print(len(docs))
save_embeddings(docs)
