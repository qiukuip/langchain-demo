from langchain.agents import AgentState


class UserPreference(AgentState):
    user_preferences: dict

