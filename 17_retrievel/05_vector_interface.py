from docling_core.types import DoclingDocument

FILE_PATH = "https://arxiv.org/pdf/2408.09869"
loader = DoclingLoader(file_path=FILE_PATH)
documents = loader.load()
for document in loader.lazy_load():
    print(document)
