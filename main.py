from collections.abc import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest, wrap_model_call, ModelResponse
from langchain_core.messages import ToolMessage
from langchain_core.stores import InMemoryStore
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.testing import startswith_

from context import Context

load_dotenv(verbose=True)


@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for query: {query}"


@tool
def get_weather(city: str) -> str:
    """Get weather information for a location."""
    return f"It's always sunny in {city}"


@wrap_model_call
def state_based_tools(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Filter tools based on conversation state."""
    state = request.state
    is_authenticated = state.get("authenticated", False)
    message_count = len(state("messages"))

    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith("public_")]
        request = request.override(tools=tools)
    elif message_count < 5:
        tools = [t for t in request.tools if t.name != "advanced_search"]
        request = request.override(tools=tools)

    return handler(request)


@wrap_model_call
def store_based_tools(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Filter tools based on Store preference."""
    user_id = request.runtime.context.user_id

    store = request.runtime.store
    feature_flags = store.get(("feature",), user_id)

    if feature_flags:
        enabled_features = feature_flags.value.get("enabled_tools", [])
        tools = [t for t in request.tools if t.name in enabled_features]
        request = request.override(tools=tools)

    return handler(request)


@wrap_model_call
def handle_tool_errors(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(content=f"Tool error: Please check your input and try again.({str(e)})",
                           tool_call_id=request.tool_call["id"])


@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on user role."""
    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "You are a helpful assistant."

    if user_role == "expert":
        return f"{base_prompt} Provide detailed technical responses."
    elif user_role == "beginner":
        return f"{base_prompt} Explain concepts simply and avoid jargon."

    return base_prompt


model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    max_tokens=1000,
    timeout=30,
    max_retries=2,
)
agent = create_agent(
    model=model,
    tools=[search, get_weather],
    middleware=[state_based_tools, user_role_prompt, handle_tool_errors],
    system_prompt="You are a helpful assistant, be concise and accurate.",
    context_schema=Context,
    store=InMemoryStore
)

# messages = [
#     SystemMessage("You are a helpful assistant that translates English to Chinese. Translate the user sentence."),
#     HumanMessage("I love programming.")
# ]
messages = [
    {"role": "user", "content": "Explain machine learning"}
]

result = agent.invoke({"messages": messages}, context={"user_role": "expert"})

print(result["messages"][-1].content_blocks)
