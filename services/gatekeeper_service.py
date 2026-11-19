from typing import Optional
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.delegation import CustomerAgentDelegation
from app.schemas.gatekeeper import GatekeeperEvaluateRequest, GatekeeperDecisionResponse
from app.core.policy_engine import GatekeeperPolicyEngine
from app.services.audit_service import AuditService


class GatekeeperService:
    @staticmethod
    def evaluate_and_audit(
        db: Session, request: GatekeeperEvaluateRequest, client_ip: Optional[str] = None
    ) -> GatekeeperDecisionResponse:
        """
        Policy Enforcement Point (PEP) coordinator.
        Queries PDP, evaluates policy rules, records audit entry atomically,
        and returns the decision response.
        """
        # Lookup Agent
        agent = db.query(Agent).filter(Agent.agent_id == request.agent_id).first()

        # Lookup Customer Delegation
        delegation = (
            db.query(CustomerAgentDelegation)
            .filter(
                CustomerAgentDelegation.customer_id == request.customer_id,
                CustomerAgentDelegation.agent_id == request.agent_id,
            )
            .first()
        )

        # Run PDP Decision Engine
        result = GatekeeperPolicyEngine.evaluate(
            agent=agent,
            delegation=delegation,
            action=request.action,
            amount_inr=request.amount_inr,
        )

        # Record into Audit Log with Date & Time
        audit_entry = AuditService.record_log(
            db=db,
            action=request.action,
            decision=result.decision,
            reason_code=result.reason_code,
            reason_details=result.reason_details,
            customer_id=request.customer_id,
            agent_id=request.agent_id,
            amount_inr=request.amount_inr,
            payload=request.model_dump(),
            client_ip=client_ip,
        )

        return GatekeeperDecisionResponse(
            decision=result.decision,
            reason_code=result.reason_code,
            reason_details=result.reason_details,
            agent_id=request.agent_id,
            customer_id=request.customer_id,
            action=request.action,
            amount_inr=request.amount_inr,
            timestamp=audit_entry.timestamp,
            log_id=audit_entry.log_id,
        )
