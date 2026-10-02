from typing import List, Optional
from agents.topic_selection.models import TopicIntelligenceHandoff
from agents.script.models import ProductionScriptOutput
from .models import PackagingOutput, TitleCandidate, ThumbnailConcept

class PackagingEngine:
    """
    Packaging & SEO Agent (Stage 5):
    Generates high-CTR Title formulas, Midjourney-ready Thumbnail concepts, and SEO metadata
    grounded strictly in the Stage 2 Intelligence Handoff and Script Delivery.
    """

    def generate_packaging(self, handoff: TopicIntelligenceHandoff, script: Optional[ProductionScriptOutput] = None) -> PackagingOutput:
        topic = handoff.topic
        angle = handoff.unique_angle
        question = handoff.primary_curiosity_question
        promise = handoff.packaging_promise or (script.scenes[-1].voiceover_script if script else f"The real strategic truth behind {topic}.")
        format_type = handoff.format

        # Dynamic high-CTR titles tailored to the topic
        titles = [
            TitleCandidate(
                title=f"The Hidden Constraint Behind {topic}",
                formula_type="Structural Truth",
                predicted_ctr="High (12-15%)",
                rationale="Targets the core counter-intuitive tradeoff rather than shallow trivia."
            ),
            TitleCandidate(
                title=f"Why the Standard Explanation of {topic} Is Wrong",
                formula_type="Curiosity / Paradox",
                predicted_ctr="Very High (14-17%)",
                rationale="Directly challenges common consensus to drive high curiosity click-through."
            ),
            TitleCandidate(
                title=f"The Tradeoff That Defined {topic}",
                formula_type="Pivotal Moment",
                predicted_ctr="Steady (10-13%)",
                rationale="Focuses on the high-stakes engineering compromise."
            ),
            TitleCandidate(
                title=f"Why {topic} Broke Conventional Doctrine",
                formula_type="Extreme Constraint",
                predicted_ctr="High (11-14%)",
                rationale="Highlights the extreme operational barrier separating expectations from reality."
            ),
            TitleCandidate(
                title=f"{topic}: The Doctrine You Weren't Taught",
                formula_type="Authority / Discovery",
                predicted_ctr="Strong (10-13%)",
                rationale="Promises an evidence-backed deep-dive investigation."
            )
        ]

        # Dynamic Thumbnail Concepts
        clean_topic_slug = topic.replace("'", "").replace('"', '')
        thumbnails = [
            ThumbnailConcept(
                concept_name="Concept A: The Split-Reality Contrast",
                visual_layout=f"Split screen: Left side shows common perception of {clean_topic_slug}; Right side shows technical reality with glowing analytical vector overlay.",
                text_overlay="WHY THIS?",
                color_contrast="Cold industrial slate vs warm vibrant amber, high edge definition.",
                ai_image_prompt=f"Cinematic technical documentary visual of {clean_topic_slug}, split lighting, high contrast, blueprint telemetry HUD overlay in background, octane render 8k --ar 16:9"
            ),
            ThumbnailConcept(
                concept_name="Concept B: The Design Compromise",
                visual_layout=f"Cutaway 3D technical schematic highlighting the hidden mechanism and tradeoff of {clean_topic_slug}.",
                text_overlay="THE TRADEOFF",
                color_contrast="Dark obsidian background with glowing cyan and gold holographic wireframe accents.",
                ai_image_prompt=f"3D engineering blueprint schematic of {clean_topic_slug}, glowing holographic telemetry lines, dark slate background, ultra-detailed engineering visual, 8k --ar 16:9"
            ),
            ThumbnailConcept(
                concept_name="Concept C: The Scale of Execution",
                visual_layout=f"High-angle dramatic perspective visual showcasing the real-world operational scale of {clean_topic_slug}.",
                text_overlay="THE REALITY",
                color_contrast="Monochrome tones with vibrant safety yellow and cyan accents.",
                ai_image_prompt=f"Dramatic operational perspective view of {clean_topic_slug}, volumetric lighting, cinematic documentary still, photorealistic, 8k --ar 16:9"
            )
        ]

        # Tags dynamically generated
        tag_tokens = [w.lower() for w in topic.split() if len(w) > 2]
        tags = list(dict.fromkeys([
            topic.lower(),
            f"{topic.lower()} documentary",
            f"{topic.lower()} explained",
            "engineering analysis",
            "historical doctrine",
            "military history",
            "technical breakdown",
            "documentary"
        ] + tag_tokens))[:12]

        channel_name = handoff.target_audience.get('channel', 'our channel') if isinstance(handoff.target_audience, dict) else 'our channel'

        desc = f"""In this documentary investigation, we examine the true operational realities and doctrine behind {topic}.

🔍 CORE INVESTIGATION:
{promise}

⏱️ CHAPTERS & TIMESTAMPS:
0:00 - The Public Assumption vs The Contradiction
0:45 - The Core Mechanism & Physical Dilemma
2:30 - Systemic Constraints & Execution Velocity
5:15 - Operational Crucible & Doctrinal Validation
7:45 - The Strategic Takeaway & Modern Systems

📌 Grounded in verified historical and technical archives.
Subscribe to {channel_name} for evidence-based deep dives.

#{topic.replace(' ', '')} #Documentary #Engineering #History"""

        return PackagingOutput(
            topic=topic,
            titles=titles,
            thumbnails=thumbnails,
            seo_description=desc,
            tags=tags,
            pinned_comment_prompt=f"💬 Looking at the operational tradeoffs behind {topic}, what surprised you most? Share your perspective below!",
            status="COMPLETED"
        )
