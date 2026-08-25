from crm_backend.app.services.automation_engine import publish_event, process_pending_events
from crm_backend.app.core.db import SessionLocal
from crm_backend.app.models.database import AutomationEventType
from crm_backend.app.repositories.crm_repositories import HCPRepository, InteractionRepository
from crm_backend.app.schemas.crm_schemas import InteractionCreate
from datetime import datetime
import sys

print("Starting test...", flush=True)

db = SessionLocal()
hcp = HCPRepository.get_by_name(db, 'Sharma')
if not hcp:
    hcp = HCPRepository.create(db, type('o',(object,),{'name':'Sharma','specialty':'Cardiology','hospital_clinic':'Test','email':'sharma@test.com','phone':None,'product_preference':'CardioPlus'})())
    
interaction = InteractionRepository.create(db, InteractionCreate(
    hcp_id=hcp.id, user_id=1, interaction_type='In-Person Meeting',
    date_time=datetime.utcnow(), product_discussed='CardioPlus',
    notes='Test', outcome='Test', follow_up_date=datetime.utcnow()
), user_id=1)

print(f"Created interaction: {interaction.id}", flush=True)

eid = publish_event(
    event_type=AutomationEventType.INTERACTION_CREATED.value,
    source_id=interaction.id,
    source_type='interaction',
    user_id=1,
    payload={'hcp_name': 'Dr. Sharma', 'priority': 'High'}
)
print(f"Published event: {eid}", flush=True)

result = process_pending_events()
print(f"Processed: {result['processed']} events", flush=True)

for r in result['results']:
    for a in r['result']['actions']:
        print(f"Action: {a['action_type']}, Success: {a['result']['success']}", flush=True)

db.close()
print("Test complete!", flush=True)