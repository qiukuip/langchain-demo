from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", streaming=False)
agent = create_agent(model=model)
for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "Introduce yourself to me."}]},
        stream_mode=["messages", "updates"],
        version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        print(token, end="|", flush=True)
    elif chunk["type"] == "updates":
        for source, update in chunk["data"].items():
            if source in ("model", "tools"):
                message = update["messages"][-1]
                if isinstance(message, AIMessage) and message.tool_calls:
                    print(f"Tool call: {message.tool_calls}")
                if isinstance(message, ToolMessage):
                    print(f"Tool Response: {message.content_blocks}")
