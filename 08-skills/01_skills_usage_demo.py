from typing import Literal

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from pydantic import BaseModel, Field

load_dotenv()


class Ticket(BaseModel):
    ticket_id: str = Field(description="Ticket ID")
    customer_name: str = Field(description="Customer name")
    content: str = Field(description="Content of the ticket")
    status: Literal[
        "New", "Processing", "Complete", "Complete but rejected", "Pending CSG", "Pending PDG", "Pending refund"
    ] = Field(description="Status of the ticket")


@tool
def update_ticket_status(
        ticket: Ticket,
        new_status: Literal[
            "New", "Processing", "Complete", "Complete but rejected", "Pending CSG", "Pending PDG", "Pending refund"],
        runtime: ToolRuntime) -> str | Ticket:
    current_status = ticket.status
    if current_status in ("Complete", "Complete but rejected"):
        return f"#{ticket.ticket_id} is complete, update is not allowed!"
    ticket.status = new_status
    return ticket


backend = FilesystemBackend(root_dir="./")
agent = create_deep_agent(
    model="ollama:llama3.1",
    backend=backend,
    skills=["./skills"]
)
