import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from crm_backend.app.core.db import SessionLocal, Base, engine
from crm_backend.app.models.database import User, HCP, Interaction, FollowUp, AIInsight
from crm_backend.app.core.security import hash_password
from crm_backend.app.services.crm_services import InteractionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

def seed_db():
    # Drop all tables and recreate for clean schema
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Ensure tables exist
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Clear existing tables for a clean seed
        logger.info("Clearing existing tables...")
        db.query(FollowUp).delete()
        db.query(AIInsight).delete()
        db.query(Interaction).delete()
        db.query(HCP).delete()
        db.query(User).delete()
        db.commit()

        # 1. Create Default Users
        logger.info("Creating default users...")
        hashed_pw = hash_password("password123")
        user1 = User(
            username="rep1",
            email="representative1@pharma.com",
            hashed_password=hashed_pw,
            role="medical_representative"
        )
        user2 = User(
            username="admin",
            email="admin@pharma.com",
            hashed_password=hashed_pw,
            role="medical_representative"
        )
        db.add_all([user1, user2])
        db.commit()
        db.refresh(user1)

        # 2. Create Doctors (HCPs)
        logger.info("Creating doctor profiles...")
        hcps = [
            HCP(
                name="Sarah Jenkins",
                specialty="Cardiology",
                hospital_clinic="Metro Heart Clinic",
                email="sjenkins@metroheart.com",
                phone="555-0192",
                product_preference="CardioPlus"
            ),
            HCP(
                name="Robert Sharma",
                specialty="Endocrinology",
                hospital_clinic="City Endocrinology Center",
                email="rsharma@cityendo.com",
                phone="555-0143",
                product_preference="LipoCare"
            ),
            HCP(
                name="Michael Chang",
                specialty="Neurology",
                hospital_clinic="Chang Neurology Clinic",
                email="mchang@changneuro.com",
                phone="555-0187",
                product_preference="NeuroZest"
            ),
            HCP(
                name="Emily Watson",
                specialty="Gastroenterology",
                hospital_clinic="Watson Digestive Clinic",
                email="ewatson@watsonclinic.com",
                phone="555-0121",
                product_preference="GastroShield"
            ),
            HCP(
                name="James Peterson",
                specialty="Immunology",
                hospital_clinic="State Immunology Center",
                email="jpeterson@stateimmuno.org",
                phone="555-0155",
                product_preference="Immunex"
            )
        ]
        db.add_all(hcps)
        db.commit()
        
        for h in hcps:
            db.refresh(h)

        # 3. Create Interactions & Follow-Ups
        logger.info("Logging historical interactions...")
        now = datetime.utcnow()
        
        # Interactions for Dr. Sarah Jenkins
        inter1 = Interaction(
            hcp_id=hcps[0].id,
            user_id=user1.id,
            interaction_type="In-Person Meeting",
            date_time=now - timedelta(days=20),
            product_discussed="CardioPlus",
            notes="Met Dr. Jenkins for lunch. Discussed CardioPlus Phase III trials. She was extremely interested in the reduced risk profile and asked for copy of the slides.",
            outcome="High interest. Requested trial data files.",
            follow_up_date=now - timedelta(days=13)
        )
        inter2 = Interaction(
            hcp_id=hcps[0].id,
            user_id=user1.id,
            interaction_type="Email",
            date_time=now - timedelta(days=13),
            product_discussed="CardioPlus",
            notes="Sent the CardioPlus Phase III PDF data via email. Checked in on her schedule for next meeting.",
            outcome="Follow up email sent.",
            follow_up_date=None
        )
        inter3 = Interaction(
            hcp_id=hcps[0].id,
            user_id=user1.id,
            interaction_type="Call",
            date_time=now - timedelta(days=2),
            product_discussed="CardioPlus",
            notes="Call to confirm receipt of the trial data. Dr. Jenkins read it and was highly impressed with cardiac mortality rates. She requested formulary add-on paperwork.",
            outcome="Loves the results. Requested formulary paperwork next week.",
            follow_up_date=now + timedelta(days=5)
        )
        
        # Interactions for Dr. Robert Sharma
        inter4 = Interaction(
            hcp_id=hcps[1].id,
            user_id=user1.id,
            interaction_type="In-Person Meeting",
            date_time=now - timedelta(days=15),
            product_discussed="LipoCare",
            notes="Visited Dr. Sharma at City Endo. Discussed LipoCare for diabetic patient cholesterol management. He is somewhat concerned with potential liver enzyme elevations. Provided safety charts.",
            outcome="Neutral. Will review safety chart and clinical trial summaries.",
            follow_up_date=now + timedelta(days=7)
        )
        
        # Interactions for Dr. Michael Chang
        inter5 = Interaction(
            hcp_id=hcps[2].id,
            user_id=user1.id,
            interaction_type="Call",
            date_time=now - timedelta(days=25),
            product_discussed="NeuroZest",
            notes="Quick check-in call with Dr. Chang. He has been prescribing NeuroZest for mild cognitive impairment. Reports positive feedback from 3 patients, but wants pricing charts for Medicare patients.",
            outcome="Positive interest, pricing queries.",
            follow_up_date=now - timedelta(days=18)
        )
        inter6 = Interaction(
            hcp_id=hcps[2].id,
            user_id=user1.id,
            interaction_type="Email",
            date_time=now - timedelta(days=18),
            product_discussed="NeuroZest",
            notes="Emailed the Medicare formulary pricing schedule and Patient Copay coupons to Dr. Chang's nurse.",
            outcome="Copay information sent.",
            follow_up_date=now + timedelta(days=12)
        )

        # Interactions for Dr. Emily Watson
        inter7 = Interaction(
            hcp_id=hcps[3].id,
            user_id=user1.id,
            interaction_type="Call",
            date_time=now - timedelta(days=30),
            product_discussed="GastroShield",
            notes="Introductory call to present GastroShield. Dr. Watson was extremely busy with patients, could not talk long. Suggested emailing information packet.",
            outcome="Busy, suggested email.",
            follow_up_date=now - timedelta(days=25)
        )
        inter8 = Interaction(
            hcp_id=hcps[3].id,
            user_id=user1.id,
            interaction_type="Email",
            date_time=now - timedelta(days=25),
            product_discussed="GastroShield",
            notes="Sent the digital introductory information packet for GastroShield.",
            outcome="Sent initial collateral.",
            follow_up_date=now + timedelta(days=4)
        )

        db.add_all([inter1, inter2, inter3, inter4, inter5, inter6, inter7, inter8])
        db.commit()

        # 4. Add Follow-up task items
        logger.info("Adding follow-ups...")
        followups = [
            FollowUp(
                interaction_id=inter3.id,
                hcp_id=hcps[0].id,
                follow_up_date=now + timedelta(days=5),
                priority_level="High",
                status="Pending",
                ai_recommendation="Send clinical trial addendum on cardiac safety and deliver formulary application form."
            ),
            FollowUp(
                interaction_id=inter4.id,
                hcp_id=hcps[1].id,
                follow_up_date=now + timedelta(days=7),
                priority_level="Medium",
                status="Pending",
                ai_recommendation="Schedule follow-up call to review safety charts and see if he has questions regarding liver safety."
            ),
            FollowUp(
                interaction_id=inter6.id,
                hcp_id=hcps[2].id,
                follow_up_date=now + timedelta(days=12),
                priority_level="Low",
                status="Pending",
                ai_recommendation="Follow up during monthly visit to assess patient outcomes on NeuroZest."
            ),
            FollowUp(
                interaction_id=inter8.id,
                hcp_id=hcps[3].id,
                follow_up_date=now + timedelta(days=4),
                priority_level="Medium",
                status="Pending",
                ai_recommendation="Email follow-up to schedule brief in-person details meeting for GastroShield."
            ),
            # Already completed follow-up for Chang
            FollowUp(
                interaction_id=inter5.id,
                hcp_id=hcps[2].id,
                follow_up_date=now - timedelta(days=18),
                priority_level="Medium",
                status="Completed",
                ai_recommendation="Deliver patient copay cards."
            )
        ]
        db.add_all(followups)
        db.commit()

        # 5. Populate AI Insights using service calculations
        logger.info("Compiling and upserting AI insights...")
        for h in hcps:
            InteractionService.update_hcp_insights(db, h.id)
            
        logger.info("Seeding completed successfully!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
