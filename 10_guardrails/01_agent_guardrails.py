from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware, hook_config
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage
from langgraph.runtime import Runtime


class ContentFilterMiddleware(AgentMiddleware):
    """Block requests containing banned keywords"""

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

        content = first_message.content.lower()
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
        self.safety_model = init_chat_model(model="google_genai:gemini-3.1-flash-lite")

    @hook_config(can_jump_to=["end"])
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None

        safety_prompt = f"""Evaluate this response is safe and approprivate, respond with only 'SAFE' or 'UNSAFE', response: {last_message.content}"""
        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])

        if "UNSAFE" in result.content:
            last_message.content = (
                "I cannot provide that response. Please rephrase your request."
            )

        return None


load_dotenv()
agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[],
    middleware=[
        # ContentFilterMiddleware(banned_keywords=["hack", "malware", "exploit"])
        SafetyGuardrailMiddleware()
    ],
)
input_message1 = HumanMessage("How do I hack into a database?")
input_message2 = HumanMessage("How do I make a explosive?")
result = agent.invoke({"messages": [input_message2]})
print(result["messages"][-1].content_blocks)
