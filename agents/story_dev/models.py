from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TensionLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"

class StoryArchetype(str, Enum):
    DISASTER_INVESTIGATION = "DISASTER_INVESTIGATION"   # e.g., Flight 19, Titanic, Air accidents, Disappearances
    ENGINEERING_PARADOX = "ENGINEERING_PARADOX"         # e.g., WWII Bombers, SR-71, Concorde
    SCIENTIFIC_DISCOVERY = "SCIENTIFIC_DISCOVERY"       # e.g., Quantum physics, Penicillin, DNA
    HISTORICAL_DECISION = "HISTORICAL_DECISION"         # e.g., Battle of Midway, Enigma, Strategic choices
    SYSTEMIC_FAILURE = "SYSTEMIC_FAILURE"               # e.g., Boeing 747 volcanic ash, Grid blackout
    GENERAL_DOCUMENTARY = "GENERAL_DOCUMENTARY"

class ArchetypeClassificationResult(BaseModel):
    archetype: StoryArchetype
    subtype: Optional[str] = None  # e.g. DISAPPEARANCE, ACCIDENT, MISSING_PATROL, SEARCH_AND_RECOVERY, MULTI_ROLE_COMPROMISE, DOCTRINAL_CHOICE
    confidence: float = 90.0
    central_question: str = ""
    supporting_fact_ids: List[str] = Field(default_factory=list)
    alternative_archetypes: List[str] = Field(default_factory=list)

class RevelationStructure(BaseModel):
    assumption: str
    evidence: str
    contradiction: str
    explanation: str
    new_understanding: str

class InformationGainMetric(BaseModel):
    viewer_knowledge_before: str
    viewer_knowledge_after: str
    genuine_change: str
    gain_level: str = "HIGH"  # LOW / MEDIUM / HIGH

class AudienceAssumptionEvidence(BaseModel):
    assumption: str
    source_type: str = "POPULAR_NARRATIVE"  # SEARCH_QUERY_PATTERN / COMMENTS / COMPETITOR_TITLES / POPULAR_NARRATIVE / RESEARCH_DATA
    source_types: List[str] = Field(default_factory=lambda: ["POPULAR_NARRATIVE", "SEARCH_QUERY_PATTERN"])
    confidence: float = 85.0
    evidence: str

class ModernAnalogyMetadata(BaseModel):
    label: str = "MODERN ANALOGY — NOT HISTORICAL FACT"
    analogy_strength: str = "MEDIUM"  # LOW / MEDIUM / HIGH
    similarity_dimension: str
    historical_basis: str
    modern_basis: str
    boundary_limit: str
    influence_claim_supported: bool = False

class OpenLoopItem(BaseModel):
    loop_id: str
    question: str
    topic_id: str = ""
    entity_ids: List[str] = Field(default_factory=list)
    opened_at_beat: int = 1
    partially_answered_beat: Optional[int] = None
    expanded_beat: Optional[int] = None
    resolved_at_beat: int = 5
    resolution_fact_ids: List[str] = Field(default_factory=list)
    resolution_claim_ids: List[str] = Field(default_factory=list)
    resolution_type: str = "FULL"  # FULL / PARTIAL / PROBABILISTIC / CONTESTED / UNRESOLVED
    resolution_quality: float = 90.0  # 0-100
    is_entity_consistent: bool = True
    status: str = "PAID"  # OPEN / EXPANDED / PAID / UNPAID / INVALID
    resolution_confidence: float = 85.0
    
    # Backward compatibility aliases
    opened_beat: Optional[int] = None
    resolved_beat: Optional[int] = None

    def __init__(self, **data: Any):
        if "opened_at_beat" in data and "opened_beat" not in data:
            data["opened_beat"] = data["opened_at_beat"]
        elif "opened_beat" in data and "opened_at_beat" not in data:
            data["opened_at_beat"] = data["opened_beat"]
        if "resolved_at_beat" in data and "resolved_beat" not in data:
            data["resolved_beat"] = data["resolved_at_beat"]
        elif "resolved_beat" in data and "resolved_at_beat" not in data:
            data["resolved_at_beat"] = data["resolved_beat"]
        super().__init__(**data)

