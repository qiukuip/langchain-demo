from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, AIMessageChunk, AnyMessage, ToolMessage

load_dotenv()


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


weather_model = init_chat_model("google_genai:gemini-3.1-flash-lite")
weather_agent = create_agent(
    model=weather_model,
    tools=[get_weather],
    name="weather_agent",
)


def call_weather_agent(query: str) -> str:
    """Query the weather agent."""
    result = weather_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].text


supervisor_model = init_chat_model("google_genai:gemini-3.1-flash-lite")
agent = create_agent(
    model=supervisor_model,
    tools=[call_weather_agent],
    name="supervisor",
)


def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="|")
    if token.tool_call_chunks:
        print(token.tool_call_chunks)


def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool calls: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool response: {message.content_blocks}")


input_message = {"role": "user", "content": "What is the weather in Boston?"}
current_agent = None
for chunk in agent.stream(
    {"messages": [input_message]},
    stream_mode=["messages", "updates"],
    subgraphs=True,
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if agent_name := metadata.get("lc_agent_name"):
            if agent_name != current_agent:
                print(f"🤖 {agent_name}: ")
                current_agent = agent_name
        if isinstance(token, AIMessageChunk):
            _render_message_chunk(token)
    elif chunk["type"] == "updates":
        for source, update in chunk["data"].items():
            if source in ("model", "tools"):
                _render_completed_message(update["messages"][-1])
