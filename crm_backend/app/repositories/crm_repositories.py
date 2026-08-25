from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from crm_backend.app.models.database import (
    User, HCP, Interaction, FollowUp, AIInsight,
    AutomationEvent, AutomationAction, AuditLog,
    ApprovalRequest, Notification, EmailDraft,
    Document, DocumentChunk, KnowledgeSource
)
from crm_backend.app.schemas.crm_schemas import (
    UserCreate, HCPCreate, HCPUpdate, InteractionCreate, InteractionUpdate,
    FollowUpCreate, FollowUpUpdate, ApprovalRequestCreate, ApprovalRequestUpdate,
    NotificationCreate, EmailDraftCreate, EmailDraftUpdate,
    DocumentCreate, DocumentUpdate, KnowledgeSourceCreate, KnowledgeSourceUpdate
)

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create(db: Session, user: UserCreate, hashed_pwd: str) -> User:
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_pwd,
            role=user.role or "medical_representative"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


class HCPRepository:
    @staticmethod
    def get_by_id(db: Session, hcp_id: int) -> Optional[HCP]:
        return db.query(HCP).filter(HCP.id == hcp_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[HCP]:
        # Perform case-insensitive sub-string match for robustness
        return db.query(HCP).filter(HCP.name.ilike(f"%{name}%")).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[HCP]:
        return db.query(HCP).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, hcp: HCPCreate) -> HCP:
        db_hcp = HCP(
            name=hcp.name,
            specialty=hcp.specialty,
            hospital_clinic=hcp.hospital_clinic,
            email=hcp.email,
            phone=hcp.phone,
            product_preference=hcp.product_preference
        )
        db.add(db_hcp)
        db.commit()
        db.refresh(db_hcp)
        return db_hcp

    @staticmethod
    def update(db: Session, db_hcp: HCP, hcp_update: HCPUpdate) -> HCP:
        update_data = hcp_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_hcp, key, value)
        db_hcp.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_hcp)
        return db_hcp


class InteractionRepository:
    @staticmethod
    def get_by_id(db: Session, interaction_id: int) -> Optional[Interaction]:
        return db.query(Interaction).filter(Interaction.id == interaction_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Interaction]:
        return db.query(Interaction).order_by(desc(Interaction.date_time)).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_hcp(db: Session, hcp_id: int) -> List[Interaction]:
        return db.query(Interaction).filter(Interaction.hcp_id == hcp_id).order_by(desc(Interaction.date_time)).all()

    @staticmethod
    def create(db: Session, interaction: InteractionCreate, user_id: int) -> Interaction:
        db_interaction = Interaction(
            hcp_id=interaction.hcp_id,
            user_id=user_id,
            interaction_type=interaction.interaction_type,
            date_time=interaction.date_time,
            product_discussed=interaction.product_discussed,
            notes=interaction.notes,
            outcome=interaction.outcome,
            follow_up_date=interaction.follow_up_date
        )
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        return db_interaction

    @staticmethod
    def update(db: Session, db_interaction: Interaction, interaction_update: InteractionUpdate) -> Interaction:
        update_data = interaction_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_interaction, key, value)
        db_interaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_interaction)
        return db_interaction

    @staticmethod
    def delete(db: Session, db_interaction: Interaction) -> None:
        db.delete(db_interaction)
        db.commit()


