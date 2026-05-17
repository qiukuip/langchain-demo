import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)
# response = model.invoke("生成一张狸花猫的图片，直接给图片，不需要思考过程。")
for chunk in model.stream("生成一张狸花猫的图片。"):
    has_text = None
    for part in chunk.content_blocks:
        if part["type"] == "text":
            print(part["text"], end="", flush=True)
            has_text = True
        elif part["type"] == "reasoning":
            print("\n思考中")
        elif part["type"] == "tool_use":
            print(f"\n检测到工具调用: {part.name}", flush=True)
