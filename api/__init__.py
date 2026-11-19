from fastapi import APIRouter

from app.api.gatekeeper_routes import router as gatekeeper_router
from app.api.agent_routes import router as agent_router
from app.api.delegation_routes import router as delegation_router
from app.api.audit_routes import router as audit_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(gatekeeper_router)
api_router.include_router(agent_router)
api_router.include_router(delegation_router)
api_router.include_router(audit_router)