class FollowUpRepository:
    @staticmethod
    def get_by_id(db: Session, followup_id: int) -> Optional[FollowUp]:
        return db.query(FollowUp).filter(FollowUp.id == followup_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[FollowUp]:
        query = db.query(FollowUp)
        if status:
            query = query.filter(FollowUp.status == status)
        return query.order_by(FollowUp.follow_up_date).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_hcp(db: Session, hcp_id: int) -> List[FollowUp]:
        return db.query(FollowUp).filter(FollowUp.hcp_id == hcp_id).order_by(FollowUp.follow_up_date).all()

    @staticmethod
    def create(db: Session, followup: FollowUpCreate) -> FollowUp:
        db_followup = FollowUp(
            interaction_id=followup.interaction_id,
            hcp_id=followup.hcp_id,
            follow_up_date=followup.follow_up_date,
            priority_level=followup.priority_level,
            status=followup.status or "Pending",
            ai_recommendation=followup.ai_recommendation
        )
        db.add(db_followup)
        db.commit()
        db.refresh(db_followup)
        return db_followup

    @staticmethod
    def update(db: Session, db_followup: FollowUp, followup_update: FollowUpUpdate) -> FollowUp:
        update_data = followup_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_followup, key, value)
        db_followup.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_followup)
        return db_followup


class AIInsightRepository:
    @staticmethod
    def get_by_hcp(db: Session, hcp_id: int) -> Optional[AIInsight]:
        return db.query(AIInsight).filter(AIInsight.hcp_id == hcp_id).first()

    @staticmethod
    def upsert(
        db: Session,
        hcp_id: int,
        summary: Optional[str] = None,
        sentiment: Optional[str] = None,
        engagement_score: Optional[int] = None,
        medical_interests: Optional[str] = None,
        product_preferences: Optional[str] = None
    ) -> AIInsight:
        db_insight = db.query(AIInsight).filter(AIInsight.hcp_id == hcp_id).first()
        if not db_insight:
            db_insight = AIInsight(hcp_id=hcp_id)
            db.add(db_insight)

        if summary is not None:
            db_insight.summary = summary
        if sentiment is not None:
            db_insight.sentiment = sentiment
        if engagement_score is not None:
            db_insight.engagement_score = engagement_score
        if medical_interests is not None:
            db_insight.medical_interests = medical_interests
        if product_preferences is not None:
            db_insight.product_preferences = product_preferences

        db_insight.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(db_insight)
        return db_insight


