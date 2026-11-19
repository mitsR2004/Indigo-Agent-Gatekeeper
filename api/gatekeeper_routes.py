from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.gatekeeper import GatekeeperEvaluateRequest, GatekeeperDecisionResponse
from app.services.gatekeeper_service import GatekeeperService

router = APIRouter(prefix="/gatekeeper", tags=["Gatekeeper PDP / PEP"])


@router.post("/evaluate", response_model=GatekeeperDecisionResponse)
def evaluate_agent_action(
    payload: GatekeeperEvaluateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Core Gatekeeper Policy Enforcement Point.
    Evaluates whether an external AI agent is allowed to execute an action
    on behalf of an IndiGo customer.
    
    Returns:
    - ALLOW
    - ASK_CUSTOMER
    - BLOCK
    """
    client_ip = request.client.host if request.client else "unknown"
    response = GatekeeperService.evaluate_and_audit(db=db, request=payload, client_ip=client_ip)
    return response
