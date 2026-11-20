import sys
from pathlib import Path
from datetime import datetime, timezone

# ------------------------------------------------------------------------------
# Resolve Python Import Conflict:
# When Streamlit runs 'dashboard/app.py', Python sets sys.path[0] to '.../dashboard'
# and may register 'app' as the script 'dashboard/app.py' in sys.modules.
# We remove 'dashboard/' from sys.path, insert project root at index 0,
# and clear any shadowed 'app' module so that the real backend package 'app' is imported.
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = Path(__file__).resolve().parent

# 1. Remove dashboard directory from sys.path to prevent module collisions
sys.path = [p for p in sys.path if Path(p).resolve() != DASHBOARD_DIR]

# 2. Insert project root at the very front of sys.path
base_dir_str = str(BASE_DIR)
if base_dir_str in sys.path:
    sys.path.remove(base_dir_str)
sys.path.insert(0, base_dir_str)

# 3. Unshadow 'app' if it was registered as a single module pointing to dashboard/app.py
if "app" in sys.modules:
    mod = sys.modules["app"]
    if not hasattr(mod, "__path__") or "dashboard" in getattr(mod, "__file__", ""):
        sys.modules.pop("app", None)
import streamlit as st
import pandas as pd

from app.database import Base, engine, SessionLocal
from app.models.customer import Customer
from app.models.agent import Agent
from app.models.delegation import CustomerAgentDelegation
from app.models.audit_log import AuditLog
from app.schemas.gatekeeper import GatekeeperEvaluateRequest
from app.schemas.agent import AgentCreate
from app.schemas.delegation import DelegationCreate, DelegationUpdatePermissions
from app.services.gatekeeper_service import GatekeeperService
from app.services.agent_service import AgentService
from app.services.delegation_service import DelegationService
from app.services.audit_service import AuditService
from app.core.constants import ActionType, DecisionType, ReasonCode, AgentStatus, DelegationStatus
from scripts.seed_data import seed_database
from dashboard.styles import CUSTOM_CSS, INDIGO_NAVY

# Initialize DB tables
Base.metadata.create_all(bind=engine)

