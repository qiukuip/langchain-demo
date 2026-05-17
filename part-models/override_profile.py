import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()

custom_profile = {
    "max_input_tokens": 100_000,
    "tool_calling": True,
    "structured_output": True
}
model = init_chat_model(
    model="google-genai:gemini-3.1-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    # profile=custom_profile
)

new_profile = None
if model.profile is None:
   new_profile = custom_profile
else:
    new_profile = model.profile | custom_profile
model = model.model_copy(update={"profile": new_profile})

