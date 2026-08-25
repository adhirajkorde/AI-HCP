import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq

from crm_backend.app.core.config import settings
from crm_backend.app.agent.state import AgentState, AgentOutput, SupervisorDecision
from crm_backend.app.schemas.crm_schemas import ExtractedEntities, AIChatResponse
from crm_backend.app.repositories.crm_repositories import HCPRepository
from crm_backend.app.services.automation_engine import publish_event
from crm_backend.app.models.database import AutomationEventType

logger = logging.getLogger("agents")


def get_llm():
    """Get Groq LLM instance if available."""
    if settings.GROQ_API_KEY:
        return ChatGroq(
            temperature=0.0,
            model_name=settings.DEFAULT_MODEL,
            groq_api_key=settings.GROQ_API_KEY
        )
    return None


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
        return now + timedelta(days=7)


def interaction_agent(state: AgentState, db: Optional[Session] = None) -> AgentState:
    """Agent 1: Extract HCP, product, discussion topics, interaction type, intent, action items."""
    text = state.get("text", "")
    logger.info(f"InteractionAgent processing: {text[:100]}...")

    llm = get_llm()
    if llm:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert CRM assistant for pharmaceutical sales.
Analyze the user's interaction log and extract structured information.

Return JSON with:
- hcp_name: Doctor name (e.g. "Sharma", remove "Dr." prefix)
- specialty: Medical specialty if mentioned
- hospital_clinic: Hospital/clinic name if mentioned
- interaction_type: One of "In-Person Meeting", "Call", "Email"
- product_discussed: Product name (CardioPlus, NeuroZest, LipoCare, GastroShield, Immunex)
- notes: Comprehensive notes capturing discussion points
- outcome: Short summary of meeting outcome
- follow_up_date: Relative date description (e.g. "next week", "tomorrow") or null
- intent: Primary intent (information_request, trial_inquiry, sample_request, follow_up_scheduling, general_discussion)
- action_items: List of specific action items mentioned
- requested_information: List of information HCP requested

Example:
Input: "Met Dr Sharma today. Discussed CardioPlus. Interested in clinical trial data. Follow up next Tuesday."
Output:
{
  "hcp_name": "Sharma",
  "specialty": "Cardiology",
  "hospital_clinic": "",
  "interaction_type": "In-Person Meeting",
  "product_discussed": "CardioPlus",
  "notes": "Met Dr Sharma today. Discussed CardioPlus. Interested in clinical trial data.",
  "outcome": "HCP interested in clinical trial data for CardioPlus",
  "follow_up_date": "next Tuesday",
  "intent": "trial_inquiry",
  "action_items": ["Send clinical trial data for CardioPlus"],
  "requested_information": ["Clinical trial data for CardioPlus"]
}

