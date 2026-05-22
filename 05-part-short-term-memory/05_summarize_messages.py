from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import RunnableConfig

load_dotenv()

agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model="google_genai:gemini-2.5-flash-lite",
            trigger=("tokens", 2000),
            keep=("messages", 2),
        )
    ],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig | None = {"configurable": {"thread_id": "1"}}

agent.invoke(
    {"messages": [{"role": "user", "content": "你好，我叫鲍勃！"}]}, config=config
)
agent.invoke(
    {"messages": [{"role": "user", "content": "写一首关于猫的诗。"}]}, config=config
)
agent.invoke({"messages": [{"role": "user", "content": "关于狗的。"}]}, config=config)
response = agent.invoke(
    {"messages": [{"role": "user", "content": "我的名字是什么？"}]}, config=config
)
print(response["messages"][-1].pretty_print())
