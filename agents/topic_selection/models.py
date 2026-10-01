from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ==========================================
# 1. ENUMS & CORE STATUSES
# ==========================================

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

class ProductionStatus(str, Enum):
    PASS_PRODUCTION = "PASS"
    REVISE = "REVISE"
    BLOCKED = "BLOCKED"

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

# ==========================================
# 2. EVIDENCE & CLAIM ENGINE MODELS
# ==========================================

class FactItem(BaseModel):
    fact_id: str
    claim: str                                  # Exact factual claim
    source_ref: str                             # Source link / document reference
    evidence: str                               # What the source actually establishes
    confidence: float = 90.0                    # 0-100 numeric confidence
    supports_narrative_claim: str = ""          # Which narrative claim it supports
    does_not_establish: str = ""                # Negative boundary: what cannot be inferred
    is_verified: bool = True
    status: str = "ALLOWED"                     # ALLOWED / FORBIDDEN / NEEDS_VERIFICATION

class ClaimItem(BaseModel):
    claim_id: str
    statement: str
    supported_by_fact_id: Optional[str] = None
    verification_status: str = "VERIFIED"       # VERIFIED / UNVERIFIED / FORBIDDEN / NEEDS_VERIFICATION
    claim_type: str = "HISTORICAL_FACT"         # HISTORICAL_FACT / MODERN_ANALOGY / STRATEGIC_INFERENCE
    forbidden_reason: Optional[str] = None

# ==========================================
# 3. RESEARCH PACKET
# ==========================================

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

# ==========================================
# 4. 12-DIMENSIONAL SCORING & DECISION
# ==========================================

class ScoreBreakdown(BaseModel):
    demand: float
    curiosity: float
    audience_fit: float
    competition_opportunity: float
    content_gap: float
    series_potential: float
    evidence_strength: float
    narrative_payoff_potential: float
    format_fit: float
    timing: float
    feasibility: float
    packaging: float

class MachineTopicDecision(BaseModel):
    topic: str
    decision: DecisionType
    topic_opportunity_score: float
    score: Optional[float] = None
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

    def __init__(self, **data: Any):
        if "topic_opportunity_score" in data and "score" not in data:
            data["score"] = data["topic_opportunity_score"]
        elif "score" in data and "topic_opportunity_score" not in data:
            data["topic_opportunity_score"] = data["score"]
        super().__init__(**data)

class TopicIntelligenceHandoff(BaseModel):
    topic: str
    topic_id: str
    decision: DecisionType
    topic_opportunity_score: float
    opportunity_score: Optional[float] = None
    confidence: float
    
    entity_ids: List[str] = Field(default_factory=list)
    core_facts: List[FactItem] = Field(default_factory=list)
    core_claims: List[ClaimItem] = Field(default_factory=list)
    core_contradiction: str
    common_assumption: str
    evidence_base: str
    content_gap: str
    unique_angle: str
    primary_curiosity_question: str
    secondary_questions: List[str] = Field(default_factory=list)
    key_reveal: str
    payoff_target: str
    factual_risks: List[str] = Field(default_factory=list)
    forbidden_claims: List[str] = Field(default_factory=list)
    visual_opportunities: List[str] = Field(default_factory=list)
    
    format: RecommendedFormat
    target_length: str
    target_audience: Dict[str, Any]
    retention_strategy: str
    packaging_promise: str
    sources: List[str] = Field(default_factory=list)
    next_agent: str = "Story Dev Agent"

    def __init__(self, **data: Any):
        if "topic_opportunity_score" in data and "opportunity_score" not in data:
            data["opportunity_score"] = data["topic_opportunity_score"]
        elif "opportunity_score" in data and "topic_opportunity_score" not in data:
            data["topic_opportunity_score"] = data["opportunity_score"]
        super().__init__(**data)


