from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from crm_backend.app.core.db import Base
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="medical_representative", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    specialty = Column(String(100), nullable=False, index=True)
    hospital_clinic = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(50), nullable=True)
    product_preference = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interactions = relationship("Interaction", back_populates="hcp", cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="hcp", cascade="all, delete-orphan")
    ai_insight = relationship("AIInsight", back_populates="hcp", uselist=False, cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # Email, Call, In-Person Meeting
    date_time = Column(DateTime, nullable=False)
    product_discussed = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    outcome = Column(String(255), nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hcp = relationship("HCP", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
    followups = relationship("FollowUp", back_populates="interaction", cascade="all, delete-orphan")


class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="SET NULL"), nullable=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False)
    follow_up_date = Column(DateTime, nullable=False)
    priority_level = Column(String(50), nullable=False)  # Low, Medium, High
    status = Column(String(50), default="Pending", nullable=False)  # Pending, Completed
    ai_recommendation = Column(Text, nullable=True)
    ai_reason = Column(Text, nullable=True)
    ai_confidence = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hcp = relationship("HCP", back_populates="followups")
    interaction = relationship("Interaction", back_populates="followups")


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)  # Positive, Neutral, Negative
    engagement_score = Column(Integer, default=50, nullable=False)  # 0 to 100
    medical_interests = Column(Text, nullable=True)  # Comma separated or text
    product_preferences = Column(Text, nullable=True)  # Comma separated or text
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hcp = relationship("HCP", back_populates="ai_insight")


class AutomationEventType(str, enum.Enum):
    INTERACTION_CREATED = "interaction.created"
    INTERACTION_UPDATED = "interaction.updated"
    FOLLOWUP_CREATED = "followup.created"
    FOLLOWUP_COMPLETED = "followup.completed"
    FOLLOWUP_OVERDUE = "followup.overdue"
    HCP_UPDATED = "hcp.updated"
    DOCUMENT_UPLOADED = "document.uploaded"
    HIGH_PRIORITY_DETECTED = "high_priority.detected"
    SENTIMENT_NEGATIVE = "sentiment.negative"
    ENGAGEMENT_DECLINING = "engagement.declining"
    REPEATED_REQUEST = "repeated.request"
    NO_RECENT_INTERACTION = "no_recent_interaction"


class AutomationActionType(str, enum.Enum):
    CREATE_FOLLOWUP = "create_followup"
    UPDATE_HCP = "update_hcp"
    CREATE_NOTIFICATION = "create_notification"
    GENERATE_SUMMARY = "generate_summary"
    GENERATE_EMAIL_DRAFT = "generate_email_draft"
    SCHEDULE_REMINDER = "schedule_reminder"
    UPDATE_ANALYTICS = "update_analytics"
    SEND_WEBHOOK = "send_webhook"
    CREATE_APPROVAL_REQUEST = "create_approval_request"
    UPDATE_AI_INSIGHT = "update_ai_insight"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    AUTO_APPROVED = "auto_approved"


class NotificationSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class AutomationEvent(Base):
    __tablename__ = "automation_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Enum(AutomationEventType), nullable=False, index=True)
    source_id = Column(Integer, nullable=True)  # interaction_id, followup_id, hcp_id, etc.
    source_type = Column(String(50), nullable=True)  # "interaction", "followup", "hcp", "document"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    payload = Column(JSON, nullable=True)  # Full event data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)

    user = relationship("User")


class AutomationAction(Base):
    __tablename__ = "automation_actions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("automation_events.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(Enum(AutomationActionType), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    event = relationship("AutomationEvent")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # e.g., "interaction.created", "followup.approved"
    action = Column(String(100), nullable=False)  # e.g., "create", "update", "delete", "approve", "reject"
    agent = Column(String(100), nullable=True)  # e.g., "InteractionAgent", "SupervisorAgent", "Human"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    source_id = Column(Integer, nullable=True)  # ID of the entity affected
    source_type = Column(String(50), nullable=True)  # "interaction", "followup", "hcp", "email_draft", "approval"
    input_reference = Column(JSON, nullable=True)  # Input that triggered the action
    output = Column(JSON, nullable=True)  # Result of the action
    status = Column(String(50), default="success", nullable=False)  # success, failed, partial
    error = Column(Text, nullable=True)
    approval_status = Column(Enum(ApprovalStatus), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User")


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(String(100), nullable=False, index=True)  # "send_email", "update_hcp_critical", "external_webhook", "bulk_action"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # AI agent or user
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # Manager/admin who can approve
    source_id = Column(Integer, nullable=True)  # ID of related entity
    source_type = Column(String(50), nullable=True)  # "email_draft", "hcp", "interaction", "webhook"
    input_data = Column(JSON, nullable=True)  # Full context for decision
    risk_level = Column(String(50), default="medium", nullable=False)  # low, medium, high, critical
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, index=True)
    decision_reason = Column(Text, nullable=True)
    decided_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester = relationship("User", foreign_keys=[requested_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    decider = relationship("User", foreign_keys=[decided_by])


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(NotificationSeverity), default=NotificationSeverity.INFO, nullable=False)
    event_type = Column(String(100), nullable=True)  # e.g., "followup.overdue", "approval.required"
    source_id = Column(Integer, nullable=True)
    source_type = Column(String(50), nullable=True)
    read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)
    action_url = Column(String(500), nullable=True)  # Link to relevant page
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User")


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="SET NULL"), nullable=True)
    followup_id = Column(Integer, ForeignKey("followups.id", ondelete="SET NULL"), nullable=True)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(100), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    generated_by = Column(String(50), default="AI", nullable=False)  # "AI", "Human", "Template"
    ai_reason = Column(Text, nullable=True)  # Why AI generated this email
    ai_confidence = Column(Integer, nullable=True)  # 0-100
    status = Column(String(50), default="draft", nullable=False)  # draft, pending_approval, approved, rejected, sent, failed
    approval_request_id = Column(Integer, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hcp = relationship("HCP")
    interaction = relationship("Interaction")
    followup = relationship("FollowUp")
    approval_request = relationship("ApprovalRequest")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(100), nullable=True)  # "product", "clinical", "faq", "training", "regulatory"
    tags = Column(JSON, nullable=True)  # List of tags
    status = Column(String(50), default="processing", nullable=False)  # processing, ready, failed, archived
    extracted_text = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uploader = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # Vector embedding as JSON array
    token_count = Column(Integer, nullable=True)
    chunk_metadata = Column(JSON, nullable=True)  # Section, page, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False)  # "document", "url", "manual"
    is_active = Column(Boolean, default=True, nullable=False)
    document_ids = Column(JSON, nullable=True)  # List of document IDs
    embedding_model = Column(String(100), nullable=True)
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=200)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User")


# Add relationships to existing models
User.automation_events = relationship("AutomationEvent", back_populates="user")
User.audit_logs = relationship("AuditLog", back_populates="user")
User.notifications = relationship("Notification", back_populates="user")
User.approval_requests_requested = relationship("ApprovalRequest", foreign_keys="ApprovalRequest.requested_by", back_populates="requester")
User.approval_requests_assigned = relationship("ApprovalRequest", foreign_keys="ApprovalRequest.assigned_to", back_populates="assignee")
User.approval_requests_decided = relationship("ApprovalRequest", foreign_keys="ApprovalRequest.decided_by", back_populates="decider")
User.documents = relationship("Document", back_populates="uploader")
User.knowledge_sources = relationship("KnowledgeSource", back_populates="creator")
