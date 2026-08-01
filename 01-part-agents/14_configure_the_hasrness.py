from deepagents import FilesystemMiddleware, MemoryMiddleware, SubAgentMiddleware, SubAgent
from deepagents.backends import StateBackend
from deepagents.middleware import SummarizationMiddleware, SkillsMiddleware
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware, PIIMiddleware, ModelRetryMiddleware, ToolRetryMiddleware, \
    HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


@tool
def search_user_count(query: str) -> str:
    """Search for a query and return a short summary."""
    return f"There are 300 users"


load_dotenv()

backend = StateBackend()
model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.5,
    max_tokens=2000,
    timeout=600
)
agent = create_agent(
    name="MyAgent",
    model=model,
    tools=[search_user_count],
    middleware=[
        FilesystemMiddleware(backend=backend),
        SummarizationMiddleware(backend=backend, model=model),
        MemoryMiddleware(backend=backend, sources=["./AGENTS.md"]),
        SkillsMiddleware(backend=backend, sources=["./skills/"]),
        TodoListMiddleware(),
        SubAgentMiddleware(
            backend=backend,
            subagents=[
                SubAgent(
                    name="researcher",
                    model=model,
                    description="Searches and returns a structured summary.",
                    system_prompt="Use the search tool to research the question and summarize key points.",
                    tools=[search_user_count],
                    middleware=[]
                )
            ]
        ),
        ModelRetryMiddleware(max_retries=3),
        ToolRetryMiddleware(max_retries=3),
        PIIMiddleware("email"),
        HumanInTheLoopMiddleware(interrupt_on={"write_file": True})
    ]
)
