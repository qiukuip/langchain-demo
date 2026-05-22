import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter


load_dotenv()

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,  # 1 request evenry 10s
    check_every_n_seconds=0.1,  # check every 100ms weather allowed to make a request
    max_bucket_size=10,  #Controls the max burst size
)
# model = init_chat_model(
#     model="gemini-3.1-flash-lite",
#     api_key=os.getenv("GOOGLE_API_KEY"),
#     rate_limiter=rate_limiter,
#     model_provider="google_genai"
# ).bind(response_logprobs=True,
#        logprobs=10)
model = init_chat_model(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    rate_limiter=rate_limiter,
    model_provider="google_genai"
)
response = model.invoke("为什么很少看见绿色的花？")
print(response.content_blocks)
