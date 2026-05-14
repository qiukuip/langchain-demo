import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    max_tokens=1000,
    timeout=30,
    max_retries=3
)

conversations1 = [
    {"role": "system", "content": "你是一个有用的英中翻译助手，将英文翻译成中文。"},
    {"role": "user", "content": "翻译：I love programming."},
    {"role": "system", "content": "我喜欢编程。"},
    {"role": "user", "content": "翻译：I love building applications."}
]
resp1 = model.invoke(conversations1)
print("resp1: ")
print(resp1)

conversations2 = [
    SystemMessage("你是一个有用的英中翻译助手，将英文翻译成中文。"),
    HumanMessage("翻译：I love programming."),
    SystemMessage("我喜欢编程。"),
    HumanMessage("翻译：I love building applications.")
]
resp2 = model.invoke(conversations2)
print("resp2: ")
print(resp2)
