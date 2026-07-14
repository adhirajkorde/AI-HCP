from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from crm_backend.app.core.db import get_db
from crm_backend.app.services.crm_services import AuthService, InteractionService
from crm_backend.app.repositories.crm_repositories import InteractionRepository, HCPRepository
from crm_backend.app.schemas.crm_schemas import InteractionCreate, InteractionResponse, AIChatRequest, AIChatResponse, UserResponse
from crm_backend.app.agent.agent import run_agent

router = APIRouter(prefix="/interactions", tags=["Interactions"])

@router.get("", response_model=List[InteractionResponse])
def list_interactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return InteractionRepository.get_all(db, skip=skip, limit=limit)

@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def log_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return InteractionService.log_interaction(db, interaction, current_user.id)

@router.post("/ai", response_model=AIChatResponse)
def analyze_interaction_text(
    payload: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    # Run the AI/NLP agent to extract details
    agent_response = run_agent(payload.text, current_user.id, db)
    return agent_response

@router.post("/ai/confirm", response_model=InteractionResponse)
def confirm_ai_interaction(
    interaction_data: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    # Commit the confirmed interaction
    return InteractionService.log_interaction(db, interaction_data, current_user.id)
