from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool


@tool
def is_blacklisted(username: str) -> bool:
    """Check if username is blacklisted"""
    return username.startswith("A") or username.startswith("B")


load_dotenv()
model = init_chat_model(
    model="gemini-2.5-flash-lite",
    model_provider="google_genai"
)
messages = [{"role": "user", "content": "Is Alice a blacklisted user?"}]
# model_with_tools = model.bind_tools([is_blacklisted], tool_choice="any")
model_with_tools = model.bind_tools([is_blacklisted], tool_choice="is_blacklisted")
ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    tool_call_name = tool_call["name"]
    print(f"tool_call_name: {tool_call_name}")
    if tool_call_name == "is_blacklisted":
        tool_result = is_blacklisted.invoke(tool_call)
        print(f"tool_result: {tool_result}")
        messages.append(tool_result)

final_response = model_with_tools.invoke(messages)
print(final_response.content_blocks)
