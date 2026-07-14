from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from crm_backend.app.core.db import get_db
from crm_backend.app.services.crm_services import AuthService, AnalyticsService
from crm_backend.app.schemas.crm_schemas import UserResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return AnalyticsService.get_dashboard_summary(db)

@router.get("/metrics", response_model=Dict[str, Any])
def get_analytics_metrics(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return AnalyticsService.get_analytics_metrics(db)
