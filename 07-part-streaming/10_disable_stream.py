from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", streaming=False)
agent = create_agent(model=model)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Introduce yourself to me."}]},
    version="v2",
)
print(result)
print(result.interrupts)
print(result.value)
