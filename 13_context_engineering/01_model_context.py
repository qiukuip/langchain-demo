from typing import Callable

from langchain.agents.middleware import dynamic_prompt, ModelRequest, wrap_model_call, ModelResponse
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from pydantic import BaseModel, Field


@dynamic_prompt
def dynamic_prompt(request: ModelRequest) -> str:
    messages = request.state["messages"]
    base_prompt = "You are a helpful assistant."
    if len(messages) > 10:
        base_prompt += "\nThis is a long conversation, be extra concise."
    return base_prompt


@wrap_model_call
def wrap_model_call(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    upload_files = request.state.get("upload_files", [])
    if upload_files:
        file_descriptions = []
        for file in upload_files:
            file_descriptions.append(
                f"- {file['name']} ({file['type']}: {file['summary']})"
            )
        file_context = f"Files you have to access to in this conversation: {', '.join(file_descriptions)}"
        messages = [
            *request.state["messages"],
            {"role": "user", "content": file_context}
        ]

        request = request.override(messages=messages)
    return handler(request)


@tool(parse_docstring=True)
def search_orders(
        user_id: str,
        status: str,
        limit: int = 10
) -> str:
    """Search for user orders by status.

    Use this when the user asks about order history or wants to check
    order status. Always filter by the provided status.

    Args:
        user_id: Unique identifier for the user
        status: Order status: 'pending', 'shipped', or 'delivered'
        limit: Maximum number of results to return
    """
    pass


@wrap_model_call
def state_based_tools(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Filter tools based on conversation State."""
    # Read from State: check if user has authenticated
    state = request.state
    is_authenticated = state.get("authenticated", False)
    message_count = len(state["messages"])

    # Only enable sensitive tools after authentication
    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith("public_")]
        request = request.override(tools=tools)
    elif message_count < 5:
        # Limit tools early in conversation
        tools = [t for t in request.tools if t.name != "advanced_search"]
        request = request.override(tools=tools)

    return handler(request)


large_model = init_chat_model("claude-sonnet-4-6")
standard_model = init_chat_model("gpt-5.5")
efficient_model = init_chat_model("gpt-5.4-mini")


@wrap_model_call
def state_based_model(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Select model based on State conversation length."""
    # request.messages is a shortcut for request.state["messages"]
    message_count = len(request.messages)

    if message_count > 20:
        # Long conversation - use model with larger context window
        model = large_model
    elif message_count > 10:
        # Medium conversation
        model = standard_model
    else:
        # Short conversation - use efficient model
        model = efficient_model

    request = request.override(model=model)

    return handler(request)


class SimpleResponse(BaseModel):
    """Simple response for early conversation."""
    answer: str = Field(description="A brief answer")


class DetailedResponse(BaseModel):
    """Detailed response for established conversation."""
    answer: str = Field(description="A detailed answer")
    reasoning: str = Field(description="Explanation of reasoning")
    confidence: float = Field(description="Confidence score 0-1")


@wrap_model_call
def state_based_output(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Select output format based on State."""
    # request.messages is a shortcut for request.state["messages"]
    message_count = len(request.messages)

    if message_count < 3:
        # Early conversation - use simple format
        request = request.override(response_format=SimpleResponse)
    else:
        # Established conversation - use detailed format
        request = request.override(response_format=DetailedResponse)

    return handler(request)
