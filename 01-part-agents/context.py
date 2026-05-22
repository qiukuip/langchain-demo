from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Context(TypedDict):
    user_id: str
    user_role: str
