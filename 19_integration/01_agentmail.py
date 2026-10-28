"""Use AgentMail tools from a LangChain agent.

Set ``AGENTMAIL_API_KEY`` in the repository's ``.env`` file before running.
The example uses a local Ollama model, so Ollama must be running with the
``llama3.1`` model available.
"""

import os

import httpx
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_agentmail import AgentMailToolkit
from langchain_ollama import ChatOllama

load_dotenv()
AGENTMAIL_BASE_URL = "https://api.agentmail.to/v0"

# This installed toolkit version has no list-inboxes tool. Use the current
# AgentMail REST API to find an inbox, then let the toolkit list its messages.
toolkit = AgentMailToolkit(base_url=AGENTMAIL_BASE_URL)
list_messages_tool = next(
    tool for tool in toolkit.get_tools() if tool.name == "list_messages"
)

response = httpx.get(
    f"{AGENTMAIL_BASE_URL}/inboxes",
    headers={"Authorization": f"Bearer {os.environ['AGENTMAIL_API_KEY']}"},
    timeout=30,
)
response.raise_for_status()
inboxes = response.json().get("inboxes", [])
if not inboxes:
    raise RuntimeError("No AgentMail inboxes found. Create an inbox first.")

# This installed toolkit version does not expose list_inboxes. Resolve the
# inbox before invoking the agent, so the model never has to invent an ID.
selected_inbox = inboxes[0]
inbox_email = selected_inbox.get("email") or selected_inbox.get("inbox_id")


@tool
def list_recent_messages() -> str:
    """List recent messages from the selected AgentMail inbox."""
    return list_messages_tool.invoke(
        {"inbox_id": selected_inbox["inbox_id"], "limit": 10}
    )


agent = create_agent(
    model=ChatOllama(model="llama3.1"),
    tools=[
        *(tool for tool in toolkit.get_tools() if tool.name != "list_messages"),
        list_recent_messages,
    ],
    system_prompt=(
        f"You are an email assistant for the inbox {inbox_email}. "
        "Use list_recent_messages to inspect its recent email and summarize "
        "the newest message. Do not send or reply to email unless the user "
        "explicitly asks you to."
    ),
)

result = agent.invoke(
    {"messages": [("user", "Summarize the most recent email in my inbox.")]}
)
print(result["messages"][-1].content)
