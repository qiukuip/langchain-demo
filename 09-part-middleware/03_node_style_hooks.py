from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_model, before_model
from langchain.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.runtime import Runtime

load_dotenv()


@before_model(can_jump_to=["end"])
def check_message_limit(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print("before model hook call")
    print(f"message count: {len(state['messages'])}")
    if len(state["messages"]) >= 2:
        return {"messages": [AIMessage("对话消息数量已超上限")], "jump_to": "end"}
    return None


@after_model
def log_response(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print(f"Model returned: {state['messages'][-1].content_blocks}")
    return None


model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
agent = create_agent(
    model=model, tools=[], middleware=[check_message_limit, log_response]
)
input_message = {"role": "user", "content": "生日蛋糕的平均价格一般是多少？"}
result = agent.invoke({"messages": [input_message]})
print(result)
