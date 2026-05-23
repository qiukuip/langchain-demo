from typing import Any, NotRequired

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_model
from langchain.chat_models import init_chat_model
from langgraph.runtime import Runtime


class TrackingState(AgentState):
    model_call_count: NotRequired[int]


@after_model(state_schema=TrackingState)
def increment_after_model(
    state: TrackingState, runtime: Runtime
) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}


load_dotenv()
model = init_chat_model(
    model="gemini-3.1-flash-lite", model_provider="google_genai", temperature=0.7
)
agent = create_agent(model=model, tools=[], middleware=[increment_after_model])
input_message = {"role": "user", "content": "火星的赤道周长是多少公里？"}
result = agent.invoke({"messages": [input_message]})
print(result)
print(result["messages"][-1].content_blocks)
