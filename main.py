from collections.abc import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest, wrap_model_call, ModelResponse, wrap_tool_call
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import ToolMessage
from langchain_core.stores import InMemoryStore
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from contact_info import ContactInfo
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


base_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    max_tokens=1000,
    timeout=30,
    max_retries=2
)
advanced_model = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
    temperature=0.7,
    max_tokens=1000,
    timeout=30,
    max_retries=2
)


@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Choose model based on conversation complexity."""
    message_count = len(request.state["messages"])
    print("message_count: ", message_count)

    if message_count > 10:
        curr_model = advanced_model
    else:
        curr_model = base_model

    return handler(request.override(model=curr_model))


@wrap_model_call
def state_based_tools(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Filter tools based on conversation state."""
    state = request.state
    print("state: ", state)
    is_authenticated = state.get("authenticated", False)
    message_count = len(state["messages"])

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
def context_based_tools(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    if request.runtime is None or request.runtime.context is None:
        user_role = "viewer"
    else:
        user_role = request.runtime.context.get("user_role", "viewer")

    if user_role == "admin":
        pass
    elif user_role == "editor":
        tools = [t for t in request.tools if t.name != "delete_data"]
        request = request.override(tools=tools)
    else:
        tools = [t for t in request.tools if t.name.startswith("read_")]
        request = request.override(tools=tools)

    return handler(request)


@wrap_tool_call
def handle_tool_errors(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]):
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


# agent = create_agent(
#     name="research_assistant",
#     model=base_model,
#     tools=[search, get_weather],
#     middleware=[dynamic_model_selection, state_based_tools, user_role_prompt, handle_tool_errors],
#     system_prompt="You are a helpful assistant, be concise and accurate.",
#     context_schema=Context,
#     store=InMemoryStore()
# )

# messages = [
#     SystemMessage("You are a helpful assistant that translates English to Chinese. Translate the user sentence."),
#     HumanMessage("I love programming.")
# ]
# messages = [
#     {"role": "user", "content": "什么是机器学习？请用中文回答。"}
# ]
#
# result = agent.invoke({"messages": messages}, context={"user_role": "user", "user_id": "u01"})
# print(result)
#
# messages = [
#     {"role": "user", "content": "什么是机器学习？请用中文回答。"}
# ]
# result = agent.invoke({"messages": messages}, context={"user_role": "expert", "user_id": "u02"})
# print(result)

agent = create_agent(
    name="contact_info_extractor",
    model=base_model,
    response_format=ToolStrategy(ContactInfo)
)

messages = [
    {"role": "user", "content": "从以下信息中提取联系人信息：John Doe, john@gmail.com, (555) 123-45467"}
]
result = agent.invoke({"messages": messages})
print(result["structured_response"])
