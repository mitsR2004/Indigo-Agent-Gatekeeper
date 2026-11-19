from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.core.constants import AgentStatus


class AgentCreate(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier (e.g., 6E-AGT-EXPEDIA)")
    agent_name: str = Field(..., description="Name of the AI agent")
    developer_organization: str = Field(..., description="Provider / Organization")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE, description="Initial lifecycle status")


class AgentUpdateStatus(BaseModel):
    status: AgentStatus = Field(..., description="New lifecycle status")


class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    developer_organization: str
    status: str
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
