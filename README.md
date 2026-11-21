# ✈️ IndiGo Airlines — Agent Gatekeeper

> **Academic Capstone Project in AI Systems Architecture & Digital Governance**  
> **Course:** MBA in Technology Management / Digital Business Strategy  
> **Domain:** Airline Operations, Autonomous AI Governance & Consumer Risk Management

---

## 1. Executive Summary & Problem Statement

As generative AI and personal assistant technologies (e.g., Google Gemini, Apple Intelligence, AutoGPT, travel aggregator bots) become ubiquitous, passengers increasingly delegate operational tasks to autonomous AI agents. While this enables friction-free travel management, it introduces severe strategic, financial, and legal vulnerabilities for **IndiGo Airlines**:

1. **Unauthorized Financial Commitments**: Autonomous agents making high-value bookings without explicit passenger awareness.
2. **Itinerary Disruption**: Autonomous agents modifying flight sectors or dates without explicit confirmation, causing missed flights.
3. **Refund Fraud & Inadvertent Cancellations**: Hallucinating or rogue agents triggering non-reversible ticket cancellations.
4. **Lack of Non-Repudiation**: Customers claiming *"I did not book this; my AI bot did it without my consent"*, leading to chargeback disputes and regulatory scrutiny under **DGCA (Directorate General of Civil Aviation)** and India's **Digital Personal Data Protection Act (DPDPA)**.

### The Solution: IndiGo Agent Gatekeeper
The **Agent Gatekeeper** is a zero-trust **Policy Enforcement Point (PEP)** and **Policy Decision Point (PDP)** sitting between external customer AI agents and IndiGo's Core Booking Services. Every request is verified in real time against customer-granted permissions, an automated spending threshold of **₹5,000**, and mandatory human-in-the-loop policies for sensitive actions.

---

## 2. Core Specifications & Architectural Framework

### 2.1 The 4 Supported Actions
| Action Identifier | Description | Inherent Risk Level | Policy Rule |
| :--- | :--- | :--- | :--- |
| `VIEW_FLIGHT_FARES` | Querying flight schedules, seat availability, and pricing. | Low (Read-Only) | `ALLOW` if agent registered & delegation active. |
| `BOOK_FLIGHT` | Reserving a seat and initiating payment transaction. | High (Financial) | `ALLOW` if $\le$ ₹5,000; `ASK_CUSTOMER` if $>$ ₹5,000. |
| `CHANGE_FLIGHT` | Rescheduling flight dates, sectors, or seat tiers. | High (Operational & Fare Difference) | `ALLOW` if fee/fare diff $\le$ ₹5,000; `ASK_CUSTOMER` if $>$ ₹5,000. |
| `REQUEST_REFUND` | Cancelling ticket and initiating fund reversal. | Critical (Cash Outflow / Policy Irreversible) | **ALWAYS `ASK_CUSTOMER`** (if permitted). |

### 2.2 The 3 Gatekeeper Decisions
```text
                   +----------------------------------+
                   | Incoming AI Agent Action Request |
                   +----------------------------------+
                                    |
                                    v
                   +----------------------------------+
                   |  IndiGo Gatekeeper Engine (PDP)  |
                   |  - Agent Registry Verification   |
                   |  - Customer Delegation Check     |
                   |  - Spending Limit (Rs. 5,000)    |
                   |  - Refund Step-Up Policy         |
                   +----------------------------------+
                        /           |           \
                       /            |            \
                      v             v             v
                 +---------+  +--------------+  +---------+
                 |  ALLOW  |  | ASK CUSTOMER |  |  BLOCK  |
                 +---------+  +--------------+  +---------+
                      |             |                |
                Autonomous      Step-Up 2FA /    Immediate
                Execution       App Push Token   Rejection
```

1. **`ALLOW`**: The action is executed autonomously with zero customer disruption (valid agent, active delegation, permitted action, amount $\le$ ₹5,000 or fare query).
2. **`ASK_CUSTOMER`**: Step-up human-in-the-loop verification required (triggered when transaction exceeds ₹5,000 or for any refund operation).
3. **`BLOCK`**: Request is denied immediately with a structured reason code (unregistered agent, revoked access, unpermitted action, or globally suspended agent).

