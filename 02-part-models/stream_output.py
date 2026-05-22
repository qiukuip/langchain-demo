import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    max_tokens=1000,
    timeout=30,
    max_retries=3
)

for chunk in model.stream("为什么太阳东升西落？"):
    print(chunk.text, end="|", flush=True)
