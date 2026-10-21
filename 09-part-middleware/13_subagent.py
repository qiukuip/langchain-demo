from deepagents import SubAgentMiddleware
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get weather in a city."""
    return f"The weather in {city} is sunny."


agent = create_agent(
    model="ollama:llama3.1",
    middleware=[
        SubAgentMiddleware(
            subagents=[
                {
                    "name": "weather_agent",
                    "description": "This subagent can get weather in cities.",
                    "system_prompt": "Use the get_weather tool get the weather in a city.",
                    "tools": [get_weather],
                    "model": "ollama:llama3.1",
                    "middleware": []
                }
            ],
            backend=None
        )
    ]
)

response = agent.invoke(
    {
        "messages": [HumanMessage(content="明天大阪的天气是什么样的？")]
    }
)
for message in response["messages"]:
    print(message.pretty_print())
