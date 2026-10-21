from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import FilesystemFileSearchMiddleware
from langchain_core.messages import HumanMessage

load_dotenv()

workspace = Path(__file__).parent / "workspace"

agent = create_agent(
    model="ollama:llama3.1",
    tools=[],
    middleware=[
        FilesystemFileSearchMiddleware(
            root_path=workspace.__str__(),
            use_ripgrep=True,
            max_file_size_mb=10
        )
    ]
)
result = agent.invoke(
    {
        "messages": [HumanMessage(content="找出所有包含 hello  的文件。")]
    }
)
for message in result["messages"]:
    print(message.pretty_print())
