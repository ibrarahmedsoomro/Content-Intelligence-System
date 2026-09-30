from typing import List, Dict, Any
from pydantic import BaseModel

class TitleCandidate(BaseModel):
    title: str
    formula_type: str
    predicted_ctr: str
    rationale: str

class ThumbnailConcept(BaseModel):
    concept_name: str
    visual_layout: str
    text_overlay: str
    color_contrast: str
    ai_image_prompt: str

class PackagingOutput(BaseModel):
    topic: str
    titles: List[TitleCandidate]
    thumbnails: List[ThumbnailConcept]
    seo_description: str
    tags: List[str]
    pinned_comment_prompt: str
    status: str = "COMPLETED"
