from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SearchIntentClassification(BaseModel):
    primary_intent: str = "Investigative + Informational"
    secondary_intents: List[str] = ["Historical", "Curiosity", "Documentary"]

class QueryArchitecture(BaseModel):
    tier_a_core: List[str] = Field(default_factory=list, description="Core entities")
    tier_b_search_intent: List[str] = Field(default_factory=list, description="Search intent queries")
    tier_c_long_tail: List[str] = Field(default_factory=list, description="Specific long-tail queries")
    tier_d_semantic_support: List[str] = Field(default_factory=list, description="Entities, objects, and historical terms")

class CuriosityProfile(BaseModel):
    primary_type: str = "QUESTION"
    secondary_types: List[str] = ["MYTH VS RECORD", "CAUSAL MYSTERY", "EVIDENCE REVEAL"]

class IntrinsicPackagingAssessment(BaseModel):
    search_alignment: str = "High"         # "High" | "Medium" | "Low"
    curiosity_potential: str = "High"      # "High" | "Medium" | "Low"
    specificity: str = "High"              # "High" | "Medium" | "Low"
    audience_fit: str = "High"             # "High" | "Medium" | "Low"
    claim_risk: str = "Low"                # "Low" | "Medium" | "High"
    promise_strength: str = "High"         # "High" | "Medium" | "Low"
    naturalness: str = "High"              # "High" | "Medium" | "Low"
    historical_comparable_ctr: str = "Not Available (Requires Channel Analytics)"
    packaging_quality_score: float = 92.5  # Out of 100
    discovery_mode: str = "HYBRID"         # "SEARCH-FIRST" | "BROWSE-FIRST" | "HYBRID"

class TitleCandidate(BaseModel):
    title: str
    formula_type: str
    assessment: IntrinsicPackagingAssessment
    promise_id: str
    promise_statement: str
    rationale: str

class ThumbnailConcept(BaseModel):
    concept_name: str
    concept_type: str = "STAKES"  # "STAKES" | "EVIDENCE" | "MOMENT"
    visual_layout: str
    text_overlay: str
    color_contrast: str
    ai_image_prompt: str
    creates_question_not_answer: bool = True

class ClaimProvenanceItem(BaseModel):
    fact_id: str
    claim: str
    source: str
    source_tier: str  # "TIER 1" | "TIER 2" | "TIER 3" | "TIER 4" | "TIER 5"
    certainty: str    # "ESTABLISHED" | "REPORTED" | "UNRESOLVED"
    allowed_wording: str
    forbidden_wording: str

class PackagingHardGate(BaseModel):
    gate_id: str
    name: str
    passed: bool
    details: str

class PackagingQACheck(BaseModel):
    check_id: str
    name: str
    status: str  # "PASSED" | "FLAGGED" | "WARNING"
    details: str

class PackagingQAReport(BaseModel):
    overall_quality_score: float = 95.0
    qa_score: float = 95.0
    qa_verdict: str = "APPROVED"  # "APPROVED" | "APPROVED_WITH_NOTES" | "REQUIRES_EVIDENCE" | "REQUIRES_REPACKAGING" | "REJECTED"
    hard_gates: List[PackagingHardGate] = Field(default_factory=list)
    checks: List[PackagingQACheck] = Field(default_factory=list)
    overclaims_detected: List[str] = Field(default_factory=list)
    terminology_guards_applied: List[str] = Field(default_factory=list)
    semantic_coverage_pct: float = 100.0

class PackagingOutput(BaseModel):
    # 21-Section Output Contract
    topic: str
    primary_entity: str
    secondary_entity: str
    search_intent: SearchIntentClassification
    curiosity_profile: CuriosityProfile
    query_architecture: QueryArchitecture
    
    # 1. Primary Title
    primary_title: str
    
    # 2. Alternative Titles
    alternative_titles: List[TitleCandidate]
    
    # 3. Title Assessments (All 5 titles)
    titles: List[TitleCandidate]
    
    # 4. Search Terms & 5. Semantic Keywords
    tags: List[str]
    hashtags: List[str]
    
    # 7. Optimized Description & 8. Chapters
    seo_description: str
    chapters_text: str
    
    # 11-13. Thumbnail Concepts
    thumbnails: List[ThumbnailConcept]
    
    # 14. Title/Thumbnail Pairing
    title_thumbnail_pairing_rationale: str
    
    # 15. Core Content Promise & 16. Open Loops
    core_content_promise: str
    open_loop_ids: List[str]
    
    # 17. Source/Claim Register & 18. Claim-Risk Report
    source_claim_register: List[ClaimProvenanceItem]
    claim_risk_summary: str
    
    # 19. Competitor Differentiation
    competitor_differentiation: str
    
    # 20. QA Report & 21. Final Status
    pinned_comment_prompt: str
    qa_report: PackagingQAReport
    final_status: str = "APPROVED"
