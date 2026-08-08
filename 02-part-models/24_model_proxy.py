from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
model = init_chat_model(
    name="gemini",
    model="google_genai:gemini-3.1-flash-lite",
    base_url="http://proxy.example.com:8000"
)
