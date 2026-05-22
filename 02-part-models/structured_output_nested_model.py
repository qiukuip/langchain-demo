from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(verbose=True)


class Actor(BaseModel):
    name: str
    role: str


class MovieDetails(BaseModel):
    title: str
    year: int
    cast: list[Actor]
    genres: list[str]
    budget: float | None = Field(None, description="预算，单位为百万")


model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
model_with_structure = model.with_structured_output(MovieDetails)
response = model_with_structure.invoke("请提供电影《火星救援》的信息。")
print(response)
