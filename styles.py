# IndiGo Brand Styles & CSS Helpers
INDIGO_NAVY = "#001b94"
INDIGO_SKY = "#1e88e5"
INDIGO_LIGHT_BG = "#f5f7fc"

CUSTOM_CSS = f"""
<style>
    /* IndiGo Airline Corporate Theme */
    .indigo-header {{
        background: linear-gradient(135deg, {INDIGO_NAVY} 0%, #0033cc 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 27, 148, 0.15);
    }}
    .indigo-header h1 {{
        color: white !important;
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }}
    .indigo-header p {{
        color: #e0e7ff;
        margin: 6px 0 0 0;
        font-size: 15px;
    }}
    .metric-card {{
        background: white;
        padding: 16px;
        border-radius: 10px;
        border-left: 4px solid {INDIGO_NAVY};
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}
    .decision-badge-allow {{
        background-color: #d1fae5;
        color: #065f46;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 16px;
        display: inline-block;
        border: 1px solid #10b981;
    }}
    .decision-badge-ask {{
        background-color: #fef3c7;
        color: #92400e;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 16px;
        display: inline-block;
        border: 1px solid #f59e0b;
    }}
    .decision-badge-block {{
        background-color: #fee2e2;
        color: #991b1b;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 16px;
        display: inline-block;
        border: 1px solid #ef4444;
    }}
    .card-box {{
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 16px;
    }}
</style>
"""