class AutomationEventRepository:
    @staticmethod
    def create(db: Session, event_type: str, source_id: Optional[int] = None,
               source_type: Optional[str] = None, user_id: Optional[int] = None,
               payload: Optional[Dict[str, Any]] = None) -> AutomationEvent:
        event = AutomationEvent(
            event_type=event_type,
            source_id=source_id,
            source_type=source_type,
            user_id=user_id,
            payload=payload
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_unprocessed(db: Session, limit: int = 100) -> List[AutomationEvent]:
        return db.query(AutomationEvent).filter(
            AutomationEvent.processed == False
        ).order_by(AutomationEvent.created_at).limit(limit).all()

    @staticmethod
    def mark_processed(db: Session, event_id: int, error: Optional[str] = None) -> Optional[AutomationEvent]:
        event = db.query(AutomationEvent).filter(AutomationEvent.id == event_id).first()
        if event:
            event.processed = True
            event.processed_at = datetime.utcnow()
            event.error = error
            db.commit()
            db.refresh(event)
        return event

    @staticmethod
    def get_by_id(db: Session, event_id: int) -> Optional[AutomationEvent]:
        return db.query(AutomationEvent).filter(AutomationEvent.id == event_id).first()


class AutomationActionRepository:
    @staticmethod
    def create(db: Session, event_id: int, action_type: str,
               input_data: Optional[Dict[str, Any]] = None) -> AutomationAction:
        action = AutomationAction(
            event_id=event_id,
            action_type=action_type,
            status="pending",
            input_data=input_data
        )
        db.add(action)
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def start(db: Session, action_id: int) -> Optional[AutomationAction]:
        action = db.query(AutomationAction).filter(AutomationAction.id == action_id).first()
        if action:
            action.status = "running"
            action.started_at = datetime.utcnow()
            db.commit()
            db.refresh(action)
        return action

    @staticmethod
    def complete(db: Session, action_id: int, output_data: Optional[Dict[str, Any]] = None,
                 error: Optional[str] = None) -> Optional[AutomationAction]:
        action = db.query(AutomationAction).filter(AutomationAction.id == action_id).first()
        if action:
            action.status = "completed" if not error else "failed"
            action.completed_at = datetime.utcnow()
            action.output_data = output_data
            action.error = error
            db.commit()
            db.refresh(action)
        return action

    @staticmethod
    def increment_retry(db: Session, action_id: int) -> Optional[AutomationAction]:
        action = db.query(AutomationAction).filter(AutomationAction.id == action_id).first()
        if action:
            action.retry_count += 1
            action.status = "pending"
            db.commit()
            db.refresh(action)
        return action

    @staticmethod
    def get_by_event(db: Session, event_id: int) -> List[AutomationAction]:
        return db.query(AutomationAction).filter(AutomationAction.event_id == event_id).all()


class AuditLogRepository:
    @staticmethod
    def create(db: Session, event_type: str, action: str, agent: Optional[str] = None,
               user_id: Optional[int] = None, source_id: Optional[int] = None,
               source_type: Optional[str] = None, input_reference: Optional[Dict[str, Any]] = None,
               output: Optional[Dict[str, Any]] = None, status: str = "success",
               error: Optional[str] = None, approval_status: Optional[str] = None) -> AuditLog:
        log = AuditLog(
            event_type=event_type,
            action=action,
            agent=agent,
            user_id=user_id,
            source_id=source_id,
            source_type=source_type,
            input_reference=input_reference,
            output=output,
            status=status,
            error=error,
            approval_status=approval_status
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_by_source(db: Session, source_type: str, source_id: int) -> List[AuditLog]:
        return db.query(AuditLog).filter(
            AuditLog.source_type == source_type,
            AuditLog.source_id == source_id
        ).order_by(desc(AuditLog.created_at)).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100,
                user_id: Optional[int] = None, event_type: Optional[str] = None) -> List[AuditLog]:
        query = db.query(AuditLog)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        return query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()


class ApprovalRequestRepository:
    @staticmethod
    def create(db: Session, request: ApprovalRequestCreate, requested_by: Optional[int] = None) -> ApprovalRequest:
        approval = ApprovalRequest(
            request_type=request.request_type,
            title=request.title,
            description=request.description,
            requested_by=requested_by,
            assigned_to=request.assigned_to,
            source_id=request.source_id,
            source_type=request.source_type,
            input_data=request.input_data,
            risk_level=request.risk_level,
            expires_at=request.expires_at,
            status="pending"
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        return approval

    @staticmethod
    def get_by_id(db: Session, approval_id: int) -> Optional[ApprovalRequest]:
        return db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()

    @staticmethod
    def get_pending(db: Session, assigned_to: Optional[int] = None,
                    request_type: Optional[str] = None) -> List[ApprovalRequest]:
        query = db.query(ApprovalRequest).filter(ApprovalRequest.status == "pending")
        if assigned_to:
            query = query.filter(ApprovalRequest.assigned_to == assigned_to)
        if request_type:
            query = query.filter(ApprovalRequest.request_type == request_type)
        return query.order_by(ApprovalRequest.created_at).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100,
                status: Optional[str] = None, assigned_to: Optional[int] = None) -> List[ApprovalRequest]:
        query = db.query(ApprovalRequest)
        if status:
            query = query.filter(ApprovalRequest.status == status)
        if assigned_to:
            query = query.filter(ApprovalRequest.assigned_to == assigned_to)
        return query.order_by(desc(ApprovalRequest.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def decide(db: Session, approval_id: int, status: str, decided_by: int,
               decision_reason: Optional[str] = None) -> Optional[ApprovalRequest]:
        approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
        if approval:
            approval.status = status
            approval.decided_by = decided_by
            approval.decided_at = datetime.utcnow()
            approval.decision_reason = decision_reason
            db.commit()
            db.refresh(approval)
        return approval

    @staticmethod
    def expire_old(db: Session) -> int:
        now = datetime.utcnow()
        expired = db.query(ApprovalRequest).filter(
            ApprovalRequest.status == "pending",
            ApprovalRequest.expires_at < now
        ).all()
        count = 0
        for approval in expired:
            approval.status = "expired"
            count += 1
        if count > 0:
            db.commit()
        return count


class NotificationRepository:
    @staticmethod
    def create(db: Session, notification: NotificationCreate) -> Notification:
        notif = Notification(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            severity=notification.severity,
            event_type=notification.event_type,
            source_id=notification.source_id,
            source_type=notification.source_type,
            action_url=notification.action_url
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def get_by_user(db: Session, user_id: int, unread_only: bool = False,
                    limit: int = 50) -> List[Notification]:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.read == False)
        return query.order_by(desc(Notification.created_at)).limit(limit).all()

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).count()

    @staticmethod
    def mark_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if notif:
            notif.read = True
            notif.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notif)
        return notif

    @staticmethod
    def mark_all_read(db: Session, user_id: int) -> int:
        result = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).update({Notification.read: True, Notification.read_at: datetime.utcnow()})
        db.commit()
        return result