Respond ONLY with valid JSON."""),
            ("user", "Analyze: {text}")
        ])
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({"text": text})
    else:
        # Fallback to local extraction
        result = local_interaction_extractor(text)

    entities = ExtractedEntities(
        hcp_name=f"Dr. {result.get('hcp_name', 'Unknown')}",
        specialty=result.get("specialty") or "General Medicine",
        hospital_clinic=result.get("hospital_clinic") or "General Hospital",
        interaction_type=result.get("interaction_type") or "In-Person Meeting",
        product_discussed=result.get("product_discussed") or "CardioPlus",
        outcome=result.get("outcome") or "Discussion completed",
        notes=result.get("notes") or text,
        follow_up_date=result.get("follow_up_date")
    )

    agent_outputs = state.get("agent_outputs", {})
    agent_outputs["interaction"] = AgentOutput(
        agent="interaction",
        success=True,
        output=result,
        confidence=0.9 if llm else 0.6
    ).model_dump()

    return {
        **state,
        "entities": entities,
        "agent_outputs": agent_outputs,
        "current_agent": "sentiment"
    }


def local_interaction_extractor(text: str) -> Dict[str, Any]:
    """Fallback NLP entity extractor using regex and heuristics."""
    import re
    
    # Find doctor name
    hcp_match = re.search(r'(?:Dr\.\s*|Dr\s+)([A-Z][a-zA-Z]*)', text, re.IGNORECASE)
    hcp_name = hcp_match.group(1) if hcp_match else "Sharma"
    
    # Find product discussed
    products = ["CardioPlus", "NeuroZest", "LipoCare", "GastroShield", "Immunex"]
    product_discussed = "CardioPlus"
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

    # Find follow up
    follow_up_date = None
    if "follow up" in text.lower() or "next week" in text.lower() or "tomorrow" in text.lower() or "next tuesday" in text.lower():
        if "next week" in text.lower():
            follow_up_date = "next week"
        elif "tomorrow" in text.lower():
            follow_up_date = "tomorrow"
        elif "next tuesday" in text.lower() or "next tue" in text.lower():
            follow_up_date = "next Tuesday"
        else:
            follow_up_date = "next week"

    # Determine intent
    intent = "general_discussion"
    text_lower = text.lower()
    if "trial" in text_lower or "clinical" in text_lower:
        intent = "trial_inquiry"
    elif "sample" in text_lower:
        intent = "sample_request"
    elif "information" in text_lower or "data" in text_lower or "details" in text_lower:
        intent = "information_request"
    elif "follow up" in text_lower:
        intent = "follow_up_scheduling"

    action_items = []
    if "send" in text_lower or "email" in text_lower:
        action_items.append(f"Send information about {product_discussed}")
    if "follow up" in text_lower:
        action_items.append("Schedule follow-up meeting")

    requested_info = []
    if "clinical trial" in text_lower:
        requested_info.append(f"Clinical trial data for {product_discussed}")
    if "safety" in text_lower:
        requested_info.append(f"Safety profile for {product_discussed}")

    return {
        "hcp_name": hcp_name,
        "specialty": "Cardiology" if "cardio" in text_lower else "General Medicine",
        "hospital_clinic": "General Hospital",
        "interaction_type": interaction_type,
        "product_discussed": product_discussed,
        "notes": text.strip(),
        "outcome": f"Discussed {product_discussed}. HCP showed interest.",
        "follow_up_date": follow_up_date,
        "intent": intent,
        "action_items": action_items,
        "requested_information": requested_info
    }


def sentiment_agent(state: AgentState, db: Optional[Session] = None) -> AgentState:
    """Agent 2: Determine sentiment, engagement level, confidence."""
    text = state.get("text", "")
    interaction_output = state.get("agent_outputs", {}).get("interaction", {}).get("output", {})
    logger.info("SentimentAgent analyzing sentiment...")

    llm = get_llm()
    if llm:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze the sentiment and engagement level of this HCP interaction.
Consider the language used, specific requests, and overall tone.

Return JSON with:
- sentiment: One of "Positive", "Neutral", "Negative"
- engagement_score: Integer 0-100 (higher = more engaged)
- confidence: Float 0-1 (confidence in assessment)
- key_indicators: List of phrases that indicate sentiment
- engagement_signals: List of positive engagement signals found
- concerns: List of concerns or negative signals found

Example:
Input: "Met Dr Sharma today. Discussed CardioPlus. Interested in clinical trial data. Follow up next Tuesday."
Output:
{
  "sentiment": "Positive",
  "engagement_score": 85,
  "confidence": 0.9,
  "key_indicators": ["Interested in clinical trial data", "Follow up next Tuesday"],
  "engagement_signals": ["Requested clinical trial data", "Proposed specific follow-up timeline"],
  "concerns": []
}"""),
            ("user", "Analyze sentiment: {text}\n\nExtracted context: {context}")
        ])
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "text": text,
            "context": json.dumps(interaction_output)
        })
    else:
        result = local_sentiment_analyzer(text)

    agent_outputs = state.get("agent_outputs", {})
    agent_outputs["sentiment"] = AgentOutput(
        agent="sentiment",
        success=True,
        output=result,
        confidence=result.get("confidence", 0.7)
    ).model_dump()

    return {
        **state,
        "sentiment": result.get("sentiment", "Neutral"),
        "engagement_score": result.get("engagement_score", 50),
        "agent_outputs": agent_outputs,
        "current_agent": "hcp"
    }


