from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import get_usage_metadata_callback


load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite"
)
with get_usage_metadata_callback() as cb:
    model.invoke("你好！")
    print(cb.usage_metadata)

