from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.schemas.agent import AgentCreate
from app.core.constants import AgentStatus


class AgentService:
    @staticmethod
    def register_agent(db: Session, agent_data: AgentCreate) -> Agent:
        existing = db.query(Agent).filter(Agent.agent_id == agent_data.agent_id).first()
        if existing:
            # Update existing
            existing.agent_name = agent_data.agent_name
            existing.developer_organization = agent_data.developer_organization
            existing.status = agent_data.status.value
            db.commit()
            db.refresh(existing)
            return existing

        agent = Agent(
            agent_id=agent_data.agent_id,
            agent_name=agent_data.agent_name,
            developer_organization=agent_data.developer_organization,
            status=agent_data.status.value,
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    @staticmethod
    def get_agent(db: Session, agent_id: str) -> Optional[Agent]:
        return db.query(Agent).filter(Agent.agent_id == agent_id).first()

    @staticmethod
    def list_agents(db: Session) -> List[Agent]:
        return db.query(Agent).order_by(Agent.registered_at.desc()).all()

    @staticmethod
    def update_status(db: Session, agent_id: str, status: AgentStatus) -> Optional[Agent]:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if agent:
            agent.status = status.value
            db.commit()
            db.refresh(agent)
        return agent
