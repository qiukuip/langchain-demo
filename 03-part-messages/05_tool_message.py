from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

load_dotenv()

ai_message = AIMessage(
    content=[],
    tool_calls=[
        {"id": "call_123", "name": "get_weather", "args": {"location": "东京"}}
    ],
)
weather_result = "晴，12度"
tool_message = ToolMessage(content=weather_result, tool_call_id="call_123")
messages = [HumanMessage("东京的天气怎么样？"), ai_message, tool_message]
model = init_chat_model("google_genai:gemini-2.5-flash-lite")
response = model.invoke(messages)
print(response)
