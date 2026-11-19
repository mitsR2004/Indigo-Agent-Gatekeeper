import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.core.constants import ActionType, DecisionType, ReasonCode


class AuditService:
    @staticmethod
    def record_log(
        db: Session,
        action: ActionType,
        decision: DecisionType,
        reason_code: ReasonCode,
        reason_details: str,
        customer_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        amount_inr: Optional[float] = None,
        payload: Optional[Dict[str, Any]] = None,
        client_ip: Optional[str] = None,
    ) -> AuditLog:
        """
        Creates an immutable, timestamped audit log entry.
        Guarantees that every evaluation has a permanent forensic record.
        """
        log_entry = AuditLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),  # Date & time accurately recorded
            customer_id=customer_id,
            agent_id=agent_id,
            action=action.value if hasattr(action, "value") else str(action),
            amount_inr=amount_inr,
            decision=decision.value if hasattr(decision, "value") else str(decision),
            reason_code=reason_code.value if hasattr(reason_code, "value") else str(reason_code),
            reason_details=reason_details,
            request_payload=json.dumps(payload, default=str) if payload else None,
            client_ip=client_ip,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_logs(
        db: Session,
        limit: int = 100,
        offset: int = 0,
        customer_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        decision: Optional[str] = None,
        action: Optional[str] = None,
    ) -> List[AuditLog]:
        query = db.query(AuditLog)
        if customer_id and isinstance(customer_id, str):
            query = query.filter(AuditLog.customer_id == customer_id)
        if agent_id and isinstance(agent_id, str):
            query = query.filter(AuditLog.agent_id == agent_id)
        if decision and isinstance(decision, str):
            query = query.filter(AuditLog.decision == decision)
        if action and isinstance(action, str):
            query = query.filter(AuditLog.action == action)

        lim = int(limit) if isinstance(limit, (int, str)) and str(limit).isdigit() else 100
        off = int(offset) if isinstance(offset, (int, str)) and str(offset).isdigit() else 0

        return query.order_by(AuditLog.timestamp.desc()).offset(off).limit(lim).all()
