from typing import Dict, Any, List
from agents.topic_selection.models import ScriptHandoffPacket
from .models import StoryDevOutput, BeatItem

class StoryDevEngine:
    """
    Story Development Agent:
    Transforms approved angle & topic handoff into a 5-beat cinematic narrative architecture.
    """

    def generate_story(self, handoff: ScriptHandoffPacket) -> StoryDevOutput:
        topic = handoff.approved_topic
        angle = handoff.approved_angle
        question = handoff.viewer_question
        gap = handoff.content_gap

        beats = [
            BeatItem(
                beat_number=1,
                title="The Common Myth & The Hook",
                narrative_goal="Shatter conventional wisdom within the first 15 seconds.",
                tension_level=7,
                key_revelation=f"Why the obvious explanation about '{handoff.approved_topic}' is dangerously incomplete.",
                visual_anchor="High-contrast archival opening, dramatic audio riser with stark title typography."
            ),
            BeatItem(
                beat_number=2,
                title="The Hidden Crisis / Structural Dilemma",
                narrative_goal="Introduce the real-world stakes and insurmountable engineering/historical roadblock.",
                tension_level=8,
                key_revelation="The critical limitation that traditional solutions failed to address.",
                visual_anchor="Fast-paced blueprint overlays, theater operation maps, and classified document reveals."
            ),
            BeatItem(
                beat_number=3,
                title="The Counter-Intuitive Breakthrough",
                narrative_goal="Unveil the unorthodox decision that defied conventional thinking.",
                tension_level=9,
                key_revelation=f"The strategic tradeoff: {angle}",
                visual_anchor="3D tactical model animation showing internal mechanics or battlefield maneuvers."
            ),
            BeatItem(
                beat_number=4,
                title="The Crucible in Action (Real-World Test)",
                narrative_goal="Show the consequence of this strategy under extreme pressure.",
                tension_level=10,
                key_revelation="How theoretical engineering met the harsh reality of combat/high-stakes operations.",
                visual_anchor="Authentic combat footage, cockpit comms audio waveforms, intense kinetic pacing."
            ),
            BeatItem(
                beat_number=5,
                title="The Final Revelation & Lasting Impact",
                narrative_goal="Deliver the profound takeaway that permanently shifts the viewer's mental model.",
                tension_level=6,
                key_revelation=f"The reason this single decision defined an era and still influences modern doctrine.",
                visual_anchor="Wide cinematic aerial shot fading into clean visual summary card."
            )
        ]

        return StoryDevOutput(
            topic=topic,
            approved_angle=angle,
            core_thesis=f"Rather than a simple comparison, {topic} was determined by {gap}.",
            hook_promise=f"In the next minutes, uncover why {question}",
            target_audience_appeal="Fast-paced, cinematic, documentary-grade tension with zero filler.",
            narrative_arc=beats,
            retention_strategy="Micro-curiosity loops placed at every 90-second checkpoint to sustain 70%+ view duration.",
            emotional_payoff="A complete transformation from superficial curiosity to deep mechanical understanding.",
            status="COMPLETED"
        )