# Set page config
st.set_page_config(
    page_title="IndiGo Agent Gatekeeper",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_db():
    return SessionLocal()


def render_decision_badge(decision: str):
    dec = str(decision).upper()
    if dec == "ALLOW":
        return '<span class="decision-badge-allow">✓ ALLOW</span>'
    elif dec == "ASK_CUSTOMER":
        return '<span class="decision-badge-ask">⚠️ ASK CUSTOMER</span>'
    else:
        return '<span class="decision-badge-block">✕ BLOCK</span>'


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(
        f"""
        <div style="background-color: {INDIGO_NAVY}; padding: 16px; border-radius: 8px; color: white; text-align: center; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0; font-size: 20px;">IndiGo 6E Gatekeeper</h2>
            <p style="margin: 4px 0 0 0; font-size: 13px; color: #cbd5e1;">AI Agent Governance Gateway</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙️ Governance Policies")
    st.info(
        "**Spending Limit:** ₹5,000.00\n\n"
        "Transactions <= ₹5,000 with permission are **ALLOWED**.\n\n"
        "Transactions > ₹5,000 trigger **ASK CUSTOMER**."
    )
    st.warning(
        "**Mandatory Refund Policy:**\n\n"
        "ALL refund requests require **ASK CUSTOMER**, regardless of amount, to ensure passenger consent."
    )

    st.markdown("---")
    st.markdown("### 🔄 Database Reset")
    if st.button("Reset / Re-Seed Database", use_container_width=True):
        seed_database()
        st.success("Database restored to default demo state!")
        st.rerun()

    st.markdown("---")
    st.caption("MBA Academic Capstone Project | Zero-Trust Architecture")


# ==============================================================================
# HEADER & SUMMARY METRICS
# ==============================================================================
st.markdown(
    """
    <div class="indigo-header">
        <h1>✈️ IndiGo Airlines — Agent Gatekeeper & Governance Portal</h1>
        <p>Policy Enforcement Point (PEP) & Decision Point (PDP) for Autonomous Customer AI Agents</p>
    </div>
    """,
    unsafe_allow_html=True,
)

db = get_db()
try:
    total_customers = db.query(Customer).count()
    total_agents = db.query(Agent).count()
    active_delegations = db.query(CustomerAgentDelegation).filter(CustomerAgentDelegation.status == "ACTIVE").count()
    total_audits = db.query(AuditLog).count()
finally:
    db.close()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Registered Passengers", value=total_customers)
with col2:
    st.metric(label="AI Agents in Registry", value=total_agents)
with col3:
    st.metric(label="Active Delegations", value=active_delegations)
with col4:
    st.metric(label="Audit Trail Events", value=total_audits)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# MAIN NAVIGATION TABS
# ==============================================================================
tab_tests, tab_sim, tab_delegation, tab_agents, tab_audit = st.tabs(
    [
        "🎯 Compulsory Test Cases",
        "🛡️ Live Gatekeeper Simulator",
        "👥 Customer Permissions & Revocation",
        "🤖 Agent Registry",
        "📜 Forensic Audit Logs",
    ]
)

# ==============================================================================
# TAB 1: 1-CLICK COMPULSORY TEST CASES
# ==============================================================================
with tab_tests:
    st.subheader("🎯 Six Compulsory MBA Evaluation Test Cases")
    st.write(
        "Verify all mandatory behavioral specifications with a single click. "
        "Each test exercises the Gatekeeper decision engine and records an immutable audit log."
    )

    if st.button("▶ Run All 6 Compulsory Test Cases Now", type="primary", use_container_width=True):
        db = get_db()
        try:
            compulsory_tests = [
                {
                    "id": "TC-1",
                    "title": "Registered agent viewing flight fares",
                    "agent_id": "6E-AGT-GEMINI",
                    "customer_id": "6E-CUST-1001",
                    "action": ActionType.VIEW_FLIGHT_FARES,
                    "amount": 0.0,
                    "expected": DecisionType.ALLOW,
                },
                {
                    "id": "TC-2",
                    "title": "Unknown agent attempting a booking",
                    "agent_id": "UNKNOWN-ROGUE-AGENT-999",
                    "customer_id": "6E-CUST-1001",
                    "action": ActionType.BOOK_FLIGHT,
                    "amount": 3200.0,
                    "expected": DecisionType.BLOCK,
                },
                {
                    "id": "TC-3",
                    "title": "Booking above Rs. 5,000",
                    "agent_id": "6E-AGT-GEMINI",
                    "customer_id": "6E-CUST-1001",
                    "action": ActionType.BOOK_FLIGHT,
                    "amount": 7500.0,
                    "expected": DecisionType.ASK_CUSTOMER,
                },
                {
                    "id": "TC-4",
                    "title": "Booking below Rs. 5,000 with prior authorization",
                    "agent_id": "6E-AGT-GEMINI",
                    "customer_id": "6E-CUST-1001",
                    "action": ActionType.BOOK_FLIGHT,
                    "amount": 4200.0,
                    "expected": DecisionType.ALLOW,
                },
                {
                    "id": "TC-5",
                    "title": "Revoked agent attempting an action",
                    "agent_id": "6E-AGT-SIRI",
                    "customer_id": "6E-CUST-1002",
                    "action": ActionType.VIEW_FLIGHT_FARES,
                    "amount": 0.0,
                    "expected": DecisionType.BLOCK,
                },
                {
                    "id": "TC-6",
                    "title": "Registered agent requesting a refund",
                    "agent_id": "6E-AGT-GEMINI",
                    "customer_id": "6E-CUST-1001",
                    "action": ActionType.REQUEST_REFUND,
                    "amount": 3000.0,
                    "expected": DecisionType.ASK_CUSTOMER,
                },
            ]

            results = []
            all_passed = True
            for tc in compulsory_tests:
                req = GatekeeperEvaluateRequest(
                    agent_id=tc["agent_id"],
                    customer_id=tc["customer_id"],
                    action=tc["action"],
                    amount_inr=tc["amount"],
                )
                res = GatekeeperService.evaluate_and_audit(db=db, request=req, client_ip="127.0.0.1")
                is_pass = res.decision == tc["expected"]
                if not is_pass:
                    all_passed = False

                results.append(
                    {
                        "Test ID": tc["id"],
                        "Scenario": tc["title"],
                        "Action": tc["action"].value,
                        "Amount (₹)": f"₹{tc['amount']:,.2f}",
                        "Expected": tc["expected"].value,
                        "Actual Decision": res.decision.value,
                        "Status": "✅ PASS" if is_pass else "❌ FAIL",
                        "Reason Code": res.reason_code.value,
                        "Explanation": res.reason_details,
                        "Timestamp": res.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    }
                )

            if all_passed:
                st.success("🎉 All 6 Compulsory Test Cases PASSED with 100% policy compliance!")
            else:
                st.error("One or more test cases did not match expected decisions.")

            # Render styled results cards
            for r in results:
                status_color = "#10b981" if "PASS" in r["Status"] else "#ef4444"
                st.markdown(
                    f"""
                    <div class="card-box" style="border-left: 6px solid {status_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: {INDIGO_NAVY};">{r['Test ID']}: {r['Scenario']}</h4>
                            <span style="font-weight: bold; font-size: 16px; color: {status_color};">{r['Status']}</span>
                        </div>
                        <div style="margin-top: 8px; display: flex; gap: 24px; font-size: 14px;">
                            <span><b>Action:</b> {r['Action']}</span>
                            <span><b>Amount:</b> {r['Amount (₹)']}</span>
                            <span><b>Expected:</b> {render_decision_badge(r['Expected'])}</span>
                            <span><b>Actual:</b> {render_decision_badge(r['Actual Decision'])}</span>
                        </div>
                        <p style="margin: 8px 0 0 0; color: #334155; font-size: 14px;"><b>Rationale:</b> {r['Explanation']}</p>
                        <small style="color: #64748b;">Logged at: {r['Timestamp']} | Code: {r['Reason Code']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        finally:
            db.close()
    else:
        st.info("Click the button above to run all 6 compulsory tests live against the Gatekeeper decision engine.")


# ==============================================================================
# TAB 2: LIVE GATEKEEPER SIMULATOR
# ==============================================================================
with tab_sim:
    st.subheader("🛡️ Live Gatekeeper Action Simulator")
    st.write("Simulate any AI agent request in real time and observe the policy decision.")

    db = get_db()
    try:
        customers = db.query(Customer).all()
        agents = db.query(Agent).all()

        cust_options = {f"{c.full_name} ({c.customer_id})": c.customer_id for c in customers}
        agent_options = {f"{a.agent_name} ({a.agent_id}) [{a.status}]": a.agent_id for a in agents}
        agent_options["[Simulate Unknown / Unregistered Agent]"] = "UNKNOWN-AGENT-404"
    finally:
        db.close()

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("#### 1. Configure Request Payload")
        selected_cust_label = st.selectbox("Select Customer:", list(cust_options.keys()))
        selected_customer_id = cust_options[selected_cust_label]

        selected_agent_label = st.selectbox("Select AI Agent:", list(agent_options.keys()))
        selected_agent_id = agent_options[selected_agent_label]

        selected_action = st.selectbox(
            "Select Requested Action:",
            [
                ActionType.VIEW_FLIGHT_FARES.value,
                ActionType.BOOK_FLIGHT.value,
                ActionType.CHANGE_FLIGHT.value,
                ActionType.REQUEST_REFUND.value,
            ],
            index=1,
        )

        amount_val = 0.0
        if selected_action in [ActionType.BOOK_FLIGHT.value, ActionType.CHANGE_FLIGHT.value, ActionType.REQUEST_REFUND.value]:
            amount_val = st.number_input(
                "Transaction Amount (₹ INR):",
                min_value=0.0,
                max_value=100000.0,
                value=4200.0 if selected_action == ActionType.BOOK_FLIGHT.value else 2500.0,
                step=500.0,
                help="Threshold check: Amounts <= ₹5,000 can be ALLOWED (if authorized); Amounts > ₹5,000 trigger ASK CUSTOMER.",
            )

        flight_no = st.text_input("Flight Number (Optional):", value="6E-2041")

        evaluate_btn = st.button("⚡ Evaluate Request", type="primary", use_container_width=True)

    with col_result:
        st.markdown("#### 2. Gatekeeper Decision Output")
        if evaluate_btn:
            db = get_db()
            try:
                eval_req = GatekeeperEvaluateRequest(
                    agent_id=selected_agent_id,
                    customer_id=selected_customer_id,
                    action=ActionType(selected_action),
                    amount_inr=amount_val,
                    flight_number=flight_no,
                )
                eval_resp = GatekeeperService.evaluate_and_audit(db=db, request=eval_req, client_ip="127.0.0.1")

                # Visual decision card
                decision_str = eval_resp.decision.value
                badge_html = render_decision_badge(decision_str)

                border_color = (
                    "#10b981"
                    if decision_str == "ALLOW"
                    else ("#f59e0b" if decision_str == "ASK_CUSTOMER" else "#ef4444")
                )

                st.markdown(
                    f"""
                    <div style="background: white; border: 2px solid {border_color}; border-radius: 12px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                            <span style="font-size: 14px; color: #64748b; font-weight: 600;">EVALUATION RESULT</span>
                            {badge_html}
                        </div>
                        <h3 style="margin: 0 0 10px 0; color: #1e293b;">{eval_resp.reason_code.value}</h3>
                        <p style="font-size: 16px; color: #334155; line-height: 1.5;">{eval_resp.reason_details}</p>
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 16px 0;">
                        <div style="font-size: 13px; color: #64748b; line-height: 1.8;">
                            <div><b>Customer:</b> {eval_resp.customer_id}</div>
                            <div><b>Agent:</b> {eval_resp.agent_id}</div>
                            <div><b>Action:</b> {eval_resp.action.value}</div>
                            <div><b>Amount:</b> {f"₹{eval_resp.amount_inr:,.2f}" if eval_resp.amount_inr is not None else "₹0.00 (Read-Only / N/A)"}</div>
                            <div><b>Audit Timestamp:</b> {eval_resp.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}</div>
                            <div><b>Audit Log ID:</b> <code>{eval_resp.log_id}</code></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            finally:
                db.close()
        else:
            st.info("Configure request parameters on the left and click **Evaluate Request**.")


# ==============================================================================
# TAB 3: CUSTOMER PERMISSIONS & REVOCATION
# ==============================================================================
with tab_delegation:
    st.subheader("👥 Customer Permission & Delegation Management")
    st.write(
        "Manage granular permissions per AI agent, adjust spending limits, or instantly revoke agent authority with date and time."
    )

    db = get_db()
    try:
        customers = db.query(Customer).all()
        agents = db.query(Agent).all()
        cust_map = {f"{c.full_name} ({c.customer_id})": c.customer_id for c in customers}
    finally:
        db.close()

    selected_c_label = st.selectbox("Select Customer to Manage:", list(cust_map.keys()), key="del_cust_select")
    curr_customer_id = cust_map[selected_c_label]

    db = get_db()
    try:
        delegations = db.query(CustomerAgentDelegation).filter(CustomerAgentDelegation.customer_id == curr_customer_id).all()
    finally:
        db.close()

    if delegations:
        for d in delegations:
            agent_obj = next((a for a in agents if a.agent_id == d.agent_id), None)
            agent_name = agent_obj.agent_name if agent_obj else d.agent_id
            is_revoked = d.status == "REVOKED" or d.revoked_at is not None

            status_badge = (
                '<span class="decision-badge-block">✕ REVOKED</span>'
                if is_revoked
                else '<span class="decision-badge-allow">✓ ACTIVE</span>'
            )

            st.markdown(
                f"""
                <div class="card-box">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: {INDIGO_NAVY};">{agent_name} (<code>{d.agent_id}</code>)</h4>
                        {status_badge}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_edit, c_revoke = st.columns([3, 2], gap="medium")

            with c_edit:
                with st.expander(f"Edit Permissions for {d.agent_id}", expanded=not is_revoked):
                    v_fares = st.checkbox("Can View Flight Fares", value=d.can_view_fares, key=f"vf_{d.delegation_id}")
                    v_book = st.checkbox("Can Book Flight", value=d.can_book_flight, key=f"vb_{d.delegation_id}")
                    v_change = st.checkbox("Can Change Flight", value=d.can_change_flight, key=f"vc_{d.delegation_id}")
                    v_refund = st.checkbox("Can Request Refund", value=d.can_request_refund, key=f"vr_{d.delegation_id}")
                    v_limit = st.number_input(
                        "Spending Limit (INR):",
                        min_value=0.0,
                        max_value=50000.0,
                        value=float(d.spending_limit_inr),
                        step=500.0,
                        key=f"vl_{d.delegation_id}",
                    )

                    if st.button("Save Permission Changes", key=f"btn_save_{d.delegation_id}"):
                        db = get_db()
                        try:
                            updates = DelegationUpdatePermissions(
                                can_view_fares=v_fares,
                                can_book_flight=v_book,
                                can_change_flight=v_change,
                                can_request_refund=v_refund,
                                spending_limit_inr=v_limit,
                            )
                            DelegationService.update_permissions(db=db, delegation_id=d.delegation_id, updates=updates)
                            st.success("Permissions updated successfully!")
                            st.rerun()
                        finally:
                            db.close()

            with c_revoke:
                st.markdown("##### Instant Agent Revocation")
                if not is_revoked:
                    revoke_reason = st.text_input(
                        "Revocation Reason:",
                        value="Customer initiated security revocation",
                        key=f"rev_reason_{d.delegation_id}",
                    )
                    if st.button("⛔ Revoke Agent Authority Now", key=f"btn_rev_{d.delegation_id}", type="primary"):
                        db = get_db()
                        try:
                            DelegationService.revoke_delegation(
                                db=db, delegation_id=d.delegation_id, reason=revoke_reason
                            )
                            st.error(f"Agent '{d.agent_id}' has been REVOKED! Exact timestamp recorded.")
                            st.rerun()
                        finally:
                            db.close()
                else:
                    rev_time_str = d.revoked_at.strftime("%Y-%m-%d %H:%M:%S UTC") if d.revoked_at else "N/A"
                    st.warning(
                        f"**Access Revoked on:** {rev_time_str}\n\n"
                        f"**Reason:** {d.revocation_reason or 'No reason specified'}\n\n"
                        "All subsequent actions by this agent are BLOCKED."
                    )
                    if st.button("Re-instate / Re-authorize Agent", key=f"re_instate_{d.delegation_id}"):
                        db = get_db()
                        try:
                            req_data = DelegationCreate(
                                customer_id=d.customer_id,
                                agent_id=d.agent_id,
                                can_view_fares=d.can_view_fares,
                                can_book_flight=d.can_book_flight,
                                can_change_flight=d.can_change_flight,
                                can_request_refund=d.can_request_refund,
                                spending_limit_inr=d.spending_limit_inr,
                            )
                            DelegationService.create_or_update_delegation(db=db, data=req_data)
                            st.success(f"Agent '{d.agent_id}' re-authorized!")
                            st.rerun()
                        finally:
                            db.close()

            st.markdown("---")
    else:
        st.info("No active agent delegations for this passenger.")


# ==============================================================================
# TAB 4: AGENT REGISTRY
# ==============================================================================
with tab_agents:
    st.subheader("🤖 IndiGo Agent Registry")
    st.write("All autonomous AI agents registered with IndiGo's Gatekeeper.")

    db = get_db()
    try:
        agents = db.query(Agent).all()
        agent_data = [
            {
                "Agent ID": a.agent_id,
                "Name": a.agent_name,
                "Developer / Provider": a.developer_organization,
                "Global Status": a.status,
                "Registered At": a.registered_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
            for a in agents
        ]
        st.dataframe(pd.DataFrame(agent_data), use_container_width=True, hide_index=True)
    finally:
        db.close()

    st.markdown("---")
    st.markdown("#### Register a New AI Agent")
    with st.form("register_agent_form"):
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            new_agent_id = st.text_input("Agent ID (e.g., 6E-AGT-CHATGPT):", value="6E-AGT-CHATGPT")
        with col_a2:
            new_agent_name = st.text_input("Agent Name:", value="OpenAI Travel Concierge")
        with col_a3:
            new_developer = st.text_input("Developer / Organization:", value="OpenAI Inc.")

        submitted = st.form_submit_button("Register Agent", type="primary")
        if submitted:
            db = get_db()
            try:
                new_agent = AgentCreate(
                    agent_id=new_agent_id.strip(),
                    agent_name=new_agent_name.strip(),
                    developer_organization=new_developer.strip(),
                    status=AgentStatus.ACTIVE,
                )
                AgentService.register_agent(db=db, agent_data=new_agent)
                st.success(f"Agent '{new_agent_id}' registered successfully!")
                st.rerun()
            finally:
                db.close()


# ==============================================================================
# TAB 5: FORENSIC AUDIT TRAIL
# ==============================================================================
with tab_audit:
    st.subheader("📜 Forensic Audit Trail")
    st.write(
        "Tamper-evident, timestamped log of all agent authorization requests, decisions, and policy rationales."
    )

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        f_decision = st.selectbox("Filter by Decision:", ["ALL", "ALLOW", "ASK_CUSTOMER", "BLOCK"])
    with f_col2:
        f_action = st.selectbox(
            "Filter by Action:",
            ["ALL", "VIEW_FLIGHT_FARES", "BOOK_FLIGHT", "CHANGE_FLIGHT", "REQUEST_REFUND"],
        )
    with f_col3:
        f_limit = st.slider("Max Logs to Display:", min_value=10, max_value=200, value=50, step=10)

    db = get_db()
    try:
        decision_param = None if f_decision == "ALL" else f_decision
        action_param = None if f_action == "ALL" else f_action
        logs = AuditService.get_logs(db=db, limit=f_limit, decision=decision_param, action=action_param)

        if logs:
            log_records = [
                {
                    "Timestamp (UTC)": l.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Decision": l.decision,
                    "Action": l.action,
                    "Amount (₹)": f"₹{l.amount_inr:,.2f}" if l.amount_inr is not None else "₹0.00",
                    "Customer": l.customer_id or "N/A",
                    "Agent": l.agent_id or "N/A",
                    "Reason Code": l.reason_code,
                    "Details": l.reason_details,
                    "Log ID": l.log_id[:8] + "...",
                }
                for l in logs
            ]
            st.dataframe(pd.DataFrame(log_records), use_container_width=True, hide_index=True)
        else:
            st.info("No audit logs matching current filter.")
    finally:
        db.close()
