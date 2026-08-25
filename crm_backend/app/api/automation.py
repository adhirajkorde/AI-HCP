from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from crm_backend.app.core.db import get_db
from crm_backend.app.services.crm_services import AuthService
from crm_backend.app.repositories.crm_repositories import (
    AutomationEventRepository, AutomationActionRepository,
    AuditLogRepository, ApprovalRequestRepository,
    NotificationRepository, EmailDraftRepository,
    DocumentRepository, DocumentChunkRepository, KnowledgeSourceRepository
)
from crm_backend.app.schemas.crm_schemas import (
    UserResponse, ApprovalRequestCreate, ApprovalRequestUpdate,
    NotificationCreate, EmailDraftCreate, EmailDraftUpdate,
    DocumentCreate, DocumentUpdate, KnowledgeSourceCreate, KnowledgeSourceUpdate,
    AutomationEventResponse, AutomationActionResponse, AuditLogResponse,
    ApprovalRequestResponse, NotificationResponse, EmailDraftResponse,
    DocumentResponse, DocumentChunkResponse, KnowledgeSourceResponse,
    AIInsightRequest, AIInsightAnswer, AIActionCenterResponse,
    AlertResponse, AIActionItem
)
from crm_backend.app.services.automation_engine import automation_engine, publish_event
from crm_backend.app.models.database import (
    AutomationEvent, AutomationAction, FollowUp, User,
    AutomationEventType, AutomationActionType, ApprovalStatus,
    NotificationSeverity
)

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.post("/events", response_model=AutomationEventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_type: str,
    source_id: Optional[int] = None,
    source_type: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    event = AutomationEventRepository.create(db, event_type, source_id, source_type, current_user.id, payload)
    return event


@router.post("/events/{event_id}/process")
def process_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    result = automation_engine.process_event(event_id)
    return result


@router.post("/events/process-pending")
def process_pending_events(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    result = automation_engine.process_pending_events(limit)
    return result


@router.get("/events", response_model=List[AutomationEventResponse])
def list_events(
    skip: int = 0,
    limit: int = 100,
    processed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    query = db.query(AutomationEventRepository.__dict__["create"].__self__.__class__.__bases__[0].__name__ if False else None)
    # Simple query
    q = db.query(AutomationEventRepository.create.__self__.__class__.__bases__[0] if False else None)
    from crm_backend.app.models.database import AutomationEvent
    q = db.query(AutomationEvent)
    if processed is not None:
        q = q.filter(AutomationEvent.processed == processed)
    return q.order_by(AutomationEvent.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/events/{event_id}", response_model=AutomationEventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    event = AutomationEventRepository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/events/{event_id}/actions", response_model=List[AutomationActionResponse])
def get_event_actions(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return AutomationActionRepository.get_by_event(db, event_id)


# Audit Log endpoints
@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return AuditLogRepository.get_all(db, skip, limit, user_id, event_type)


@router.get("/audit-logs/source/{source_type}/{source_id}", response_model=List[AuditLogResponse])
def get_audit_logs_by_source(
    source_type: str,
    source_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return AuditLogRepository.get_by_source(db, source_type, source_id)


# Approval Request endpoints
@router.post("/approvals", response_model=ApprovalRequestResponse, status_code=status.HTTP_201_CREATED)
def create_approval_request(
    request: ApprovalRequestCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    approval = ApprovalRequestRepository.create(db, request, requested_by=current_user.id)
    return approval


@router.get("/approvals", response_model=List[ApprovalRequestResponse])
def list_approval_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    assigned_to_me: bool = False,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    if assigned_to_me:
        return ApprovalRequestRepository.get_pending(db, assigned_to=current_user.id)
    return ApprovalRequestRepository.get_all(db, skip, limit, status, current_user.id if status == "pending" else None)


@router.get("/approvals/pending", response_model=List[ApprovalRequestResponse])
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return ApprovalRequestRepository.get_pending(db, assigned_to=current_user.id)


@router.get("/approvals/{approval_id}", response_model=ApprovalRequestResponse)
def get_approval_request(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    approval = ApprovalRequestRepository.get_by_id(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return approval


@router.patch("/approvals/{approval_id}", response_model=ApprovalRequestResponse)
def decide_approval(
    approval_id: int,
    update: ApprovalRequestUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    approval = ApprovalRequestRepository.get_by_id(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    if approval.assigned_to and approval.assigned_to != current_user.id:
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(status_code=403, detail="Not authorized to decide this approval")

    if update.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")

    approval = ApprovalRequestRepository.decide(db, approval_id, update.status, current_user.id, update.decision_reason)

    # If approved and there's an email draft, update its status
    if update.status == "approved" and approval.source_type == "email_draft" and approval.source_id:
        from crm_backend.app.repositories.crm_repositories import EmailDraftRepository
        EmailDraftRepository.update(db, approval.source_id, EmailDraftUpdate(status="approved"))

    return approval


# Notification endpoints
@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    if notification.user_id != current_user.id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Can only create notifications for yourself")
    return NotificationRepository.create(db, notification)


@router.get("/notifications", response_model=List[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return NotificationRepository.get_by_user(db, current_user.id, unread_only, limit)


@router.get("/notifications/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    count = NotificationRepository.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    notif = NotificationRepository.mark_read(db, notification_id, current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@router.post("/notifications/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    count = NotificationRepository.mark_all_read(db, current_user.id)
    return {"marked_read": count}


# Email Draft endpoints
@router.post("/email-drafts", response_model=EmailDraftResponse, status_code=status.HTTP_201_CREATED)
def create_email_draft(
    draft: EmailDraftCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return EmailDraftRepository.create(db, draft)


@router.get("/email-drafts", response_model=List[EmailDraftResponse])
def list_email_drafts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    hcp_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return EmailDraftRepository.get_all(db, skip, limit, status, hcp_id)


@router.get("/email-drafts/pending-approval", response_model=List[EmailDraftResponse])
def get_pending_approval_drafts(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return EmailDraftRepository.get_by_status(db, "pending_approval")


@router.get("/email-drafts/{draft_id}", response_model=EmailDraftResponse)
def get_email_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    draft = EmailDraftRepository.get_by_id(db, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Email draft not found")
    return draft


@router.patch("/email-drafts/{draft_id}", response_model=EmailDraftResponse)
def update_email_draft(
    draft_id: int,
    update: EmailDraftUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    draft = EmailDraftRepository.update(db, draft_id, update)
    if not draft:
        raise HTTPException(status_code=404, detail="Email draft not found")
    return draft


@router.post("/email-drafts/{draft_id}/send")
def send_email_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    draft = EmailDraftRepository.get_by_id(db, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Email draft not found")

    if draft.status not in ["approved", "draft"]:
        raise HTTPException(status_code=400, detail="Email must be approved or in draft status to send")

    # Check if approval is required
    if draft.approval_request_id:
        from crm_backend.app.repositories.crm_repositories import ApprovalRequestRepository
        approval = ApprovalRequestRepository.get_by_id(db, draft.approval_request_id)
        if approval and approval.status != "approved":
            raise HTTPException(status_code=400, detail="Email draft requires approval before sending")

    # Send email (placeholder - integrate with actual email service)
    try:
        import os
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        email_host = os.environ.get("EMAIL_HOST")
        email_port = int(os.environ.get("EMAIL_PORT", 587))
        email_user = os.environ.get("EMAIL_USERNAME")
        email_pass = os.environ.get("EMAIL_PASSWORD")
        email_from = os.environ.get("EMAIL_FROM", email_user)

        if not all([email_host, email_user, email_pass, email_from]):
            EmailDraftRepository.mark_failed(db, draft_id, "Email credentials not configured")
            raise HTTPException(status_code=500, detail="Email service not configured")

        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = draft.recipient_email
        msg['Subject'] = draft.subject
        msg.attach(MIMEText(draft.body, 'plain'))

        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)

        EmailDraftRepository.mark_sent(db, draft_id)

        # Log audit
        from crm_backend.app.repositories.crm_repositories import AuditLogRepository
        AuditLogRepository.create(
            db,
            event_type="email.sent",
            action="send",
            agent="Human",
            user_id=current_user.id,
            source_id=draft_id,
            source_type="email_draft",
            output={"recipient": draft.recipient_email, "subject": draft.subject}
        )

        return {"success": True, "message": "Email sent successfully"}

    except HTTPException:
        raise
    except Exception as e:
        EmailDraftRepository.mark_failed(db, draft_id, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


# Document endpoints
@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    doc: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return DocumentRepository.create(db, doc, uploaded_by=current_user.id)


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return DocumentRepository.get_all(db, skip, limit, status, category)


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    doc = DocumentRepository.get_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.patch("/documents/{doc_id}", response_model=DocumentResponse)
def update_document(
    doc_id: int,
    update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    doc = DocumentRepository.update(db, doc_id, update)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/documents/{doc_id}/process")
def process_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    doc = DocumentRepository.get_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Extract text based on file type
    extracted_text = ""
    try:
        import os
        file_path = doc.file_path
        if not os.path.exists(file_path):
            DocumentRepository.update_status(db, doc_id, "failed", error="File not found")
            raise HTTPException(status_code=404, detail="File not found on disk")

        if doc.mime_type == "application/pdf":
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
        elif doc.mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            import docx
            doc_doc = docx.Document(file_path)
            for para in doc_doc.paragraphs:
                extracted_text += para.text + "\n"
        elif doc.mime_type == "text/plain":
            with open(file_path, 'r') as f:
                extracted_text = f.read()
        else:
            DocumentRepository.update_status(db, doc_id, "failed", error=f"Unsupported file type: {doc.mime_type}")
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Chunk text
        chunk_size = 1000
        chunk_overlap = 200
        chunks = []
        for i in range(0, len(extracted_text), chunk_size - chunk_overlap):
            chunk_text = extracted_text[i:i + chunk_size]
            if chunk_text.strip():
                chunks.append({
                    "chunk_index": len(chunks),
                    "content": chunk_text,
                    "token_count": len(chunk_text.split()),
                    "metadata": {"start_char": i, "end_char": min(i + chunk_size, len(extracted_text))}
                })

        # Save chunks
        DocumentChunkRepository.create_batch(db, doc_id, chunks)

        DocumentRepository.update_status(
            db, doc_id, "ready",
            extracted_text=extracted_text,
            chunk_count=len(chunks)
        )

        # Publish event
        publish_event(
            event_type=AutomationEventType.DOCUMENT_UPLOADED.value,
            source_id=doc_id,
            source_type="document",
            user_id=current_user.id,
            payload={"document_id": doc_id, "chunk_count": len(chunks)}
        )

        return {"success": True, "chunk_count": len(chunks), "text_length": len(extracted_text)}

    except Exception as e:
        DocumentRepository.update_status(db, doc_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


# Knowledge Source endpoints
@router.post("/knowledge-sources", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_source(
    source: KnowledgeSourceCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return KnowledgeSourceRepository.create(db, source, created_by=current_user.id)


@router.get("/knowledge-sources", response_model=List[KnowledgeSourceResponse])
def list_knowledge_sources(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return KnowledgeSourceRepository.get_all(db, active_only)


@router.get("/knowledge-sources/{ks_id}", response_model=KnowledgeSourceResponse)
def get_knowledge_source(
    ks_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    ks = KnowledgeSourceRepository.get_by_id(db, ks_id)
    if not ks:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    return ks


@router.patch("/knowledge-sources/{ks_id}", response_model=KnowledgeSourceResponse)
def update_knowledge_source(
    ks_id: int,
    update: KnowledgeSourceUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    ks = KnowledgeSourceRepository.update(db, ks_id, update)
    if not ks:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    return ks


@router.delete("/knowledge-sources/{ks_id}")
def delete_knowledge_source(
    ks_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    if not KnowledgeSourceRepository.delete(db, ks_id):
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    return {"success": True}


# AI Action Center
@router.get("/action-center", response_model=AIActionCenterResponse)
def get_action_center(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    from crm_backend.app.repositories.crm_repositories import FollowUpRepository, HCPRepository

    pending_approvals = []
    generated_followups = []
    email_drafts = []
    upcoming_actions = []
    failed_automations = []
    recent_decisions = []

    # Pending approvals
    approvals = ApprovalRequestRepository.get_pending(db, assigned_to=current_user.id)
    for a in approvals:
        pending_approvals.append(AIActionItem(
            id=f"approval-{a.id}",
            type="approval",
            title=a.title,
            description=a.description or "",
            hcp_id=a.source_id if a.source_type == "hcp" else None,
            priority="high" if a.risk_level in ["high", "critical"] else "medium",
            status=a.status,
            source_interaction_id=a.source_id if a.source_type == "interaction" else None,
            created_at=a.created_at,
            requires_approval=True,
            approval_request_id=a.id
        ))

    # Generated follow-ups (pending)
    # Get recent interactions that created follow-ups
    from crm_backend.app.models.database import FollowUp
    recent_followups = db.query(FollowUp).filter(
        FollowUp.status == "Pending"
    ).order_by(FollowUp.created_at.desc()).limit(10).all()

    for f in recent_followups:
        hcp = HCPRepository.get_by_id(db, f.hcp_id)
        generated_followups.append(AIActionItem(
            id=f"followup-{f.id}",
            type="followup",
            title=f"Follow up with Dr. {hcp.name if hcp else 'Unknown'}",
            description=f.ai_recommendation or "",
            hcp_id=f.hcp_id,
            hcp_name=hcp.name if hcp else None,
            priority=f.priority_level.lower(),
            status=f.status.lower(),
            source_interaction_id=f.interaction_id,
            created_at=f.created_at,
            requires_approval=False
        ))

    # Email drafts pending approval
    drafts = EmailDraftRepository.get_by_status(db, "pending_approval")
    for d in drafts:
        email_drafts.append(AIActionItem(
            id=f"email-{d.id}",
            type="email_draft",
            title=f"Email to Dr. {d.recipient_name}: {d.subject}",
            description=d.ai_reason or "",
            hcp_id=d.hcp_id,
            hcp_name=d.recipient_name,
            priority="medium",
            status=d.status,
            source_interaction_id=d.interaction_id,
            created_at=d.created_at,
            requires_approval=True,
            approval_request_id=d.approval_request_id
        ))

    # Upcoming automated actions (scheduled follow-ups due soon)
    from datetime import datetime, timedelta
    upcoming = db.query(FollowUp).filter(
        FollowUp.status == "Pending",
        FollowUp.follow_up_date <= datetime.utcnow() + timedelta(days=3)
    ).order_by(FollowUp.follow_up_date).limit(10).all()

    for f in upcoming:
        hcp = HCPRepository.get_by_id(db, f.hcp_id)
        upcoming_actions.append(AIActionItem(
            id=f"upcoming-{f.id}",
            type="automation",
            title=f"Upcoming: Follow up with Dr. {hcp.name if hcp else 'Unknown'}",
            description=f.ai_recommendation or "",
            hcp_id=f.hcp_id,
            hcp_name=hcp.name if hcp else None,
            priority=f.priority_level.lower(),
            status="scheduled",
            source_interaction_id=f.interaction_id,
            created_at=f.follow_up_date,
            requires_approval=False
        ))

    # Failed automations
    from crm_backend.app.models.database import AutomationAction
    failed_actions = db.query(AutomationAction).filter(
        AutomationAction.status == "failed"
    ).order_by(AutomationAction.completed_at.desc()).limit(10).all()

    for a in failed_actions:
        failed_automations.append(AIActionItem(
            id=f"failed-{a.id}",
            type="automation",
            title=f"Failed: {a.action_type}",
            description=a.error or "Unknown error",
            priority="high",
            status="failed",
            created_at=a.created_at,
            requires_approval=False
        ))

    # Recent AI decisions (audit logs)
    audit_logs = AuditLogRepository.get_all(db, 0, 10, event_type="interaction.created")
    for log in audit_logs:
        recent_decisions.append(AIActionItem(
            id=f"decision-{log.id}",
            type="decision",
            title=f"{log.agent or 'System'}: {log.action}",
            description=log.error or "Completed",
            priority="low",
            status=log.status,
            created_at=log.created_at,
            requires_approval=False
        ))

    return AIActionCenterResponse(
        pending_approvals=pending_approvals,
        generated_followups=generated_followups,
        email_drafts=email_drafts,
        upcoming_actions=upcoming_actions,
        failed_automations=failed_automations,
        recent_decisions=recent_decisions
    )


# Alerts
@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    from crm_backend.app.models.database import Notification
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.read == False)
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

    alerts = []
    for n in notifications:
        alerts.append(AlertResponse(
            id=n.id,
            type=n.event_type or "notification",
            severity=n.severity,
            title=n.title,
            description=n.message,
            source=n.source_type or "system",
            source_id=n.source_id,
            timestamp=n.created_at,
            read=n.read,
            resolved=n.read
        ))

    # Add overdue follow-up alerts
    from crm_backend.app.models.database import FollowUp
    from datetime import datetime
    overdue = db.query(FollowUp).filter(
        FollowUp.status == "Pending",
        FollowUp.follow_up_date < datetime.utcnow()
    ).all()

    for f in overdue:
        hcp = HCPRepository.get_by_id(db, f.hcp_id)
        alerts.append(AlertResponse(
            id=f"overdue-{f.id}",
            type="followup.overdue",
            severity="high" if f.priority_level == "High" else "warning",
            title=f"Overdue Follow-up: Dr. {hcp.name if hcp else 'Unknown'}",
            description=f"Follow-up was due on {f.follow_up_date.strftime('%Y-%m-%d')}. {f.ai_recommendation or ''}",
            source="followup",
            source_id=f.id,
            timestamp=f.follow_up_date,
            read=False,
            resolved=False
        ))

    return alerts


# AI RAG Query
@router.post("/ai/query", response_model=AIInsightAnswer)
def query_knowledge_base(
    request: AIInsightRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    # Placeholder for RAG implementation
    # This will be fully implemented in Phase 9
    return AIInsightAnswer(
        answer="RAG query functionality will be implemented in Phase 9. Please upload documents and configure knowledge sources first.",
        sources=[],
        confidence=0,
        model_used="none"
    )