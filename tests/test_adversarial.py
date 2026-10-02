import json
import pytest
from pathlib import Path
from agents.topic_selection.models import ResearchPacket, DecisionType
from agents.topic_selection.engine import TopicSelectionEngine
from agents.story_dev.engine import StoryDevEngine
from agents.story_dev.models import StoryArchetype
from agents.script.engine import ScriptEngine
from agents.packaging.engine import PackagingEngine

DATA_RESEARCH_DIR = Path(__file__).parent.parent / "data" / "research"

def test_patch_10_central_question_driven_archetype_classification():
    """
    Patch 1 & 10: Archetype classification based on central question & evidence graph (not title keywords alone).
    - Flight 19 -> DISASTER_INVESTIGATION (subtype = MISSING_PATROL / DISAPPEARANCE)
    - Glenn Miller -> DISASTER_INVESTIGATION (subtype = DISAPPEARANCE, not forced into HISTORICAL_DECISION)
    - WWII Bombers -> ENGINEERING_PARADOX (subtype = MULTI_ROLE_COMPROMISE)
    - SR-71 Blackbird -> ENGINEERING_PARADOX (subtype = SUPERSONIC_THERMAL_BARRIER)
    """
    story_engine = StoryDevEngine()
    topic_engine = TopicSelectionEngine()

    # 1. Flight 19
    f19_data = json.load(open(DATA_RESEARCH_DIR / "2026-09-30-bermuda-triangle-flight19.json", "r", encoding="utf-8"))
    _, handoff_f19, _ = topic_engine.evaluate(ResearchPacket(**f19_data))
    story_f19 = story_engine.generate_story(handoff_f19)
    assert story_f19.archetype == StoryArchetype.DISASTER_INVESTIGATION
    assert story_f19.subtype in ["MISSING_PATROL", "DISAPPEARANCE"]

    # 2. Glenn Miller (Disappearance case)
    gm_data = json.load(open(DATA_RESEARCH_DIR / "custom-glenn-miller-.json", "r", encoding="utf-8"))
    _, handoff_gm, _ = topic_engine.evaluate(ResearchPacket(**gm_data))
    story_gm = story_engine.generate_story(handoff_gm)
    assert story_gm.archetype == StoryArchetype.DISASTER_INVESTIGATION
    assert story_gm.subtype == "DISAPPEARANCE"

    # 3. WWII Bombers
    bomber_data = json.load(open(DATA_RESEARCH_DIR / "2026-09-30-bomber-research.json", "r", encoding="utf-8"))
    _, handoff_b, _ = topic_engine.evaluate(ResearchPacket(**bomber_data))
    story_b = story_engine.generate_story(handoff_b)
    assert story_b.archetype == StoryArchetype.ENGINEERING_PARADOX
    assert story_b.subtype == "MULTI_ROLE_COMPROMISE"

    # 4. SR-71 Blackbird
    sr71_data = json.load(open(DATA_RESEARCH_DIR / "2026-09-30-sr71-blackbird.json", "r", encoding="utf-8"))
    _, handoff_sr, _ = topic_engine.evaluate(ResearchPacket(**sr71_data))
    story_sr = story_engine.generate_story(handoff_sr)
    assert story_sr.archetype == StoryArchetype.ENGINEERING_PARADOX

def test_patch_11_certainty_preservation_and_causal_integrity():
    """
    Patch 2, 5 & 11: Epistemic certainty preservation & Causal integrity audit (QA-05).
    Verifies that probabilistic evidence is not overstated into false direct certainty.
    """
    f19_data = json.load(open(DATA_RESEARCH_DIR / "2026-09-30-bermuda-triangle-flight19.json", "r", encoding="utf-8"))
    topic_engine = TopicSelectionEngine()
    story_engine = StoryDevEngine()
    script_engine = ScriptEngine()

    _, handoff, _ = topic_engine.evaluate(ResearchPacket(**f19_data))
    story = story_engine.generate_story(handoff)
    script = script_engine.generate_script(handoff, story)

    qa = script.qa_report
    assert qa.causal_claims_detected > 0
    assert qa.overstated_causal_claims == 0
    assert qa.supported_causal_claims == qa.causal_claims_detected
    assert any(c.check_id == "QA-05" and c.status == "PASS" for c in qa.checks)

def test_patch_12_disappearance_unresolved_honesty():
    """
    Patch 3 & 12: Historical disappearance cases with unresolved physical wreckage
    must resolve as resolution_type = UNRESOLVED, status = PAID.
    """
    f19_data = json.load(open(DATA_RESEARCH_DIR / "2026-09-30-bermuda-triangle-flight19.json", "r", encoding="utf-8"))
    topic_engine = TopicSelectionEngine()
    story_engine = StoryDevEngine()

    _, handoff, _ = topic_engine.evaluate(ResearchPacket(**f19_data))
    story = story_engine.generate_story(handoff)

    assert story.open_loops[0].resolution_type == "UNRESOLVED"
    assert story.open_loops[0].status == "PAID"
    assert story.unresolved_loops_count == 0

