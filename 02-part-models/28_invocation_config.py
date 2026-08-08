from typing import Any, Dict
from uuid import UUID

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class MyHandler(BaseCallbackHandler):
    # 当 Chain 开始运行
    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], *, run_id: UUID, **kwargs: Any
    ) -> None:
        print(f"[Chain 开始] Run ID: {run_id} | 输入数据: {inputs}")

    # 当 LLM 完成生成
    def on_llm_end(
            self, response: LLMResult, *, run_id: UUID, **kwargs: Any
    ) -> None:
        print(f"[LLM 完成] Run ID: {run_id} | Token 使用情况: {response.llm_output}")

    # 当发生错误
    def on_chain_error(
            self, error: BaseException, *, run_id: UUID, **kwargs: Any
    ) -> None:
        print(f"[报错] Run ID: {run_id} | 错误信息: {error}")


load_dotenv()

model = init_chat_model(
    model="google_genai:gemini-3.1-flash-lite"
)
response = model.invoke(
    "给我讲一个笑话",
    config={
        "run_name": "joke_generation",
        "tags": ["humor", "demo"],
        "metadata": {"user_id": "123"},
        "callbacks": [MyHandler()]
    }
)
print(response)
