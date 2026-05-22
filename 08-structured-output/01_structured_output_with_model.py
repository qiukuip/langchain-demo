from dataclasses import dataclass
from typing import TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from pydantic import BaseModel, Field

load_dotenv()


class ContactInfo1(BaseModel):
    name: str = Field(description="The name of the person")
    email: str = Field(description="The email of the person")
    phone: str = Field(description="The phone of the person")


@dataclass
class ContactInfo2:
    name: str  # The name of the person
    email: str  # The email of the person
    phone: str  # The phone of the person


class ContactInfo3(TypedDict):
    """Contact information for a person"""

    name: str  # The name of the person
    email: str  # The email of the person
    phone: str  # The phone of the person


contact_info_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "The name of the person"},
        "email": {"type": "string", "description": "The email of the person"},
        "phone": {"type": "string", "description": "The phone of the person"},
    },
}


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    response_format=ProviderStrategy(contact_info_schema),
)
input_message = {
    "role": "user",
    "content": "Extract user information from the following content: name: Alice, email: alice@earth.com, phone: (053) 888-123445",
}
result = agent.invoke({"messages": [input_message]})
print(result["structured_response"])
