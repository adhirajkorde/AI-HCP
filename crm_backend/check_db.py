from app.core.db import SessionLocal, Base, engine
from sqlalchemy import inspect
import sys

db = SessionLocal()
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)
if 'followups' in tables:
    cols = inspector.get_columns('followups')
    for c in cols:
        print('  ' + c['name'] + ': ' + str(c['type']))
db.close()