class EmailDraftRepository:
    @staticmethod
    def create(db: Session, draft: EmailDraftCreate) -> EmailDraft:
        email = EmailDraft(
            hcp_id=draft.hcp_id,
            interaction_id=draft.interaction_id,
            followup_id=draft.followup_id,
            recipient_email=draft.recipient_email,
            recipient_name=draft.recipient_name,
            subject=draft.subject,
            body=draft.body,
            generated_by=draft.generated_by,
            ai_reason=draft.ai_reason,
            ai_confidence=draft.ai_confidence,
            status="draft"
        )
        db.add(email)
        db.commit()
        db.refresh(email)
        return email

    @staticmethod
    def get_by_id(db: Session, draft_id: int) -> Optional[EmailDraft]:
        return db.query(EmailDraft).filter(EmailDraft.id == draft_id).first()

    @staticmethod
    def get_by_hcp(db: Session, hcp_id: int) -> List[EmailDraft]:
        return db.query(EmailDraft).filter(EmailDraft.hcp_id == hcp_id).order_by(desc(EmailDraft.created_at)).all()

    @staticmethod
    def get_by_status(db: Session, status: str, limit: int = 100) -> List[EmailDraft]:
        return db.query(EmailDraft).filter(EmailDraft.status == status).order_by(desc(EmailDraft.created_at)).limit(limit).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100,
                status: Optional[str] = None, hcp_id: Optional[int] = None) -> List[EmailDraft]:
        query = db.query(EmailDraft)
        if status:
            query = query.filter(EmailDraft.status == status)
        if hcp_id:
            query = query.filter(EmailDraft.hcp_id == hcp_id)
        return query.order_by(desc(EmailDraft.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, draft_id: int, update: EmailDraftUpdate) -> Optional[EmailDraft]:
        draft = db.query(EmailDraft).filter(EmailDraft.id == draft_id).first()
        if draft:
            update_data = update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(draft, key, value)
            draft.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(draft)
        return draft

    @staticmethod
    def mark_sent(db: Session, draft_id: int) -> Optional[EmailDraft]:
        draft = db.query(EmailDraft).filter(EmailDraft.id == draft_id).first()
        if draft:
            draft.status = "sent"
            draft.sent_at = datetime.utcnow()
            db.commit()
            db.refresh(draft)
        return draft

    @staticmethod
    def mark_failed(db: Session, draft_id: int, error: str) -> Optional[EmailDraft]:
        draft = db.query(EmailDraft).filter(EmailDraft.id == draft_id).first()
        if draft:
            draft.status = "failed"
            draft.error = error
            db.commit()
            db.refresh(draft)
        return draft


class DocumentRepository:
    @staticmethod
    def create(db: Session, doc: DocumentCreate, uploaded_by: Optional[int] = None) -> Document:
        document = Document(
            filename=doc.filename,
            original_filename=doc.original_filename,
            file_path=doc.file_path,
            file_size=doc.file_size,
            mime_type=doc.mime_type,
            uploaded_by=uploaded_by,
            category=doc.category,
            tags=doc.tags,
            status="processing"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_by_id(db: Session, doc_id: int) -> Optional[Document]:
        return db.query(Document).filter(Document.id == doc_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100,
                status: Optional[str] = None, category: Optional[str] = None) -> List[Document]:
        query = db.query(Document)
        if status:
            query = query.filter(Document.status == status)
        if category:
            query = query.filter(Document.category == category)
        return query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, doc_id: int, update: DocumentUpdate) -> Optional[Document]:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            update_data = update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(doc, key, value)
            doc.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(doc)
        return doc

    @staticmethod
    def update_status(db: Session, doc_id: int, status: str, error: Optional[str] = None,
                      extracted_text: Optional[str] = None, chunk_count: int = 0) -> Optional[Document]:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = status
            doc.error = error
            doc.extracted_text = extracted_text
            doc.chunk_count = chunk_count
            doc.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(doc)
        return doc


class DocumentChunkRepository:
    @staticmethod
    def create_batch(db: Session, document_id: int, chunks: List[Dict[str, Any]]) -> List[DocumentChunk]:
        db_chunks = []
        for chunk_data in chunks:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk_data.get("chunk_index", 0),
                content=chunk_data.get("content", ""),
                embedding=chunk_data.get("embedding"),
                token_count=chunk_data.get("token_count"),
                chunk_metadata=chunk_data.get("metadata")
            )
            db.add(chunk)
            db_chunks.append(chunk)
        db.commit()
        for chunk in db_chunks:
            db.refresh(chunk)
        return db_chunks

    @staticmethod
    def get_by_document(db: Session, document_id: int) -> List[DocumentChunk]:
        return db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()

    @staticmethod
    def search_by_embedding(db: Session, query_embedding: List[float],
                            limit: int = 5, min_similarity: float = 0.7) -> List[DocumentChunk]:
        # This is a placeholder - in production, use pgvector or similar for actual vector search
        # For now, return recent chunks as fallback
        return db.query(DocumentChunk).join(Document).filter(
            Document.status == "ready"
        ).order_by(desc(DocumentChunk.created_at)).limit(limit).all()


