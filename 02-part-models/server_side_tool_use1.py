from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client()
grounding_tool = genai.types.Tool(google_search=genai.types.GoogleSearch())
config = genai.types.GenerateContentConfig(tools=[grounding_tool])
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="谁赢得了2024年欧洲杯？",
    config=config
)

print(response.text)
