from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator

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
    APPROVED_FOR_PRODUCTION = "APPROVED_FOR_PRODUCTION"
    REVISE_REQUIRED = "REVISE_REQUIRED"
    BLOCKED = "BLOCKED"
    NEED_MORE_RESEARCH = "NEED_MORE_RESEARCH"

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

class ClaimType(str, Enum):
    FACT = "FACT"
    HISTORICAL_FACT = "HISTORICAL_FACT"
    DIRECT_OBSERVATION = "DIRECT_OBSERVATION"
    SOURCE_INTERPRETATION = "SOURCE_INTERPRETATION"
    INFERENCE = "INFERENCE"
    HISTORICAL_CONSENSUS = "HISTORICAL_CONSENSUS"
    CONTESTED_CLAIM = "CONTESTED_CLAIM"
    PROBABILISTIC_EXPLANATION = "PROBABILISTIC_EXPLANATION"
    MODERN_ANALOGY = "MODERN_ANALOGY"
    SPECULATION = "SPECULATION"
    UNRESOLVED = "UNRESOLVED"

# ==========================================
# 2. EVIDENCE & CLAIM REGISTRY MODELS
# ==========================================

class SourceItem(BaseModel):
    source_id: str
    url: str
    source_type: str = "PRIMARY"  # PRIMARY / SECONDARY / ARCHIVAL / TELEMETRY / INQUIRY
    authority_level: int = Field(default=85, ge=0, le=100)
    supports: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)

class FactItem(BaseModel):
    fact_id: str
    topic_id: str = ""
    entity_ids: List[str] = Field(default_factory=list)
    claim: str                                  # Exact factual statement
    evidence: str                               # What the source actually establishes
    source_ids: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None            # Backward compatibility
    claim_type: ClaimType = ClaimType.FACT
    confidence: float = Field(default=90.0, ge=0, le=100)
    allowed_for_story: bool = True
    establishes: str = ""                       # Positive boundary
    does_not_establish: str = ""                # Negative boundary: what cannot be inferred
    supports_narrative_claim: str = ""
    limitations: List[str] = Field(default_factory=list)
    is_verified: bool = True
    status: str = "ALLOWED"                     # ALLOWED / FORBIDDEN / NEEDS_VERIFICATION

class ClaimItem(BaseModel):
    claim_id: str
    claim: str
    claim_type: ClaimType = ClaimType.SOURCE_INTERPRETATION
    source_ids: List[str] = Field(default_factory=list)
    fact_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=85.0, ge=0, le=100)
    certainty_language: str = "likely"          # confirmed / likely / possible / speculative
    allowed: bool = True
    statement: Optional[str] = None             # Backward compatibility
    supported_by_fact_id: Optional[str] = None  # Backward compatibility
    verification_status: str = "VERIFIED"

    def __init__(self, **data: Any):
        if "statement" in data and "claim" not in data:
            data["claim"] = data["statement"]
        if "claim" in data and "statement" not in data:
            data["statement"] = data["claim"]
        if "supported_by_fact_id" in data and "fact_ids" not in data:
            data["fact_ids"] = [data["supported_by_fact_id"]] if data["supported_by_fact_id"] else []
        super().__init__(**data)

class AudienceAssumptionItem(BaseModel):
    assumption_id: str
    statement: str
    source_types: List[str] = Field(default_factory=lambda: ["SEARCH_QUERY_PATTERN", "POPULAR_NARRATIVE"])
    source_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=75.0, ge=0, le=100)
    status: str = "SUPPORTED"                   # SUPPORTED / WEAKLY_SUPPORTED / UNKNOWN / CONTESTED

class ContradictionItem(BaseModel):
    contradiction_id: str
    statement: str
    fact_ids: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=85.0, ge=0, le=100)
    type: str = "OPERATIONAL"                   # FACTUAL / STRATEGIC / OPERATIONAL / PERCEPTUAL / CAUSAL

# ==========================================
# 3. RESEARCH PACKET & INPUT NORMALIZATION
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

    @model_validator(mode='before')
    @classmethod
    def normalize_competitors(cls, data: Any) -> Any:
        if isinstance(data, dict) and "competitor_examples" in data:
            normalized = []
            for item in data["competitor_examples"]:
                if isinstance(item, str):
                    normalized.append({"title": item, "views": 100000})
                else:
                    normalized.append(item)
            data["competitor_examples"] = normalized
        return data

class NormalizedRunContext(BaseModel):
    schema_version: str = "final"
    run_id: str
    topic_id: str
    topic_title: str
    channel_profile: str = "Default Aviation & Military Intelligence"
    target_format: str = "LONG_FORM"
    target_length_seconds: int = 570
    research_packet: ResearchPacket
    source_registry: List[SourceItem] = Field(default_factory=list)
    prior_topic_history: List[str] = Field(default_factory=list)

# ==========================================
# 4. 12-DIMENSIONAL SCORING & DECISION MODELS
# ==========================================

class DimensionScore(BaseModel):
    raw_score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0, le=100)
    weighted_contribution: float = Field(ge=0, le=100)
    evidence_basis: str = ""
    confidence: float = Field(default=85.0, ge=0, le=100)

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

    # Detailed dimensional contributions map
    dimensions_detail: Optional[Dict[str, DimensionScore]] = None

class HardGateAudit(BaseModel):
    gate_a_evidence: bool = True
    gate_b_audience: bool = True
    gate_c_curiosity_demand: bool = True
    gate_d_differentiation: bool = True
    gate_e_depth_format: bool = True
    gate_f_reliability: bool = True
    all_passed: bool = True
    failed_gate_reason: Optional[str] = None

class MachineTopicDecision(BaseModel):
    topic: str
    topic_id: str = ""
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    decision: DecisionType
    recommended_format: RecommendedFormat
    timing_action: TimingState
    production_effort: ProductionEffort
    primary_angle: str
    alternative_angles: List[str] = Field(default_factory=list)
    viewer_question: str
    content_gap_reason: str
    reason: str
    scores: ScoreBreakdown
    hard_gate_audit: Optional[HardGateAudit] = None
    validation: str = "VALID"
    topic_type: str = "General"

# ==========================================
# 5. CONTENT INTELLIGENCE HANDOFF CONTRACT
# ==========================================

class TopicIntelligenceHandoff(BaseModel):
    topic: str
    topic_id: str = ""
    opportunity_score: float = 0.0
    decision: str = "MAKE"
    confidence: float = 80.0
    
    entity_ids: List[str] = Field(default_factory=list)
    core_facts: List[FactItem] = Field(default_factory=list)
    core_fact_ids: List[str] = Field(default_factory=list)
    sources: List[SourceItem] = Field(default_factory=list)
    claim_items: List[ClaimItem] = Field(default_factory=list)

    audience_assumption: Optional[AudienceAssumptionItem] = None
    common_assumption: str = ""
    core_contradiction: str = ""
    contradiction_item: Optional[ContradictionItem] = None
    unique_angle: str = ""
    novelty_angle: str = ""
    content_gap: str = ""

    primary_curiosity_question: str = ""
    secondary_questions: List[str] = Field(default_factory=list)

    evidence_constraints: List[str] = Field(default_factory=list)
    factual_risks: List[str] = Field(default_factory=list)
    forbidden_claims: List[str] = Field(default_factory=list)

    candidate_payoffs: List[str] = Field(default_factory=list)
    payoff_target: str = ""
    visual_opportunities: List[str] = Field(default_factory=list)

    format: str = "LONG_FORM"
    target_length: int = 570
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    packaging_promise: str = ""
