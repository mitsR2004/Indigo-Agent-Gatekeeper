import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.delegation import CustomerAgentDelegation
from app.schemas.delegation import DelegationCreate, DelegationUpdatePermissions
from app.core.constants import DelegationStatus


class DelegationService:
    @staticmethod
    def create_or_update_delegation(db: Session, data: DelegationCreate) -> CustomerAgentDelegation:
        delegation = (
            db.query(CustomerAgentDelegation)
            .filter(
                CustomerAgentDelegation.customer_id == data.customer_id,
                CustomerAgentDelegation.agent_id == data.agent_id,
            )
            .first()
        )

        if delegation:
            delegation.status = DelegationStatus.ACTIVE.value
            delegation.can_view_fares = data.can_view_fares
            delegation.can_book_flight = data.can_book_flight
            delegation.can_change_flight = data.can_change_flight
            delegation.can_request_refund = data.can_request_refund
            delegation.spending_limit_inr = data.spending_limit_inr
            delegation.revoked_at = None
            delegation.revocation_reason = None
            db.commit()
            db.refresh(delegation)
            return delegation

        new_delegation = CustomerAgentDelegation(
            delegation_id=str(uuid.uuid4()),
            customer_id=data.customer_id,
            agent_id=data.agent_id,
            status=DelegationStatus.ACTIVE.value,
            can_view_fares=data.can_view_fares,
            can_book_flight=data.can_book_flight,
            can_change_flight=data.can_change_flight,
            can_request_refund=data.can_request_refund,
            spending_limit_inr=data.spending_limit_inr,
            granted_at=datetime.now(timezone.utc),
        )
        db.add(new_delegation)
        db.commit()
        db.refresh(new_delegation)
        return new_delegation

    @staticmethod
    def get_delegation(db: Session, customer_id: str, agent_id: str) -> Optional[CustomerAgentDelegation]:
        return (
            db.query(CustomerAgentDelegation)
            .filter(
                CustomerAgentDelegation.customer_id == customer_id,
                CustomerAgentDelegation.agent_id == agent_id,
            )
            .first()
        )

    @staticmethod
    def get_by_id(db: Session, delegation_id: str) -> Optional[CustomerAgentDelegation]:
        return db.query(CustomerAgentDelegation).filter(CustomerAgentDelegation.delegation_id == delegation_id).first()

    @staticmethod
    def list_by_customer(db: Session, customer_id: str) -> List[CustomerAgentDelegation]:
        return (
            db.query(CustomerAgentDelegation)
            .filter(CustomerAgentDelegation.customer_id == customer_id)
            .all()
        )

    @staticmethod
    def list_all(db: Session) -> List[CustomerAgentDelegation]:
        return db.query(CustomerAgentDelegation).all()

    @staticmethod
    def update_permissions(
        db: Session, delegation_id: str, updates: DelegationUpdatePermissions
    ) -> Optional[CustomerAgentDelegation]:
        delegation = db.query(CustomerAgentDelegation).filter(CustomerAgentDelegation.delegation_id == delegation_id).first()
        if not delegation:
            return None

        if updates.can_view_fares is not None:
            delegation.can_view_fares = updates.can_view_fares
        if updates.can_book_flight is not None:
            delegation.can_book_flight = updates.can_book_flight
        if updates.can_change_flight is not None:
            delegation.can_change_flight = updates.can_change_flight
        if updates.can_request_refund is not None:
            delegation.can_request_refund = updates.can_request_refund
        if updates.spending_limit_inr is not None:
            delegation.spending_limit_inr = updates.spending_limit_inr

        db.commit()
        db.refresh(delegation)
        return delegation

    @staticmethod
    def revoke_delegation(
        db: Session, delegation_id: str, reason: str = "Customer requested revocation"
    ) -> Optional[CustomerAgentDelegation]:
        """Revokes an agent delegation, stamping the exact date and time of revocation."""
        delegation = db.query(CustomerAgentDelegation).filter(CustomerAgentDelegation.delegation_id == delegation_id).first()
        if not delegation:
            return None

        delegation.status = DelegationStatus.REVOKED.value
        # Exact date and time recorded
        delegation.revoked_at = datetime.now(timezone.utc)
        delegation.revocation_reason = reason

        db.commit()
        db.refresh(delegation)
        return delegation
