from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

custom_profile = {
    "max_input_tokens": 100_000,
    "tool_calling": False,
    "structured_output": False
}
load_dotenv()
model = init_chat_model(
    model="gemini-3.1-flash-lite-image",
    model_provider="google_genai",
    profile=custom_profile
)
messages = [HumanMessage("Create a picture of a cat")]
result = model.invoke(messages)
print(result.content_blocks)
