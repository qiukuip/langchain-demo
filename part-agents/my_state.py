from dataclasses import dataclass
from typing import TypedDict


@dataclass
class MyState(TypedDict):
    authenticated: bool
