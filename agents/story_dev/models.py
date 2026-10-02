from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TensionLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"

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
    resolution_quality: float = 90.0 # 0-100
    is_entity_consistent: bool = True
    status: str = "PAID"  # OPEN / EXPANDED / PAID / UNPAID / INVALID
    
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

class StoryBeatIntelligence(BaseModel):
    beat_number: int
    title: str
    function_role: str
    core_question: str
    revelation: RevelationStructure
    information_gain: InformationGainMetric
    narrative_dependency_score: int = Field(ge=0, le=10) # 0=unnecessary/filler, 9-10=essential
    dependency_audit: Optional[DependencyAuditCriteria] = None
    supporting_fact_ids: List[str] = Field(default_factory=list)
    associated_open_loop_ids: List[str] = Field(default_factory=list)
    visual_strategy: str
    tension_attribute: TensionLevel = TensionLevel.MEDIUM
    modern_analogy_label: Optional[str] = None # e.g. "MODERN ANALOGY — NOT HISTORICAL FACT"
    beat_score: BeatScoreBreakdown

class StoryIntelligenceBlueprint(BaseModel):
    """
    Stage 3 Story Intelligence Blueprint:
    Replaces shallow generic templates with a rigorous 100-point beat intelligence model,
    open-loop tracking, narrative dependency verification, and information gain diffs.
    """
    topic: str
    topic_id: str
    core_thesis: str
    primary_curiosity_question: str
    secondary_questions: List[str] = Field(default_factory=list)
    central_contradiction: str
    open_loops: List[OpenLoopItem] = Field(default_factory=list)
    payoff_target: str
    beats: List[StoryBeatIntelligence] = Field(default_factory=list)
    
    overall_story_intelligence_score: float
    factual_confidence: float
    drama_integrity_passed: bool = True
    entity_consistency_passed: bool = True
    unresolved_loops_count: int = 0
    status: str = "COMPLETED"

