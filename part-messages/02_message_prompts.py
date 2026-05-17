import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


load_dotenv()

model = init_chat_model("google_genai:gemini-3.1-flash-lite", api_key=os.getenv("GOOGLE_API_KEY"))
# messages = [
#     SystemMessage("你是一个专业的诗人。"),
#     HumanMessage("写一首关于春天的俳句。"),
#     AIMessage("樱桃花绽放。")
# ]
messages = [
    {"role": "system", "content": "你是一个专业的诗人。"},
    {"role": "user", "content": "写一首关于春天的俳句。"},
    {"role": "assistant", "content": "樱桃花绽放。"}
]
response = model.invoke(messages)
print(response)

