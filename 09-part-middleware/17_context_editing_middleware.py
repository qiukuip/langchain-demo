from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get weather in a city."""
    return f"It's sunny in {city}!"


agent = create_agent(
    model="ollama:llama3.1",
    tools=[get_weather],
    middleware=[
        ContextEditingMiddleware(
            edits=[ClearToolUsesEdit(trigger=1000,
                                     keep=2,
                                     clear_tool_inputs=False,
                                     exclude_tools=[],
                                     placeholder="This tool message has been removed.")],
            token_count_method="approximate",
        )
    ]
)
response = agent.invoke(
    {"messages": [HumanMessage(content="帮我查询布鲁塞尔、九州、洛杉矶、加利福尼亚的天气。")]}
)
for message in response["messages"]:
    print(message.pretty_print())
