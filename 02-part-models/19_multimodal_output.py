from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
model = ChatGoogleGenerativeAI(
    model="",
    temperature=0.8,
    max_tokens=100_000
)
result = model.invoke("Create a picture of a cat")
print(result.content_blocks)
