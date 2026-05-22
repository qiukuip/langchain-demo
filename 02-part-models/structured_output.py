import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from movie import Movie

load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)

model_with_structure = model.with_structured_output(Movie, include_raw=True)
response = model_with_structure.invoke("请提供电影《盗梦空间》的详情。")
print(response)
