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
    ai_reason: Optional[str] = None
    ai_confidence: Optional[int] = None

class FollowUpUpdate(BaseModel):
    follow_up_date: Optional[datetime] = None
    priority_level: Optional[str] = None
    status: Optional[str] = None
    ai_recommendation: Optional[str] = None
    ai_reason: Optional[str] = None
    ai_confidence: Optional[int] = None

class FollowUpResponse(BaseModel):
    id: int
    interaction_id: Optional[int] = None
    hcp_id: int
    follow_up_date: datetime
    priority_level: str
    status: str
    ai_recommendation: Optional[str] = None
    ai_reason: Optional[str] = None
    ai_confidence: Optional[int] = None
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


# Automation Event schemas
class AutomationEventResponse(BaseModel):
    id: int
    event_type: str
    source_id: Optional[int] = None
    source_type: Optional[str] = None
    user_id: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime
    processed: bool
    processed_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class AutomationActionResponse(BaseModel):
    id: int
    event_id: int
    action_type: str
    status: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Audit Log schemas
class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    action: str
    agent: Optional[str] = None
    user_id: Optional[int] = None
    source_id: Optional[int] = None
    source_type: Optional[str] = None
    input_reference: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    status: str
    error: Optional[str] = None
    approval_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Approval Request schemas
class ApprovalRequestCreate(BaseModel):
    request_type: str
    title: str
    description: Optional[str] = None
    source_id: Optional[int] = None
    source_type: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    risk_level: str = "medium"
    assigned_to: Optional[int] = None
    expires_at: Optional[datetime] = None


class ApprovalRequestUpdate(BaseModel):
    status: str  # approved, rejected
    decision_reason: Optional[str] = None


class ApprovalRequestResponse(BaseModel):
    id: int
    request_type: str
    title: str
    description: Optional[str] = None
    requested_by: Optional[int] = None
    assigned_to: Optional[int] = None
    source_id: Optional[int] = None
    source_type: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    risk_level: str
    status: str
    decision_reason: Optional[str] = None
    decided_by: Optional[int] = None
    decided_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Notification schemas
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    severity: str
    event_type: Optional[str] = None
    source_id: Optional[int] = None
    source_type: Optional[str] = None
    read: bool
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    severity: str = "info"
    event_type: Optional[str] = None
    source_id: Optional[int] = None
    source_type: Optional[str] = None
    action_url: Optional[str] = None


# Email Draft schemas
class EmailDraftCreate(BaseModel):
    hcp_id: int
    interaction_id: Optional[int] = None
    followup_id: Optional[int] = None
    recipient_email: str
    recipient_name: str
    subject: str
    body: str
    generated_by: str = "AI"
    ai_reason: Optional[str] = None
    ai_confidence: Optional[int] = None


class EmailDraftUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = None
    recipient_email: Optional[str] = None


class EmailDraftResponse(BaseModel):
    id: int
    hcp_id: int
    interaction_id: Optional[int] = None
    followup_id: Optional[int] = None
    recipient_email: str
    recipient_name: str
    subject: str
    body: str
    generated_by: str
    ai_reason: Optional[str] = None
    ai_confidence: Optional[int] = None
    status: str
    approval_request_id: Optional[int] = None
    sent_at: Optional[datetime] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document schemas
class DocumentCreate(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentUpdate(BaseModel):
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str
    extracted_text: Optional[str] = None
    chunk_count: int
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    embedding: Optional[List[float]] = None
    token_count: Optional[int] = None
    chunk_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Knowledge Source schemas
class KnowledgeSourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: str = "document"
    document_ids: Optional[List[int]] = None
    embedding_model: Optional[str] = None
    chunk_size: int = 1000
    chunk_overlap: int = 200


class KnowledgeSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    document_ids: Optional[List[int]] = None


class KnowledgeSourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    source_type: str
    is_active: bool
    document_ids: Optional[List[int]] = None
    embedding_model: Optional[str] = None
    chunk_size: int
    chunk_overlap: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Insight Enhanced
class AIInsightRequest(BaseModel):
    question: str
    hcp_id: Optional[int] = None
    knowledge_source_id: Optional[int] = None


class AIInsightAnswer(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    confidence: int
    model_used: str


# AI Action Center schemas
class AIActionItem(BaseModel):
    id: str
    type: str  # followup, email_draft, approval, notification, automation
    title: str
    description: str
    hcp_id: Optional[int] = None
    hcp_name: Optional[str] = None
    priority: str  # high, medium, low
    status: str  # pending, approved, rejected, completed, failed
    source_interaction_id: Optional[int] = None
    created_at: datetime
    requires_approval: bool
    approval_request_id: Optional[int] = None


class AIActionCenterResponse(BaseModel):
    pending_approvals: List[AIActionItem] = []
    generated_followups: List[AIActionItem] = []
    email_drafts: List[AIActionItem] = []
    upcoming_actions: List[AIActionItem] = []
    failed_automations: List[AIActionItem] = []
    recent_decisions: List[AIActionItem] = []


# Alert schemas
class AlertResponse(BaseModel):
    id: int
    type: str
    severity: str
    title: str
    description: str
    source: str
    source_id: Optional[int] = None
    timestamp: datetime
    read: bool
    resolved: bool

    class Config:
        from_attributes = True


# Automation History
class AutomationHistoryItem(BaseModel):
    event_id: int
    event_type: str
    event_created_at: datetime
    actions: List[AutomationActionResponse] = []
    overall_status: str

    class Config:
        from_attributes = True
