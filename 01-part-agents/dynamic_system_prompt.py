from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from context import Context

load_dotenv(verbose=True)


@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    """根据用户角色生成系统提示词。"""
    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "你是一个有用的 AI 助手。"

    if user_role == "expert":
        return f"{base_prompt}请提供详细且专业的信息。"
    elif user_role == "user":
        return f"{base_prompt}简单解释概念，避免使用行业术语。"

    return base_prompt


agent = create_agent(
    name="research_assistant",
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    middleware=[user_role_prompt],
    context_schema=Context
)
result = agent.invoke(
    {"messages": [HumanMessage("什么是机器学习？")]},
    context=Context(user_id="u01", user_role="expert")
)
print(result["messages"][-1].content)
