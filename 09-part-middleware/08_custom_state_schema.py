from typing import Any, NotRequired
from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langgraph.runtime import Runtime


class CustomState(AgentState):
    model_call_count: NotRequired[int]
    user_id: NotRequired[int]


class CallCounterMiddleware(AgentMiddleware[CustomState]):
    state_schema = CustomState

    def before_model(
        self, state: CustomState, runtime: Runtime
    ) -> dict[str, Any] | None:
        count = state.get("model_call_count", 0)
        if count > 10:
            return {"jump_to": "end"}
        return None

    def after_model(
        self, state: CustomState, runtime: Runtime
    ) -> dict[str, Any] | None:
        return {"model_call_count": state.get("model_call_count", 0) + 1}


load_dotenv()
model = init_chat_model(
    model="gemini-3.1-flash-lite", model_provider="google_genai", temperature=0.7
)
agent = create_agent(model=model, tools=[], middleware=[CallCounterMiddleware()])
result = agent.invoke(
    {
        "messages": [
            HumanMessage("骑个破摩托车，在居民区道路上疯狂制造噪音的人是什么心理？")
        ],
        "model_call_count": 10,
        "user_id": "abc123",
    }
)
print(result)
