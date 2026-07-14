from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Any, Dict

# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = "medical_representative"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


# HCP schemas
class HCPCreate(BaseModel):
    name: str = Field(..., min_length=1)
    specialty: str = Field(..., min_length=1)
    hospital_clinic: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    product_preference: Optional[str] = None

class HCPUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    hospital_clinic: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    product_preference: Optional[str] = None

class HCPResponse(BaseModel):
    id: int
    name: str
    specialty: str
    hospital_clinic: str
    email: Optional[str] = None
    phone: Optional[str] = None
    product_preference: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Interaction schemas
class InteractionCreate(BaseModel):
    hcp_id: int
    interaction_type: str  # Email, Call, In-Person Meeting
    date_time: datetime
    product_discussed: str
    notes: Optional[str] = None
    outcome: Optional[str] = None
    follow_up_date: Optional[datetime] = None

class InteractionUpdate(BaseModel):
    interaction_type: Optional[str] = None
    date_time: Optional[datetime] = None
    product_discussed: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    follow_up_date: Optional[datetime] = None

class InteractionResponse(BaseModel):
    id: int
    hcp_id: int
    user_id: int
    interaction_type: str
    date_time: datetime
    product_discussed: str
    notes: Optional[str] = None
    outcome: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Follow-up schemas
class FollowUpCreate(BaseModel):
    interaction_id: Optional[int] = None
    hcp_id: int
    follow_up_date: datetime
    priority_level: str  # Low, Medium, High
    status: Optional[str] = "Pending"  # Pending, Completed
    ai_recommendation: Optional[str] = None

class FollowUpUpdate(BaseModel):
    follow_up_date: Optional[datetime] = None
    priority_level: Optional[str] = None
    status: Optional[str] = None
    ai_recommendation: Optional[str] = None

class FollowUpResponse(BaseModel):
    id: int
    interaction_id: Optional[int] = None
    hcp_id: int
    follow_up_date: datetime
    priority_level: str
    status: str
    ai_recommendation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Insight schemas
class AIInsightResponse(BaseModel):
    id: int
    hcp_id: int
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    engagement_score: int
    medical_interests: Optional[str] = None
    product_preferences: Optional[str] = None
    last_updated: datetime

    class Config:
        from_attributes = True


# Combined detailed HCP view
class HCPDetailResponse(BaseModel):
    hcp: HCPResponse
    interactions: List[InteractionResponse] = []
    followups: List[FollowUpResponse] = []
    ai_insight: Optional[AIInsightResponse] = None

    class Config:
        from_attributes = True


# AI Agent Schemas
class AIChatRequest(BaseModel):
    text: str

class ExtractedEntities(BaseModel):
    hcp_name: Optional[str] = None
    specialty: Optional[str] = None
    hospital_clinic: Optional[str] = None
    interaction_type: Optional[str] = None  # Email, Call, In-Person Meeting
    product_discussed: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[str] = None  # text format, e.g. "next week" or "2026-07-20"

class AIChatResponse(BaseModel):
    success: bool
    message: str
    entities: ExtractedEntities
    summary: str
    sentiment: str  # Positive, Neutral, Negative
    engagement_score: int  # 0 to 100
    follow_up_action: Optional[str] = None
    suggested_priority: str = "Medium"  # Low, Medium, High
    raw_result: Optional[Dict[str, Any]] = None
