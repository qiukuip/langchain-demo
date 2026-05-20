from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool


load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city"""
    return f"It's always sunny in {city}"


agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=[get_weather])
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="updates",
    version="v2",
):
    if chunk["type"] == "updates":
        for step, data in chunk["data"].items():
            print(f"Step: {step}")
            print(f"Content: {data['messages'][-1].content_blocks}")
