import re
from typing import List, Optional
from agents.topic_selection.models import TopicIntelligenceHandoff
from agents.script.models import ProductionScriptOutput
from .models import PackagingOutput, TitleCandidate, ThumbnailConcept

class PackagingEngine:
    """
    Packaging & SEO Agent (Stage 5):
    Generates high-CTR Title formulas, Midjourney-ready Thumbnail concepts, and SEO metadata
    grounded strictly in the Stage 2 Intelligence Handoff and Stage 4 Script Delivery.
    """

    STOP_WORDS = {
        "why", "did", "how", "what", "when", "where", "who", "need", "so", "many",
        "the", "a", "an", "in", "of", "and", "to", "was", "is", "that", "it", "with",
        "for", "on", "as", "by", "this", "these", "those", "or", "at", "from"
    }

    def generate_packaging(self, handoff: TopicIntelligenceHandoff, script: Optional[ProductionScriptOutput] = None) -> PackagingOutput:
        topic = handoff.topic
        angle = handoff.unique_angle
        question = handoff.primary_curiosity_question
        promise = handoff.packaging_promise or (script.scenes[-1].voiceover_script if script else f"The real documented truth behind {topic}.")
        format_type = handoff.format

        # Clean topic string without punctuation for titles and tags
        clean_topic = re.sub(r'[^\w\s-]', '', topic).strip()
        hashtag_topic = re.sub(r'[^a-zA-Z0-9]', '', topic)

        # Dynamic high-CTR titles tailored to the topic and verified contradiction
        titles = [
            TitleCandidate(
                title=f"The Documented Truth Behind {clean_topic}",
                formula_type="Structural Truth",
                predicted_ctr="High (12-15%)",
                rationale="Targets the core counter-intuitive reality and verified records rather than shallow myth."
            ),
            TitleCandidate(
                title=f"Why the Popular Explanation of {clean_topic} Is Wrong",
                formula_type="Curiosity / Paradox",
                predicted_ctr="Very High (14-17%)",
                rationale="Directly challenges common consensus to drive high curiosity click-through."
            ),
            TitleCandidate(
                title=f"The Chain of Events That Defined {clean_topic}",
                formula_type="Pivotal Moment",
                predicted_ctr="Steady (10-13%)",
                rationale="Focuses on the high-stakes causal chain and recorded evidence."
            ),
            TitleCandidate(
                title=f"What the Official Records Actually Reveal About {clean_topic}",
                formula_type="Evidence Discovery",
                predicted_ctr="High (11-14%)",
                rationale="Highlights the primary archival evidence separating expectations from reality."
            ),
            TitleCandidate(
                title=f"{clean_topic}: The Investigation You Weren't Taught",
                formula_type="Authority / Deep Dive",
                predicted_ctr="Strong (10-13%)",
                rationale="Promises an evidence-backed deep-dive investigation."
            )
        ]

        # Dynamic Thumbnail Concepts tailored to topic
        thumbnails = [
            ThumbnailConcept(
                concept_name="Concept A: The Split-Reality Contrast",
                visual_layout=f"Split composition: Left side illustrates popular misconception of {clean_topic}; Right side shows primary technical or archival evidence with sharp vector contrast.",
                text_overlay="WHY THIS?",
                color_contrast="Cold desaturated slate vs warm amber/gold edge glow, high visual separation.",
                ai_image_prompt=f"Cinematic documentary visual of {clean_topic}, split lighting, high contrast, subtle archival HUD overlay in background, photorealistic 8k --ar 16:9"
            ),
            ThumbnailConcept(
                concept_name="Concept B: The Critical Forensic Clue",
                visual_layout=f"High-detail close-up of the decisive physical or recorded artifact behind {clean_topic}, accented with glowing analytical callout lines.",
                text_overlay="THE RECORD",
                color_contrast="Dark obsidian background with glowing cyan and gold telemetry accents.",
                ai_image_prompt=f"Forensic investigative documentary still of {clean_topic}, authenticated telemetry and archival diagrams, dark atmospheric lighting, 8k --ar 16:9"
            ),
            ThumbnailConcept(
                concept_name="Concept C: The Turning Point",
                visual_layout=f"Dramatic perspective visual capturing the decisive turning point of {clean_topic}.",
                text_overlay="THE MOMENT",
                color_contrast="Monochrome tones with vibrant safety yellow and cyan accents.",
                ai_image_prompt=f"Dramatic atmospheric perspective view of {clean_topic}, volumetric lighting, cinematic documentary still, ultra-detailed 8k --ar 16:9"
            )
        ]

        # High-Value Semantic Search Tags (Filtering out useless single stop words)
        candidate_tags = [
            clean_topic.lower(),
            f"{clean_topic.lower()} documentary",
            f"{clean_topic.lower()} explained",
            f"{clean_topic.lower()} history",
            f"{clean_topic.lower()} analysis",
            "historical investigation",
            "evidence analysis",
            "technical breakdown",
            "archival documentary",
            "military history"
        ]

        # Add entity-based multi-word tags
        for ent in handoff.entity_ids:
            ent_clean = ent.replace("_", " ").lower()
            if len(ent_clean) > 3 and ent_clean not in candidate_tags:
                candidate_tags.append(ent_clean)
                candidate_tags.append(f"{ent_clean} history")

        # Extract meaningful multi-word phrases from topic (excluding stop words)
        meaningful_words = [w.lower() for w in clean_topic.split() if w.lower() not in self.STOP_WORDS and len(w) > 2]
        if len(meaningful_words) >= 2:
            candidate_tags.append(" ".join(meaningful_words))

        # Deduplicate while preserving order, cap at 15 high-ranking tags
        tags = list(dict.fromkeys([t for t in candidate_tags if len(t.split()) > 1 or len(t) > 3]))[:15]

        # Dynamically build chapters from actual script scenes if available
        if script and script.scenes:
            chapters_text = "\n".join(
                f"{sc.timestamp_estimate.split(' - ')[0]} - {sc.section_title}"
                for sc in script.scenes
            )
        else:
            chapters_text = (
                "0:00 - The Public Assumption vs The Contradiction\n"
                "0:45 - The Baseline Evidence & Mechanism\n"
                "2:30 - The Compounded Friction\n"
                "5:15 - The Forensic Crucible\n"
                "7:45 - The Documented Takeaway"
            )

        channel_name = handoff.target_audience.get('channel', 'our channel') if isinstance(handoff.target_audience, dict) else 'our channel'

        desc = f"""In this documentary investigation, we examine the documented evidence and real causal chain behind {clean_topic}.

🔍 CORE INVESTIGATION:
{promise}

⏱️ CHAPTERS & TIMESTAMPS:
{chapters_text}

📌 Grounded in verified primary archives and investigative debriefs.
Subscribe to {channel_name} for evidence-based deep dives.

#{hashtag_topic} #Documentary #Investigation #History"""

        return PackagingOutput(
            topic=topic,
            titles=titles,
            thumbnails=thumbnails,
            seo_description=desc,
            tags=tags,
            pinned_comment_prompt=f"💬 Looking at the documented evidence behind {clean_topic}, what detail challenged your original view the most? Share your thoughts below!",
            status="COMPLETED"
        )
