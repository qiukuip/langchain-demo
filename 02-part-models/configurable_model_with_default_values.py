import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    configurable_fields=("model", "model_provider", "temperature", "max_tokens"),
    config_prefix="fist"
)
response = model.invoke("告诉我今天的日期。")
print(response)
print("=====")
response = model.invoke(
    "主流的图形用户界面操作系统有哪些？",
    config={
        "configurable": {
            "first_model": "gemini-3.1-flash-lite",
            "first_model_provider": "google_genai",
            "first_temperature": 0.5,
            "first_max_tokens": 100
        }
    }
)
print(response)
