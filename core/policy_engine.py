from dataclasses import dataclass
from typing import Optional

from app.core.constants import (
    ActionType,
    DecisionType,
    ReasonCode,
    AgentStatus,
    DelegationStatus,
)
from app.models.agent import Agent
from app.models.delegation import CustomerAgentDelegation


@dataclass
class PolicyEvaluationResult:
    decision: DecisionType
    reason_code: ReasonCode
    reason_details: str


class GatekeeperPolicyEngine:
    """
    IndiGo Agent Gatekeeper Policy Decision Point (PDP).
    
    Evaluates runtime action requests against:
    1. Agent Registration & Global Lifecycle Status
    2. Customer Delegation & Revocation Status
    3. Action-Specific Permission Grants
    4. Monetary Spending Limits (Default Rs. 5,000 threshold)
    5. Mandatory Step-Up Confirmation for Refund Operations
    """

    @staticmethod
    def evaluate(
        agent: Optional[Agent],
        delegation: Optional[CustomerAgentDelegation],
        action: ActionType,
        amount_inr: Optional[float] = None,
    ) -> PolicyEvaluationResult:
        # Step 1: Agent Registration Check
        if agent is None:
            return PolicyEvaluationResult(
                decision=DecisionType.BLOCK,
                reason_code=ReasonCode.AGENT_NOT_REGISTERED,
                reason_details="Agent is not registered in the IndiGo Agent Registry.",
            )

        # Step 1B: Agent Global Status Check
        if agent.status != AgentStatus.ACTIVE.value:
            return PolicyEvaluationResult(
                decision=DecisionType.BLOCK,
                reason_code=ReasonCode.AGENT_GLOBALLY_REVOKED,
                reason_details=f"Agent '{agent.agent_id}' is globally {agent.status.lower()} by IndiGo administration.",
            )

        # Step 2: Customer Delegation Check
        if delegation is None:
            return PolicyEvaluationResult(
                decision=DecisionType.BLOCK,
                reason_code=ReasonCode.NO_DELEGATION_FOUND,
                reason_details=f"No delegation record found linking customer to agent '{agent.agent_id}'.",
            )

        # Step 2B: Customer Delegation Revocation Check
        if delegation.status == DelegationStatus.REVOKED.value or delegation.revoked_at is not None:
            revoked_time_str = (
                delegation.revoked_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                if delegation.revoked_at
                else "previously"
            )
            return PolicyEvaluationResult(
                decision=DecisionType.BLOCK,
                reason_code=ReasonCode.CUSTOMER_REVOKED_AGENT,
                reason_details=(
                    f"Customer revoked permissions for agent '{agent.agent_id}' on {revoked_time_str}. "
                    f"Reason: {delegation.revocation_reason or 'No reason provided'}."
                ),
            )

        # Step 3: Granular Action Permission Check
        action_allowed = False
        if action == ActionType.VIEW_FLIGHT_FARES:
            action_allowed = delegation.can_view_fares
        elif action == ActionType.BOOK_FLIGHT:
            action_allowed = delegation.can_book_flight
        elif action == ActionType.CHANGE_FLIGHT:
            action_allowed = delegation.can_change_flight
        elif action == ActionType.REQUEST_REFUND:
            action_allowed = delegation.can_request_refund

        if not action_allowed:
            return PolicyEvaluationResult(
                decision=DecisionType.BLOCK,
                reason_code=ReasonCode.ACTION_PERMISSION_DENIED,
                reason_details=f"Customer has not granted permission for action '{action.value}'.",
            )

        # Step 4: Action-Specific Logic & Spending Limit Evaluation
        if action == ActionType.VIEW_FLIGHT_FARES:
            return PolicyEvaluationResult(
                decision=DecisionType.ALLOW,
                reason_code=ReasonCode.FARE_QUERY_AUTHORIZED,
                reason_details="Agent is authorized to view flight fares on behalf of customer.",
            )

        # Mandatory Rule: All refund requests must always return ASK_CUSTOMER
        if action == ActionType.REQUEST_REFUND:
            refund_amount_str = f" of Rs. {amount_inr:,.2f}" if amount_inr is not None else ""
            return PolicyEvaluationResult(
                decision=DecisionType.ASK_CUSTOMER,
                reason_code=ReasonCode.REFUND_REQUIRES_CUSTOMER_CONFIRMATION,
                reason_details=(
                    f"Refund request{refund_amount_str} requires explicit customer confirmation "
                    "as refunds involve financial reversals."
                ),
            )

        # Step 5: Spending Limit Evaluation for BOOK_FLIGHT and CHANGE_FLIGHT
        effective_limit = delegation.spending_limit_inr
        transaction_amount = amount_inr if amount_inr is not None else 0.0

        if transaction_amount <= effective_limit:
            if action == ActionType.BOOK_FLIGHT:
                return PolicyEvaluationResult(
                    decision=DecisionType.ALLOW,
                    reason_code=ReasonCode.BOOKING_WITHIN_LIMIT,
                    reason_details=(
                        f"Booking amount of Rs. {transaction_amount:,.2f} is within the authorized "
                        f"spending limit of Rs. {effective_limit:,.2f}."
                    ),
                )
            else:  # CHANGE_FLIGHT
                return PolicyEvaluationResult(
                    decision=DecisionType.ALLOW,
                    reason_code=ReasonCode.CHANGE_WITHIN_LIMIT,
                    reason_details=(
                        f"Flight change amount of Rs. {transaction_amount:,.2f} is within the authorized "
                        f"spending limit of Rs. {effective_limit:,.2f}."
                    ),
                )
        else:
            return PolicyEvaluationResult(
                decision=DecisionType.ASK_CUSTOMER,
                reason_code=ReasonCode.SPENDING_LIMIT_EXCEEDED,
                reason_details=(
                    f"Transaction amount of Rs. {transaction_amount:,.2f} exceeds the authorized spending "
                    f"limit of Rs. {effective_limit:,.2f}. Step-up customer approval required."
                ),
            )
