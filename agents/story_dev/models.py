from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BeatItem(BaseModel):
    beat_number: int
    title: str
    narrative_goal: str
    tension_level: int = Field(default=5, ge=1, le=10)
    key_revelation: str
    visual_anchor: str

class StoryDevOutput(BaseModel):
    topic: str
    approved_angle: str
    core_thesis: str
    hook_promise: str
    target_audience_appeal: str
    narrative_arc: List[BeatItem]
    retention_strategy: str
    emotional_payoff: str
    status: str = "COMPLETED"
