from typing import List

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_core.messages import BaseMessage, HumanMessage

load_dotenv()

agent = create_agent(
    model="ollama:llama0.1",
    tools=[],
    middleware=[
        ModelFallbackMiddleware(
            first_model="ollama:llama3.1"
        ),
    ]
)
messages: List[BaseMessage] = [HumanMessage(content="你是 LLaMA3.1 吗？")]
response = agent.invoke({"messages": messages})
for msg in response["messages"]:
    print(msg.pretty_print())
