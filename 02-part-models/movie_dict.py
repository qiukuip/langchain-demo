from typing_extensions import Annotated, TypedDict


class MovieDict(TypedDict):
    """电影详情。"""
    title: Annotated[str, ..., "电影名称"]
    year: Annotated[str, ..., "发行年度"]
    director: Annotated[str, ..., "导演"]
    rating: Annotated[float, ..., "评分"]

