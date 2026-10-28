from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool


@tool
def get_weather(city: str):
    """Get weather information for a city."""
    return f"It's 75 degrees and sunny in {city}."


evaluator = create_trajectory_llm_as_judge(
    model="ollama:llama3.1",
    prompt=TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE,
)


def test_trajectory_quality():
    agent = create_agent(
        model="ollama:llama3.1",
        tools=[get_weather]
    )
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in Seattle?")]
    })

    evaluation = evaluator(
        outputs=result["messages"]
    )
    assert evaluation["score"] is True
