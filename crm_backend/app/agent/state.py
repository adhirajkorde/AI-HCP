from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel
from crm_backend.app.schemas.crm_schemas import ExtractedEntities

class AgentState(TypedDict):
    # Standard LangGraph conversation state
    messages: List[Dict[str, Any]]
    text: str
    
    # Extraction output
    entities: Optional[ExtractedEntities]
    summary: Optional[str]
    sentiment: Optional[str]
    engagement_score: Optional[int]
    follow_up_action: Optional[str]
    suggested_priority: Optional[str]
    
    # Tool execution state
    selected_tool: Optional[str]
    tool_args: Optional[Dict[str, Any]]
    tool_response: Optional[Dict[str, Any]]
    
    # Meta / Execution state
    db_user_id: Optional[int]
    error: Optional[str]
