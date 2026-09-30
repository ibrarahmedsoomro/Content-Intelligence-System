from typing import List, Optional
from pydantic import BaseModel, Field

class ScriptScene(BaseModel):
    scene_number: int
    timestamp_estimate: str
    section_title: str
    visual_direction: str
    audio_sfx: str
    voiceover_script: str
    retention_hook: Optional[str] = None

class ProductionScriptOutput(BaseModel):
    topic: str
    format: str
    estimated_duration: str
    total_word_count: int
    hook_opening: str
    scenes: List[ScriptScene]
    pacing_notes: str
    status: str = "COMPLETED"
