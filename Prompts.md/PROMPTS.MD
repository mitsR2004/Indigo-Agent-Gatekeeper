PROMPTS.md

Project: IndiGo Airlines – AI Agent Gatekeeper

1. Project Overview and Development

Prompt:

Develop an AI Agent Gatekeeper system for IndiGo Airlines that controls and monitors autonomous AI agents performing airline-related activities.

The system should work as a centralized security and policy enforcement mechanism between AI agents and airline services. Every request made by an AI agent must be checked before execution.

The application should have a user-friendly dashboard where customers can monitor agent activities, manage permissions, simulate requests, and review audit logs.

2. AI Agent Registry

Prompt:

Create an AI Agent Registry to maintain a record of all authorized AI agents.

Each agent should have:

* Unique Agent ID.
* Agent Name.
* Registration Status.
* Assigned Customer.
* Authorized Permissions.

The system must verify agent registration before allowing any action. Unknown or unregistered agents must be blocked immediately.

3. Customer Authorization and Permissions

Prompt:

Develop a customer permission management system that allows customers to control what their AI agents can do on their behalf.

Provide permissions for:

* Viewing flight fares.
* Booking flights.
* Changing flights.
* Requesting refunds.

Only actions permitted by the customer should be processed. The system must check customer authorization before executing every request.

4. Three Gatekeeper Policy Decisions

Prompt:

Implement three types of policy decisions in the Gatekeeper Engine.

ALLOW:
Allow an action when the AI agent is registered, customer authorization is active, the requested action is permitted, and the transaction is within the authorized spending limit.

ASK CUSTOMER:
Ask for customer confirmation when a transaction exceeds ₹5,000 or when a refund request requires explicit customer approval.

BLOCK:
Immediately reject requests from unregistered agents, agents with revoked permissions, or agents attempting unauthorized actions.

Every decision must include a clear reason explaining why the request was allowed, sent for confirmation, or blocked.

5. Spending Limit Enforcement

Prompt:

Implement a financial spending limit of ₹5,000 for autonomous AI agents.

The Gatekeeper should evaluate the transaction amount before allowing a booking.

* Transactions up to ₹5,000 can be allowed when all permissions are valid.
* Transactions above ₹5,000 must require additional customer approval.
* The system must not execute high-value transactions without the required confirmation.

Display the policy decision and reason on the dashboard.

6. Refund Protection Mechanism

Prompt:

Develop a refund protection mechanism to prevent unauthorized financial reversals.

Every refund request must require explicit customer confirmation, irrespective of the transaction amount.

The system should:

* Identify refund requests.
* Generate an ASK CUSTOMER decision.
* Explain why customer approval is required.
* Prevent automatic refund execution without confirmation.

Use the reason code REFUND_REQUIRES_CUSTOMER_CONFIRMATION.

7. Instant Agent Revocation

Prompt:

Create an Instant Agent Revocation feature that allows customers to immediately withdraw permissions granted to an AI agent.

The feature should:

* Allow customers to select an agent.
* Provide a reason for revocation.
* Immediately change the agent status to REVOKED.
* Record the exact date and time of revocation.
* Block all subsequent requests from that agent.

Revoked agents must not be allowed to perform any action unless they are explicitly reauthorized.

8. Forensic Audit Trail

Prompt:

Develop a Forensic Audit Trail to maintain a permanent record of all AI agent activities and Gatekeeper decisions.

Each audit record should include:

* Timestamp in UTC.
* Customer ID.
* Agent ID.
* Requested Action.
* Transaction Amount.
* Gatekeeper Decision.
* Reason Code.
* Decision Details.

The audit trail should support filtering by decision and action and help identify unauthorized activities.

9. Live Gatekeeper Simulator

Prompt:

Create a Live Gatekeeper Simulator where users can test different AI agent requests in real time.

Allow users to select:

* Customer.
* AI Agent.
* Requested Action.
* Transaction Amount.
* Flight Number (optional).

After submitting a request, display the Gatekeeper decision with its policy justification and audit information.

10. Compulsory Test Cases

Prompt:

Create six compulsory test cases to verify the mandatory security and authorization policies of the IndiGo Agent Gatekeeper.

The six test cases should include:

1. Registered agent viewing flight fares – Expected: ALLOW.
2. Unknown agent attempting a booking – Expected: BLOCK.
3. Booking above ₹5,000 – Expected: ASK CUSTOMER.
4. Booking below ₹5,000 with prior authorization – Expected: ALLOW.
5. Revoked agent attempting an action – Expected: BLOCK.
6. Registered agent requesting a refund – Expected: ASK CUSTOMER.

Display the expected decision, actual decision, test result, and reason for each test case.

All six tests should pass when the system correctly follows the defined policies.

11. Dashboard and User Interface

Prompt:

Develop a simple and professional dashboard for the IndiGo Agent Gatekeeper application.

The dashboard should contain:

* Registered Passengers.
* AI Agents in Registry.
* Active Delegations.
* Audit Trail Events.
* Compulsory Test Cases.
* Live Gatekeeper Simulator.
* Customer Permissions and Revocation.
* Agent Registry.
* Forensic Audit Logs.

Use a clean interface with clear decision indicators for ALLOW, ASK CUSTOMER, and BLOCK.

12. Final System Validation

Prompt:

Perform complete validation of the IndiGo Agent Gatekeeper application.

Verify that:

1. Only registered agents can perform authorized actions.
2. Customer permissions are checked before every request.
3. Transactions above ₹5,000 require customer approval.
4. Refund requests require explicit customer confirmation.
5. Revoked agents are immediately blocked.
6. All requests and policy decisions are recorded in the audit trail.
7. All six compulsory test cases produce the expected results.

Ensure that the system follows a zero-trust security approach and maintains transparency, customer control, and accountability.

⸻

Project Objective:

To develop a secure AI Agent Gatekeeper system that ensures autonomous AI agents operate within customer-granted permissions, financial limits, and airline policies while maintaining transparency and accountability.
