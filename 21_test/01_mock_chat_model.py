from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain.messages import AIMessage, ToolCall
from langchain_core.language_models import FakeListChatModel

model = GenericFakeChatModel(
    messages=iter([
        AIMessage(content="Test AI message1", tool_calls=[ToolCall(name="foo", args={"bar": "baz"}, id="call_1")]),
        "bar"
    ]))

response = model.invoke("hello")
print(response.content_blocks)

print("====")

model = FakeListChatModel(responses=["Paris", "The Eiffel Tower"])
response = model.invoke("What is the capital of France?")
print(response.content_blocks)
# AIMessage(content='Paris', ...)
response = model.invoke("What is a famous landmark there?")
# AIMessage(content='The Eiffel Tower', ...)
print(response.content_blocks)
