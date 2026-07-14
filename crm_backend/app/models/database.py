from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from crm_backend.app.core.db import Base

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
