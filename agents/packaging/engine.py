from typing import List
from agents.topic_selection.models import ScriptHandoffPacket
from agents.script.models import ProductionScriptOutput
from .models import PackagingOutput, TitleCandidate, ThumbnailConcept

class PackagingEngine:
    """
    Packaging & SEO Agent:
    Generates high-CTR Title formulas, Midjourney-ready Thumbnail concepts, SEO description, and audience retention prompts.
    """

    def generate_packaging(self, handoff: ScriptHandoffPacket, script: ProductionScriptOutput = None) -> PackagingOutput:
        topic = handoff.approved_topic
        angle = handoff.approved_angle
        question = handoff.viewer_question
        keywords = handoff.core_facts[2].replace("Key keywords: ", "").split(", ") if len(handoff.core_facts) > 2 else [topic]

        titles = [
            TitleCandidate(
                title=f"Why America Had to Build the Plane Everyone Hated",
                formula_type="Curiosity / Paradox",
                predicted_ctr="High (11-14%)",
                rationale="Creates immediate curiosity tension around an unexpected conflict."
            ),
            TitleCandidate(
                title=f"The Hidden Flaw That Saved {keywords[0] if keywords else topic}",
                formula_type="Contradiction",
                predicted_ctr="Very High (13-16%)",
                rationale="Hooks viewers with a counter-intuitive engineering secret."
            ),
            TitleCandidate(
                title=f"{topic}: The Untold Military Doctrine",
                formula_type="Authority / Documentary",
                predicted_ctr="Steady (8-10%)",
                rationale="Attracts high-intent search and documentary enthusiasts."
            ),
            TitleCandidate(
                title=f"The 1 Decision That Changed {keywords[0] if keywords else topic} Forever",
                formula_type="Pivotal Moment",
                predicted_ctr="High (10-12%)",
                rationale="Singular focal point creates a powerful narrative hook."
            ),
            TitleCandidate(
                title=f"Why Nobody Talks About the {keywords[1] if len(keywords) > 1 else 'Secret'} Crisis",
                formula_type="Forbidden Knowledge",
                predicted_ctr="Very High (14-17%)",
                rationale="Appeals to mystery and insider historical insight."
            )
        ]

        thumbnails = [
            ThumbnailConcept(
                concept_name="Concept A: The Stark Split-Contradiction",
                visual_layout="Split screen: Left side shows dark stormy combat skies with damaged bomber; Right side shows glowing golden blueprint schematics.",
                text_overlay="WHY BOTH?",
                color_contrast="High contrast between cold steel blue and warning amber/cyan.",
                ai_image_prompt=f"Cinematic 8k shot of {topic}, dark dramatic lighting, volumetric clouds, photorealistic archival style, extreme detail, octane render --ar 16:9"
            ),
            ThumbnailConcept(
                concept_name="Concept B: The Classified Redaction",
                visual_layout="Close-up of pilot looking intensely at cockpit dial with huge glowing red emergency stamp.",
                text_overlay="THE SECRET FLAW",
                color_contrast="Deep black vignette with blinding crimson and neon yellow accents.",
                ai_image_prompt=f"Photorealistic 1940s cockpit interior, military pilot silhouette illuminated by glowing instruments, high drama, cinematic depth of field, 8k --ar 16:9"
            ),
            ThumbnailConcept(
                concept_name="Concept C: The Giant Scale Contrast",
                visual_layout="Massive formation of bombers dwarfing an ominous low-angle cloud layer with striking typography.",
                text_overlay="TOO RISKY?",
                color_contrast="Emerald green radar glow contrasting against pitch-black void.",
                ai_image_prompt=f"Epic wide angle view of military bomber fleet flying through sunset clouds, cinematic lighting, ultra-realistic, national geographic documentary quality --ar 16:9"
            )
        ]

        tags = [
            "military aviation", "ww2 bombers", "aviation history", "skunk works",
            "documentary", "military strategy", "cold war", "flight mystery",
            "b17 flying fortress", "b24 liberator", "sr71 blackbird", "aero engineering"
        ]

        desc = f"""In this documentary breakdown, we uncover the untold truth behind {topic}.

🔍 WHY THIS MATTERS:
{angle}

⏱️ TIMESTAMPS:
0:00 - The Impossible Contradiction
0:45 - The Hidden Crisis & Theater Demands
2:30 - The Compromise Engineers Had to Make
5:15 - Combat Deployment: Theory Meets Reality
7:45 - The Final Verdict & Modern Legacy

📌 Subscribe to {handoff.target_audience.get('channel', 'our channel')} for deep-dive aviation, military history, and high-curiosity documentary investigations.

#AviationHistory #Documentary #MilitaryStrategy #UntoldStories"""

        return PackagingOutput(
            topic=topic,
            titles=titles,
            thumbnails=thumbnails,
            seo_description=desc,
            tags=tags,
            pinned_comment_prompt=f"💬 Which strategy do you think was more crucial for the final outcome? Let us know your thoughts in the comments below!",
            status="COMPLETED"
        )
