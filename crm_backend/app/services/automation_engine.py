import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session
from crm_backend.app.core.db import SessionLocal
from crm_backend.app.repositories.crm_repositories import (
    AutomationEventRepository, AutomationActionRepository,
    AuditLogRepository, ApprovalRequestRepository,
    NotificationRepository, EmailDraftRepository,
    InteractionRepository, HCPRepository, FollowUpRepository,
    AIInsightRepository, UserRepository
)
from crm_backend.app.models.database import (
    AutomationEvent, AutomationAction,
    AutomationEventType, AutomationActionType, ApprovalStatus,
    NotificationSeverity, User, HCP, Interaction, FollowUp
)
from crm_backend.app.services.crm_services import InteractionService
from crm_backend.app.schemas.crm_schemas import (
    FollowUpCreate, EmailDraftCreate, NotificationCreate,
    ApprovalRequestCreate
)

logger = logging.getLogger("automation_engine")


class AutomationEngine:
    def __init__(self):
        self.action_handlers: Dict[str, Callable] = {}
        self._register_default_actions()

    def _register_default_actions(self):
        self.register_action(AutomationActionType.CREATE_FOLLOWUP.value, self._create_followup)
        self.register_action(AutomationActionType.UPDATE_HCP.value, self._update_hcp)
        self.register_action(AutomationActionType.CREATE_NOTIFICATION.value, self._create_notification)
        self.register_action(AutomationActionType.GENERATE_SUMMARY.value, self._generate_summary)
        self.register_action(AutomationActionType.GENERATE_EMAIL_DRAFT.value, self._generate_email_draft)
        self.register_action(AutomationActionType.SCHEDULE_REMINDER.value, self._schedule_reminder)
        self.register_action(AutomationActionType.UPDATE_ANALYTICS.value, self._update_analytics)
        self.register_action(AutomationActionType.SEND_WEBHOOK.value, self._send_webhook)
        self.register_action(AutomationActionType.CREATE_APPROVAL_REQUEST.value, self._create_approval_request)
        self.register_action(AutomationActionType.UPDATE_AI_INSIGHT.value, self._update_ai_insight)

    def register_action(self, action_type: str, handler: Callable):
        self.action_handlers[action_type] = handler

    def publish_event(self, event_type: str, source_id: Optional[int] = None,
                      source_type: Optional[str] = None, user_id: Optional[int] = None,
                      payload: Optional[Dict[str, Any]] = None) -> int:
        db = SessionLocal()
        try:
            event = AutomationEventRepository.create(
                db, event_type, source_id, source_type, user_id, payload
            )
            logger.info(f"Published event: {event_type} (ID: {event.id})")
            return event.id
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            raise
        finally:
            db.close()

    def process_event(self, event_id: int) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            event = AutomationEventRepository.get_by_id(db, event_id)
            if not event:
                return {"success": False, "error": "Event not found"}

            if event.processed:
                return {"success": False, "error": "Event already processed"}

            actions_created = self._determine_actions(db, event)
            results = []

            for action_type, input_data in actions_created:
                action = AutomationActionRepository.create(db, event.id, action_type, input_data)
                result = self._execute_action(db, action)
                results.append({
                    "action_id": action.id,
                    "action_type": action_type,
                    "result": result
                })

            AutomationEventRepository.mark_processed(db, event.id)
            return {"success": True, "actions": results}

        except Exception as e:
            logger.error(f"Failed to process event {event_id}: {e}")
            AutomationEventRepository.mark_processed(db, event_id, str(e))
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def process_pending_events(self, limit: int = 50) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            events = AutomationEventRepository.get_unprocessed(db, limit)
            results = []
            for event in events:
                result = self.process_event(event.id)
                results.append({"event_id": event.id, "result": result})
            return {"success": True, "processed": len(results), "results": results}
        finally:
            db.close()

    def _determine_actions(self, db: Session, event: AutomationEvent) -> List[tuple]:
        actions = []
        payload = event.payload or {}
        event_type = event.event_type

        if event_type == AutomationEventType.INTERACTION_CREATED.value:
            interaction_id = event.source_id
            interaction = InteractionRepository.get_by_id(db, interaction_id)
            if interaction:
                actions.append((AutomationActionType.CREATE_FOLLOWUP.value, {
                    "interaction_id": interaction_id,
                    "hcp_id": interaction.hcp_id,
                    "user_id": event.user_id
                }))
                actions.append((AutomationActionType.UPDATE_AI_INSIGHT.value, {
                    "hcp_id": interaction.hcp_id
                }))
                actions.append((AutomationActionType.GENERATE_EMAIL_DRAFT.value, {
                    "interaction_id": interaction_id,
                    "hcp_id": interaction.hcp_id
                }))

                if payload.get("priority") == "High" or payload.get("sentiment") == "Negative":
                    actions.append((AutomationActionType.CREATE_NOTIFICATION.value, {
                        "user_id": event.user_id,
                        "title": "High Priority Interaction",
                        "message": f"High priority interaction logged with {payload.get('hcp_name', 'HCP')}",
                        "severity": "high",
                        "event_type": "high_priority.detected",
                        "source_id": interaction_id,
                        "source_type": "interaction"
                    }))
                    actions.append((AutomationActionType.SEND_WEBHOOK.value, {
                        "event_type": "high_priority_interaction",
                        "data": payload
                    }))

        elif event_type == AutomationEventType.FOLLOWUP_OVERDUE.value:
            followup_id = event.source_id
            followup = FollowUpRepository.get_by_id(db, followup_id)
            if followup:
                hcp = HCPRepository.get_by_id(db, followup.hcp_id)
                actions.append((AutomationActionType.CREATE_NOTIFICATION.value, {
                    "user_id": followup.hcp_id,
                    "title": "Follow-up Overdue",
                    "message": f"Follow-up for Dr. {hcp.name if hcp else 'Unknown'} is overdue",
                    "severity": "high",
                    "event_type": "followup.overdue",
                    "source_id": followup_id,
                    "source_type": "followup",
                    "action_url": f"/followups"
                }))
                actions.append((AutomationActionType.CREATE_APPROVAL_REQUEST.value, {
                    "request_type": "escalate_overdue",
                    "title": f"Escalate Overdue Follow-up: Dr. {hcp.name if hcp else 'Unknown'}",
                    "description": f"High priority follow-up is overdue. Consider manager escalation.",
                    "source_id": followup_id,
                    "source_type": "followup",
                    "risk_level": "high"
                }))

        elif event_type == AutomationEventType.SENTIMENT_NEGATIVE.value:
            hcp_id = event.source_id
            hcp = HCPRepository.get_by_id(db, hcp_id)
            if hcp:
                actions.append((AutomationActionType.CREATE_NOTIFICATION.value, {
                    "user_id": event.user_id,
                    "title": "Negative Sentiment Detected",
                    "message": f"Negative sentiment detected for Dr. {hcp.name}. Review interaction.",
                    "severity": "warning",
                    "event_type": "sentiment.negative",
                    "source_id": hcp_id,
                    "source_type": "hcp"
                }))

        elif event_type == AutomationEventType.ENGAGEMENT_DECLINING.value:
            hcp_id = event.source_id
            hcp = HCPRepository.get_by_id(db, hcp_id)
            if hcp:
                actions.append((AutomationActionType.CREATE_APPROVAL_REQUEST.value, {
                    "request_type": "re_engagement_campaign",
                    "title": f"Re-engagement Needed: Dr. {hcp.name}",
                    "description": f"Dr. {hcp.name}'s engagement score has declined significantly.",
                    "source_id": hcp_id,
                    "source_type": "hcp",
                    "risk_level": "medium"
                }))

        elif event_type == AutomationEventType.REPEATED_REQUEST.value:
            hcp_id = event.source_id
            hcp = HCPRepository.get_by_id(db, hcp_id)
            if hcp:
                actions.append((AutomationActionType.CREATE_NOTIFICATION.value, {
                    "user_id": event.user_id,
                    "title": "Repeated Information Request",
                    "message": f"Dr. {hcp.name} has requested the same information multiple times.",
                    "severity": "warning",
                    "event_type": "repeated.request",
                    "source_id": hcp_id,
                    "source_type": "hcp"
                }))

        elif event_type == AutomationEventType.NO_RECENT_INTERACTION.value:
            hcp_id = event.source_id
            hcp = HCPRepository.get_by_id(db, hcp_id)
            if hcp:
                actions.append((AutomationActionType.CREATE_APPROVAL_REQUEST.value, {
                    "request_type": "schedule_touchpoint",
                    "title": f"No Recent Interaction: Dr. {hcp.name}",
                    "description": f"It has been 60+ days since last interaction with Dr. {hcp.name}.",
                    "source_id": hcp_id,
                    "source_type": "hcp",
                    "risk_level": "low"
                }))

        return actions

    def _execute_action(self, db: Session, action) -> Dict[str, Any]:
        handler = self.action_handlers.get(action.action_type)
        if not handler:
            error = f"No handler for action type: {action.action_type}"
            logger.error(error)
            AutomationActionRepository.complete(db, action.id, error=error)
            return {"success": False, "error": error}

        AutomationActionRepository.start(db, action.id)
        try:
            result = handler(db, action.input_data or {})
            AutomationActionRepository.complete(db, action.id, output_data=result)
            return {"success": True, "output": result}
        except Exception as e:
            logger.error(f"Action {action.action_type} failed: {e}")
            AutomationActionRepository.complete(db, action.id, error=str(e))
            return {"success": False, "error": str(e)}

    def _create_followup(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        interaction_id = input_data.get("interaction_id")
        hcp_id = input_data.get("hcp_id")
        user_id = input_data.get("user_id")

        if not interaction_id or not hcp_id:
            return {"success": False, "error": "Missing interaction_id or hcp_id"}

        interaction = InteractionRepository.get_by_id(db, interaction_id)
        if not interaction:
            return {"success": False, "error": "Interaction not found"}

        if interaction.follow_up_date:
            existing = FollowUpRepository.get_by_hcp(db, hcp_id)
            for f in existing:
                if f.interaction_id == interaction_id:
                    return {"success": True, "message": "Follow-up already exists", "followup_id": f.id}

            followup_data = FollowUpCreate(
                interaction_id=interaction_id,
                hcp_id=hcp_id,
                follow_up_date=interaction.follow_up_date,
                priority_level="Medium",
                status="Pending",
                ai_recommendation=f"Follow up regarding {interaction.product_discussed} as discussed."
            )
            followup = FollowUpRepository.create(db, followup_data)
            return {"success": True, "followup_id": followup.id}

        return {"success": True, "message": "No follow-up date in interaction"}

    def _update_hcp(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        hcp_id = input_data.get("hcp_id")
        updates = input_data.get("updates", {})

        if not hcp_id:
            return {"success": False, "error": "Missing hcp_id"}

        hcp = HCPRepository.get_by_id(db, hcp_id)
        if not hcp:
            return {"success": False, "error": "HCP not found"}

        for key, value in updates.items():
            if hasattr(hcp, key):
                setattr(hcp, key, value)
        hcp.updated_at = datetime.utcnow()
        db.commit()
        return {"success": True, "hcp_id": hcp.id, "updated_fields": list(updates.keys())}

    def _create_notification(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = input_data.get("user_id")
        if not user_id:
            return {"success": False, "error": "Missing user_id"}

        notif_data = NotificationCreate(
            user_id=user_id,
            title=input_data.get("title", "Notification"),
            message=input_data.get("message", ""),
            severity=input_data.get("severity", "info"),
            event_type=input_data.get("event_type"),
            source_id=input_data.get("source_id"),
            source_type=input_data.get("source_type"),
            action_url=input_data.get("action_url")
        )
        notif = NotificationRepository.create(db, notif_data)
        return {"success": True, "notification_id": notif.id}

    def _generate_summary(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        interaction_id = input_data.get("interaction_id")
        if not interaction_id:
            return {"success": False, "error": "Missing interaction_id"}

        interaction = InteractionRepository.get_by_id(db, interaction_id)
        if not interaction:
            return {"success": False, "error": "Interaction not found"}

        hcp = HCPRepository.get_by_id(db, interaction.hcp_id)
        summary = (
            f"Interaction Summary:\n"
            f"HCP: Dr. {hcp.name if hcp else 'Unknown'}\n"
            f"Date: {interaction.date_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"Type: {interaction.interaction_type}\n"
            f"Product: {interaction.product_discussed}\n"
            f"Outcome: {interaction.outcome or 'None'}\n"
            f"Notes: {interaction.notes or 'None'}"
        )
        return {"success": True, "summary": summary}

    def _generate_email_draft(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        interaction_id = input_data.get("interaction_id")
        hcp_id = input_data.get("hcp_id")

        if not interaction_id or not hcp_id:
            return {"success": False, "error": "Missing interaction_id or hcp_id"}

        interaction = InteractionRepository.get_by_id(db, interaction_id)
        hcp = HCPRepository.get_by_id(db, hcp_id)

        if not interaction or not hcp:
            return {"success": False, "error": "Interaction or HCP not found"}

        if not hcp.email:
            return {"success": False, "error": "HCP has no email address"}

        subject = f"Follow-up: {interaction.product_discussed} - {interaction.interaction_type}"
        body = (
            f"Dear Dr. {hcp.name},\n\n"
            f"Thank you for the {interaction.interaction_type.lower()} on "
            f"{interaction.date_time.strftime('%B %d, %Y')}. "
            f"It was a pleasure discussing {interaction.product_discussed} with you.\n\n"
        )

        if interaction.outcome:
            body += f"As discussed, {interaction.outcome.lower()}.\n\n"

        body += (
            f"As promised, I am following up with the requested information. "
            f"Please find the relevant materials attached.\n\n"
            f"If you have any questions or need additional information, please don't hesitate to reach out.\n\n"
            f"Best regards,\n"
            f"Your Medical Representative"
        )

        draft_data = EmailDraftCreate(
            hcp_id=hcp_id,
            interaction_id=interaction_id,
            recipient_email=hcp.email,
            recipient_name=hcp.name,
            subject=subject,
            body=body,
            generated_by="AI",
            ai_reason=f"Auto-generated follow-up email for interaction #{interaction_id} regarding {interaction.product_discussed}",
            ai_confidence=85
        )
        draft = EmailDraftRepository.create(db, draft_data)

        return {"success": True, "email_draft_id": draft.id}

    def _schedule_reminder(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Reminder scheduled (placeholder)"}

    def _update_analytics(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Analytics updated (placeholder)"}

    def _send_webhook(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        import os
        import requests

        webhook_url = os.environ.get("N8N_WEBHOOK_URL")
        if not webhook_url:
            return {"success": False, "error": "N8N_WEBHOOK_URL not configured"}

        event_type = input_data.get("event_type", "unknown")
        data = input_data.get("data", {})

        try:
            response = requests.post(webhook_url, json={
                "event": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }, timeout=10)
            response.raise_for_status()
            return {"success": True, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Webhook failed: {e}")
            return {"success": False, "error": str(e)}

    def _create_approval_request(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        from crm_backend.app.schemas.crm_schemas import ApprovalRequestCreate

        request = ApprovalRequestCreate(
            request_type=input_data.get("request_type", "general"),
            title=input_data.get("title", "Approval Required"),
            description=input_data.get("description"),
            source_id=input_data.get("source_id"),
            source_type=input_data.get("source_type"),
            input_data=input_data,
            risk_level=input_data.get("risk_level", "medium")
        )

        managers = db.query(User).filter(User.role.in_(["manager", "admin"])).all()
        assigned_to = managers[0].id if managers else None

        approval = ApprovalRequestRepository.create(db, request, assigned_to=assigned_to)

        if assigned_to:
            notif_data = NotificationCreate(
                user_id=assigned_to,
                title="Approval Required",
                message=f"New approval request: {request.title}",
                severity="warning",
                event_type="approval.required",
                source_id=approval.id,
                source_type="approval_request",
                action_url=f"/approvals/{approval.id}"
            )
            NotificationRepository.create(db, notif_data)

        return {"success": True, "approval_request_id": approval.id}

    def _update_ai_insight(self, db: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        hcp_id = input_data.get("hcp_id")
        if not hcp_id:
            return {"success": False, "error": "Missing hcp_id"}

        InteractionService.update_hcp_insights(db, hcp_id)
        return {"success": True, "hcp_id": hcp_id}


automation_engine = AutomationEngine()


def publish_event(event_type: str, source_id: Optional[int] = None,
                  source_type: Optional[str] = None, user_id: Optional[int] = None,
                  payload: Optional[Dict[str, Any]] = None) -> int:
    return automation_engine.publish_event(event_type, source_id, source_type, user_id, payload)


def process_pending_events(limit: int = 50) -> Dict[str, Any]:
    return automation_engine.process_pending_events(limit)