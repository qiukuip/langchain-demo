from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime


class LoggingMiddleware(AgentMiddleware):
    def before_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        print(f"About to call model with {len(state['messages'])} messages")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Model returned: {state['messages'][-1].content}")
        return None

    async def abefore_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        print("Async function abefore_model")


load_dotenv()
agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[],
    middleware=[LoggingMiddleware()],
)
result = agent.invoke({"messages": [{"role": "user", "content": "彩虹有几种颜色？"}]})
print(result)
