import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()

user_message = "介绍一下你自己。"
model = init_chat_model(api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.7)
response = None
if len(user_message) > 5:
    response = model.invoke(
        user_message,
        config={
            "configurable": {
                "model": "google_genai:gemini-3.1-flash-lite"
            }
        }
    )
else:
    response = model.invoke(
        user_message,
        config={
            "configurable": {
                "model": "google_genai:gemini-2.5-flash-lite"
            }
        }
    )
print(response)

