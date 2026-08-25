import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from crm_backend.app.core.config import settings
from crm_backend.app.schemas.crm_schemas import AIChatResponse, ExtractedEntities

# Setup logging
logger = logging.getLogger("agent")

# Try to import langchain packages, fallback if not installed or fails
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain/Groq libraries not available. Falling back to Mock NLP extraction.")

# Import new multi-agent workflow
from crm_backend.app.agent.agents import run_multi_agent_workflow

def parse_relative_date(date_str: str) -> datetime:
    """Parses relative date texts like 'next week' to a standard datetime."""
    now = datetime.utcnow()
    text = date_str.lower()
    if "tomorrow" in text:
        return now + timedelta(days=1)
    elif "next week" in text or "follow up next week" in text:
        return now + timedelta(days=7)
    elif "next month" in text:
        return now + timedelta(days=30)
    elif "two weeks" in text or "2 weeks" in text:
        return now + timedelta(days=14)
    else:
        # Default follow up in 7 days
        return now + timedelta(days=7)

def local_mock_extractor(text: str) -> Dict[str, Any]:
    """Fallback NLP entity extractor using regex and heuristics."""
    # Find doctor name
    hcp_match = re.search(r'(?:Dr\.\s*|Dr\s+)([A-Z][a-zA-Z]*)', text, re.IGNORECASE)
    hcp_name = hcp_match.group(1) if hcp_match else "Sharma"
    if not hcp_name.startswith("Dr."):
        full_hcp_name = f"Dr. {hcp_name}"
    else:
        full_hcp_name = hcp_name
        
    # Find product discussed
    products = ["CardioPlus", "NeuroZest", "LipoCare", "GastroShield", "Immunex"]
    product_discussed = "CardioPlus"  # default
    for p in products:
        if p.lower() in text.lower():
            product_discussed = p
            break
            
    # Find interaction type
    interaction_type = "In-Person Meeting"
    if "email" in text.lower():
        interaction_type = "Email"
    elif "call" in text.lower() or "phone" in text.lower():
        interaction_type = "Call"
    elif "meet" in text.lower() or "visit" in text.lower() or "met" in text.lower():
        interaction_type = "In-Person Meeting"

    # Find sentiment
    sentiment = "Neutral"
    engagement_score = 50
    pos_words = ["interested", "positive", "happy", "liked", "loves", "agreed", "great", "excellent", "trial", "willing"]
    neg_words = ["uninterested", "negative", "busy", "rejected", "disliked", "concern", "complained", "skeptical", "hard"]
    
    pos_count = sum(1 for w in pos_words if w in text.lower())
    neg_count = sum(1 for w in neg_words if w in text.lower())
    
    if pos_count > neg_count:
        sentiment = "Positive"
        engagement_score = 80 + min(15, pos_count * 2)
    elif neg_count > pos_count:
        sentiment = "Negative"
        engagement_score = 30 - min(15, neg_count * 2)
    else:
        sentiment = "Neutral"
        engagement_score = 55

    # Find follow up
    follow_up_date_str = None
    follow_up_action = None
    priority = "Medium"
    
    if "follow up" in text.lower() or "next week" in text.lower() or "tomorrow" in text.lower():
        follow_up_action = f"Provide clinical details or follow up on {product_discussed}."
        if "next week" in text.lower():
            follow_up_date_str = "next week"
            priority = "Medium"
        elif "tomorrow" in text.lower():
            follow_up_date_str = "tomorrow"
            priority = "High"
        else:
            follow_up_date_str = "next week"
            priority = "Medium"

    # Clean text to notes
    notes = text.strip()
    outcome = "Discussed clinical details of " + product_discussed

    return {
        "hcp_name": hcp_name,
        "full_hcp_name": full_hcp_name,
        "interaction_type": interaction_type,
        "product_discussed": product_discussed,
        "notes": notes,
        "outcome": outcome,
        "follow_up_date": follow_up_date_str,
        "sentiment": sentiment,
        "engagement_score": engagement_score,
        "summary": f"Logged interaction with {full_hcp_name} discussing {product_discussed}. Doctor reaction was {sentiment.lower()} (Engagement Score: {engagement_score}%). Follow-up scheduled for {follow_up_date_str or 'none'}.",
        "follow_up_action": follow_up_action,
        "suggested_priority": priority
    }


def groq_llm_extractor(text: str) -> Dict[str, Any]:
    """Extracts entities using Groq LLM API and structured prompt."""
    if not LANGCHAIN_AVAILABLE or not settings.GROQ_API_KEY:
        raise ValueError("Groq API Key not configured or dependencies missing")

    # Define ChatGroq LLM
    llm = ChatGroq(
        temperature=0.0,
        model_name=settings.DEFAULT_MODEL,
        groq_api_key=settings.GROQ_API_KEY
    )

    # Output JSON format schema prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert CRM assistant for a pharmaceutical sales team.
