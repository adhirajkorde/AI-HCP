from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from crm_backend.app.core.db import Base, engine
from crm_backend.app.api import auth, hcps, interactions, followups, analytics

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Auto-create tables (SQLite/PostgreSQL fallback)
try:
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.error(f"Error during database table initialization: {e}")

app = FastAPI(
    title="AI-First HCP CRM API",
    description="Backend API for pharmaceutical sales interaction logs & AI insight summaries.",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(hcps.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")
app.include_router(followups.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AI-First HCP CRM Backend API",
        "docs": "/docs"
    }
