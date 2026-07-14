from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from crm_backend.app.models.database import User, HCP, Interaction, FollowUp, AIInsight
from crm_backend.app.schemas.crm_schemas import UserCreate, HCPCreate, HCPUpdate, InteractionCreate, InteractionUpdate, FollowUpCreate, FollowUpUpdate

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
