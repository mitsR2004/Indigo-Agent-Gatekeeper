from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from app.database import Base, engine
from app.api import api_router

# Create DB tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local dashboards and cross-origin agents
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["System"])
def root_status():
    return {
        "system": "IndiGo Agent Gatekeeper",
        "version": APP_VERSION,
        "status": "OPERATIONAL",
        "policy_spending_limit_inr": 5000.00,
        "supported_actions": [
            "VIEW_FLIGHT_FARES",
            "BOOK_FLIGHT",
            "CHANGE_FLIGHT",
            "REQUEST_REFUND",
        ],
        "possible_decisions": ["ALLOW", "ASK_CUSTOMER", "BLOCK"],
        "docs_url": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "HEALTHY"}
