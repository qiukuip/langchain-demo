from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import Runnable

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.5,
    include_thoughts=True,
    # thinking_budget=1024,
    thinking_level="medium"
)
agent: Runnable = create_agent(
    model=model,
    tools=[]
)
# 过于简单的问题，模型可能不会生成思考摘要。
run = agent.stream_events(
    {"messages": [{"role": "user", "content": "计算前50个素数的和，并说明计算步骤。"}]},
    version="v3"
)
for message in run.messages:
    for token in message.reasoning:
        print(f"[thinking] {token}", end="")
    for token in message.text:
        print(token, end="", flush=True)
