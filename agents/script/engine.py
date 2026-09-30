from typing import List
from agents.story_dev.models import StoryDevOutput
from agents.topic_selection.models import ScriptHandoffPacket
from .models import ProductionScriptOutput, ScriptScene

class ScriptEngine:
    """
    Script Agent:
    Transforms Story Dev Architecture into a full broadcast/YouTube production script with visual, audio, and voiceover tracks.
    """

    def generate_script(self, handoff: ScriptHandoffPacket, story: StoryDevOutput) -> ProductionScriptOutput:
        topic = handoff.approved_topic
        angle = handoff.approved_angle
        question = handoff.viewer_question
        is_short = handoff.format == "SHORTS"

        if is_short:
            scenes = [
                ScriptScene(
                    scene_number=1,
                    timestamp_estimate="0:00 - 0:08",
                    section_title="The Instant Shock Hook",
                    visual_direction="Extreme close-up on machinery/cockpit with rapid kinetic cut to massive explosion/flight path.",
                    audio_sfx="Heavy low-end impact boom, sharp riser cutting immediately to silence.",
                    voiceover_script=f"Most people think {topic} was straightforward. But the reality is far stranger.",
                    retention_hook="Immediate pattern-break statement."
                ),
                ScriptScene(
                    scene_number=2,
                    timestamp_estimate="0:08 - 0:28",
                    section_title="The Hidden Truth",
                    visual_direction="Fast-paced 3D blueprint animation highlighting the core tension.",
                    audio_sfx="Tense clock ticking synth, ambient turbine roar in the background.",
                    voiceover_script=f"Here is what history textbooks left out: {angle}. When tested under real conditions, engineers discovered a fatal dilemma.",
                    retention_hook="Unresolved question before final reveal."
                ),
                ScriptScene(
                    scene_number=3,
                    timestamp_estimate="0:28 - 0:45",
                    section_title="The Payoff & Climax",
                    visual_direction="Cinematic aerial combat shot fading to clean graphical summary.",
                    audio_sfx="Deep bass drop, crisp outro synth chord.",
                    voiceover_script=f"And that is why {question.replace('Why did ', 'why ')} If you love untold aviation breakthroughs, hit subscribe for more.",
                    retention_hook="Strong closure with natural call to action."
                )
            ]
            duration = "45 Seconds"
            words = 125
        else:
            scenes = [
                ScriptScene(
                    scene_number=1,
                    timestamp_estimate="0:00 - 0:45",
                    section_title="Cold Open & The Impossible Question",
                    visual_direction="[VISUAL: High-contrast 4K remastered archival footage. Dark vignette. Camera slowly zooms into cockpit instruments. On-screen text: DECLASSIFIED ARCHIVE.]",
                    audio_sfx="[AUDIO: Subdued radar blips fading into a haunting low orchestral cello drone. Sudden metallic snap on cut.]",
                    voiceover_script=f"If you look at the official records of {topic}, one glaring contradiction immediately stands out. On paper, it seemed impossible. Yet behind closed doors, military command authorized a radical pivot.",
                    retention_hook="Hook promise: Reveals the hidden classified tradeoff within 60 seconds."
                ),
                ScriptScene(
                    scene_number=2,
                    timestamp_estimate="0:45 - 2:30",
                    section_title="The Structural Flaw & Hidden Crisis",
                    visual_direction="[VISUAL: Split-screen tactical maps showing Pacific vs European theater ranges with red combat radii pulsing.]",
                    audio_sfx="[AUDIO: Driving electronic-cinematic pulse, analog radio static chirps.]",
                    voiceover_script=f"To understand why, we have to look past the surface. {story.core_thesis} Standard doctrine failed because the operational demands in different theaters were completely irreconcilable.",
                    retention_hook="Presents data visualization that debunks top competitor assumptions."
                ),
                ScriptScene(
                    scene_number=3,
                    timestamp_estimate="2:30 - 5:15",
                    section_title="The Engineering / Strategic Crucible",
                    visual_direction="[VISUAL: Dynamic 3D schematic breakdown showing fuel capacity, armor weight, and altitude limits under stress.]",
                    audio_sfx="[AUDIO: Mechanical pneumatic sound design, dramatic percussion build-up.]",
                    voiceover_script=f"This led to the ultimate compromise: {angle}. Every single advantage in one category came at a staggering penalty in another. But the commanders had no other choice.",
                    retention_hook="Micro-cliffhanger before the pivotal mission breakdown."
                ),
                ScriptScene(
                    scene_number=4,
                    timestamp_estimate="5:15 - 7:45",
                    section_title="The Real-World Test & Climax",
                    visual_direction="[VISUAL: Authentic combat mission camera footage synchronized with actual declassified radio transmission audio.]",
                    audio_sfx="[AUDIO: Heavy visceral flak explosions, authentic distorted cockpit radio comms.]",
                    voiceover_script="When these machines were finally deployed into high-altitude combat, theory collided violently with reality. Crews were pushed past the breaking point, but the strategic doctrine proved decisive.",
                    retention_hook="Audio-waveform synchronization keeps viewer locked in."
                ),
                ScriptScene(
                    scene_number=5,
                    timestamp_estimate="7:45 - 9:30",
                    section_title="The Legacy & Final Verdict",
                    visual_direction="[VISUAL: Elegant slow-motion aerial cinematography of surviving aircraft in golden hour sunlight. Seamless outro animation.]",
                    audio_sfx="[AUDIO: Warm resonant synth chords resolving tension. Gentle ambient wind.]",
                    voiceover_script=f"Today, historians often debate which design was superior. But as we have seen, they were never meant to compete—they were built to solve two entirely different puzzles of war. That is the untold truth of {topic}.",
                    retention_hook="Deep mental model shift that drives comments and re-shares."
                )
            ]
            duration = "9 Minutes 30 Seconds"
            words = 1450

        return ProductionScriptOutput(
            topic=topic,
            format="SHORTS" if is_short else "LONG_FORM_DOCUMENTARY",
            estimated_duration=duration,
            total_word_count=words,
            hook_opening=scenes[0].voiceover_script,
            scenes=scenes,
            pacing_notes="Maintain brisk 145-155 WPM voiceover delivery. Visual cuts every 3.5 to 5 seconds. Avoid dead air.",
            status="COMPLETED"
        )
