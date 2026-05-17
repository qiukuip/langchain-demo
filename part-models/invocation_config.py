import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)
response = model.invoke(
    "给我讲一个苏联笑话",
    config={
        "run_name": "joke_generation",
        "tags": ["humor", "demo"],
        "metadata": {"user_id": "123"},
        "callbacks": []
    }
)
print(response)

