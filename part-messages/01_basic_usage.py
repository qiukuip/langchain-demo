import os
from typing import List

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

load_dotenv()

model = init_chat_model(
    model="gemini-3.1-flash-lite",
    model_provider="google_genai",
    api_key=os.getenv("GOOGLE_API_KEY"),
)
system_message = SystemMessage("你是一个非常有用的小助手。")
human_message = HumanMessage("介绍一下你自己。")
messages: List[BaseMessage] = [system_message, human_message]
response = model.invoke(messages)
print(response)

