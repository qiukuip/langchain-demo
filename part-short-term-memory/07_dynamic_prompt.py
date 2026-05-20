from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain.tools import tool
from pydantic import BaseModel


class CustomContext(BaseModel):
    username: str


@tool
def get_weather(city: str) -> str:
    """Get the weather in a city"""
    return f"The weather in {city} is always sunny."


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    username = None
    context = request.runtime.context
    if context is None:
        username = "UnknownUser"
    else:
        username = context.username
    return f"You are a helpful assistant, address the user as {username}"


load_dotenv()
agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[get_weather],
    middleware=[dynamic_system_prompt],
    context_schema=CustomContext,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in NewYork?"}]},
    context=CustomContext(username="Alice"),
)
for msg in result["messages"]:
    msg.pretty_print()

