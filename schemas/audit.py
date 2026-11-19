from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: str
    timestamp: datetime
    customer_id: Optional[str] = None
    agent_id: Optional[str] = None
    action: str
    amount_inr: Optional[float] = None
    decision: str
    reason_code: str
    reason_details: str
    request_payload: Optional[str] = None
    client_ip: Optional[str] = None
