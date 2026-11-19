from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.core.constants import ActionType, DecisionType, ReasonCode


class GatekeeperEvaluateRequest(BaseModel):
    agent_id: str = Field(..., description="Unique ID of the AI agent requesting action")
    customer_id: str = Field(..., description="Customer ID on whose behalf the action is performed")
    action: ActionType = Field(..., description="One of the 4 supported actions")
    amount_inr: Optional[float] = Field(None, ge=0, description="Transaction amount in INR (if applicable)")
    flight_number: Optional[str] = Field(None, description="Flight number (e.g., 6E-2041)")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context or metadata")


class GatekeeperDecisionResponse(BaseModel):
    decision: DecisionType = Field(..., description="Policy decision: ALLOW, ASK_CUSTOMER, or BLOCK")
    reason_code: ReasonCode = Field(..., description="Standardized machine-readable reason code")
    reason_details: str = Field(..., description="Human-readable justification for the decision")
    agent_id: str
    customer_id: str
    action: ActionType
    amount_inr: Optional[float] = None
    timestamp: datetime = Field(..., description="Accurate evaluation date and time (ISO 8601)")
    log_id: str = Field(..., description="Audit log reference ID")
