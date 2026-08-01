import urllib.error
import urllib.request

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool


@tool
def fetch_text_from_url(url: str) -> str:
    """fetch text from url"""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read()
            text = raw.decode("utf-8", errors="replace")
            return text
    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"


SYSTEM_PROMPT = """You are a literary data assistant.

## Capabilities

- `fetch_text_from_url`: loads document text from a URL into the conversation.
Do not guess line counts or positions—ground them in tool results from the saved file."
"""

load_dotenv()

model = init_chat_model(
    model="gemini-2.5-flash-lite",
    model_provider="google-genai",
    temperature=0.3,
    max_tokens=25000,
    timeout=600
)
agent = create_agent(
    model=model,
    tools=[fetch_text_from_url],
    system_prompt=SYSTEM_PROMPT,
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Get content from http://book.yidiantime.com/xxshuo/detail/1489240601"}]},
    config={"configurable": {"thread_id": "0102"}}
)
print(result["messages"][-1].content_blocks)
