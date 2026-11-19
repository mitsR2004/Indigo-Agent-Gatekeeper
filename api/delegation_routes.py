from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.delegation import (
    DelegationCreate,
    DelegationResponse,
    DelegationUpdatePermissions,
    DelegationRevokeRequest,
)
from app.services.delegation_service import DelegationService

router = APIRouter(prefix="/delegations", tags=["Customer Permissions & Revocation"])


@router.post("", response_model=DelegationResponse, status_code=status.HTTP_201_CREATED)
def grant_or_update_delegation(payload: DelegationCreate, db: Session = Depends(get_db)):
    """Grant or update permissions for an AI agent on behalf of a customer."""
    return DelegationService.create_or_update_delegation(db=db, data=payload)


@router.get("", response_model=List[DelegationResponse])
def list_all_delegations(db: Session = Depends(get_db)):
    """List all delegations across the system."""
    return DelegationService.list_all(db=db)


@router.get("/customer/{customer_id}", response_model=List[DelegationResponse])
def list_customer_delegations(customer_id: str, db: Session = Depends(get_db)):
    """List all agent delegations granted by a specific customer."""
    return DelegationService.list_by_customer(db=db, customer_id=customer_id)


@router.patch("/{delegation_id}/permissions", response_model=DelegationResponse)
def update_permissions(
    delegation_id: str,
    payload: DelegationUpdatePermissions,
    db: Session = Depends(get_db),
):
    """Update granular action permissions or spending limit for an existing delegation."""
    delegation = DelegationService.update_permissions(db=db, delegation_id=delegation_id, updates=payload)
    if not delegation:
        raise HTTPException(status_code=404, detail="Delegation not found.")
    return delegation


@router.post("/{delegation_id}/revoke", response_model=DelegationResponse)
def revoke_agent_access(
    delegation_id: str,
    payload: DelegationRevokeRequest,
    db: Session = Depends(get_db),
):
    """
    Instantly revoke an agent's authority.
    Records the exact revocation date and time for auditability.
    Subsequent actions attempted by this agent will be BLOCKED.
    """
    delegation = DelegationService.revoke_delegation(
        db=db, delegation_id=delegation_id, reason=payload.revocation_reason or "Customer revoked access"
    )
    if not delegation:
        raise HTTPException(status_code=404, detail="Delegation not found.")
    return delegation
