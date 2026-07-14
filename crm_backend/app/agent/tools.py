import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from crm_backend.app.core.db import SessionLocal
from crm_backend.app.repositories.crm_repositories import HCPRepository, InteractionRepository, FollowUpRepository, AIInsightRepository
from crm_backend.app.schemas.crm_schemas import HCPCreate, InteractionCreate, InteractionUpdate, FollowUpCreate, FollowUpUpdate

logger = logging.getLogger("agent_tools")

# Helpers to resolve database session inside tools if not provided
def get_db_session() -> Session:
    return SessionLocal()


def log_interaction_tool(
    hcp_name: str,
    interaction_type: str,
    product_discussed: str,
    notes: Optional[str] = None,
    outcome: Optional[str] = None,
    date_time_str: Optional[str] = None,
    follow_up_date_str: Optional[str] = None,
    user_id: int = 1,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Logs a new interaction with an HCP. Creates the HCP if they do not exist."""
    created_session = False
    if db is None:
        db = get_db_session()
        created_session = True
        
    try:
        # 1. Resolve or create HCP
        hcp = HCPRepository.get_by_name(db, hcp_name)
        if not hcp:
            logger.info(f"HCP '{hcp_name}' not found. Auto-creating profile.")
            hcp_create = HCPCreate(
                name=hcp_name,
                specialty="General Medicine",  # Default placeholder
                hospital_clinic="General Hospital (AI Auto-created)",
                email=None,
                phone=None,
                product_preference=product_discussed
            )
            # Create HCP using service logic or direct repo
            hcp = HCPRepository.create(db, hcp_create)
            AIInsightRepository.upsert(
                db,
                hcp_id=hcp.id,
                summary="Profile auto-created by AI Agent during interaction logging.",
                sentiment="Neutral",
                engagement_score=50,
                medical_interests=hcp.specialty,
                product_preferences=product_discussed
            )

        # 2. Parse Date
        date_time = datetime.utcnow()
        if date_time_str:
            try:
                date_time = datetime.fromisoformat(date_time_str.replace("Z", "+00:00"))
            except ValueError:
                pass

        follow_up_date = None
        if follow_up_date_str:
            try:
                follow_up_date = datetime.fromisoformat(follow_up_date_str.replace("Z", "+00:00"))
            except ValueError:
                # Handle relative descriptions like "next week"
                if "week" in follow_up_date_str.lower():
                    follow_up_date = datetime.utcnow() + timedelta(days=7)
                elif "tomorrow" in follow_up_date_str.lower():
                    follow_up_date = datetime.utcnow() + timedelta(days=1)
                elif "month" in follow_up_date_str.lower():
                    follow_up_date = datetime.utcnow() + timedelta(days=30)

        # 3. Create Interaction
        interaction_data = InteractionCreate(
            hcp_id=hcp.id,
            interaction_type=interaction_type or "In-Person Meeting",
            date_time=date_time,
            product_discussed=product_discussed,
            notes=notes,
            outcome=outcome,
            follow_up_date=follow_up_date
        )
        
        # Log via repository
        new_interaction = InteractionRepository.create(db, interaction_data, user_id)
        
        # 4. Auto-create follow-up in CRM if scheduled
        if follow_up_date:
            followup_data = FollowUpCreate(
                interaction_id=new_interaction.id,
                hcp_id=hcp.id,
                follow_up_date=follow_up_date,
                priority_level="Medium",
                status="Pending",
                ai_recommendation=f"Follow up regarding discussion of {product_discussed}."
            )
            FollowUpRepository.create(db, followup_data)

        # 5. Refresh Insights
        from crm_backend.app.services.crm_services import InteractionService
        InteractionService.update_hcp_insights(db, hcp.id)

        db.commit()
        return {
            "success": True,
            "interaction_id": new_interaction.id,
            "hcp_id": hcp.id,
            "hcp_name": hcp.name,
            "message": f"Successfully logged {interaction_type} interaction with Dr. {hcp.name} regarding {product_discussed}."
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error logging interaction: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if created_session:
            db.close()


def edit_interaction_tool(
    interaction_id: int,
    interaction_type: Optional[str] = None,
    product_discussed: Optional[str] = None,
    notes: Optional[str] = None,
    outcome: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Modifies an existing interaction in the CRM."""
    created_session = False
    if db is None:
        db = get_db_session()
        created_session = True
        
    try:
        db_inter = InteractionRepository.get_by_id(db, interaction_id)
        if not db_inter:
            return {"success": False, "error": f"Interaction ID {interaction_id} not found"}

        update_schema = InteractionUpdate(
            interaction_type=interaction_type,
            product_discussed=product_discussed,
            notes=notes,
            outcome=outcome
        )
        
        updated_inter = InteractionRepository.update(db, db_inter, update_schema)
        
        # Refresh insights
        from crm_backend.app.services.crm_services import InteractionService
        InteractionService.update_hcp_insights(db, updated_inter.hcp_id)
        
        db.commit()
        return {
            "success": True,
            "interaction_id": updated_inter.id,
            "message": f"Interaction details for ID {interaction_id} updated successfully."
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        if created_session:
            db.close()


def hcp_profile_lookup_tool(
    hcp_name: str,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Searches and retrieves detailed profile information for an HCP."""
    created_session = False
    if db is None:
        db = get_db_session()
        created_session = True
        
    try:
        hcp = HCPRepository.get_by_name(db, hcp_name)
        if not hcp:
            return {"success": False, "error": f"Dr. {hcp_name} not found in the database."}

        insights = AIInsightRepository.get_by_hcp(db, hcp.id)
        interactions = InteractionRepository.get_by_hcp(db, hcp.id)
        followups = FollowUpRepository.get_by_hcp(db, hcp.id)

        return {
            "success": True,
            "hcp": {
                "id": hcp.id,
                "name": hcp.name,
                "specialty": hcp.specialty,
                "hospital_clinic": hcp.hospital_clinic,
                "email": hcp.email,
                "phone": hcp.phone,
                "product_preference": hcp.product_preference
            },
            "insights": {
                "summary": insights.summary if insights else "No insights generated yet.",
                "sentiment": insights.sentiment if insights else "Neutral",
                "engagement_score": insights.engagement_score if insights else 50,
                "product_preferences": insights.product_preferences if insights else None
            },
            "interactions_count": len(interactions),
            "pending_followups_count": len([f for f in followups if f.status == "Pending"])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if created_session:
            db.close()


def followup_recommendation_tool(
    hcp_id: int,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Generates AI follow-up recommendation strategies for a specific HCP."""
    created_session = False
    if db is None:
        db = get_db_session()
        created_session = True
        
    try:
        hcp = HCPRepository.get_by_id(db, hcp_id)
        if not hcp:
            return {"success": False, "error": f"HCP ID {hcp_id} not found."}

        insights = AIInsightRepository.get_by_hcp(db, hcp_id)
        interactions = InteractionRepository.get_by_hcp(db, hcp_id)

        # Build recommendation strategies based on current status
        score = insights.engagement_score if insights else 50
        sentiment = insights.sentiment if insights else "Neutral"
        
        rec = ""
        priority = "Medium"
        timeframe_days = 7
        
        if score < 40:
            rec = f"Low engagement detected. Reconnect with Dr. {hcp.name} by providing clinical trial papers on {hcp.product_preference or 'our therapies'} to establish scientific interest."
            priority = "High"
            timeframe_days = 5
        elif sentiment == "Positive":
            rec = f"Excellent positive sentiment. Follow up with Dr. {hcp.name} with sample deliveries or formulary listing documents for {hcp.product_preference or 'discussed products'}."
            priority = "Medium"
            timeframe_days = 10
        else:
            rec = f"Standard follow-up schedule. Send clinical updates on {hcp.product_preference or 'recent therapeutics'} via email."
            priority = "Low"
            timeframe_days = 14

        return {
            "success": True,
            "hcp_name": hcp.name,
            "engagement_score": score,
            "sentiment": sentiment,
            "recommended_priority": priority,
            "recommended_date": (datetime.utcnow() + timedelta(days=timeframe_days)).isoformat(),
            "recommendation": rec
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if created_session:
            db.close()


def interaction_insights_tool(
    hcp_id: int,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Computes specific insights and discussion statistics for an HCP."""
    created_session = False
    if db is None:
        db = get_db_session()
        created_session = True
        
    try:
        hcp = HCPRepository.get_by_id(db, hcp_id)
        if not hcp:
            return {"success": False, "error": f"HCP ID {hcp_id} not found."}

        interactions = InteractionRepository.get_by_hcp(db, hcp_id)
        
        products = {}
        types = {}
        for inter in interactions:
            products[inter.product_discussed] = products.get(inter.product_discussed, 0) + 1
            types[inter.interaction_type] = types.get(inter.interaction_type, 0) + 1

        return {
            "success": True,
            "hcp_name": hcp.name,
            "total_interactions": len(interactions),
            "product_distribution": products,
            "channel_distribution": types,
            "clinical_profile": {
                "specialty": hcp.specialty,
                "facility": hcp.hospital_clinic
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if created_session:
            db.close()
