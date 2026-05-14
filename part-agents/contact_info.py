from dataclasses import dataclass
from typing import TypedDict


@dataclass
class ContactInfo(TypedDict):
    name: str
    email: str
    phone: str
    address: str
