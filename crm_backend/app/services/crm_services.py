from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import desc
from sqlalchemy.orm import Session
import logging
from crm_backend.app.core.db import get_db
from crm_backend.app.core.security import verify_password, hash_password, create_access_token, verify_token
from crm_backend.app.repositories.crm_repositories import UserRepository, HCPRepository, InteractionRepository, FollowUpRepository, AIInsightRepository
from crm_backend.app.models.database import User, HCP, Interaction, FollowUp, AIInsight
from crm_backend.app.schemas.crm_schemas import UserCreate, UserLogin, UserResponse, HCPCreate, HCPUpdate, InteractionCreate, FollowUpCreate, FollowUpUpdate, Token, HCPDetailResponse

logger = logging.getLogger("crm_services")

# OAuth2 context
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class AuthService:
    @staticmethod
    def register_user(db: Session, user: UserCreate) -> UserResponse:
        db_user = UserRepository.get_by_username(db, user.username)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        hashed_pwd = hash_password(user.password)
        new_user = UserRepository.create(db, user, hashed_pwd)
        return UserResponse.from_orm(new_user)

    @staticmethod
    def login_for_access_token(db: Session, credentials: UserLogin) -> Token:
        user = UserRepository.get_by_username(db, credentials.username)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role}
        )
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = UserRepository.get_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user


class HCPService:
    @staticmethod
    def create_hcp(db: Session, hcp: HCPCreate):
        existing_hcp = HCPRepository.get_by_name(db, hcp.name)
        if existing_hcp:
            return existing_hcp
        # Just create
        new_hcp = HCPRepository.create(db, hcp)
        # Initialize default AI Insights
        AIInsightRepository.upsert(
            db,
            hcp_id=new_hcp.id,
            summary="New doctor profile created. No interactions logged yet.",
            sentiment="Neutral",
            engagement_score=50,
            medical_interests=new_hcp.specialty,
            product_preferences=new_hcp.product_preference or "None"
        )
        return new_hcp

    @staticmethod
    def get_hcp_profile(db: Session, hcp_id: int) -> HCPDetailResponse:
        hcp = HCPRepository.get_by_id(db, hcp_id)
        if not hcp:
            raise HTTPException(status_code=404, detail="HCP not found")
        
        interactions = InteractionRepository.get_by_hcp(db, hcp_id)
        followups = FollowUpRepository.get_by_hcp(db, hcp_id)
        ai_insight = AIInsightRepository.get_by_hcp(db, hcp_id)

        # Fallback if no insight exists yet
        if not ai_insight:
            ai_insight = AIInsightRepository.upsert(
                db, 
                hcp_id=hcp_id, 
                summary="Profile setup complete.", 
                sentiment="Neutral", 
                engagement_score=50
            )

        return HCPDetailResponse(
            hcp=hcp,
            interactions=interactions,
            followups=followups,
            ai_insight=ai_insight
        )


class InteractionService:
    @staticmethod
    def log_interaction(db: Session, interaction: InteractionCreate, user_id: int):
        # Create interaction
        new_interaction = InteractionRepository.create(db, interaction, user_id)

        # Auto-schedule followup if follow_up_date is provided
        if interaction.follow_up_date:
            followup_data = FollowUpCreate(
                interaction_id=new_interaction.id,
                hcp_id=interaction.hcp_id,
                follow_up_date=interaction.follow_up_date,
                priority_level="Medium",
                status="Pending",
                ai_recommendation=f"Follow up regarding {interaction.product_discussed} as scheduled."
            )
            FollowUpRepository.create(db, followup_data)

        # Update AI insights based on this interaction notes
        InteractionService.update_hcp_insights(db, interaction.hcp_id)

        # Publish automation event
        try:
            from crm_backend.app.services.automation_engine import publish_event
            from crm_backend.app.models.database import AutomationEventType
            hcp = HCPRepository.get_by_id(db, interaction.hcp_id)
            publish_event(
                event_type=AutomationEventType.INTERACTION_CREATED.value,
                source_id=new_interaction.id,
                source_type="interaction",
                user_id=user_id,
                payload={
                    "interaction_id": new_interaction.id,
                    "hcp_id": interaction.hcp_id,
                    "hcp_name": hcp.name if hcp else "Unknown",
                    "product_discussed": interaction.product_discussed,
                    "interaction_type": interaction.interaction_type,
                    "sentiment": "Neutral",  # Will be updated by AI
                    "priority": "Medium"
                }
            )
        except Exception as e:
            logger.warning(f"Failed to publish automation event: {e}")

        return new_interaction

    @staticmethod
    def update_hcp_insights(db: Session, hcp_id: int):
        # Retrieve all interactions for HCP
        interactions = InteractionRepository.get_by_hcp(db, hcp_id)
        if not interactions:
            return

        # Simple text sentiment heuristics for local mock mode
        # Count positive/negative keywords in notes
        pos_keywords = ["interested", "positive", "happy", "liked", "loves", "agreed", "great", "excellent", "trials", "willing"]
        neg_keywords = ["uninterested", "negative", "busy", "rejected", "disliked", "concern", "complained", "skeptical"]

        total_sentiment_score = 0
        all_notes = []
        products = set()

        for inter in interactions:
            notes = (inter.notes or "").lower()
            all_notes.append(inter.notes or "")
            if inter.product_discussed:
                products.add(inter.product_discussed)
            
            # Basic keyword score
            score = 0
            for w in pos_keywords:
                score += notes.count(w)
            for w in neg_keywords:
                score -= notes.count(w)
            
            # Map score to a simple rating
            total_sentiment_score += score

        # Compute engagement score (combining interaction frequency and sentiment)
        # Base is 50, +5 for each interaction (up to +30), sentiment adjustment
        base_engagement = 50 + (len(interactions) * 5)
        base_engagement = max(10, min(95, base_engagement + (total_sentiment_score * 3)))

        # Determine sentiment text
        if total_sentiment_score > 1:
            overall_sentiment = "Positive"
        elif total_sentiment_score < -1:
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Neutral"

        # Construct summary
        recent_interactions = interactions[:3]
        summary_bullets = [f"Logged {inter.interaction_type} on {inter.date_time.strftime('%Y-%m-%d')} discussing {inter.product_discussed} (Outcome: {inter.outcome or 'None'})." for inter in recent_interactions]
        summary = f"Doctor has {len(interactions)} recorded interactions. Recent touchpoints:\n- " + "\n- ".join(summary_bullets)

        hcp = HCPRepository.get_by_id(db, hcp_id)
        product_preferences = ", ".join(list(products)) if products else (hcp.product_preference or "None")

        # Upsert
        AIInsightRepository.upsert(
            db,
            hcp_id=hcp_id,
            summary=summary,
            sentiment=overall_sentiment,
            engagement_score=int(base_engagement),
            medical_interests=hcp.specialty,
            product_preferences=product_preferences
        )


