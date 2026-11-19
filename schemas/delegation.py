from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.core.constants import DelegationStatus
from app.config import DEFAULT_SPENDING_LIMIT_INR


class DelegationCreate(BaseModel):
    customer_id: str
    agent_id: str
    can_view_fares: bool = True
    can_book_flight: bool = True
    can_change_flight: bool = False
    can_request_refund: bool = False
    spending_limit_inr: float = Field(default=DEFAULT_SPENDING_LIMIT_INR, ge=0)


class DelegationUpdatePermissions(BaseModel):
    can_view_fares: Optional[bool] = None
    can_book_flight: Optional[bool] = None
    can_change_flight: Optional[bool] = None
    can_request_refund: Optional[bool] = None
    spending_limit_inr: Optional[float] = Field(None, ge=0)


class DelegationRevokeRequest(BaseModel):
    revocation_reason: Optional[str] = Field("Customer initiated revocation", description="Reason for revoking agent access")


class DelegationResponse(BaseModel):
    delegation_id: str
    customer_id: str
    agent_id: str
    status: str
    can_view_fares: bool
    can_book_flight: bool
    can_change_flight: bool
    can_request_refund: bool
    spending_limit_inr: float
    granted_at: datetime
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
