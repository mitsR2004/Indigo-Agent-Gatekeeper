from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit-logs", tags=["Forensic Audit Trail"])


@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    customer_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    decision: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Retrieve immutable audit logs stamped with exact date and time.
    Provides complete forensic trail for MBA demonstration and compliance audits.
    """
    return AuditService.get_logs(
        db=db,
        limit=limit,
        offset=offset,
        customer_id=customer_id,
        agent_id=agent_id,
        decision=decision,
        action=action,
    )