class AnalyticsService:
    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        hcps_count = db.query(HCP).count()
        interactions_count = db.query(Interaction).count()
        pending_followups = db.query(FollowUp).filter(FollowUp.status == "Pending").count()

        # Get AI insights summaries
        insights = db.query(AIInsight).all()
        avg_engagement = sum([i.engagement_score for i in insights]) / len(insights) if insights else 50
        
        positive_count = sum([1 for i in insights if i.sentiment == "Positive"])
        neutral_count = sum([1 for i in insights if i.sentiment == "Neutral"])
        negative_count = sum([1 for i in insights if i.sentiment == "Negative"])

        # Fetch recent activities (last 5 interactions)
        recent_interactions = db.query(Interaction).order_by(desc(Interaction.created_at)).limit(5).all()
        recent_activities = []
        for ri in recent_interactions:
            hcp = HCPRepository.get_by_id(db, ri.hcp_id)
            recent_activities.append({
                "id": ri.id,
                "hcp_name": hcp.name if hcp else "Unknown",
                "hcp_id": ri.hcp_id,
                "interaction_type": ri.interaction_type,
                "product_discussed": ri.product_discussed,
                "outcome": ri.outcome,
                "date_time": ri.date_time,
                "created_at": ri.created_at
            })

        return {
            "total_hcps": hcps_count,
            "total_interactions": interactions_count,
            "upcoming_followups": pending_followups,
            "ai_insights_summary": {
                "average_engagement_score": round(avg_engagement, 1),
                "sentiment_distribution": {
                    "Positive": positive_count,
                    "Neutral": neutral_count,
                    "Negative": negative_count
                }
            },
            "recent_activities": recent_activities
        }

    @staticmethod
    def get_analytics_metrics(db: Session) -> Dict[str, Any]:
        # Sentiment trends
        insights = db.query(AIInsight).all()
        sentiment_distribution = {
            "Positive": sum([1 for i in insights if i.sentiment == "Positive"]),
            "Neutral": sum([1 for i in insights if i.sentiment == "Neutral"]),
            "Negative": sum([1 for i in insights if i.sentiment == "Negative"])
        }

        # Products discussed stats
        interactions = db.query(Interaction).all()
        product_stats = {}
        for inter in interactions:
            p = inter.product_discussed
            if p:
                product_stats[p] = product_stats.get(p, 0) + 1

        product_data = [{"name": k, "value": v} for k, v in product_stats.items()]

        # Engagement scores mapping
        engagement_scores = [i.engagement_score for i in insights]
        engagement_distribution = {
            "High (80-100)": sum([1 for s in engagement_scores if s >= 80]),
            "Medium (50-79)": sum([1 for s in engagement_scores if 50 <= s < 80]),
            "Low (0-49)": sum([1 for s in engagement_scores if s < 50])
        }

        # Follow-up completion rate
        total_followups = db.query(FollowUp).count()
        completed_followups = db.query(FollowUp).filter(FollowUp.status == "Completed").count()
        completion_rate = (completed_followups / total_followups * 100) if total_followups > 0 else 0

        # Create monthly interaction trend (last 6 months - mock structured data grouped)
        # For simplicity in SQLite/Postgres grouping, we will query dates directly and map
        monthly_trend = {}
        for inter in interactions:
            month_key = inter.date_time.strftime("%b %Y")
            monthly_trend[month_key] = monthly_trend.get(month_key, 0) + 1
        
        monthly_data = [{"month": k, "count": v} for k, v in monthly_trend.items()]
        # Sort monthly data by date if possible (quick fallback logic)
        monthly_data = sorted(monthly_data, key=lambda x: datetime.strptime(x["month"], "%b %Y") if "%b %Y" in x["month"] else datetime.now())[-6:]

        return {
            "sentiment_trends": sentiment_distribution,
            "engagement_score_distribution": engagement_distribution,
            "product_discussion_stats": product_data,
            "followup_metrics": {
                "total": total_followups,
                "completed": completed_followups,
                "completion_rate": round(completion_rate, 1)
            },
            "monthly_interaction_trends": monthly_data
        }