class BeatScoreBreakdown(BaseModel):
    curiosity: float = Field(ge=0, le=100)
    information_gain: float = Field(ge=0, le=100)
    narrative_necessity: float = Field(ge=0, le=100)
    evidence_strength: float = Field(ge=0, le=100)
    payoff_contribution: float = Field(ge=0, le=100)
    novelty: float = Field(ge=0, le=100)
    retention_function: float = Field(ge=0, le=100)
    visual_potential: float = Field(ge=0, le=100)
    stakes: float = Field(ge=0, le=100)
    total_beat_score: float = Field(ge=0, le=100)

class DependencyAuditCriteria(BaseModel):
    breaks_causal_understanding: bool = True
    removes_necessary_evidence: bool = True
    breaks_open_loop: bool = True
    removes_payoff_setup: bool = True
    makes_later_beat_confusing: bool = True
    is_filler: bool = False

class NarrativeValidityGateResult(BaseModel):
    derives_from_verified_facts: bool = True
    answers_real_question: bool = True
    advances_thesis: bool = True
    narrative_domain_consistency: bool = True
    template_contamination_free: bool = True
    bounded_claims: bool = True
    is_valid: bool = True
    rejection_reasons: List[str] = Field(default_factory=list)

class TemplateContaminationCheckResult(BaseModel):
    contamination_detected: bool = False
    contaminated_terms: List[str] = Field(default_factory=list)
    archetype_mismatch_flags: List[str] = Field(default_factory=list)
    score: float = 0.0  # 0 = clean

class StoryBeatIntelligence(BaseModel):
    beat_number: int
    slot_name: str = "SLOT"  # e.g. "SLOT 1: Hook & Central Question"
    title: str
    function_role: str
    core_question: str
    revelation: RevelationStructure
    information_gain: InformationGainMetric
    narrative_dependency_score: int = Field(ge=0, le=10)  # 0=filler, 9-10=essential
    dependency_audit: Optional[DependencyAuditCriteria] = None
    supporting_fact_ids: List[str] = Field(default_factory=list)
    supporting_claim_ids: List[str] = Field(default_factory=list)
    associated_open_loop_ids: List[str] = Field(default_factory=list)
    visual_strategy: str
    tension_attribute: TensionLevel = TensionLevel.MEDIUM
    modern_analogy: Optional[ModernAnalogyMetadata] = None
    modern_analogy_label: Optional[str] = None
    validity_gate: Optional[NarrativeValidityGateResult] = None
    beat_score: BeatScoreBreakdown

class StoryIntelligenceBlueprint(BaseModel):
    """
    Stage 3 Story Intelligence Blueprint:
    Replaces generic fixed templates with dynamic evidence-derived story reasoning,
    archetype classification, template contamination detection, and narrative validity gates.
    """
    topic: str
    topic_id: str
    archetype: StoryArchetype = StoryArchetype.GENERAL_DOCUMENTARY
    subtype: Optional[str] = None
    archetype_classification: Optional[ArchetypeClassificationResult] = None
    audience_assumption: Optional[AudienceAssumptionEvidence] = None
    core_thesis: str
    primary_curiosity_question: str
    secondary_questions: List[str] = Field(default_factory=list)
    central_contradiction: str
    open_loops: List[OpenLoopItem] = Field(default_factory=list)
    payoff_target: str
    beats: List[StoryBeatIntelligence] = Field(default_factory=list)
    
    contamination_check: TemplateContaminationCheckResult = Field(default_factory=TemplateContaminationCheckResult)
    overall_story_intelligence_score: float
    factual_confidence: float
    narrative_validity_passed: bool = True
    drama_integrity_passed: bool = True
    entity_consistency_passed: bool = True
    unresolved_loops_count: int = 0
    status: str = "COMPLETED"