def test_patch_13_qa_separate_metrics_observability():
    """
    Patch 4 & 13: QA-01 exposes separate fact_coverage_rate and fact_accuracy_rate.
    QA-05, QA-08, QA-09, QA-10 expose structured observability.
    """
    bomber_data = json.load(open(DATA_RESEARCH_DIR / "2026-09-30-bomber-research.json", "r", encoding="utf-8"))
    topic_engine = TopicSelectionEngine()
    story_engine = StoryDevEngine()
    script_engine = ScriptEngine()

    _, handoff, _ = topic_engine.evaluate(ResearchPacket(**bomber_data))
    story = story_engine.generate_story(handoff)
    script = script_engine.generate_script(handoff, story)

    qa = script.qa_report
    assert hasattr(qa, "fact_coverage_rate")
    assert hasattr(qa, "fact_accuracy_rate")
    assert qa.fact_coverage_rate >= 80.0
    assert qa.fact_accuracy_rate >= 90.0

    assert hasattr(qa, "causal_claims_detected")
    assert hasattr(qa, "supported_causal_claims")
    assert hasattr(qa, "topic_domain_match")
    assert hasattr(qa, "entity_match")
    assert hasattr(qa, "lexical_contamination")
    assert hasattr(qa, "semantic_contamination")
    assert hasattr(qa, "information_gain_score")
    assert hasattr(qa, "retention_functions_count")

def test_adversarial_topic_bleed_and_synonym_contamination():
    """
    Patch 6: Semantic concept family contamination prevents synonym bypass.
    Flight 19 must not inherit manufacturing / production concept family.
    """
    f19_data = json.load(open(DATA_RESEARCH_DIR / "2026-09-30-bermuda-triangle-flight19.json", "r", encoding="utf-8"))
    topic_engine = TopicSelectionEngine()
    story_engine = StoryDevEngine()

    _, handoff, _ = topic_engine.evaluate(ResearchPacket(**f19_data))
    story = story_engine.generate_story(handoff)

    assert story.contamination_check.contamination_detected is False
    assert story.narrative_validity_passed is True

    full_story_text = " ".join([b.revelation.explanation + " " + b.revelation.new_understanding for b in story.beats]).lower()
    for forbidden in ["manufacturing velocity", "industrial production ecosystem", "factory velocity", "production infrastructure"]:
        assert forbidden not in full_story_text

def test_all_standard_research_datasets_e2e():
    """
    Patch 14 & 15: Run end-to-end pipeline across all research datasets.
    Zero unhandled exceptions, reproducible scores, valid production decisions.
    """
    topic_engine = TopicSelectionEngine()
    story_engine = StoryDevEngine()
    script_engine = ScriptEngine()
    packaging_engine = PackagingEngine()

    for file_path in DATA_RESEARCH_DIR.glob("*.json"):
        raw = json.load(open(file_path, "r", encoding="utf-8"))
        packet = ResearchPacket(**raw)
        dec, handoff, report = topic_engine.evaluate(packet)
        assert 0 <= dec.score <= 100

        if dec.decision != DecisionType.SKIP:
            story = story_engine.generate_story(handoff)
            assert 0 <= story.overall_story_intelligence_score <= 100
            assert len(story.beats) == 5

            script = script_engine.generate_script(handoff, story)
            assert 0 <= script.qa_report.script_quality_score <= 100
            assert len(script.qa_report.checks) == 11
            assert script.qa_report.qa_verdict in ["APPROVED_FOR_PRODUCTION", "REVISE_REQUIRED", "BLOCKED"]

            pkg = packaging_engine.generate_packaging(handoff, script)
            assert len(pkg.titles) == 5
            assert len(pkg.thumbnails) == 3
            assert pkg.qa_report.qa_verdict in ["APPROVED", "APPROVED_WITH_NOTES"]
            assert len(pkg.qa_report.checks) == 25
            assert len(pkg.qa_report.hard_gates) == 10

def test_packaging_qa_and_source_bounded_wording():
    """
    Validates Packaging QA (QA-01 through QA-25) and 10 Hard Gates:
    - Grounded historical terminology (routine training mission, reported compass problems)
    - Rejection of overclaims (no 'the whole truth', 'confirmed cause', 'full transcript')
    - Thumbnail-title complementarity
    - Source provenance adherence
    """
    f19_data = json.load(open(DATA_RESEARCH_DIR / "2026-09-30-bermuda-triangle-flight19.json", "r", encoding="utf-8"))
    topic_engine = TopicSelectionEngine()
    story_engine = StoryDevEngine()
    script_engine = ScriptEngine()
    packaging_engine = PackagingEngine()

    _, handoff, _ = topic_engine.evaluate(ResearchPacket(**f19_data))
    story = story_engine.generate_story(handoff)
    script = script_engine.generate_script(handoff, story)
    pkg = packaging_engine.generate_packaging(handoff, script)

    # 1. QA Matrix Checks
    assert pkg.qa_report.qa_score >= 90.0
    assert pkg.qa_report.qa_verdict == "APPROVED"
    assert len(pkg.qa_report.checks) == 25
    assert len(pkg.qa_report.hard_gates) == 10
    assert len(pkg.qa_report.overclaims_detected) == 0

    # 2. Source-Bounded Terminology Checks
    desc = pkg.seo_description.lower()
    assert "compounding compass malfunctions" not in desc
    assert "reported compass and navigation problems" in desc
    assert "routine navigation training mission" in desc
    assert "national archives materials" in desc or "national archives records" in desc

    # 3. Keyword & Tag Integrity
    for tag in pkg.tags:
        assert not tag.startswith("#")
    assert "flight 19 radio transmissions" in pkg.query_architecture.tier_c_long_tail or "flight 19 radio transmissions" in pkg.tags

    # 4. Thumbnail & Title Complementarity
    for th in pkg.thumbnails:
        assert th.creates_question_not_answer is True
        for t in pkg.titles:
            assert th.text_overlay.lower() != t.title.lower()
