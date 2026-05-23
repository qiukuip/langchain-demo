from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
agent = create_agent(
    model=model,
    tools=[],
    middleware=[TodoListMiddleware()],
)
message_content = """
请分析加利福尼亚中央谷地的杏仁种植业在未来30年面临的气候变化风险，并估算其经济影响。具体需要回答：假设当前气候趋势持续，到2050年，
加利福尼亚中央谷地杏仁产量可能减少的百分比及其对该州经济的潜在年度损失是多少美元？这些美元按照2025年11月的汇率能够购买多少比特币？
这是一个复杂的多步骤任务，请务必先调用 write_todos 工具，将问题拆解为具体的待办任务清单，然后再开始规划。
"""
message_content1 = """
请帮我规划一次去上海的三天两夜的旅行。这是一个复杂的多步骤任务，请务必先调用 write_todos 工具，将行程拆解为具体的待办任务清单，然后再开始规划。
"""
input_message = {"role": "user", "content": message_content}
result = agent.invoke({"messages": [input_message]})
print(result)
