from langchain.agents.middleware import AgentMiddleware

from custom_state import CustomState


class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState
    tools = []
