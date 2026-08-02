from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field


class Movie(BaseModel):
    """电影详情。"""
    title: str = Field(description="电影名称")
    year: int = Field(description="发行年度")
    director: str = Field(description="导演")
    rating: float = Field(description="评分，十分制")


load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite"
)

# include_raw 会同时包含未结构化的信息和结构化的信息
model_with_structure = model.with_structured_output(Movie, include_raw=True)
response = model_with_structure.invoke("请提供电影《盗梦空间》的信息。")
print(response)
