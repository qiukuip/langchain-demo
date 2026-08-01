from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.runtime import Runtime
from langgraph.typing import ContextT


class CustomState(AgentState):
    user_preferences: dict


class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState

    def before_model(self, state: CustomState, runtime: Runtime[ContextT]) -> dict[str, Any] | None:
        return {"user_preferences": {"style": "专业", "verbosity": "详细"}}

    def after_model(self, state: CustomState, runtime: Runtime[ContextT]) -> dict[str, Any] | None:
        if "user_preferences" in state:
            print(f"user_preferences: {state['user_preferences']}")
        else:
            print("user_preferences: Not found")


load_dotenv(verbose=True)

agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    middleware=[CustomMiddleware()],
)
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "我喜欢专业的解释。"}],
    }
)
print(result["messages"][-1].content_blocks)
