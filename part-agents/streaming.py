from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
)
for chunk in agent.stream({
    "messages": [HumanMessage("搜索 AI 新闻并总结新发现。")]
}, stream_mode="values"):
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        if isinstance(latest_message, HumanMessage):
            print(f"User: {latest_message.content}")
        elif isinstance(latest_message, AIMessage):
            print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
