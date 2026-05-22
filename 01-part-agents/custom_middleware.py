from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime
from langgraph.typing import ContextT

from custom_state import CustomState


class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState

    def before_model(self, state: CustomState, runtime: Runtime[ContextT]) -> dict[str, Any] | None:
        state["state1"] = "value of state1"
        state["state2"] = "value of state2"
