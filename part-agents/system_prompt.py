from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(verbose=True)

base_model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
literacy_agent = create_agent(
    model=base_model,
    system_prompt=SystemMessage(
        content=[
            {
                "type": "text",
                "text": "You are an AI assistant tasked with analyzing literary works."
            },
            {
                "type": "text",
                "text": "<the entire contents of 'Pride and Prejudice'>",
                "cache_control": {"type": "ephemeral"}
            }
        ]
    )
)

result = literacy_agent.invoke(
    {
        "messages": [HumanMessage("Analyze the major themes in 'Pride and Prejudice'")]
    }
)
print(result)
