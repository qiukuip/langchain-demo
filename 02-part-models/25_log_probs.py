from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="你好",
    config=types.GenerateContentConfig(
        temperature=0.2,
        response_logprobs=True,
        logprobs=5,
    )
)

# 直接从 candidates 中获取 logprobs
logprobs_result = response.candidates[0].logprobs_result
print(logprobs_result)
