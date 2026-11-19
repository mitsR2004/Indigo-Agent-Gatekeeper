import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Mandatory requirement: Audit log with date and time (ISO compliant)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    customer_id = Column(String(64), ForeignKey("customers.customer_id"), nullable=True, index=True)
    agent_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=True, index=True)
    
    action = Column(String(64), nullable=False, index=True)
    amount_inr = Column(Float, nullable=True)
    decision = Column(String(32), nullable=False, index=True)  # ALLOW, ASK_CUSTOMER, BLOCK
    reason_code = Column(String(64), nullable=False)
    reason_details = Column(Text, nullable=False)
    request_payload = Column(Text, nullable=True)
    client_ip = Column(String(64), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="audit_logs")
    agent = relationship("Agent", back_populates="audit_logs")

    def __repr__(self):
        return (
            f"<AuditLog {self.log_id[:8]} | {self.timestamp.isoformat()} | "
            f"Action:{self.action} | Decision:{self.decision} | Reason:{self.reason_code}>"
        )
