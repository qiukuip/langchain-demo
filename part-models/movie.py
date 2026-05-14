from pydantic import BaseModel, Field


class Movie(BaseModel):
    """电影详情。"""
    title: str = Field(description="电影名称")
    year: int = Field(description="发行年度")
    director: str = Field(description="导演")
    rating: float = Field(description="评分，十分制")
