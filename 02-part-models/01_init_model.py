from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model2 = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite",
    temperature=0.7,
    max_tokens=1000,
    timeout=30,
    max_retries=2
)

result = model2.invoke("请问唐朝共存在了多少年？直接给出数字，不需要解释。")
print(result)
