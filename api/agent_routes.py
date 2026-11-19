from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdateStatus
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agent Registry"])


@router.post("/register", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def register_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Register a new customer AI agent or update existing agent profile."""
    return AgentService.register_agent(db=db, agent_data=agent_data)


@router.get("", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    """Retrieve all registered AI agents in the IndiGo ecosystem."""
    return AgentService.list_agents(db=db)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Lookup agent by unique identifier."""
    agent = AgentService.get_agent(db=db, agent_id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")
    return agent


@router.patch("/{agent_id}/status", response_model=AgentResponse)
def update_agent_status(agent_id: str, payload: AgentUpdateStatus, db: Session = Depends(get_db)):
    """Admin endpoint to suspend or revoke an agent globally."""
    agent = AgentService.update_status(db=db, agent_id=agent_id, status=payload.status)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")
    return agent
