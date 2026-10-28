from langchain_core.documents import Document

documents = [
    Document(
        id="1",
        page_content="This is the content of first page",
        metadata={"source": "mammal-pets-doc"}
    ),
    Document(
        id="1",
        page_content="This is the content of first page",
        metadata={"source": "mammal-pets-doc"}
    )
]
