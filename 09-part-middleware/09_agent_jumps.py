from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_agent, after_model
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage
from langgraph.runtime import Runtime


@after_agent
def after_agent_call(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print("after agent call")
    return None


@after_model(can_jump_to=["end"])
def check_content_blocked(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    last_message = state["messages"][-1].content_blocks
    if len(last_message) > 10:
        return {
            "messages": [AIMessage("I cannot response to that request.")],
            "jump_to": "end",
        }
    return None


load_dotenv()
model = init_chat_model(
    model="gemini-3.1-flash-lite", model_provider="google_genai", temperature=0.8
)
agent = create_agent(
    model=model, tools=[], middleware=[after_agent_call, check_content_blocked]
)
result = agent.invoke({"messages": [HumanMessage("狗的寿命一般有多长？")]})
print(result)
