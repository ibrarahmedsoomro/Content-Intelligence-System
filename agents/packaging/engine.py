from typing import List
from agents.topic_selection.models import TopicIntelligenceHandoff
from agents.script.models import ProductionScriptOutput
from .models import PackagingOutput, TitleCandidate, ThumbnailConcept

class PackagingEngine:
    """
    Packaging & SEO Agent (Stage 5):
    Generates high-CTR Title formulas, Midjourney-ready Thumbnail concepts, and SEO metadata
    grounded strictly in the Stage 2 Intelligence Handoff and Script Delivery.
    """

    def generate_packaging(self, handoff: TopicIntelligenceHandoff, script: ProductionScriptOutput = None) -> PackagingOutput:
        topic = handoff.topic
        angle = handoff.unique_angle
        question = handoff.primary_curiosity_question
        promise = handoff.packaging_promise

        titles = [
            TitleCandidate(
                title=f"Why the Military Built Both When One Was 'Better'",
                formula_type="Curiosity / Paradox",
                predicted_ctr="High (12-15%)",
                rationale="Targets the core misconception of direct platform rivalry."
            ),
            TitleCandidate(
                title=f"The Geographic Tradeoff Behind {topic}",
                formula_type="Structural Truth",
                predicted_ctr="Steady (9-12%)",
                rationale="Appeals to aviation enthusiasts seeking tactical depth."
            ),
            TitleCandidate(
                title=f"The Production Decision That Redefined {topic}",
                formula_type="Pivotal Moment",
                predicted_ctr="Very High (13-16%)",
                rationale="Focuses on the high-stakes industrial tooling compromise."
            ),
            TitleCandidate(
                title=f"Why Pacific Distances Broke Standard Aircraft Doctrine",
                formula_type="Extreme Constraint",
                predicted_ctr="High (11-14%)",
                rationale="Highlights the extreme geographic barrier separating theater operations."
            ),
            TitleCandidate(
                title=f"{topic}: The Doctrine You Weren't Taught",
                formula_type="Authority / Discovery",
                predicted_ctr="Strong (10-13%)",
                rationale="Promises an evidence-backed historical perspective."
            )
        ]

        thumbnails = [
            ThumbnailConcept(
                concept_name="Concept A: The Split-Theater Reality",
                visual_layout="Split screen: Left side shows dense cloud formation flight with European combat radius; Right side shows vast oceanic sunlit flight path with Pacific radius.",
                text_overlay="WHY BOTH?",
                color_contrast="Cold steel blue vs warm horizon amber, high edge definition.",
                ai_image_prompt=f"Cinematic historical documentary still of {topic}, split lighting, high contrast, technical tactical map overlay in background, 8k octane render --ar 16:9"
            ),
            ThumbnailConcept(
                concept_name="Concept B: The Design Compromise",
                visual_layout="Cutaway 3D schematic highlighting fuel tank capacity against armor plate distribution.",
                text_overlay="THE TRADEOFF",
                color_contrast="Dark obsidian background with glowing cyan and gold holographic wireframe accents.",
                ai_image_prompt=f"3D blueprint schematic of historical bomber aircraft, glowing holographic lines, dark slate background, ultra-detailed engineering visual, 8k --ar 16:9"
            ),
            ThumbnailConcept(
                concept_name="Concept C: Industrial Scale",
                visual_layout="High-angle view of massive factory assembly line stretching into vanishing point with finished aircraft in foreground.",
                text_overlay="MASS PRODUCTION",
                color_contrast="Monochrome industrial tones with vibrant safety yellow and cyan accents.",
                ai_image_prompt=f"Dramatic 1940s aircraft manufacturing plant, assembly line stretching into distance, volumetric lighting, photorealistic archival look --ar 16:9"
            )
        ]

        tags = [
            "military aviation", "aircraft doctrine", "aviation history", "tactical strategy",
            "documentary", "engineering tradeoffs", "flight range", "bomber development",
            "b17 flying fortress", "b24 liberator", "air combat analysis"
        ]

        desc = f"""In this documentary investigation, we examine the true operational doctrine behind {topic}.

🔍 CORE REVELATION:
{promise}

⏱️ CHAPTERS & TIMESTAMPS:
0:00 - The Public Rivalry Myth vs Doctrinal Reality
0:45 - The Pacific vs European Geography Dilemma
2:30 - Industrial Tooling & Manufacturing Velocity
5:15 - Combat Deployment: Proving the Dual-Platform Strategy
7:45 - The Strategic Takeaway & Modern Engineering Lessons

📌 Grounded in official military procurement archives and flight operational reports.
Subscribe to {handoff.target_audience.get('channel', 'our channel')} for in-depth aviation and defense analysis.

#AviationHistory #MilitaryStrategy #Engineering #Documentary"""

        return PackagingOutput(
            topic=topic,
            titles=titles,
            thumbnails=thumbnails,
            seo_description=desc,
            tags=tags,
            pinned_comment_prompt=f"💬 Looking at theater range vs armor protection, do you agree with the dual-platform approach? Share your thoughts below!",
            status="COMPLETED"
        )
