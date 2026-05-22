from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ClearToolUsesEdit,
    ContextEditingMiddleware,
    FilesystemFileSearchMiddleware,
    HostExecutionPolicy,
    LLMToolSelectorMiddleware,
    ModelCallLimitMiddleware,
    ModelFallbackMiddleware,
    ModelRetryMiddleware,
    PIIMiddleware,
    ShellToolMiddleware,
    SummarizationMiddleware,
    TodoListMiddleware,
    ToolCallLimitMiddleware,
    ToolRetryMiddleware,
)
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
custom_profile = {"max_input_tokens": 100_000, "tool_calling": True}
model = init_chat_model(
    model="gemini-3.1-flash-lite", model_provider="google_genai", profile=custom_profile
)
agent = create_agent(
    model=model,
    tools=[],
    checkpointer=InMemorySaver(),
    middleware=[
        SummarizationMiddleware(
            model=model,
            trigger=[("tokens", 3000), ("messages", 6)],
            keep=("messages", 20),
        ),
        ModelCallLimitMiddleware(thread_limit=10, run_limit=5, exit_behavior="end"),
        ToolCallLimitMiddleware(thread_limit=20, run_limit=10),
        ToolCallLimitMiddleware(
            tool_name="search", thread_limit=5, run_limit=3, exit_behavior="continue"
        ),
        ModelFallbackMiddleware(
            "google_genai:gemini-2.5-flash-lite", "google_genai:gemini-3-flash-preview"
        ),
        PIIMiddleware(pii_type="email", strategy="redact", apply_to_input=True),
        PIIMiddleware(pii_type="credit_card", strategy="mask", apply_to_input=True),
        PIIMiddleware(
            pii_type="phone_number",
            detector=r"\+?\d{3}[\s.-]?\d{4}[\s.-]?\d{4}",
            strategy="mask",
            apply_to_output=True,
        ),
        TodoListMiddleware(),
        LLMToolSelectorMiddleware(
            model="google_genai:gemini-2.5-flash-lite",
            system_prompt="You are a helpful tool selector.",
            max_tools=3,
            always_include=[],
        ),
        ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
        ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=2.0),
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=100_000,
                    keep=3,
                    clear_tool_inputs=False,
                    exclude_tools=[],
                    placeholder="['cleared']",
                )
            ]
        ),
        ShellToolMiddleware(
            workspace_root="/Users/longkun/Documents/others",
            execution_policy=HostExecutionPolicy(),
        ),
        FilesystemFileSearchMiddleware(
            root_path="/Users/longkun/Documents/others", use_ripgrep=True
        ),
    ],
)
input_message1 = {
    "role": "user",
    "content": "Hello, my name is Alice, my phone is 123-1223-2334, my credit cart number is 1234556789",
}
input_message2 = {
    "role": "user",
    "content": "What is my phone number and credit card number?",
}
input_message3 = {"role": "user", "content": "List files in my home directory"}
input_message4 = {"role": "user", "content": "Find Java file and explain it's content"}
# respone1 = agent.invoke(
#     {"messages": [input_message1]}, config={"configurable": {"thread_id": "09-02"}}
# )
# print(respone1["messages"][-1].content_blocks)
# print("=====")
# response2 = agent.invoke(
#     {"messages": [input_message2]}, config={"configurable": {"thread_id": "09-02"}}
# )
# print(response2["messages"][-1].content_blocks)
# response3 = agent.invoke(
#     {"messages": [input_message3]}, config={"configurable": {"thread_id": "09-02"}}
# )
# print(response3["messages"][-1].content_blocks)
response4 = agent.invoke(
    {"messages": [input_message4]}, config={"configurable": {"thread_id": "09-02"}}
)
print(response4["messages"][-1])
