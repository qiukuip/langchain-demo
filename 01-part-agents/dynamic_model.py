from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(verbose=True)

base_model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
advanced_model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")


@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """根据任务复杂度选择对应的模型"""
    message_count = len(request.state["messages"])
    print("message count: ", message_count)

    if message_count > 10:
        model = base_model
    else:
        model = advanced_model
    print("selected model: ", model.model)
    request = request.override(model=model)
    return handler(request)


agent = create_agent(
    model=base_model,
    tools=[],
    middleware=[dynamic_model_selection]
)

messages = [

]
result = agent.invoke({"messages": [{"role": "user", "content": "1 + 1 = ?"}]})
print(result["messages"][-1].content_blocks)