Analyze the user's interaction log and return a JSON object with the following fields:
- hcp_name: The name of the doctor (e.g. "Sharma", "Sarah Jenkins"). Remove "Dr." prefix.
- interaction_type: Standardized interaction type. Must be one of: "In-Person Meeting", "Call", "Email".
- product_discussed: The pharmaceutical product discussed (e.g. CardioPlus, NeuroZest, LipoCare).
- notes: Comprehensive notes capturing doctor feedback and discussion points.
- outcome: Short summary of the meeting outcome.
- follow_up_date: Approximate follow-up date description (e.g. "tomorrow", "next week", "2026-07-20", or null if not requested).
- sentiment: Sentiment of the interaction. Must be one of: "Positive", "Neutral", "Negative".
- engagement_score: Numeric score between 0 and 100 representing the doctor's interest.
- summary: A single-paragraph professional narrative summary of the interaction.
- follow_up_action: Specific recommended action for follow up, if any.
- suggested_priority: Priority of follow-up. Must be one of: "High", "Medium", "Low".

Example input: "Had a great lunch meeting with Dr Jenkins. We discussed NeuroZest. She wants to see more clinical trial data. I will email her next week."
Example output:
{{
  "hcp_name": "Jenkins",
  "interaction_type": "In-Person Meeting",
  "product_discussed": "NeuroZest",
  "notes": "Had a great lunch meeting. Discussed NeuroZest. Dr. Jenkins requested clinical trial papers.",
  "outcome": "Doctor is interested, requested clinical trial data.",
  "follow_up_date": "next week",
  "sentiment": "Positive",
  "engagement_score": 85,
  "summary": "Sales representative met Dr. Jenkins for lunch to discuss NeuroZest. The meeting went very well, with the doctor showing positive interest and requesting further clinical trial data. A follow-up email will be sent next week.",
  "follow_up_action": "Email clinical trials data for NeuroZest.",
  "suggested_priority": "Medium"
}}

Respond ONLY with valid JSON. Do not include markdown code block syntax (like ```json ... ```)."""),
        ("user", "Analyze this text: {text}")
    ])

    chain = prompt | llm | JsonOutputParser()
    return chain.invoke({"text": text})


def run_agent(text: str, user_id: int = 1, db: Optional[Session] = None) -> AIChatResponse:
    """Executes the AI agent to parse natural language logs using multi-agent workflow."""
    try:
        # Use new multi-agent workflow
        logger.info("Running multi-agent workflow for interaction analysis.")
        result = run_multi_agent_workflow(text, user_id, db)
        
        # Convert to AIChatResponse format for backward compatibility
        entities = result.get("entities")
        if entities is None:
            entities = ExtractedEntities()
        
        return AIChatResponse(
            success=result.get("success", True),
            message=result.get("message", "Multi-agent analysis complete."),
            entities=entities,
            summary=result.get("summary", ""),
            sentiment=result.get("sentiment", "Neutral"),
            engagement_score=result.get("engagement_score", 50),
            follow_up_action=result.get("follow_up_action"),
            suggested_priority=result.get("suggested_priority", "Medium"),
            raw_result=result
        )
        
    except Exception as e:
        logger.error(f"Multi-agent workflow failed: {e}")
        # Fallback to legacy extraction
        try:
            if settings.GROQ_API_KEY and LANGCHAIN_AVAILABLE:
                logger.info("Falling back to Groq LLM extraction.")
                extracted = groq_llm_extractor(text)
            else:
                logger.info("Falling back to Local Mock NLP heuristic engine.")
                extracted = local_mock_extractor(text)

            # Standardize doctor name
            hcp_name = extracted.get("hcp_name") or "Sharma"
            if not hcp_name.startswith("Dr. "):
                full_hcp_name = f"Dr. {hcp_name}"
            else:
                full_hcp_name = hcp_name
                hcp_name = hcp_name.replace("Dr. ", "")

            # Map to Pydantic schemas
            entities = ExtractedEntities(
                hcp_name=full_hcp_name,
                specialty=extracted.get("specialty") or "General Medicine",
                hospital_clinic=extracted.get("hospital_clinic") or "General Hospital",
                interaction_type=extracted.get("interaction_type") or "In-Person Meeting",
                product_discussed=extracted.get("product_discussed") or "CardioPlus",
                outcome=extracted.get("outcome") or "Discussed clinical trials",
                notes=extracted.get("notes") or text,
                follow_up_date=extracted.get("follow_up_date")
            )

            return AIChatResponse(
                success=True,
                message="Natural language input successfully parsed by AI CRM Agent (legacy).",
                entities=entities,
                summary=extracted.get("summary") or f"Logged interaction with {full_hcp_name}.",
                sentiment=extracted.get("sentiment") or "Neutral",
                engagement_score=int(extracted.get("engagement_score") or 50),
                follow_up_action=extracted.get("follow_up_action"),
                suggested_priority=extracted.get("suggested_priority") or "Medium",
                raw_result=extracted
            )
            
        except Exception as fallback_err:
            logger.error(f"Fallback also failed: {fallback_err}")
            return AIChatResponse(
                success=False,
                message=f"Agent process failed completely: {str(e)}. Fallback error: {str(fallback_err)}",
                entities=ExtractedEntities(),
                summary="",
                sentiment="Neutral",
                engagement_score=50,
                follow_up_action=None,
                suggested_priority="Medium",
                raw_result={}
            )
