from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
google_search_tool = {
    "google_search": {}
}
model_with_tools = model.bind(tools=[google_search_tool])
response = model_with_tools.invoke("今天苹果公司的股价是多少？")
print(response)
