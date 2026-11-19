from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.core.constants import AgentStatus


class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String(64), primary_key=True, index=True)
    agent_name = Column(String(128), nullable=False)
    developer_organization = Column(String(128), nullable=False)
    api_key_hash = Column(String(256), nullable=True)
    status = Column(String(32), default=AgentStatus.ACTIVE.value, nullable=False)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    delegations = relationship("CustomerAgentDelegation", back_populates="agent", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="agent")

    def __repr__(self):
        return f"<Agent {self.agent_id} - {self.agent_name} ({self.status})>"
