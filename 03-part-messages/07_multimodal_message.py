from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "请使用中文描述一下这张图片"},
            {
                "type": "image",
                "url": "https://tse3.mm.bing.net/th/id/OIP.QiFZTRUHXrLP0GBVbV44LQHaEK?rs=1&pid=ImgDetMain&o=7&rm=3",
            },
        ],
    }
]
model = init_chat_model("google_genai:gemini-2.5-flash-lite")
response = model.invoke(messages)
print(response)

