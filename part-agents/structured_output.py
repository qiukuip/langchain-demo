from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from contact_info import ContactInfo

load_dotenv(verbose=True)

agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    response_format=ToolStrategy(ContactInfo)
)
result = agent.invoke(
    {
        "messages": [HumanMessage("请从以下信息中提取信息：张三 z@gmail.com (555) 123-4567 韩国大邱")]
    }
)
print(result["messages"][-1].content)
