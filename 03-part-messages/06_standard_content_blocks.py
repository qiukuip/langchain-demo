from langchain_core.messages import AIMessage


message = AIMessage(
    content=[
        {
            "type": "thinking",
            "thinking": "thinking content...",
            "signature": "WauJskdzp",
        },
        {"type": "text", "text": "text content..."},
    ]
)

content_blocks = message.content_blocks
print(content_blocks)

