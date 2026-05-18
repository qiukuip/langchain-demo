from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage


load_dotenv()

model = init_chat_model(model="google_genai:gemini-2.5-flash-lite")
system_message = SystemMessage("""
你是一个在Web应用开发方面拥有丰富经验的高级Python工程师，
随时提供一些代码示例并解释其中的原理。
你的解释请保持简洁且彻底。
""")
messages = [
    system_message,
    HumanMessage(id="msg1", name="Alice", content="我应该如何创建一个 Restful API？")
]
response = model.invoke(messages)
print(response)

