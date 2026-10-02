from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TraceableScene(BaseModel):
    scene_id: str
    scene_number: int
    associated_beat_id: int
    timestamp_estimate: str
    section_title: str
    supporting_fact_ids: List[str] = Field(default_factory=list)
    open_loop_ids: List[str] = Field(default_factory=list)
    payoff_contribution: str = "PARTIAL"  # PARTIAL / EXPANDED / RESOLVED
    visual_direction: str
    audio_sfx: str
    voiceover_script: str
    retention_hook: Optional[str] = None

class PromiseDeliveryAudit(BaseModel):
    title_promise: str
    hook_promise: str
    story_promise: str
    script_delivery: str
    ending_payoff: str
    promise_match_score: float = Field(ge=0, le=100)
    status: str = "PASS"  # PASS / REVISE

class QACheckItem(BaseModel):
    check_id: str
    name: str
    category: str
    status: str  # PASS / WARN / FAIL
    calculated_value: str
    threshold: str
    details: str
    is_critical: bool = True

class ScriptQAReport(BaseModel):
    fact_coverage_rate: float
    unresolved_loops: int
    promise_match_score: float
    drama_integrity_score: float
    traceability_rate: float
    pacing_wpm: float
    retention_hook_density: float
    script_quality_score: float = Field(ge=0, le=100)
    
    checks: List[QACheckItem] = Field(default_factory=list)
    promise_delivery: PromiseDeliveryAudit
    drama_integrity_check: bool = True
    entity_consistency_passed: bool = True
    modern_analogy_labeled: bool = True
    claim_verification_passed: bool = True
    
    qa_verdict: str = "APPROVED_FOR_PRODUCTION"  # APPROVED_FOR_PRODUCTION / REVISE_REQUIRED / BLOCKED
    recommendations: List[str] = Field(default_factory=list)

class ProductionScriptOutput(BaseModel):
    topic: str
    topic_id: str = ""
    format: str
    estimated_duration: str
    total_word_count: int
    calculated_wpm: float = 145.0
    hook_opening: str
    scenes: List[TraceableScene]
    pacing_notes: str
    qa_report: ScriptQAReport
    status: str = "COMPLETED"
