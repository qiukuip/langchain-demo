from langchain.agents import AgentState


class CustomState(AgentState):
    username: str

