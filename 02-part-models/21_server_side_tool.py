from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
google_maps_tool = {
    "google_maps": {}
}
model_with_tools = model.bind(tools=[google_maps_tool])
response = model_with_tools.invoke("推荐附近3公里内的咖啡店。")
print(response.content_blocks)
