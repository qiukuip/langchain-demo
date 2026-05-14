from langchain.agents import AgentState


class CustomState(AgentState):
    user_preferences: dict
