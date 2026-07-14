import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from crm_backend.app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_init")

db_url = settings.DATABASE_URL
engine = None
SessionLocal = None

# Base class for SQLAlchemy models
Base = declarative_base()

try:
    logger.info(f"Attempting to connect to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    # SQLite requires separate parameters for thread safety, check if SQLite is being used
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        # For PostgreSQL/MySQL, configure connection pool and timeouts
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=1800,
            connect_args={"connect_timeout": 5}
        )
    # Test connection
    with engine.connect() as conn:
        logger.info("Database connection successfully established.")
except Exception as e:
    logger.warning(f"Failed to connect to primary database ({db_url}): {e}")
    logger.info("Falling back to local SQLite database: sqlite:///./crm_fallback.db")
    db_url = "sqlite:///./crm_fallback.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
