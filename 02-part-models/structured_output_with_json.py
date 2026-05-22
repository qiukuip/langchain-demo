from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


json_schema = {
    "title": "电影",
    "description": "电影详情",
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "电影名称"},
        "year": {"type": "integer", "description": "发行年份"},
        "director": {"type": "string", "description": "导演"},
        "rating": {"type": "number", "description": "评分，十分制"},
    },
    "required": ["title", "year", "director", "rating"],
}

model_with_structure = init_chat_model(model="google_genai:gemini-3.1-flash-lite")
model = model_with_structure.with_structured_output(json_schema, method="json_schema")

response = model.invoke("请提供电影《盗梦空间》的信息。")
print(response)
