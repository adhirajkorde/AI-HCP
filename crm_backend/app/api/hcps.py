from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from crm_backend.app.core.db import get_db
from crm_backend.app.services.crm_services import AuthService, HCPService
from crm_backend.app.repositories.crm_repositories import HCPRepository
from crm_backend.app.schemas.crm_schemas import HCPCreate, HCPResponse, HCPDetailResponse, UserResponse

router = APIRouter(prefix="/hcps", tags=["HCPs"])

@router.get("", response_model=List[HCPResponse])
def list_hcps(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return HCPRepository.get_all(db, skip=skip, limit=limit)

@router.post("", response_model=HCPResponse, status_code=status.HTTP_201_CREATED)
def create_hcp(
    hcp: HCPCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return HCPService.create_hcp(db, hcp)

@router.get("/{hcp_id}", response_model=HCPDetailResponse)
def get_hcp_profile(
    hcp_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return HCPService.get_hcp_profile(db, hcp_id)
