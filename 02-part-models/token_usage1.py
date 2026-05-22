import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import UsageMetadataCallbackHandler


load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)
callback = UsageMetadataCallbackHandler()
response = model.invoke("你好！", config={"callbacks": [callback]})
print(response)

