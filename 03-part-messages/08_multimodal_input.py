import base64

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# 将文件进行 base64 编码后传给 llm
with open('/Users/longkun/Downloads/more&less.pdf', 'rb') as f:
    pdf_bytes = f.read()

message1 = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Summarize the document"},
        {"type": "media", "data": base64.b64encode(pdf_bytes).decode("utf-8"), "mime_type": "application/pdf"}
    ]
}

load_dotenv()

model = init_chat_model(
    model="gemini-3.1-flash-lite",
    model_provider="google_genai"
)
result = model.invoke([message1])
print(result.content_blocks)
