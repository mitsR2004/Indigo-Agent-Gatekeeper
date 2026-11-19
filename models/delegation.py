import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.core.constants import DelegationStatus
from app.config import DEFAULT_SPENDING_LIMIT_INR


class CustomerAgentDelegation(Base):
    __tablename__ = "customer_agent_delegations"

    delegation_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(64), ForeignKey("customers.customer_id"), nullable=False, index=True)
    agent_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=False, index=True)
    status = Column(String(32), default=DelegationStatus.ACTIVE.value, nullable=False)

    # Granular Action Permissions
    can_view_fares = Column(Boolean, default=True, nullable=False)
    can_book_flight = Column(Boolean, default=True, nullable=False)
    can_change_flight = Column(Boolean, default=False, nullable=False)
    can_request_refund = Column(Boolean, default=False, nullable=False)

    # Spending Limit (in INR)
    spending_limit_inr = Column(Float, default=DEFAULT_SPENDING_LIMIT_INR, nullable=False)

    # Timestamps
    granted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    revoked_at = Column(DateTime, nullable=True)  # Mandatory requirement: Revocation with date and time
    revocation_reason = Column(String(255), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="delegations")
    agent = relationship("Agent", back_populates="delegations")

    def __repr__(self):
        return (
            f"<Delegation {self.delegation_id} | Cust:{self.customer_id} -> "
            f"Agent:{self.agent_id} | Status:{self.status} | Limit:Rs.{self.spending_limit_inr}>"
        )
