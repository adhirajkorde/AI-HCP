import os
import sys
import json
from datetime import datetime, timedelta

# Add parent directory to path so crm_backend is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_backend.app.core.db import SessionLocal
from crm_backend.app.agent.tools import (
    log_interaction_tool,
    edit_interaction_tool,
    hcp_profile_lookup_tool,
    followup_recommendation_tool,
    interaction_insights_tool
)
from crm_backend.app.models.database import HCP, Interaction

def print_section(title):
    print("\n" + "="*80)
    print(f" TOOL DEMO: {title}")
    print("="*80)

def main():
    db = SessionLocal()
    try:
        # Let's get Dr. Sarah Jenkins profile first to verify her ID
        hcp = db.query(HCP).filter(HCP.name.like("%Sarah%")).first()
        if not hcp:
            print("Error: Doctor profile 'Sarah' not found in database. Please run python seed.py first.")
            return
        
        hcp_id = hcp.id
        hcp_name = hcp.name
        print(f"Target HCP for demo: Dr. {hcp_name} (ID: {hcp_id})")

        # ----------------------------------------------------
        # 1. log_interaction_tool
        # ----------------------------------------------------
        print_section("1. log_interaction_tool (Logging a new interaction)")
        print(f"Calling: log_interaction_tool(hcp_name='{hcp_name}', interaction_type='Call', product_discussed='CardioPlus', ...)")
        log_res = log_interaction_tool(
            hcp_name=hcp_name,
            interaction_type="Call",
            product_discussed="CardioPlus",
            notes="Demo check-in call. Dr. Jenkins requested pricing info for CardioPlus.",
            outcome="Pending delivery of pricing schedules.",
            follow_up_date_str="tomorrow",
            user_id=1,
            db=db
        )
        print("Result:")
        print(json.dumps(log_res, indent=2))
        
        interaction_id = log_res.get("interaction_id")

        # ----------------------------------------------------
        # 2. edit_interaction_tool
        # ----------------------------------------------------
        print_section("2. edit_interaction_tool (Modifying an existing interaction)")
        if interaction_id:
            print(f"Calling: edit_interaction_tool(interaction_id={interaction_id}, notes='Updated notes for demo...', ...)")
            edit_res = edit_interaction_tool(
                interaction_id=interaction_id,
                interaction_type="Call",
                product_discussed="CardioPlus",
                notes="Demo check-in call - UPDATE: Emailed pricing schedule immediately after call.",
                outcome="Pricing sheets emailed. Action closed.",
                db=db
            )
            print("Result:")
            print(json.dumps(edit_res, indent=2))
        else:
            print("Skipping edit tool: Log interaction failed to return an ID.")

        # ----------------------------------------------------
        # 3. hcp_profile_lookup_tool
        # ----------------------------------------------------
        print_section("3. hcp_profile_lookup_tool (Looking up a profile by doctor's name)")
        print(f"Calling: hcp_profile_lookup_tool(hcp_name='{hcp_name}')")
        lookup_res = hcp_profile_lookup_tool(
            hcp_name=hcp_name,
            db=db
        )
        print("Result:")
        # Truncate long summary for readability
        if lookup_res.get("success") and "insights" in lookup_res:
            summary = lookup_res["insights"].get("summary", "")
            if len(summary) > 150:
                lookup_res["insights"]["summary"] = summary[:150] + "..."
        print(json.dumps(lookup_res, indent=2))

        # ----------------------------------------------------
        # 4. followup_recommendation_tool
        # ----------------------------------------------------
        print_section("4. followup_recommendation_tool (Generating AI follow-up recommendation)")
        print(f"Calling: followup_recommendation_tool(hcp_id={hcp_id})")
        followup_res = followup_recommendation_tool(
            hcp_id=hcp_id,
            db=db
        )
        print("Result:")
        print(json.dumps(followup_res, indent=2))

        # ----------------------------------------------------
        # 5. interaction_insights_tool
        # ----------------------------------------------------
        print_section("5. interaction_insights_tool (Computing discussion statistics)")
        print(f"Calling: interaction_insights_tool(hcp_id={hcp_id})")
        insights_res = interaction_insights_tool(
            hcp_id=hcp_id,
            db=db
        )
        print("Result:")
        print(json.dumps(insights_res, indent=2))

        print("\n" + "="*80)
        print(" ALL 5 TOOLS EXECUTED SUCCESSFULLY!")
        print("="*80)

    except Exception as e:
        print(f"\nError occurred during execution: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
