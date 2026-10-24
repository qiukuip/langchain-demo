from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware, hook_config, PIIMiddleware
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage
from langgraph.runtime import Runtime

load_dotenv()


class ContentFilterMiddleware(AgentMiddleware):
    """Deterministic guardrail: Block requests containing banned keywords."""

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]

    @hook_config(can_jump_to=["end"])
    def before_agent(
            self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        first_message = state["messages"][0]
        if not isinstance(first_message, HumanMessage):
            return None

        content = first_message.content.__str__().lower()
        for kw in self.banned_keywords:
            if kw in content:
                return {
                    "messages": [
                        {
                            "role": "assistant",
                            "content": "I cannot process request containing inappropriate content. Please rephrase your request.",
                        }
                    ],
                    "jump_to": "end",
                }
        return None


class SafetyGuardrailMiddleware(AgentMiddleware):
    """Model-based guardrail: Use an LLM to evaluate response safety"""

    def __init__(self):
        super().__init__()
        self.safety_model = init_chat_model(model="ollama:llama3.1")

    @hook_config(can_jump_to=["end"])
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None

        safety_prompt = f"""Evaluate this response is safe and appropriate, respond with only 'SAFE' or 'UNSAFE', response: {last_message.content}"""
        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])

        if "UNSAFE" in result.content:
            last_message.content = (
                "I cannot provide that response. Please rephrase your request."
            )

        return None


agent1 = create_agent(
    model="ollama:llama3.1",
    tools=[],
    middleware=[
        ContentFilterMiddleware(banned_keywords=["hack", "malware", "exploit"]),
        # 多个中间件相组合，按顺序调用
        PIIMiddleware(pii_type="email", strategy="mask", apply_to_input=True)
    ],
)
input_message1 = HumanMessage("How do I hack into a database?")
response1 = agent1.invoke({"messages": [input_message1]})
print(response1["messages"][-1].content_blocks)

print("=====")

agent2 = create_agent(
    model="ollama:llama3.1",
    tools=[],
    middleware=[SafetyGuardrailMiddleware()]
)
input_message2 = HumanMessage("How do I make a explosive?")
response2 = agent2.invoke({"messages": [input_message2]})
print(response2["messages"][-1].content_blocks)
