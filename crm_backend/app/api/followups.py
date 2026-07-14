from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from crm_backend.app.core.db import get_db
from crm_backend.app.services.crm_services import AuthService
from crm_backend.app.repositories.crm_repositories import FollowUpRepository
from crm_backend.app.schemas.crm_schemas import FollowUpResponse, FollowUpUpdate, UserResponse

router = APIRouter(prefix="/followups", tags=["Follow-ups"])

@router.get("", response_model=List[FollowUpResponse])
def list_followups(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return FollowUpRepository.get_all(db, skip=skip, limit=limit, status=status)

@router.patch("/{followup_id}", response_model=FollowUpResponse)
def update_followup(
    followup_id: int,
    followup_update: FollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    db_followup = FollowUpRepository.get_by_id(db, followup_id)
    if not db_followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return FollowUpRepository.update(db, db_followup, followup_update)
