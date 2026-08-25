from crm_backend.app.services.automation_engine import publish_event, process_pending_events
from crm_backend.app.core.db import SessionLocal
from crm_backend.app.models.database import AutomationEventType
from crm_backend.app.repositories.crm_repositories import (
    HCPRepository, InteractionRepository, FollowUpRepository,
    EmailDraftRepository, NotificationRepository, AuditLogRepository
)
from crm_backend.app.schemas.crm_schemas import InteractionCreate
from datetime import datetime
import sys

print("=== Full E2E Test ===", flush=True)

db = SessionLocal()

# Get or create HCP
hcp = HCPRepository.get_by_name(db, 'Sharma')
if not hcp:
    hcp = HCPRepository.create(db, type('o',(object,),{
        'name': 'Sharma',
        'specialty': 'Cardiology',
        'hospital_clinic': 'Test Hospital',
        'email': 'sharma@test.com',
        'phone': None,
        'product_preference': 'CardioPlus'
    })())
    
print(f"HCP: {hcp.name} (ID: {hcp.id})", flush=True)

# Create interaction
interaction = InteractionRepository.create(db, InteractionCreate(
    hcp_id=hcp.id, user_id=1, interaction_type='In-Person Meeting',
    date_time=datetime.utcnow(), product_discussed='CardioPlus',
    notes='Met Dr Sharma today. Discussed CardioPlus. Interested in clinical trial data. Follow up next Tuesday.',
    outcome='HCP interested in clinical trial data for CardioPlus',
    follow_up_date=datetime.utcnow()
), user_id=1)

print(f"Created interaction: {interaction.id}", flush=True)

# Publish automation event
eid = publish_event(
    event_type=AutomationEventType.INTERACTION_CREATED.value,
    source_id=interaction.id,
    source_type='interaction',
    user_id=1,
    payload={
        'hcp_name': 'Dr. Sharma',
        'product_discussed': 'CardioPlus',
        'priority': 'High',
        'sentiment': 'Positive'
    }
)
print(f"Published event: {eid}", flush=True)

# Process automation events
result = process_pending_events()
print(f"Processed: {result['processed']} events", flush=True)

for r in result['results']:
    for a in r['result']['actions']:
        print(f"  Action: {a['action_type']}, Success: {a['result']['success']}", flush=True)

# Verify follow-up was created
print("\n=== Verifying Follow-up ===", flush=True)
followups = FollowUpRepository.get_by_hcp(db, hcp.id)
for f in followups:
    if f.interaction_id == interaction.id:
        print(f"Follow-up created: ID={f.id}")
        print(f"  Priority: {f.priority_level}")
        print(f"  Status: {f.status}")
        print(f"  AI Recommendation: {f.ai_recommendation}")
        print(f"  AI Reason: {f.ai_reason}")
        print(f"  AI Confidence: {f.ai_confidence}")

# Verify email draft
print("\n=== Verifying Email Draft ===", flush=True)
drafts = EmailDraftRepository.get_by_hcp(db, hcp.id)
for d in drafts:
    if d.interaction_id == interaction.id:
        print(f"Email draft created: ID={d.id}")
        print(f"  Status: {d.status}")
        print(f"  Subject: {d.subject}")
        print(f"  AI Reason: {d.ai_reason}")
        print(f"  AI Confidence: {d.ai_confidence}")

# Verify notifications
print("\n=== Verifying Notifications ===", flush=True)
notifications = NotificationRepository.get_by_user(db, 1)
for n in notifications:
    if n.source_id == interaction.id:
        print(f"Notification: {n.title}")
        print(f"  Severity: {n.severity}")
        print(f"  Message: {n.message}")

# Verify audit logs
print("\n=== Verifying Audit Logs ===", flush=True)
logs = AuditLogRepository.get_by_source(db, 'interaction', interaction.id)
for log in logs:
    print(f"Audit: {log.event_type} - {log.action} by {log.agent} (Status: {log.status})")

print("\n=== E2E Test Complete ===", flush=True)
db.close()