def local_sentiment_analyzer(text: str) -> Dict[str, Any]:
    """Fallback sentiment analysis using keyword heuristics."""
    pos_words = ["interested", "positive", "happy", "liked", "loves", "agreed", "great", 
                 "excellent", "trial", "willing", "impressed", "excited", "keen", "eager"]
    neg_words = ["uninterested", "negative", "busy", "rejected", "disliked", "concern", 
                 "complained", "skeptical", "hard", "difficult", "hesitant", "worried",
                 "declined", "not interested", "no time"]
    
    text_lower = text.lower()
    pos_count = sum(1 for w in pos_words if w in text_lower)
    neg_count = sum(1 for w in neg_words if w in text_lower)
    
    key_indicators = []
    engagement_signals = []
    concerns = []
    
    for w in pos_words:
        if w in text_lower:
            engagement_signals.append(w)
            key_indicators.append(w)
    for w in neg_words:
        if w in text_lower:
            concerns.append(w)
            key_indicators.append(w)
    
    if pos_count > neg_count:
        sentiment = "Positive"
        engagement_score = 70 + min(25, pos_count * 3)
    elif neg_count > pos_count:
        sentiment = "Negative"
        engagement_score = 30 - min(20, neg_count * 3)
    else:
        sentiment = "Neutral"
        engagement_score = 50
    
    engagement_score = max(0, min(100, engagement_score))
    confidence = 0.6 + min(0.3, (pos_count + neg_count) * 0.05)
    
    return {
        "sentiment": sentiment,
        "engagement_score": engagement_score,
        "confidence": confidence,
        "key_indicators": key_indicators,
        "engagement_signals": engagement_signals,
        "concerns": concerns
    }


def hcp_agent(state: AgentState, db: Optional[Session] = None) -> AgentState:
    """Agent 3: Identify HCP, retrieve existing profile, detect useful updates."""
    entities = state.get("entities")
    if not entities:
        return {**state, "current_agent": "followup"}
    
    hcp_name = entities.hcp_name.replace("Dr. ", "").strip() if entities.hcp_name else ""
    logger.info(f"HCPAgent looking up: {hcp_name}")

    agent_outputs = state.get("agent_outputs", {})
    
    if db and hcp_name:
        hcp = HCPRepository.get_by_name(db, hcp_name)
        if hcp:
            # Check for profile updates
            updates = {}
            if entities.specialty and entities.specialty != hcp.specialty:
                updates["specialty"] = {"current": hcp.specialty, "suggested": entities.specialty}
            if entities.hospital_clinic and entities.hospital_clinic != hcp.hospital_clinic:
                updates["hospital_clinic"] = {"current": hcp.hospital_clinic, "suggested": entities.hospital_clinic}
            if entities.product_discussed and entities.product_discussed != hcp.product_preference:
                updates["product_preference"] = {"current": hcp.product_preference, "suggested": entities.product_discussed}
            
            result = {
                "hcp_found": True,
                "hcp_id": hcp.id,
                "hcp_name": hcp.name,
                "profile_updates": updates,
                "has_updates": len(updates) > 0
            }
        else:
            result = {
                "hcp_found": False,
                "hcp_name": hcp_name,
                "suggested_create": {
                    "name": hcp_name,
                    "specialty": entities.specialty,
                    "hospital_clinic": entities.hospital_clinic,
                    "product_preference": entities.product_discussed
                }
            }
    else:
        result = {"hcp_found": False, "hcp_name": hcp_name}

    agent_outputs["hcp"] = AgentOutput(
        agent="hcp",
        success=True,
        output=result,
        confidence=0.95 if result.get("hcp_found") else 0.7
    ).model_dump()

    return {
        **state,
        "agent_outputs": agent_outputs,
        "current_agent": "followup"
    }


