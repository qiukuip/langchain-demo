from pathlib import Path

from deepagents import FilesystemMiddleware
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

load_dotenv()

workspace = Path(__file__).parent / "workspace"

agent = create_agent(
    model="ollama:llama3.1",
    tools=[],
    middleware=[
        FilesystemMiddleware(
            backend=FilesystemBackend(
                root_dir=workspace
            ),
            system_prompt="如有必要，请保存文件内容。",
            custom_tool_descriptions={
                "ls": "使用此工具列出指定目录下的文件",
                "read_file": "使用此工具读取文件内容",
                "write_file": "使用此工具将文件写入磁盘",
                "edit_file": "使用此工具编辑文件",
                "grep": "使用此工具过滤文件内容"
            },
            tools=["ls", "read_file", "write_file", "edit_file", "grep"],
        )
    ]
)
response = agent.invoke(
    {
        "messages": [HumanMessage("重复10遍“你好”，写入hello.txt中。")]
    }
)
for message in response["messages"]:
    print(message.pretty_print())
