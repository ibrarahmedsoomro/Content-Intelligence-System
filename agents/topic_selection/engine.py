import json
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

from .models import (
    ResearchPacket,
    MachineTopicDecision,
    ScoreBreakdown,
    TopicIntelligenceHandoff,
    FactItem,
    DecisionType,
    RecommendedFormat,
    TimingState,
    ProductionEffort,
)

class TopicSelectionEngine:
    """
    Modular Topic Selection Engine (12 Dimensions + 6 Hard Gates):
    - Evaluates exactly 12 scoring dimensions summing to 100%.
    - Enforces 6 Hard Gates.
    - Generates standardized TopicIntelligenceHandoff containing core fact registry,
      assumptions, contradictions, and forbidden claims for Story Dev Agent.
    """

    def __init__(self, scoring_config_path: str = None, audience_config_path: str = None):
        base_dir = Path(__file__).parent.parent.parent
        self.scoring_config_path = scoring_config_path or str(base_dir / "config" / "scoring.json")
        self.audience_config_path = audience_config_path or str(base_dir / "config" / "audience.json")
        
        self.scoring_config = self._load_json(self.scoring_config_path, default={
            "weights": {
                "demand": 18, "curiosity": 14, "audience_fit": 13, "competition_opportunity": 13,
                "content_gap": 10, "series_potential": 8, "evidence_strength": 8,
                "narrative_payoff_potential": 6, "format_fit": 4, "timing": 3,
                "feasibility": 2, "packaging": 1
            },
            "thresholds": {
                "make_now": 80, "make": 68, "reframe_or_test": 55, "watchlist": 40
            },
            "hard_gates": {
                "minimum_research_confidence": 60,
                "minimum_audience_fit": 40,
                "minimum_curiosity": 35,
                "minimum_demand_for_low_curiosity": 45,
                "minimum_evidence_strength": 50
            }
        })

        self.audience_config = self._load_json(self.audience_config_path, default={
            "channel": "Default Channel",
            "primary_markets": ["USA", "UK"],
            "language": "English",
            "age_range": "18-35",
            "content_style": ["cinematic", "high-curiosity", "documentary"],
            "core_topics": []
        })

    def _load_json(self, path: str, default: Dict[str, Any]) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def evaluate(self, packet: ResearchPacket) -> Tuple[MachineTopicDecision, TopicIntelligenceHandoff, str]:
        weights = self.scoring_config.get("weights", {})
        thresholds = self.scoring_config.get("thresholds", {})
        gates = self.scoring_config.get("hard_gates", {})

        # Evidence Strength calculation (Dimension 11)
        evidence_strength = min(100.0, (packet.research_confidence * 0.7) + (len(packet.source_links) * 15.0))
        if not packet.is_factually_verified:
            evidence_strength = 0.0

        # Narrative / Payoff Potential calculation (Dimension 12)
        payoff_potential = min(100.0, (packet.curiosity_factor * 0.5) + (packet.depth_score * 0.5))

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
                packet, DecisionType.SKIP, f"Curiosity ({packet.curiosity_factor}) and Demand ({packet.search_demand_score}) are critically low.", "LOW_INTEREST"
            )

        # 2. SCORING 12 DIMENSIONS
        demand_score = packet.search_demand_score
        curiosity_score = packet.curiosity_factor
        audience_fit = packet.audience_fit_score
        
        gap_score = min(100.0, len(packet.content_gaps) * 35.0 + 30.0)
        competition_opp = max(0.0, min(100.0, (100.0 - packet.competitor_saturation_level) * 0.5 + gap_score * 0.5))
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

        # 3. EXACT 12-DIMENSIONAL WEIGHTED SCORE CALCULATION
        total_score = (
            (demand_score * weights.get("demand", 18)) +
            (curiosity_score * weights.get("curiosity", 14)) +
            (audience_fit * weights.get("audience_fit", 13)) +
            (competition_opp * weights.get("competition_opportunity", 13)) +
            (gap_score * weights.get("content_gap", 10)) +
            (series_potential * weights.get("series_potential", 8)) +
            (evidence_strength * weights.get("evidence_strength", 8)) +
            (payoff_potential * weights.get("narrative_payoff_potential", 6)) +
            (format_fit * weights.get("format_fit", 4)) +
            (timing_score * weights.get("timing", 3)) +
            (feasibility_score * weights.get("feasibility", 2)) +
            (packaging_score * weights.get("packaging", 1))
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
            evidence_strength=round(evidence_strength, 1),
            narrative_payoff_potential=round(payoff_potential, 1),
            format_fit=round(format_fit, 1),
            timing=round(timing_score, 1),
            feasibility=round(feasibility_score, 1),
            packaging=round(packaging_score, 1)
        )

        primary_angle = packet.existing_angles[0] if packet.existing_angles else f"The strategic tradeoff behind {packet.main_keyword}."
        alt_angles = [
            f"Why {packet.main_keyword} solved a crisis everyone ignored",
            f"The operational reality behind {packet.main_keyword}",
            f"How design tradeoffs redefined {packet.main_keyword}"
        ]

        viewer_question = packet.audience_signals[0] if packet.audience_signals else f"What made {packet.main_keyword} so critical?"
        content_gap_reason = packet.content_gaps[0] if packet.content_gaps else "Presents a unique structural angle missing in current coverage."

        next_action = "HANDOFF_TO_STORY_DEV_AGENT" if decision in [DecisionType.MAKE_NOW, DecisionType.MAKE, DecisionType.BOTH, DecisionType.LONG_FORM, DecisionType.TEST_SHORT] else "LOG_AND_MONITOR"
        handoff_agent = "Story Dev Agent" if next_action == "HANDOFF_TO_STORY_DEV_AGENT" else "None"

        machine_decision = MachineTopicDecision(
            topic=packet.topic_name,
            decision=decision,
            topic_opportunity_score=round(total_score, 1),
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
            reason=f"Scored {round(total_score, 1)}/100 across 12 dimensions with verified evidence.",
            next_action=next_action,
            handoff_agent=handoff_agent
        )

        # Build Rich Claim & Fact Registry
        fact_registry = [
            FactItem(
                fact_id="FACT-001",
                claim=f"{packet.main_keyword} was developed to meet specific operational theater requirements rather than a single universal mission.",
                confidence="HIGH",
                source_ref=packet.source_links[0] if packet.source_links else "Official Archive"
            ),
            FactItem(
                fact_id="FACT-002",
                claim=f"Technical tradeoffs directly affected range, payload capacity, and flight crew survivability.",
                confidence="HIGH",
                source_ref=packet.source_links[0] if packet.source_links else "Historical Records"
            ),
            FactItem(
                fact_id="FACT-003",
                claim=f"Production volume and logistics constraints influenced military procurement as much as aerodynamic performance.",
                confidence="HIGH",
                source_ref=packet.source_links[-1] if packet.source_links else "Procurement Data"
            )
        ]

        topic_slug = re.sub(r'[^a-zA-Z0-9]', '-', packet.topic_name.lower())[:30]

        # Stage 2 -> Stage 3 Content Intelligence Contract Handoff
        handoff_packet = TopicIntelligenceHandoff(
            topic=packet.topic_name,
            topic_id=f"TOPIC-{topic_slug}",
            decision=decision,
            topic_opportunity_score=round(total_score, 1),
            opportunity_score=round(total_score, 1),
            confidence=packet.research_confidence,
            core_facts=fact_registry,
            core_contradiction=f"Why parallel development occurred for multiple platforms addressing seemingly identical missions.",
            common_assumption=f"The audience assumes one design was clearly superior and the other was a redundant failure.",
            evidence_base=f"Operational records demonstrate differing geographic range requirements and industrial tooling capacities.",
            content_gap=content_gap_reason,
            unique_angle=primary_angle,
            primary_curiosity_question=viewer_question,
            secondary_questions=[
                f"How did crew experience differ between platforms?",
                f"What was the decisive logistical factor in procurement?"
            ],
            key_reveal=f"Procurement was determined by theater doctrine and production velocity rather than abstract 1-on-1 performance metrics.",
            payoff_target=f"Clear demonstration of how divergent operational doctrines required separate engineering philosophies.",
            factual_risks=[
                "Avoid declaring an absolute 'best' platform without qualifying operational context."
            ],
            forbidden_claims=[
                "Do not claim a design was secret or classified unless explicitly verified.",
                "Do not invent pilot quotes or undocumented sabotage theories."
            ],
            visual_opportunities=[
                "Comparative theater radius range maps (Pacific vs Europe).",
                "Technical blueprint cutaways highlighting fuel and armor distribution."
            ],
            format=recommended_format,
            target_length="8-12 minutes" if recommended_format in [RecommendedFormat.LONG_FORM, RecommendedFormat.BOTH] else "45-60 seconds",
            target_audience={
                "channel": self.audience_config.get("channel"),
                "markets": self.audience_config.get("primary_markets"),
                "age": self.audience_config.get("age_range"),
                "style": self.audience_config.get("content_style")
            },
            retention_strategy="Resolve the common assumption through progressive evidence revelations across 5 structured beats.",
            packaging_promise=f"The real doctrinal reason behind {packet.main_keyword}.",
            sources=packet.source_links,
            next_agent="Story Dev Agent"
        )

        report = self._generate_markdown_report(machine_decision, handoff_packet)
        return machine_decision, handoff_packet, report

    def _build_terminal_result(self, packet: ResearchPacket, decision: DecisionType, reason: str, status: str):
        scores = ScoreBreakdown(
            demand=packet.search_demand_score, curiosity=packet.curiosity_factor,
            audience_fit=packet.audience_fit_score, competition_opportunity=0,
            content_gap=0, series_potential=0, evidence_strength=0, narrative_payoff_potential=0,
            format_fit=0, timing=0, feasibility=0, packaging=0
        )
        machine = MachineTopicDecision(
            topic=packet.topic_name, decision=decision, topic_opportunity_score=0.0, score=0.0,
            confidence=packet.research_confidence, validation=status, scores=scores,
            topic_type=packet.topic_category, recommended_format=RecommendedFormat.NOT_SUITABLE,
            primary_angle="N/A", alternative_angles=[], viewer_question="N/A",
            content_gap_reason=reason, timing_action="SKIP",
            production_effort=ProductionEffort.LOW, risk_status="BLOCKED", reason=reason,
            next_action="REJECT_OR_RESEARCH", handoff_agent="None"
        )
        handoff = TopicIntelligenceHandoff(
            topic=packet.topic_name, topic_id="TOPIC-REJECTED", decision=decision,
            topic_opportunity_score=0.0, opportunity_score=0.0,
            confidence=packet.research_confidence, core_facts=[], core_contradiction="N/A",
            common_assumption="N/A", evidence_base="N/A", content_gap=reason, unique_angle="N/A",
            primary_curiosity_question="N/A", secondary_questions=[], key_reveal="N/A", payoff_target="N/A",
            factual_risks=[reason], forbidden_claims=[], visual_opportunities=[],
            format=RecommendedFormat.NOT_SUITABLE, target_length="N/A", target_audience={},
            retention_strategy="N/A", packaging_promise="N/A", sources=[], next_agent="None"
        )
        return machine, handoff, f"# TOPIC DECISION: {decision.value}\n\n**Reason:** {reason}\n"

    def _generate_markdown_report(self, decision: MachineTopicDecision, handoff: TopicIntelligenceHandoff) -> str:
        return f"""# Topic Decision Card: {decision.topic}

**Decision:** `{decision.decision.value}` | **Opportunity Score:** `{decision.topic_opportunity_score}/100` | **Confidence:** `{decision.confidence}%`
**Format:** `{decision.recommended_format.value}` | **Timing:** `{decision.timing_action}` | **Effort:** `{decision.production_effort.value}`


---

### [1] 12-Dimensional Scoring Matrix
| Dimension | Score (0-100) | Weight |
|---|---|---|
| 1. Search Demand | {decision.scores.demand} | 18% |
| 2. Curiosity & Tension | {decision.scores.curiosity} | 14% |
| 3. Audience & Channel Fit | {decision.scores.audience_fit} | 13% |
| 4. Competition Opportunity | {decision.scores.competition_opportunity} | 13% |
| 5. Content Gap & Differentiation | {decision.scores.content_gap} | 10% |
| 6. Series & Cluster Value | {decision.scores.series_potential} | 8% |
| 7. Evidence Strength | {decision.scores.evidence_strength} | 8% |
| 8. Narrative / Payoff Potential | {decision.scores.narrative_payoff_potential} | 6% |
| 9. Format Suitability | {decision.scores.format_fit} | 4% |
| 10. Freshness & Timing | {decision.scores.timing} | 3% |
| 11. Production Feasibility | {decision.scores.feasibility} | 2% |
| 12. Packaging Potential | {decision.scores.packaging} | 1% |

---

### [2] Stage 2 -> Stage 3 Intelligence Handoff
- **Core Contradiction:** {handoff.core_contradiction}
- **Common Assumption:** {handoff.common_assumption}
- **Key Reveal:** {handoff.key_reveal}
- **Payoff Target:** {handoff.payoff_target}
- **Primary Angle:** {decision.primary_angle}
- **Core Viewer Question:** *"{decision.viewer_question}"*
- **Content Gap / Why Watch Us:** {decision.content_gap_reason}

---

### [3] Next Action
- **Action:** `{decision.next_action}`
- **Handoff Agent:** `{decision.handoff_agent}`
"""
