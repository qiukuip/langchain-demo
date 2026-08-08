from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()
grounding_tool = genai.types.Tool(google_search=genai.types.GoogleSearch())
config = genai.types.GenerateContentConfig(tools=[grounding_tool])
response = client.models.generate_content(
    model="gemini-2-flash-lite",
    contents="今天苹果公司的股价是多少？",
    config=config
)

print(response.text)
