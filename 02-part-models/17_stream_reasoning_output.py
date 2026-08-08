from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite",
    temperature=0.7,
    max_tokens=100_000,
    max_retries=3,
    reasoning_effort="medium",
    include_thoughts=True
)
for chunk in model.stream("鹦鹉为什么有很多颜色？"):
    for part in chunk.content_blocks:
        # print(f"part_type: {part['type']}")
        if part["type"] == "text":
            print(part["text"], end="", flush=True)
        elif part["type"] == "reasoning":
            print("\n思考中")
        elif part["type"] == "tool_use":
            print(f"\n检测到工具调用: {part.name}", flush=True)