def followup_agent(state: AgentState, db: Optional[Session] = None) -> AgentState:
    """Agent 4: Determine if follow-up required, type, priority, date, description."""
    interaction_output = state.get("agent_outputs", {}).get("interaction", {}).get("output", {})
    sentiment_output = state.get("agent_outputs", {}).get("sentiment", {}).get("output", {})
    entities = state.get("entities")
    
    logger.info("FollowUpAgent determining follow-up needs...")

    llm = get_llm()
    follow_up_date_str = interaction_output.get("follow_up_date")
    intent = interaction_output.get("intent", "general_discussion")
    action_items = interaction_output.get("action_items", [])
    requested_info = interaction_output.get("requested_information", [])
    sentiment = state.get("sentiment", "Neutral")
    engagement_score = state.get("engagement_score", 50)

    requires_followup = bool(follow_up_date_str or action_items or requested_info or intent in ["trial_inquiry", "sample_request", "information_request"])
    
    if llm and requires_followup:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Based on the interaction analysis, determine follow-up requirements.
Return JSON with:
- requires_followup: boolean
- followup_type: One of "information_delivery", "meeting_scheduling", "sample_delivery", "trial_data_sharing", "general_checkin"
- priority: One of "High", "Medium", "Low"
- recommended_date: ISO date string or relative description
- description: Specific follow-up task description
- ai_reason: Why this follow-up is needed
- confidence: 0-1 confidence score

Consider:
- Positive sentiment + trial inquiry = High priority, information_delivery
- Sample request = High priority, sample_delivery  
- Negative sentiment = Medium priority, general_checkin
- No specific request but follow-up mentioned = Medium priority, meeting_scheduling"""),
            ("user", """Interaction: {interaction}
