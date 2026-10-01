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
    opened_beat: int
    partially_answered_beat: Optional[int] = None
    expanded_beat: Optional[int] = None
    resolved_beat: int
    status: str = "PAID"  # OPEN / EXPANDED / PAID

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

class StoryBeatIntelligence(BaseModel):
    beat_number: int
    title: str
    function_role: str
    core_question: str
    revelation: RevelationStructure
    information_gain: InformationGainMetric
    narrative_dependency_score: int = Field(ge=0, le=10) # 0=unnecessary, 9-10=essential
    supporting_fact_ids: List[str] = Field(default_factory=list)
    associated_open_loop_ids: List[str] = Field(default_factory=list)
    visual_strategy: str
    tension_attribute: TensionLevel = TensionLevel.MEDIUM
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
    unresolved_loops_count: int = 0
    status: str = "COMPLETED"
