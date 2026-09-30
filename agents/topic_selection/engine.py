import json
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any

from .models import (
    ResearchPacket,
    MachineTopicDecision,
    ScoreBreakdown,
    ScriptHandoffPacket,
    DecisionType,
    RecommendedFormat,
    TimingState,
    ProductionEffort,
)

class TopicSelectionEngine:
    """
    Modular Topic Selection Engine:
    - Dynamically loads weights, thresholds, and hard gates from config/scoring.json.
    - Dynamically loads channel identity and market fit from config/audience.json.
    - Evaluates 12 scoring stages and 6 hard gates.
    - Generates standardized Machine Output JSON and Script Agent Handoff Packet.
    """

    def __init__(self, scoring_config_path: str = None, audience_config_path: str = None):
        base_dir = Path(__file__).parent.parent.parent
        self.scoring_config_path = scoring_config_path or str(base_dir / "config" / "scoring.json")
        self.audience_config_path = audience_config_path or str(base_dir / "config" / "audience.json")
        
        self.scoring_config = self._load_json(self.scoring_config_path, default={
            "weights": {
                "demand": 20, "curiosity": 15, "audience_fit": 15, "competition_opportunity": 15,
                "content_gap": 10, "series_potential": 10, "format_fit": 5, "timing": 5,
                "feasibility": 3, "packaging": 2
            },
            "thresholds": {
                "make_now": 80, "make": 68, "reframe_or_test": 55, "watchlist": 40
            },
            "hard_gates": {
                "minimum_research_confidence": 60,
                "minimum_audience_fit": 40,
                "minimum_curiosity": 35,
                "minimum_demand_for_low_curiosity": 45
            }
        })

        self.audience_config = self._load_json(self.audience_config_path, default={
            "channel": "Default Channel",
            "primary_markets": ["USA", "UK"],
            "language": "English",
            "age_range": "18-35",
            "content_style": ["cinematic", "high-curiosity"],
            "core_topics": []
        })

    def _load_json(self, path: str, default: Dict[str, Any]) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def evaluate(self, packet: ResearchPacket) -> Tuple[MachineTopicDecision, ScriptHandoffPacket, str]:
        weights = self.scoring_config.get("weights", {})
        thresholds = self.scoring_config.get("thresholds", {})
        gates = self.scoring_config.get("hard_gates", {})

        # 1. HARD GATES EVALUATION
        # Gate F: Reliability
        if not packet.is_factually_verified:
            return self._build_terminal_result(
                packet, DecisionType.SKIP, "Core premise cannot be verified factually. DO NOT PRODUCE.", "UNVERIFIED"
            )

        # Gate A: Evidence Confidence
        min_conf = gates.get("minimum_research_confidence", 60)
        if packet.research_confidence < min_conf:
            return self._build_terminal_result(
                packet, DecisionType.NEED_MORE_RESEARCH, f"Research confidence ({packet.research_confidence}) is below {min_conf}.", "INSUFFICIENT"
            )

        # Gate B: Audience Fit
        min_aud = gates.get("minimum_audience_fit", 40)
        if packet.audience_fit_score < min_aud:
            return self._build_terminal_result(
                packet, DecisionType.SKIP, f"Audience fit ({packet.audience_fit_score}) is below {min_aud}.", "AUDIENCE_MISMATCH"
            )

        # Gate C: Curiosity & Demand
        min_cur = gates.get("minimum_curiosity", 35)
        min_dem = gates.get("minimum_demand_for_low_curiosity", 45)
        if packet.curiosity_factor < min_cur and packet.search_demand_score < min_dem:
            return self._build_terminal_result(
                packet, DecisionType.SKIP, f"Curiosity ({packet.curiosity_factor}) and Demand ({packet.search_demand_score}) are below minimum thresholds.", "LOW_INTEREST"
            )

        # 2. SCORING STEPS
        demand_score = packet.search_demand_score
        curiosity_score = packet.curiosity_factor
        audience_fit = packet.audience_fit_score
        
        # Competition Opportunity & Content Gap
        gap_score = min(100.0, len(packet.content_gaps) * 35.0 + 30.0)
        competition_opp = max(0.0, min(100.0, (100.0 - packet.competitor_saturation_level) * 0.5 + gap_score * 0.5))

        # Series Potential
        series_potential = min(100.0, len(packet.potential_series_ideas) * 35.0 + len(packet.related_topics) * 15.0)

        # Format Fit
        if packet.curiosity_factor >= 80 and packet.depth_score >= 70:
            recommended_format = RecommendedFormat.BOTH
            format_fit = 90.0
        elif packet.depth_score >= 65:
            recommended_format = RecommendedFormat.LONG_FORM
            format_fit = 85.0
        elif packet.curiosity_factor >= 65 and packet.depth_score < 50:
            recommended_format = RecommendedFormat.SHORTS
            format_fit = 80.0
        else:
            recommended_format = RecommendedFormat.SHORTS
            format_fit = 70.0

        # Gate E: Long-form without depth -> shift to shorts
        if recommended_format == RecommendedFormat.LONG_FORM and packet.depth_score < 50.0:
            recommended_format = RecommendedFormat.SHORTS

        # Timing
        if packet.trend_momentum >= 80:
            timing_action = "MAKE_NOW"
            timing_score = 90.0
        elif packet.trend_momentum >= 50:
            timing_action = "EVERGREEN"
            timing_score = 80.0
        else:
            timing_action = "WATCH_TREND"
            timing_score = 60.0

        # Feasibility
        if packet.depth_score > 80:
            effort = ProductionEffort.HIGH
            feasibility_score = 75.0
        elif packet.depth_score > 50:
            effort = ProductionEffort.MEDIUM
            feasibility_score = 85.0
        else:
            effort = ProductionEffort.LOW
            feasibility_score = 95.0

        packaging_score = packet.visual_packaging_score

        # 3. WEIGHTED SCORE
        total_score = (
            (demand_score * weights.get("demand", 20)) +
            (curiosity_score * weights.get("curiosity", 15)) +
            (audience_fit * weights.get("audience_fit", 15)) +
            (competition_opp * weights.get("competition_opportunity", 15)) +
            (gap_score * weights.get("content_gap", 10)) +
            (series_potential * weights.get("series_potential", 10)) +
            (format_fit * weights.get("format_fit", 5)) +
            (timing_score * weights.get("timing", 5)) +
            (feasibility_score * weights.get("feasibility", 3)) +
            (packaging_score * weights.get("packaging", 2))
        ) / 100.0

        # 4. DECISION THRESHOLDS
        if total_score >= thresholds.get("make_now", 80):
            decision = DecisionType.MAKE_NOW
        elif total_score >= thresholds.get("make", 68):
            decision = DecisionType.MAKE
        elif total_score >= thresholds.get("reframe_or_test", 55):
            decision = DecisionType.REFRAME
        elif total_score >= thresholds.get("watchlist", 40):
            decision = DecisionType.WATCHLIST
        else:
            decision = DecisionType.SKIP

        # Gate D: Heavy saturation + No gap -> Reframe
        if competition_opp < 35.0 and len(packet.content_gaps) == 0:
            decision = DecisionType.REFRAME

        scores_breakdown = ScoreBreakdown(
            demand=round(demand_score, 1),
            curiosity=round(curiosity_score, 1),
            audience_fit=round(audience_fit, 1),
            competition_opportunity=round(competition_opp, 1),
            content_gap=round(gap_score, 1),
            series_potential=round(series_potential, 1),
            format_fit=round(format_fit, 1),
            timing=round(timing_score, 1),
            feasibility=round(feasibility_score, 1),
            packaging=round(packaging_score, 1)
        )

        primary_angle = packet.existing_angles[0] if packet.existing_angles else f"The strategic breakdown of {packet.main_keyword}."
        alt_angles = [
            f"Why {packet.main_keyword} solved a crisis everyone ignored",
            f"The hidden truth behind {packet.main_keyword}",
            f"How one fatal design flaw redefined {packet.main_keyword}"
        ]

        viewer_question = packet.audience_signals[0] if packet.audience_signals else f"What made {packet.main_keyword} so critical?"
        content_gap_reason = packet.content_gaps[0] if packet.content_gaps else "Presents a unique structural angle missing in current coverage."

        next_action = "HANDOFF_TO_SCRIPT_AGENT" if decision in [DecisionType.MAKE_NOW, DecisionType.MAKE, DecisionType.BOTH, DecisionType.LONG_FORM, DecisionType.TEST_SHORT] else "LOG_AND_MONITOR"
        handoff_agent = "Script Agent" if next_action == "HANDOFF_TO_SCRIPT_AGENT" else "None"

        machine_decision = MachineTopicDecision(
            topic=packet.topic_name,
            decision=decision,
            score=round(total_score, 1),
            confidence=packet.research_confidence,
            validation="VALID",
            scores=scores_breakdown,
            topic_type=packet.topic_category,
            recommended_format=recommended_format,
            primary_angle=primary_angle,
            alternative_angles=alt_angles,
            viewer_question=viewer_question,
            content_gap_reason=content_gap_reason,
            timing_action=timing_action,
            production_effort=effort,
            risk_status="CLEAR" if decision == DecisionType.MAKE_NOW else "CAUTION",
            reason=f"Scored {round(total_score, 1)}/100 across demand, curiosity, and differentiation.",
            next_action=next_action,
            handoff_agent=handoff_agent
        )

        # Handoff Packet
        handoff_packet = ScriptHandoffPacket(
            approved_topic=packet.topic_name,
            approved_angle=primary_angle,
            viewer_question=viewer_question,
            format=recommended_format,
            target_audience={
                "channel": self.audience_config.get("channel"),
                "markets": self.audience_config.get("primary_markets"),
                "age": self.audience_config.get("age_range"),
                "style": self.audience_config.get("content_style")
            },
            content_gap=content_gap_reason,
            core_facts=[
                f"Main entity: {packet.main_keyword}",
                f"Category: {packet.topic_category}",
                f"Key keywords: {', '.join(packet.related_keywords)}"
            ],
            sources=packet.source_links,
            hook_direction=f"Open with the immediate contrast between expectation and reality in {packet.main_keyword}.",
            series_context={
                "pillar": packet.topic_category,
                "ideas": packet.potential_series_ideas,
                "related": packet.related_topics
            },
            risk_notes="Ensure balanced factual presentation and avoid superficial spec debates.",
            suggested_length="8-12 minutes" if recommended_format in [RecommendedFormat.LONG_FORM, RecommendedFormat.BOTH] else "45-60 seconds",
            confidence=packet.research_confidence,
            next_agent="Script Agent"
        )

        # Human-readable report
        report = self._generate_markdown_report(machine_decision, handoff_packet)

        return machine_decision, handoff_packet, report

    def _build_terminal_result(self, packet: ResearchPacket, decision: DecisionType, reason: str, status: str):
        scores = ScoreBreakdown(
            demand=packet.search_demand_score, curiosity=packet.curiosity_factor,
            audience_fit=packet.audience_fit_score, competition_opportunity=0,
            content_gap=0, series_potential=0, format_fit=0, timing=0, feasibility=0, packaging=0
        )
        machine = MachineTopicDecision(
            topic=packet.topic_name, decision=decision, score=0.0, confidence=packet.research_confidence,
            validation=status, scores=scores, topic_type=packet.topic_category,
            recommended_format=RecommendedFormat.NOT_SUITABLE, primary_angle="N/A", alternative_angles=[],
            viewer_question="N/A", content_gap_reason=reason, timing_action="SKIP",
            production_effort=ProductionEffort.LOW, risk_status="BLOCKED", reason=reason,
            next_action="REJECT_OR_RESEARCH", handoff_agent="None" if decision != DecisionType.NEED_MORE_RESEARCH else "Research Agent"
        )
        handoff = ScriptHandoffPacket(
            approved_topic=packet.topic_name, approved_angle="N/A", viewer_question="N/A",
            format=RecommendedFormat.NOT_SUITABLE, target_audience={}, content_gap=reason,
            core_facts=[], sources=[], hook_direction="N/A", series_context={},
            risk_notes=reason, suggested_length="N/A", confidence=packet.research_confidence,
            next_agent="None"
        )
        return machine, handoff, f"# TOPIC DECISION: {decision.value}\n\n**Reason:** {reason}\n"

    def _generate_markdown_report(self, decision: MachineTopicDecision, handoff: ScriptHandoffPacket) -> str:
        return f"""# Topic Decision Card: {decision.topic}

**Decision:** `{decision.decision.value}` | **Opportunity Score:** `{decision.score}/100` | **Confidence:** `{decision.confidence}%`
**Format:** `{decision.recommended_format.value}` | **Timing:** `{decision.timing_action}` | **Effort:** `{decision.production_effort.value}`

---

### [1] Dimensional Scores
| Dimension | Score (0-100) | Weight |
|---|---|---|
| Search Demand | {decision.scores.demand} | 20% |
| Curiosity & Tension | {decision.scores.curiosity} | 15% |
| Audience & Channel Fit | {decision.scores.audience_fit} | 15% |
| Competition Opportunity | {decision.scores.competition_opportunity} | 15% |
| Content Gap & Differentiation | {decision.scores.content_gap} | 10% |
| Series & Cluster Value | {decision.scores.series_potential} | 10% |
| Format Suitability | {decision.scores.format_fit} | 5% |
| Freshness & Timing | {decision.scores.timing} | 5% |
| Production Feasibility | {decision.scores.feasibility} | 3% |
| Packaging Potential | {decision.scores.packaging} | 2% |

---

### [2] Narrative Strategy & Differentiation
- **Primary Angle:** {decision.primary_angle}
- **Core Viewer Question:** *"{decision.viewer_question}"*
- **Content Gap / Why Watch Us:** {decision.content_gap_reason}
- **Alternative Angles:**
{chr(10).join([f"  1. {a}" for a in decision.alternative_angles])}

---

### [3] Next Action
- **Action:** `{decision.next_action}`
- **Handoff Agent:** `{decision.handoff_agent}`
"""
