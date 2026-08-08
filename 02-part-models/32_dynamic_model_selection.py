from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

available_model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
exhausted_model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")


@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Choose model based on conversation complexity"""
    message_count = len(request.state["messages"])
    model = exhausted_model
    if message_count > 1:
        model = available_model
    return handler(request.override(model=model))


agent = create_agent(
    model=exhausted_model,
    tools=[],
    middleware=[dynamic_model_selection]
)
messages = [HumanMessage(content="一个月有多少天？")]
result = agent.invoke({"messages": messages})
print(result["messages"][-1])
