from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

load_dotenv()


@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    print("Getting weather")
    return f"Weather in {location}"


# 通过 LLMToolEmulator 模拟工具调用，不在列表中的工具会被真实调用。
@tool
def send_email(to: str, subject: str, content: str) -> str:
    """Send an email."""
    print("Sending email")
    print(f"Email subject: {subject}, content: {content}")
    return f"Email sent to {to} successfully."


agent = create_agent(
    model="ollama:llama3.1",
    tools=[get_weather, send_email],
    middleware=[
        LLMToolEmulator(
            model="ollama:llama3.1",
            tools=["get_weather"]
        )
    ]
)
response = agent.invoke(
    {"messages": [HumanMessage(content="帮我查询东京的天气，并用邮件发送给 aid@happ.com")]}
)
for message in response["messages"]:
    print(message.content_blocks)
