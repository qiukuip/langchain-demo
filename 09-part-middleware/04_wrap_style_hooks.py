from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel


class CustomContext(BaseModel):
    user_id: str


@wrap_model_call
def wrap_model(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    user_id = request.runtime.context.user_id
    print(f"User id: {user_id}")
    return handler(request)


load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7)
agent = create_agent(
    model=model, tools=[], middleware=[wrap_model], context_schema=CustomContext
)
input_message = {"role": "user", "content": "火星现在处于哪个季节？"}
result = agent.invoke(
    {"messages": [input_message]}, context=CustomContext(user_id="abc123")
)
print(result["messages"][-1].content_blocks)
