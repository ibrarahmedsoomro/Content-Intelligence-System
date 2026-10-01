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
    payoff_contribution: str = "PARTIAL" # PARTIAL / EXPANDED / RESOLVED
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
    promise_match_score: float = 95.0
    status: str = "PASS" # PASS / REVISE

class ScriptQAReport(BaseModel):
    fact_coverage_rate: float # % of registered facts included
    unresolved_loops: int
    drama_integrity_check: bool
    promise_delivery: PromiseDeliveryAudit
    qa_verdict: str = "APPROVED_FOR_PRODUCTION"

class ProductionScriptOutput(BaseModel):
    topic: str
    format: str
    estimated_duration: str
    total_word_count: int
    hook_opening: str
    scenes: List[TraceableScene]
    pacing_notes: str
    qa_report: ScriptQAReport
    status: str = "COMPLETED"
