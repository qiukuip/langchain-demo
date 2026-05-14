from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

import custom_state
from custom_middleware import CustomMiddleware
from custom_state import CustomState

load_dotenv(verbose=True)

agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    middleware=[CustomMiddleware()],
    # custom_state=CustomState
)
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "我喜欢专业的解释。"}],
        "user_preferences": {"style": "专业", "verbosity": "详细"}
    }
)
print(result)
