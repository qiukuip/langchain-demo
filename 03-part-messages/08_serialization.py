from langchain_core.load import dumpd, load
from langchain_core.messages import HumanMessage

message = HumanMessage("What is the Capital of France?")
serialized = dumpd(message)
restored = load(serialized)
print(restored.content_blocks)
