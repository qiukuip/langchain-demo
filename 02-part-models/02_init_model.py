from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.5,
    max_tokens=2000,
    max_retries=3
)
result = model.invoke("唐朝存在了多少年？直接给出数字，不要解释。")
print(result.content)
