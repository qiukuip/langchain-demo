from enum import Enum
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langchain.tools import tool


@tool
def save_data(query: str) -> str:
    """Save data."""
    return "Data saved successfully."


@tool
def load_data() -> str:
    """Load data."""
    return "Data loaded successfully."


load_dotenv()

model = init_chat_model(
    model="gemini-3.1-flash-lite", model_provider="google_genai", temperature=0.7
)

save_data_agent = create_agent(
    model=model,
    system_prompt="You are a save data agent. Use provided tools when need to save save.",
)
load_data_agent = create_agent(
    model=model,
    system_prompt="You are a load data agent. Use provided tools when need to load data.",
)


SUB_AGENTS = {"save_data": save_data_agent, "load_data": load_data_agent}


class AgentName(str, Enum):
    SAVE_DATA = "save_data"
    LOAD_DATA = "load_data"


@tool
def task(agent_name: AgentName, task_description: str) -> str:
    """Launch a ephemeral subagent for a task.

    Available agents:
    - save_data: Save data
    - load_data: Load data
    """
    agent = SUB_AGENTS[agent_name]
    result = agent.invoke({"messages": [{"role": "user", "content": task_description}]})
    return result["messages"][-1].content


main_agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[task],
    system_prompt="You coordinate specialized sub-agents. Available: save_data: Save data, load_data: Load data, Use the task tool to delegate work.",
)
result = main_agent.invoke(
    {
        "messages": [
            HumanMessage(
                "Save data for me, then load data for me. Do not ask me what data or file need to save or load, just call tools!!"
            )
        ]
    }
)
print(result)
