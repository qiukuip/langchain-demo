from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy, RedactionRule
from langchain_core.messages import HumanMessage

load_dotenv()

agent = create_agent(
    model="ollama:llama3.1",
    tools=[],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/Users/longkun/Documents/demos/langchain-demo.nosync/09-part-middleware/workspace1",
            startup_commands="echo $ME",
            shutdown_commands="echo shutdown session",
            shell_command="/bin/zsh",
            execution_policy=HostExecutionPolicy(),
            redaction_rules=[RedactionRule(pii_type="email", strategy="mask")],
            env={"ME": "aid"}
        )
    ]
)
response = agent.invoke(
    {
        "messages": [HumanMessage("使用 java -version 命令验证当前 Java 环境是否可用。")]
    }
)
for message in response["messages"]:
    print(message.pretty_print())
