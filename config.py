import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration (SQLite for portability and academic demonstration)
DATABASE_PATH = BASE_DIR / "indigo_gatekeeper.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

# Core Policy Constants
DEFAULT_SPENDING_LIMIT_INR = 5000.00

# Application Metadata
APP_TITLE = "IndiGo Airlines - Agent Gatekeeper API"
APP_DESCRIPTION = (
    "Authorization & Governance Gateway enforcing zero-trust policy decisions "
    "for autonomous customer AI agents."
)
APP_VERSION = "1.0.0"
