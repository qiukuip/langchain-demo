from typing import Sequence

from langgraph.store.base import IndexConfig
from langgraph.store.memory import InMemoryStore


def embed(texts: Sequence[str]) -> list[list[float]]:
    return [[1.0, 2.0] for _ in texts]


store = InMemoryStore(index=IndexConfig(embed=embed, dims=2))
user_id = "my-user"
application_context = "chitchat"
namespace = (user_id, application_context)
store.put(
    namespace,
    "a-memory",
    {
        "rules": [
            "User likes short, direct language",
            "User only speaks English & Python",
        ],
        "my-key": "my-value",
    },
)
item = store.get(namespace, "a-memory")
print(item)
items = store.search(
    namespace, filter={"my-key": "my-value"}, query="language preferences"
)
print(items)
