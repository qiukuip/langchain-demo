from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
# custom_profile = {
#     "reasoning_effort_levels": ["low", "medium", "high"],
#     "reasoning_effort_default": "low"
# }
# ChatGoogleGenerativeAI also accepts "thinking_level"
model = init_chat_model(
    model="gemini-3.1-flash-lite",
    model_provider="google_genai",
    # profile=custom_profile,
)
print(f"reasoning_effort_level: {model.profile['reasoning_effort_levels']}")
print(f"reasoning_effort_default: {model.profile['reasoning_effort_default']}")