Sentiment: {sentiment}
Engagement: {engagement}
Intent: {intent}
Action items: {actions}
Requested info: {requested}
Follow-up date mentioned: {followup_date}""")
        ])
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "interaction": json.dumps(interaction_output),
            "sentiment": sentiment,
            "engagement": engagement_score,
            "intent": intent,
            "actions": json.dumps(action_items),
            "requested": json.dumps(requested_info),
            "followup_date": follow_up_date_str or "none"
        })
    else:
        result = local_followup_decider(interaction_output, sentiment, engagement_score, intent)

    # Parse recommended date
    recommended_date = result.get("recommended_date")
    if recommended_date and isinstance(recommended_date, str):
        try:
            if "T" in recommended_date:
                pass  # Already ISO format
            else:
                recommended_date = parse_relative_date(recommended_date).isoformat()
        except:
            recommended_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

    agent_outputs = state.get("agent_outputs", {})
    agent_outputs["followup"] = AgentOutput(
        agent="followup",
        success=True,
        output={**result, "recommended_date_iso": recommended_date},
        confidence=result.get("confidence", 0.7),
        requires_approval=result.get("priority") == "High"
    ).model_dump()

    # Set approval requirement for high priority
    if result.get("priority") == "High":
        state["requires_approval"] = True
        state["approval_reason"] = "High priority follow-up requires approval"
        state["risk_level"] = "high"

    return {
        **state,
        "follow_up_action": result.get("description"),
        "suggested_priority": result.get("priority", "Medium"),
        "agent_outputs": agent_outputs,
        "current_agent": "notification"
    }


def local_followup_decider(interaction_output: Dict, sentiment: str, engagement: int, intent: str) -> Dict[str, Any]:
    """Fallback follow-up decision logic."""
    follow_up_date_str = interaction_output.get("follow_up_date")
    action_items = interaction_output.get("action_items", [])
    requested_info = interaction_output.get("requested_information", [])
    
    requires_followup = bool(follow_up_date_str or action_items or requested_info or intent in ["trial_inquiry", "sample_request", "information_request"])
    
    if not requires_followup:
        return {"requires_followup": False, "confidence": 0.8}
    
    # Determine priority
    if sentiment == "Positive" and intent in ["trial_inquiry", "sample_request"]:
        priority = "High"
        followup_type = "information_delivery" if intent == "trial_inquiry" else "sample_delivery"
    elif sentiment == "Negative":
        priority = "Medium"
        followup_type = "general_checkin"
    elif follow_up_date_str:
        priority = "Medium"
        followup_type = "meeting_scheduling"
    else:
        priority = "Medium"
        followup_type = "information_delivery"
    
    # Description
    if action_items:
        description = action_items[0]
    elif requested_info:
        description = f"Provide {requested_info[0]}"
    else:
        description = f"Follow up on {interaction_output.get('product_discussed', 'discussion')}"
    
    return {
        "requires_followup": True,
        "followup_type": followup_type,
        "priority": priority,
        "recommended_date": follow_up_date_str or "next week",
        "description": description,
        "ai_reason": f"HCP {intent.replace('_', ' ')} with {sentiment.lower()} sentiment",
        "confidence": 0.7
    }


def notification_agent(state: AgentState, db: Optional[Session] = None) -> AgentState:
    """Agent 5: Determine if notification required, recipient, severity, message."""
    logger.info("NotificationAgent evaluating notifications...")
    
    sentiment_output = state.get("agent_outputs", {}).get("sentiment", {}).get("output", {})
    followup_output = state.get("agent_outputs", {}).get("followup", {}).get("output", {})
    hcp_output = state.get("agent_outputs", {}).get("hcp", {}).get("output", {})
    entities = state.get("entities")
    
    sentiment = state.get("sentiment", "Neutral")
    engagement_score = state.get("engagement_score", 50)
    requires_followup = followup_output.get("requires_followup", False)
    priority = followup_output.get("priority", "Medium")
    
    notifications = []
    
    # Negative sentiment notification
    if sentiment == "Negative":
        notifications.append({
            "type": "sentiment_negative",
            "severity": "warning",
            "title": "Negative Sentiment Detected",
            "message": f"Negative sentiment detected for interaction with {entities.hcp_name if entities else 'HCP'}. Review recommended.",
            "recipient_role": "representative"
        })
    
    # High priority follow-up notification
    if requires_followup and priority == "High":
        notifications.append({
            "type": "high_priority_followup",
            "severity": "high",
            "title": "High Priority Follow-up Required",
            "message": f"High priority follow-up needed for {entities.hcp_name if entities else 'HCP'}: {followup_output.get('description', 'Follow up required')}",
            "recipient_role": "representative"
        })
    
    # Low engagement notification
    if engagement_score < 40:
        notifications.append({
            "type": "low_engagement",
            "severity": "info",
            "title": "Low HCP Engagement",
            "message": f"Engagement score for {entities.hcp_name if entities else 'HCP'} is {engagement_score}%. Consider re-engagement strategy.",
            "recipient_role": "representative"
        })
    
    # New HCP notification
    if hcp_output and not hcp_output.get("hcp_found", False):
        notifications.append({
            "type": "new_hcp",
            "severity": "info",
            "title": "New HCP Identified",
            "message": f"New HCP detected: {entities.hcp_name if entities else 'Unknown'}. Profile creation recommended.",
            "recipient_role": "representative"
        })

    agent_outputs = state.get("agent_outputs", {})
    agent_outputs["notification"] = AgentOutput(
        agent="notification",
        success=True,
        output={"notifications": notifications},
        confidence=0.8
    ).model_dump()

    return {
        **state,
        "agent_outputs": agent_outputs,
        "current_agent": "supervisor"
    }


def supervisor_agent(state: AgentState, db: Optional[Session] = None) -> AgentState:
    """Supervisor Agent: Coordinate agents and decide final actions."""
    logger.info("SupervisorAgent making final decisions...")
    
    interaction_output = state.get("agent_outputs", {}).get("interaction", {}).get("output", {})
    sentiment_output = state.get("agent_outputs", {}).get("sentiment", {}).get("output", {})
    hcp_output = state.get("agent_outputs", {}).get("hcp", {}).get("output", {})
    followup_output = state.get("agent_outputs", {}).get("followup", {}).get("output", {})
    notification_output = state.get("agent_outputs", {}).get("notification", {}).get("output", {})
    
    entities = state.get("entities")
    sentiment = state.get("sentiment", "Neutral")
    engagement_score = state.get("engagement_score", 50)
    requires_approval = state.get("requires_approval", False)
    risk_level = state.get("risk_level", "low")
    approval_reason = state.get("approval_reason")
    
    actions = []
    
    # Action 1: Create interaction record
    actions.append({
        "action": "create_interaction",
        "data": {
            "hcp_name": entities.hcp_name if entities else "Dr. Unknown",
            "specialty": entities.specialty if entities else "General Medicine",
            "hospital_clinic": entities.hospital_clinic if entities else "General Hospital",
            "interaction_type": entities.interaction_type if entities else "In-Person Meeting",
            "product_discussed": entities.product_discussed if entities else "CardioPlus",
            "notes": entities.notes if entities else "",
            "outcome": entities.outcome if entities else "",
            "follow_up_date": followup_output.get("recommended_date_iso") if followup_output.get("requires_followup") else None,
            "user_id": state.get("db_user_id", 1)
        },
        "auto_execute": True  # Internal CRM action - no approval needed
    })
    
    # Action 2: Create/update HCP if new
    if hcp_output and not hcp_output.get("hcp_found", False):
        suggested = hcp_output.get("suggested_create", {})
        actions.append({
            "action": "create_hcp",
            "data": suggested,
            "auto_execute": True
        })
    elif hcp_output and hcp_output.get("has_updates", False):
        actions.append({
            "action": "update_hcp",
            "data": {
                "hcp_id": hcp_output.get("hcp_id"),
                "updates": {k: v["suggested"] for k, v in hcp_output.get("profile_updates", {}).items()}
            },
            "auto_execute": False,  # Requires approval for profile changes
            "requires_approval": True,
            "approval_reason": "HCP profile update detected"
        })
    
    # Action 3: Create follow-up if required
    if followup_output.get("requires_followup", False):
        followup_priority = followup_output.get("priority", "Medium")
        actions.append({
            "action": "create_followup",
            "data": {
                "hcp_id": hcp_output.get("hcp_id") if hcp_output.get("hcp_found") else None,
                "follow_up_date": followup_output.get("recommended_date_iso"),
                "priority_level": followup_priority,
                "status": "Pending",
                "ai_recommendation": followup_output.get("description"),
                "ai_reason": followup_output.get("ai_reason"),
                "ai_confidence": int(followup_output.get("confidence", 0.7) * 100)
            },
            "auto_execute": followup_priority != "High"  # High priority requires approval
        })
        if followup_priority == "High":
            requires_approval = True
            risk_level = "high"
            approval_reason = approval_reason or "High priority follow-up requires approval"
    
    # Action 4: Create notifications
    for notif in notification_output.get("notifications", []):
        actions.append({
            "action": "create_notification",
            "data": notif,
            "auto_execute": True
        })
    
    # Action 5: Generate email draft if information requested
    requested_info = interaction_output.get("requested_information", [])
    if requested_info and entities:
        actions.append({
            "action": "generate_email_draft",
            "data": {
                "hcp_name": entities.hcp_name,
                "requested_info": requested_info,
                "product": entities.product_discussed,
                "interaction_type": entities.interaction_type
            },
            "auto_execute": False,  # Email drafts always need approval
            "requires_approval": True,
            "approval_reason": "External email requires approval before sending"
        })
        requires_approval = True
        risk_level = max(risk_level, "medium", key=lambda x: ["low", "medium", "high", "critical"].index(x))
    
    # Action 6: Publish automation event
    actions.append({
        "action": "publish_event",
        "data": {
            "event_type": AutomationEventType.INTERACTION_CREATED.value,
            "source_type": "interaction",
            "payload": {
                "hcp_name": entities.hcp_name if entities else "Unknown",
                "product_discussed": entities.product_discussed if entities else "Unknown",
                "sentiment": sentiment,
                "engagement_score": engagement_score,
                "priority": followup_output.get("priority", "Medium")
            }
        },
        "auto_execute": True
    })

    agent_outputs = state.get("agent_outputs", {})
    agent_outputs["supervisor"] = AgentOutput(
        agent="supervisor",
        success=True,
        output={
            "actions": actions,
            "requires_approval": requires_approval,
            "approval_reason": approval_reason,
            "risk_level": risk_level
        },
        confidence=0.9
    ).model_dump()

    return {
        **state,
        "automation_actions": actions,
        "requires_approval": requires_approval,
        "approval_reason": approval_reason,
        "risk_level": risk_level,
        "agent_outputs": agent_outputs,
        "current_agent": "complete"
    }


def run_multi_agent_workflow(text: str, user_id: int = 1, db: Optional[Session] = None) -> Dict[str, Any]:
    """Run the complete multi-agent workflow."""
    from crm_backend.app.schemas.crm_schemas import AIChatResponse, ExtractedEntities
    from crm_backend.app.agent.agents import local_interaction_extractor, local_sentiment_analyzer
    
    # Initialize state
    state: AgentState = {
        "messages": [],
        "text": text,
        "entities": None,
        "summary": None,
        "sentiment": None,
        "engagement_score": None,
        "follow_up_action": None,
        "suggested_priority": None,
        "selected_tool": None,
        "tool_args": None,
        "tool_response": None,
        "current_agent": "interaction",
        "agent_outputs": {},
        "requires_approval": False,
        "approval_reason": None,
        "risk_level": "low",
        "automation_actions": [],
        "db_user_id": user_id,
        "error": None
    }
    
    try:
        # Run agents in sequence
        state = interaction_agent(state, db)
        state = sentiment_agent(state, db)
        state = hcp_agent(state, db)
        state = followup_agent(state, db)
        state = notification_agent(state, db)
        state = supervisor_agent(state, db)
        
        # Build response
        entities = state.get("entities")
        supervisor_output = state.get("agent_outputs", {}).get("supervisor", {}).get("output", {})
        
        summary = f"Multi-agent analysis complete. {len(supervisor_output.get('actions', []))} actions queued."
        if state.get("requires_approval"):
            summary += f" Approval required: {state.get('approval_reason')}"
        
        return {
            "success": True,
            "message": summary,
            "entities": entities,
            "summary": summary,
            "sentiment": state.get("sentiment", "Neutral"),
            "engagement_score": state.get("engagement_score", 50),
            "follow_up_action": state.get("follow_up_action"),
            "suggested_priority": state.get("suggested_priority", "Medium"),
            "requires_approval": state.get("requires_approval", False),
            "approval_reason": state.get("approval_reason"),
            "risk_level": state.get("risk_level", "low"),
            "automation_actions": state.get("automation_actions", []),
            "agent_outputs": state.get("agent_outputs", {}),
            "raw_result": state.get("agent_outputs", {})
        }
        
    except Exception as e:
        logger.error(f"Multi-agent workflow failed: {e}")
        # Fallback to local extraction (no recursion)
        try:
            interaction_result = local_interaction_extractor(text)
            sentiment_result = local_sentiment_analyzer(text)
            
            hcp_name = interaction_result.get("hcp_name") or "Sharma"
            full_hcp_name = f"Dr. {hcp_name}"
            
            entities = ExtractedEntities(
                hcp_name=full_hcp_name,
                specialty=interaction_result.get("specialty") or "General Medicine",
                hospital_clinic=interaction_result.get("hospital_clinic") or "General Hospital",
                interaction_type=interaction_result.get("interaction_type") or "In-Person Meeting",
                product_discussed=interaction_result.get("product_discussed") or "CardioPlus",
                outcome=interaction_result.get("outcome") or "Discussed clinical trials",
                notes=interaction_result.get("notes") or text,
                follow_up_date=interaction_result.get("follow_up_date")
            )
            
            return {
                "success": True,
                "message": "Parsed using fallback NLP engine after multi-agent error.",
                "entities": entities,
                "summary": interaction_result.get("summary") or f"Logged interaction with {full_hcp_name}.",
                "sentiment": sentiment_result.get("sentiment", "Neutral"),
                "engagement_score": sentiment_result.get("engagement_score", 50),
                "follow_up_action": interaction_result.get("action_items", [None])[0],
                "suggested_priority": "Medium",
                "requires_approval": False,
                "approval_reason": None,
                "risk_level": "low",
                "automation_actions": [],
                "agent_outputs": {},
                "raw_result": {"fallback": True, "error": str(e)}
            }
        except Exception as fallback_err:
            return {
                "success": False,
                "message": f"Multi-agent workflow failed: {str(e)}. Fallback also failed: {str(fallback_err)}",
                "entities": ExtractedEntities(),
                "summary": "",
                "sentiment": "Neutral",
                "engagement_score": 50,
                "follow_up_action": None,
                "suggested_priority": "Medium",
                "requires_approval": False,
                "approval_reason": None,
                "risk_level": "low",
                "automation_actions": [],
                "agent_outputs": {},
                "raw_result": {}
            }