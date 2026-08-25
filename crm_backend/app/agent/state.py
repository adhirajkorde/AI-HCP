from typing import List, Dict, Any, Optional, TypedDict, Literal
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

    # Multi-agent state
    current_agent: Optional[str]  # interaction, sentiment, hcp, followup, notification, supervisor
    agent_outputs: Dict[str, Any]  # Outputs from each agent
    requires_approval: bool
    approval_reason: Optional[str]
    risk_level: Literal["low", "medium", "high", "critical"]
    automation_actions: List[Dict[str, Any]]  # Actions to execute after processing

    # Meta / Execution state
    db_user_id: Optional[int]
    error: Optional[str]


class AgentOutput(BaseModel):
    agent: str
    success: bool
    output: Dict[str, Any]
    confidence: float
    requires_approval: bool = False
    approval_reason: Optional[str] = None


class SupervisorDecision(BaseModel):
    next_agent: Optional[str]  # None means workflow complete
    actions: List[Dict[str, Any]] = []
    requires_approval: bool = False
    approval_reason: Optional[str] = None
    risk_level: Literal["low", "medium", "high", "critical"] = "low"