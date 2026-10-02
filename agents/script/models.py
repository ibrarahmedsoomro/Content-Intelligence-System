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
    retention_category: str = "NEW_EVIDENCE"

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

class CausalAuditItem(BaseModel):
    cause: str
    effect: str
    supporting_fact_ids: List[str] = Field(default_factory=list)
    supporting_source_ids: List[str] = Field(default_factory=list)
    certainty_supported: bool = True
    certainty_used_in_script: str = "DIRECT_FACT"  # DIRECT_FACT / PROBABILISTIC / SPECULATIVE
    status: str = "PASS"  # PASS / FAIL

class ScriptQAReport(BaseModel):
    # Separated Fact Coverage and Fact Accuracy (Patch 4 & 13)
    fact_coverage_rate: float
    fact_accuracy_rate: float = 100.0
    
    unresolved_loops: int
    promise_match_score: float
    drama_integrity_score: float
    traceability_rate: float
    pacing_wpm: float
    retention_hook_density: float
    script_quality_score: float = Field(ge=0, le=100)
    
    # Detailed Causal Inference Observability (Patch 5 & 13)
    causal_claims_detected: int = 0
    supported_causal_claims: int = 0
    overstated_causal_claims: int = 0
    causal_audit_items: List[CausalAuditItem] = Field(default_factory=list)
    
    # Domain & Contamination Observability (Patch 13)
    topic_domain_match: bool = True
    entity_match: bool = True
    lexical_contamination: bool = False
    semantic_contamination: bool = False
    
    # Retention & Information Gain Observability (Patch 13)
    information_gain_score: float = 90.0
    semantic_repetition_ratio: float = 0.0
    retention_functions_count: int = 5
    
    checks: List[QACheckItem] = Field(default_factory=list)
    promise_delivery: PromiseDeliveryAudit
    drama_integrity_check: bool = True
    entity_consistency_passed: bool = True
    modern_analogy_labeled: bool = True
    claim_verification_passed: bool = True
    
    qa_verdict: str = "APPROVED_FOR_PRODUCTION"  # APPROVED_FOR_PRODUCTION / REVISE_REQUIRED / BLOCKED / NEED_MORE_RESEARCH
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
