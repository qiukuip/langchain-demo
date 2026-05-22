import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# 一次性返回所有结果
# responses = model.batch([
#     "为什么飞机能飞起来？",
#     "什么是量子计算？"
# ])
# for response in responses:
#     print(response)

# 部分完成立即返回，无需等待所有结果
# ⚠️结果返回顺序可能与输入顺序不一致
# 可以使用 max_concurrency 控制并发任务
for response in model.batch_as_completed([
    "为什么飞机能够飞起来？",
    "什么是量子计算？"
], config={"max_concurrency": 3}):
    print(response)