---

## 3. The 6 Compulsory MBA Evaluation Test Cases

The system implements and validates the six mandatory test cases:

| ID | Test Case Scenario | Agent Status | Customer Delegation | Action Requested | Amount (₹) | Expected Decision | Reason Code |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **TC-1** | **Registered agent viewing flight fares** | `ACTIVE` | `ACTIVE` (view=True) | `VIEW_FLIGHT_FARES` | ₹0.00 | **ALLOW** | `FARE_QUERY_AUTHORIZED` |
| **TC-2** | **Unknown agent attempting a booking** | *Unregistered* | *None* | `BOOK_FLIGHT` | ₹3,200.00 | **BLOCK** | `AGENT_NOT_REGISTERED` |
| **TC-3** | **Booking above Rs. 5,000** | `ACTIVE` | `ACTIVE` (book=True) | `BOOK_FLIGHT` | ₹7,500.00 | **ASK_CUSTOMER** | `SPENDING_LIMIT_EXCEEDED` |
| **TC-4** | **Booking below Rs. 5,000 with prior authorization** | `ACTIVE` | `ACTIVE` (book=True) | `BOOK_FLIGHT` | ₹4,200.00 | **ALLOW** | `BOOKING_WITHIN_LIMIT` |
| **TC-5** | **Revoked agent attempting an action** | `ACTIVE` | `REVOKED` (timestamped) | `VIEW_FLIGHT_FARES` | ₹0.00 | **BLOCK** | `CUSTOMER_REVOKED_AGENT` |
| **TC-6** | **Registered agent requesting a refund** | `ACTIVE` | `ACTIVE` (refund=True) | `REQUEST_REFUND` | ₹3,000.00 | **ASK_CUSTOMER** | `REFUND_REQUIRES_CUSTOMER_CONFIRMATION` |

---

## 4. Database Design & Forensics

### 4.1 Schema Overview
- **`customers`**: IndiGo passenger directory (`customer_id`, `full_name`, `email`, `phone_number`, `created_at`).
- **`agents`**: Registry of recognized AI agents (`agent_id`, `agent_name`, `developer_organization`, `status`, `registered_at`).
- **`customer_agent_delegations`**: Explicit authorization contracts:
  - Granular permissions: `can_view_fares`, `can_book_flight`, `can_change_flight`, `can_request_refund`.
  - Financial limit: `spending_limit_inr` (Default: ₹5,000.00).
  - Lifecycle: `status` (`ACTIVE`/`REVOKED`), `granted_at`, and **`revoked_at` (accurate timestamp of revocation)**.
- **`audit_logs`**: Immutable, append-only log capturing:
  - `log_id` (UUID), **`timestamp` (ISO 8601 Date & Time)**, `customer_id`, `agent_id`, `action`, `amount_inr`, `decision`, `reason_code`, `reason_details`, and full request payload.

---

## 5. Quick Start & Execution Guide

### 5.1 Environment Activation
Open PowerShell in the project directory:
```powershell
# Activate the pre-configured virtual environment
.\.venv\Scripts\Activate.ps1
```

### 5.2 Database Initialization & Demo Seeding
To populate realistic IndiGo customers, registered agents, and permissions:
```powershell
python scripts/seed_data.py
```

### 5.3 Automated Verification (Pytest Suite)
Run the automated test suite covering all 23 unit and API test scenarios:
```powershell
pytest -v
```

### 5.4 One-Click CLI Compulsory Test Runner
Run the executive terminal report for the 6 compulsory test cases:
```powershell
python scripts/run_compulsory_tests.py
```

### 5.5 Launching the Streamlit Web Presentation Dashboard
```powershell
streamlit run dashboard/app.py
```
*The dashboard will automatically open in your default browser at `http://localhost:8501`.*

