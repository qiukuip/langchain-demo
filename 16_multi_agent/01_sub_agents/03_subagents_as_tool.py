from langchain.tools import tool
from langchain.agents import create_agent

# Sub-agents developed by different teams
research_agent = create_agent(
    model="gpt-5.5",
    system_prompt="You are a research specialist."
)

writer_agent = create_agent(
    model="gpt-5.5",
    system_prompt="You are a writing specialist."
)

# Registry of available sub-agents
SUBAGENTS = {
    "research": research_agent,
    "writer": writer_agent,
}


@tool
def task(
        agent_name: str,
        description: str
) -> str:
    """Launch an ephemeral subagent for a task.

    Available agents:
    - research: Research and fact-finding
    - writer: Content creation and editing
    """
    agent = SUBAGENTS[agent_name]
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": description}
        ]
    })
    return result["messages"][-1].content


@tool
def list_agent(query: str) -> str | None:
    """List all agents available."""
    for agent in SUBAGENTS.keys():
        if agent in query:
            return agent
    return None


# Main coordinator agent
main_agent = create_agent(
    model="gpt-5.5",
    tools=[task, list_agent],
    system_prompt=(
        "You coordinate specialized sub-agents."
        "Available: "
        "research (fact-finding),"
        "writer (content creation)."
        "Use the task tool to delegate work."
    )
)
