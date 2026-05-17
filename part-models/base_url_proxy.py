import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()

model = init_chat_model(
    model="gemini-2.5-flash-lite",
    base_url="https://proxy.example.com:8080",
    api_key=os.getenv("GOOGLE_API_KEY"),
    model_provider="google_genai"
).bind(response_logprobs=True,
       logprobs=10)