### 5.6 (Optional) Launching the FastAPI REST Backend
If you wish to demonstrate the interactive OpenAPI / Swagger documentation:
```powershell
uvicorn app.main:app --reload --port 8000
```
*Explore interactive API documentation at `http://localhost:8000/docs`.*

---

## 6. MBA Presentation & Demonstration Walkthrough

When presenting this project to professors, evaluators, or industry judges, follow this 5-step walkthrough:

### Step 1: 1-Click Verification of Mandatory Specifications
1. Open the Streamlit dashboard (`http://localhost:8501`).
2. Navigate to the **"🎯 Compulsory Test Cases"** tab.
3. Click the primary button **"▶ Run All 6 Compulsory Test Cases Now"**.
4. Point out the scorecard: All 6 test cases achieve **✅ PASS** status with exact policy justifications and ISO audit timestamps.

### Step 2: The ₹5,000 Spending Limit Demonstration
1. Switch to the **"🛡️ Live Gatekeeper Simulator"** tab.
2. Select passenger **Aarav Sharma (`6E-CUST-1001`)** and agent **Google Gemini (`6E-AGT-GEMINI`)**.
3. Select action `BOOK_FLIGHT` and set the amount to **₹4,200**:
   - Click **Evaluate Request** $\rightarrow$ Result is **`✓ ALLOW`** (`BOOKING_WITHIN_LIMIT`).
4. Now change the amount to **₹7,500**:
   - Click **Evaluate Request** $\rightarrow$ Result shifts to **`⚠️ ASK CUSTOMER`** (`SPENDING_LIMIT_EXCEEDED`).
   - *Talking Point*: Autonomous agents are bounded by an operational budget; large purchases require customer confirmation.

### Step 3: Mandatory Customer Consent for Refunds
1. In the Simulator, select action `REQUEST_REFUND` and set amount to **₹1,500** (below ₹5,000).
2. Click **Evaluate Request** $\rightarrow$ Result is **`⚠️ ASK CUSTOMER`** (`REFUND_REQUIRES_CUSTOMER_CONFIRMATION`).
3. *Talking Point*: Unlike bookings, refunds involve fund reversals and booking cancellation. To prevent fraudulent or hallucinated cancellations, IndiGo enforces a zero-trust policy where **all refund requests require explicit customer 2FA/push confirmation**.

### Step 4: Real-Time Agent Revocation with Timestamp
1. Navigate to the **"👥 Customer Permissions & Revocation"** tab.
2. Select **Aarav Sharma**, locate **Expedia Autonomous Travel Agent (`6E-AGT-EXPEDIA`)**.
3. Under *Instant Agent Revocation*, enter reason: *"Customer detected compromised API key"*.
4. Click **"⛔ Revoke Agent Authority Now"**:
   - The status changes to **`✕ REVOKED`** and displays the exact date and time of revocation.
5. Return to the Simulator and attempt any action with Expedia:
   - Result is immediately **`✕ BLOCK`** (`CUSTOMER_REVOKED_AGENT`).

### Step 5: Compliance & Forensic Audit Trail
1. Navigate to the **"📜 Forensic Audit Logs"** tab.
2. Demonstrate how every action attempt (allowed, stepped-up, or blocked) is permanently recorded with:
   - Accurate UTC Date and Time
   - Customer and Agent IDs
   - Financial Amounts
   - Policy Decisions and Reason Codes
3. *Talking Point*: Meets non-repudiation and compliance standards under India's **DPDPA** regulations.

---

## 7. Business & Strategic Value Summary
- **Risk Mitigation**: Eliminates unauthorized financial exposure by bounding autonomous agents to ₹5,000.
- **Consumer Trust**: Gives passengers complete autonomy with real-time kill-switches and transparent permission controls.
- **Auditability**: Complete forensic trail protects IndiGo against chargebacks and regulatory disputes.
- **Future-Ready Aviation Infrastructure**: Positions IndiGo at the forefront of the autonomous AI agent economy.
- Project documentation updated after successful testing of all six mandatory test cases.