class KnowledgeSourceRepository:
    @staticmethod
    def create(db: Session, source: KnowledgeSourceCreate, created_by: Optional[int] = None) -> KnowledgeSource:
        ks = KnowledgeSource(
            name=source.name,
            description=source.description,
            source_type=source.source_type,
            document_ids=source.document_ids,
            embedding_model=source.embedding_model,
            chunk_size=source.chunk_size,
            chunk_overlap=source.chunk_overlap,
            created_by=created_by
        )
        db.add(ks)
        db.commit()
        db.refresh(ks)
        return ks

    @staticmethod
    def get_by_id(db: Session, ks_id: int) -> Optional[KnowledgeSource]:
        return db.query(KnowledgeSource).filter(KnowledgeSource.id == ks_id).first()

    @staticmethod
    def get_all(db: Session, active_only: bool = True) -> List[KnowledgeSource]:
        query = db.query(KnowledgeSource)
        if active_only:
            query = query.filter(KnowledgeSource.is_active == True)
        return query.order_by(desc(KnowledgeSource.created_at)).all()

    @staticmethod
    def update(db: Session, ks_id: int, update: KnowledgeSourceUpdate) -> Optional[KnowledgeSource]:
        ks = db.query(KnowledgeSource).filter(KnowledgeSource.id == ks_id).first()
        if ks:
            update_data = update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(ks, key, value)
            ks.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(ks)
        return ks

    @staticmethod
    def delete(db: Session, ks_id: int) -> bool:
        ks = db.query(KnowledgeSource).filter(KnowledgeSource.id == ks_id).first()
        if ks:
            db.delete(ks)
            db.commit()
            return True
        return False
