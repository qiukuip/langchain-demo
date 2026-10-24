from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_protocol import Command
from langgraph.store.memory import InMemoryStore


@tool
def check_authentication(
        runtime: ToolRuntime
) -> str:
    """Check if user is authenticated."""
    # Read from State: check current auth status
    current_state = runtime.state
    is_authenticated = current_state.get("authenticated", False)

    if is_authenticated:
        return "User is authenticated"
    else:
        return "User is not authenticated"


agent = create_agent(
    model="gpt-5.5",
    tools=[check_authentication]
)


@dataclass
class Context:
    user_id: str


@tool
def get_preference(
        preference_key: str,
        runtime: ToolRuntime[Context]
) -> str:
    """Get user preference from Store."""
    user_id = runtime.context.user_id

    # Read from Store: get existing preferences
    store = runtime.store
    existing_prefs = store.get(("preferences",), user_id)

    if existing_prefs:
        value = existing_prefs.value.get(preference_key)
        return f"{preference_key}: {value}" if value else f"No preference set for {preference_key}"
    else:
        return "No preferences found"


agent1 = create_agent(
    model="gpt-5.5",
    tools=[get_preference],
    context_schema=Context,
    store=InMemoryStore()
)


@dataclass
class Context:
    user_id: str
    api_key: str
    db_connection: str


@tool
def fetch_user_data(
        query: str,
        runtime: ToolRuntime[Context]
) -> str:
    """Fetch data using Runtime Context configuration."""
    # Read from Runtime Context: get API key and DB connection
    user_id = runtime.context.user_id
    api_key = runtime.context.api_key
    db_connection = runtime.context.db_connection

    # Use configuration to fetch data
    results = perform_database_query(db_connection, query, api_key)

    return f"Found {len(results)} results for user {user_id}"


def perform_database_query(db_connection: str, query: str, api_key: str) -> str:
    pass


agent2 = create_agent(
    model="gpt-5.5",
    tools=[fetch_user_data],
    context_schema=Context
)

# Invoke with runtime context
result = agent2.invoke(
    {"messages": [{"role": "user", "content": "Get my data"}]},
    context=Context(
        user_id="user_123",
        api_key="sk-...",
        db_connection="postgresql://..."
    )
)


@tool
def authenticate_user(
        password: str,
        runtime: ToolRuntime
) -> Command:
    """Authenticate user and update State."""
    # Perform authentication (simplified)
    if password == "correct":
        # Write to State: mark as authenticated using Command
        return Command(
            update={"authenticated": True},
        )
    else:
        return Command(update={"authenticated": False})


agent3 = create_agent(
    model="gpt-5.5",
    tools=[authenticate_user]
)


@dataclass
class Context:
    user_id: str


@tool
def save_preference(
        preference_key: str,
        preference_value: str,
        runtime: ToolRuntime[Context]
) -> str:
    """Save user preference to Store."""
    user_id = runtime.context.user_id

    # Read existing preferences
    store = runtime.store
    existing_prefs = store.get(("preferences",), user_id)

    # Merge with new preference
    prefs = existing_prefs.value if existing_prefs else {}
    prefs[preference_key] = preference_value

    # Write to Store: save updated preferences
    store.put(("preferences",), user_id, prefs)

    return f"Saved preference: {preference_key} = {preference_value}"


agent4 = create_agent(
    model="gpt-5.5",
    tools=[save_preference],
    context_schema=Context,
    store=InMemoryStore()
)
