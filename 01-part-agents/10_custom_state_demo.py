from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState
from langchain.agents import create_agent
from langchain.agents.middleware import before_model
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.runtime import Runtime
from langgraph.typing import ContextT


class CustomState(AgentState):
    user_preferences: dict[str, Any]


@before_model
def before_model(state: CustomState, runtime: Runtime[ContextT]) -> dict[str, Any] | None:
    user_preferences = state["user_preferences"]
    print(f"style = {user_preferences['style']}")
    print(f"verbosity = {user_preferences['verbosity']}")
    return None


load_dotenv(verbose=True)

agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    middleware=[before_model],
    state_schema=CustomState
)
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "我喜欢专业的解释。"}],
        "user_preferences": {"style": "专业", "verbosity": "详细"}
    }
)
print(result["messages"][-1].content_blocks)
