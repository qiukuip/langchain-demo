from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ProviderToolSearchMiddleware
from langchain_core.tools import tool

load_dotenv()


@tool(extras={"defer_loading": True})
def fetch_data() -> list:
    """Fetch data from database."""
    return [{"id": 1, "name": "data1"}]


agent = create_agent(
    model="ollama:llama3.1",
    tools=[fetch_data],
    middleware=[
        # 服务端决定使用哪些工具，再加在完整的工具 schema
        # LLMToolSelector 是模型先选择合适的工具，再将每一个选择的工具的完整 schema 传给服务端
        ProviderToolSearchMiddleware(
            searchable_tools=["fetch_data"],
        )
    ]
)
