import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# model1 = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
model2 = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    max_tokens=1000,
    timeout=30,
    max_retries=2
)

result = model2.invoke("请问唐朝共存在了多少年？")
print(result)
