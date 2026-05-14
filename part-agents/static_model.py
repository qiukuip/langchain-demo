from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(verbose=True)

model = ChatGoogleGenerativeAI(
    name="static-model",
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    max_tokens=1000,
    timeout=30
)
agent = create_agent(
    model=model,
    tools=[],
    middleware=[],
    system_prompt=SystemMessage("你是一个知识丰富、乐于助人的 AI 助手。")
)
messages = [
    {"role": "user", "content": "介绍一下你自己"}
]
result = agent.invoke({"messages": messages})
print(result["messages"][-1].content_blocks)

