from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DecisionType(str, Enum):
    MAKE_NOW = "MAKE_NOW"
    MAKE = "MAKE"
    REFRAME = "REFRAME"
    TEST_SHORT = "TEST_SHORT"
    LONG_FORM = "LONG_FORM"
    BOTH = "BOTH"
    SERIES = "SERIES"
    WATCHLIST = "WATCHLIST"
    WAIT = "WAIT"
    NEED_MORE_RESEARCH = "NEED_MORE_RESEARCH"
    SKIP = "SKIP"

class RecommendedFormat(str, Enum):
    SHORTS = "SHORTS"
    LONG_FORM = "LONG_FORM"
    BOTH = "BOTH"
    TEST_SHORT = "TEST_SHORT"
    SERIES = "SERIES"
    WATCHLIST = "WATCHLIST"
    NOT_SUITABLE = "NOT_SUITABLE"

class TimingState(str, Enum):
    MAKE_NOW = "MAKE_NOW"
    MAKE_SOON = "MAKE_SOON"
    EVERGREEN = "EVERGREEN"
    WAIT_FOR_EVENT = "WAIT_FOR_EVENT"
    WATCH_TREND = "WATCH_TREND"
    SKIP = "SKIP"

class ProductionEffort(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

class CompetitorItem(BaseModel):
    title: str
    views: int = 0
    upload_date: Optional[str] = None
    channel_authority: Optional[str] = "MEDIUM"
    angle_used: Optional[str] = None

class ResearchPacket(BaseModel):
    topic_name: str
    main_keyword: str
    related_keywords: List[str] = Field(default_factory=list)
    search_demand_score: float = Field(default=50.0, ge=0, le=100)
    trend_momentum: float = Field(default=50.0, ge=0, le=100)
    competitor_examples: List[CompetitorItem] = Field(default_factory=list)
    competitor_saturation_level: float = Field(default=50.0, ge=0, le=100)
    audience_signals: List[str] = Field(default_factory=list)
    content_gaps: List[str] = Field(default_factory=list)
    existing_angles: List[str] = Field(default_factory=list)
    topic_category: str = "General"
    related_topics: List[str] = Field(default_factory=list)
    potential_series_ideas: List[str] = Field(default_factory=list)
    source_links: List[str] = Field(default_factory=list)
    research_confidence: float = Field(default=80.0, ge=0, le=100)
    curiosity_factor: float = Field(default=60.0, ge=0, le=100)
    audience_fit_score: float = Field(default=70.0, ge=0, le=100)
    depth_score: float = Field(default=60.0, ge=0, le=100)
    visual_packaging_score: float = Field(default=70.0, ge=0, le=100)
    is_factually_verified: bool = True

class ScoreBreakdown(BaseModel):
    demand: float
    curiosity: float
    audience_fit: float
    competition_opportunity: float
    content_gap: float
    series_potential: float
    format_fit: float
    timing: float
    feasibility: float
    packaging: float

class MachineTopicDecision(BaseModel):
    topic: str
    decision: DecisionType
    score: float
    confidence: float
    validation: str
    scores: ScoreBreakdown
    topic_type: str
    recommended_format: RecommendedFormat
    primary_angle: str
    alternative_angles: List[str] = Field(default_factory=list)
    viewer_question: str
    content_gap_reason: str
    timing_action: str
    production_effort: ProductionEffort
    risk_status: str
    reason: str
    next_action: str
    handoff_agent: str

class ScriptHandoffPacket(BaseModel):
    approved_topic: str
    approved_angle: str
    viewer_question: str
    format: RecommendedFormat
    target_audience: Dict[str, Any]
    content_gap: str
    core_facts: List[str]
    sources: List[str]
    hook_direction: str
    series_context: Dict[str, Any]
    risk_notes: str
    suggested_length: str
    confidence: float
    next_agent: str = "Script Agent"
