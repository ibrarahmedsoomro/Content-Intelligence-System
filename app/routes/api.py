import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import PlainTextResponse

from agents.topic_selection.models import (
    ResearchPacket,
    MachineTopicDecision,
    TopicIntelligenceHandoff,
    DecisionType,
)
from agents.topic_selection.engine import TopicSelectionEngine
from agents.story_dev.engine import StoryDevEngine
from agents.script.engine import ScriptEngine
from agents.packaging.engine import PackagingEngine

router = APIRouter(prefix="/api", tags=["Content Intelligence Pipeline API"])

BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_RESEARCH_DIR = BASE_DIR / "data" / "research"
OUTPUTS_DECISIONS_DIR = BASE_DIR / "outputs" / "decisions"
OUTPUTS_HANDOFFS_DIR = BASE_DIR / "outputs" / "handoffs"
OUTPUTS_STORIES_DIR = BASE_DIR / "outputs" / "stories"
OUTPUTS_SCRIPTS_DIR = BASE_DIR / "outputs" / "scripts"
OUTPUTS_PACKAGES_DIR = BASE_DIR / "outputs" / "packages"

for d in [
    CONFIG_DIR, DATA_RESEARCH_DIR, OUTPUTS_DECISIONS_DIR, 
    OUTPUTS_HANDOFFS_DIR, OUTPUTS_STORIES_DIR, OUTPUTS_SCRIPTS_DIR, OUTPUTS_PACKAGES_DIR
]:
    d.mkdir(parents=True, exist_ok=True)

# Shared Engines
topic_engine = TopicSelectionEngine()
story_engine = StoryDevEngine()
script_engine = ScriptEngine()
packaging_engine = PackagingEngine()

@router.get("/status")
def get_system_status():
    return {
        "system": "Content Intelligence System",
        "version": "3.0.0-ExpertMode",
        "scoring_dimensions_count": 12,
        "active_pipeline": [
            {"id": "research", "name": "1. Research Agent", "status": "COMPLETED", "stage": 1},
            {"id": "topic_selection", "name": "2. Topic Selection Agent (12 Dimensions)", "status": "ACTIVE", "stage": 2},
            {"id": "story_dev", "name": "3. Story Dev Agent (Beat Intelligence & Open Loops)", "status": "ACTIVE", "stage": 3},
            {"id": "script", "name": "4. Script & QA Agent (Traceable Scenes & Promise Audit)", "status": "ACTIVE", "stage": 4},
            {"id": "packaging", "name": "5. Packaging & SEO Agent (CTR Formulas & AI Prompts)", "status": "ACTIVE", "stage": 5}
        ]
    }

@router.get("/config/scoring")
def get_scoring_config():
    path = CONFIG_DIR / "scoring.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.post("/config/scoring")
def update_scoring_config(config_data: Dict[str, Any] = Body(...)):
    path = CONFIG_DIR / "scoring.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    return {"status": "SUCCESS", "message": "Scoring configuration updated."}

@router.get("/config/audience")
def get_audience_config():
    path = CONFIG_DIR / "audience.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.post("/config/audience")
def update_audience_config(config_data: Dict[str, Any] = Body(...)):
    path = CONFIG_DIR / "audience.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    return {"status": "SUCCESS", "message": "Audience configuration updated."}

@router.get("/research/list")
def list_research_packets():
    packets = []
    for file_path in DATA_RESEARCH_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                packets.append({
                    "filename": file_path.name,
                    "topic_name": content.get("topic_name", file_path.stem),
                    "main_keyword": content.get("main_keyword", ""),
                    "category": content.get("topic_category", "General"),
                    "confidence": content.get("research_confidence", 0),
                    "demand": content.get("search_demand_score", 0),
                    "curiosity": content.get("curiosity_factor", 0)
                })
        except Exception:
            continue
    return packets

@router.get("/research/{filename}")
def get_research_packet(filename: str):
    file_path = DATA_RESEARCH_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Research packet not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.post("/research/create")
def create_research_packet(packet_data: Dict[str, Any] = Body(...)):
    slug = re.sub(r'[^a-zA-Z0-9]', '-', packet_data.get("topic_name", "custom-topic").lower())[:35]
    filename = f"custom-{slug}.json"
    file_path = DATA_RESEARCH_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(packet_data, f, indent=2)
    return {"status": "SUCCESS", "filename": filename, "topic_name": packet_data.get("topic_name")}

@router.post("/evaluate")
def evaluate_single_topic(packet: ResearchPacket):
    decision, handoff, report = topic_engine.evaluate(packet)
    slug = re.sub(r'[^a-zA-Z0-9]', '-', packet.topic_name.lower())[:35]

    with open(OUTPUTS_DECISIONS_DIR / f"{slug}-decision.json", "w", encoding="utf-8") as f:
        json.dump(decision.model_dump(), f, indent=2)
    with open(OUTPUTS_DECISIONS_DIR / f"{slug}-report.md", "w", encoding="utf-8") as f:
        f.write(report)
    with open(OUTPUTS_HANDOFFS_DIR / f"{slug}-script-handoff.json", "w", encoding="utf-8") as f:
        json.dump(handoff.model_dump(), f, indent=2)

    return {
        "decision": decision.model_dump(),
        "handoff": handoff.model_dump(),
        "report_markdown": report
    }

@router.post("/pipeline/run-full")
def run_full_pipeline(packet: ResearchPacket):
    """
    End-to-End Execution across all 5 Agent Stages:
    1. Research (Ingested)
    2. Topic Selection (12 Dimensions + 6 Hard Gates)
    3. Story Dev (Beat Intelligence Score + Open Loops + Info Gain Diffs)
    4. Script Agent (Traceable Scenes + QA Promise Delivery Audit)
    5. Packaging Agent (CTR Formulas + AI Prompts + SEO)
    """
    slug = re.sub(r'[^a-zA-Z0-9]', '-', packet.topic_name.lower())[:35]

    # Stage 2: Topic Selection
    decision, handoff, report = topic_engine.evaluate(packet)
    with open(OUTPUTS_DECISIONS_DIR / f"{slug}-decision.json", "w", encoding="utf-8") as f:
        json.dump(decision.model_dump(), f, indent=2)
    with open(OUTPUTS_HANDOFFS_DIR / f"{slug}-script-handoff.json", "w", encoding="utf-8") as f:
        json.dump(handoff.model_dump(), f, indent=2)

    if decision.decision in [DecisionType.SKIP, DecisionType.NEED_MORE_RESEARCH]:
        return {
            "status": "STOPPED_AT_TOPIC_SELECTION",
            "decision": decision.model_dump(),
            "handoff": handoff.model_dump(),
            "story": None,
            "script": None,
            "packaging": None
        }

    # Stage 3: Story Dev Agent
    story = story_engine.generate_story(handoff)
    with open(OUTPUTS_STORIES_DIR / f"{slug}-story.json", "w", encoding="utf-8") as f:
        json.dump(story.model_dump(), f, indent=2)

    # Stage 4: Script & QA Agent
    script = script_engine.generate_script(handoff, story)
    with open(OUTPUTS_SCRIPTS_DIR / f"{slug}-script.json", "w", encoding="utf-8") as f:
        json.dump(script.model_dump(), f, indent=2)

    # Stage 5: Packaging & SEO Agent
    packaging = packaging_engine.generate_packaging(handoff, script)
    with open(OUTPUTS_PACKAGES_DIR / f"{slug}-packaging.json", "w", encoding="utf-8") as f:
        json.dump(packaging.model_dump(), f, indent=2)

    return {
        "status": "PIPELINE_COMPLETE",
        "decision": decision.model_dump(),
        "handoff": handoff.model_dump(),
        "story": story.model_dump(),
        "script": script.model_dump(),
        "packaging": packaging.model_dump()
    }

@router.post("/evaluate/batch")
def evaluate_batch_topics():
    results = []
    queue = {"NOW": [], "NEXT": [], "TEST": [], "WATCHLIST": [], "SKIP": []}

    for file_path in DATA_RESEARCH_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                packet = ResearchPacket(**raw_data)
                decision, handoff, report = topic_engine.evaluate(packet)
                slug = re.sub(r'[^a-zA-Z0-9]', '-', packet.topic_name.lower())[:35]

                with open(OUTPUTS_DECISIONS_DIR / f"{slug}-decision.json", "w", encoding="utf-8") as out_f:
                    json.dump(decision.model_dump(), out_f, indent=2)
                with open(OUTPUTS_HANDOFFS_DIR / f"{slug}-script-handoff.json", "w", encoding="utf-8") as out_f:
                    json.dump(handoff.model_dump(), out_f, indent=2)

                item = {
                    "filename": file_path.name,
                    "topic": decision.topic,
                    "decision": decision.decision.value,
                    "score": decision.score,
                    "confidence": decision.confidence,
                    "recommended_format": decision.recommended_format.value,
                    "primary_angle": decision.primary_angle,
                    "timing": decision.timing_action,
                    "effort": decision.production_effort.value,
                    "gap_reason": decision.content_gap_reason,
                    "scores": decision.scores.model_dump()
                }
                results.append(item)

                if decision.decision in [DecisionType.MAKE_NOW]:
                    queue["NOW"].append(item)
                elif decision.decision in [DecisionType.MAKE, DecisionType.BOTH, DecisionType.LONG_FORM]:
                    queue["NEXT"].append(item)
                elif decision.decision in [DecisionType.TEST_SHORT, DecisionType.REFRAME]:
                    queue["TEST"].append(item)
                elif decision.decision in [DecisionType.WATCHLIST, DecisionType.WAIT]:
                    queue["WATCHLIST"].append(item)
                else:
                    queue["SKIP"].append(item)
        except Exception:
            continue

    for k in queue:
        queue[k].sort(key=lambda x: x.get("score", 0), reverse=True)

    return {
        "total_evaluated": len(results),
        "queue": queue,
        "results": results
    }

@router.get("/export/{topic_slug}/markdown", response_class=PlainTextResponse)
def export_topic_markdown(topic_slug: str):
    slug = re.sub(r'[^a-zA-Z0-9]', '-', topic_slug.lower())[:35]
    dec_file = OUTPUTS_DECISIONS_DIR / f"{slug}-decision.json"
    story_file = OUTPUTS_STORIES_DIR / f"{slug}-story.json"
    script_file = OUTPUTS_SCRIPTS_DIR / f"{slug}-script.json"
    pkg_file = OUTPUTS_PACKAGES_DIR / f"{slug}-packaging.json"

    if not dec_file.exists():
        raise HTTPException(status_code=404, detail="Topic outputs not found.")

    with open(dec_file, "r", encoding="utf-8") as f:
        dec = json.load(f)
    
    story = json.load(open(story_file, "r", encoding="utf-8")) if story_file.exists() else {}
    script = json.load(open(script_file, "r", encoding="utf-8")) if script_file.exists() else {}
    pkg = json.load(open(pkg_file, "r", encoding="utf-8")) if pkg_file.exists() else {}

    md = f"""# COMPLETE PRODUCTION BUNDLE: {dec.get('topic')}

## 1. TOPIC DECISION (STAGE 2)
- **Decision:** `{dec.get('decision')}`
- **Opportunity Score:** `{dec.get('score')}/100` (Confidence: `{dec.get('confidence')}%`)
- **Format:** `{dec.get('recommended_format')}`
- **Primary Angle:** {dec.get('primary_angle')}
- **Core Viewer Question:** "{dec.get('viewer_question')}"
- **Content Gap:** {dec.get('content_gap_reason')}

---

## 2. STORY INTELLIGENCE BLUEPRINT (STAGE 3)
- **Core Thesis:** {story.get('core_thesis', 'N/A')}
- **Story Intelligence Score:** `{story.get('overall_story_intelligence_score', 'N/A')}/100`
- **Drama Integrity:** {'PASSED' if story.get('drama_integrity_passed') else 'FLAGGED'}

### 5-BEAT STRUCTURE:
"""
    for b in story.get('beats', []):
        md += f"""
### Beat #{b.get('beat_number')}: {b.get('title')}
- **Beat Score:** `{b.get('beat_score', {}).get('total_beat_score')}/100` | **Dependency:** `{b.get('narrative_dependency_score')}/10`
- **Goal:** {b.get('function_role')}
- **Revelation:** {b.get('revelation', {}).get('new_understanding')}
- **Info Gain:** {b.get('information_gain', {}).get('genuine_change')}
- **Supporting Facts:** {', '.join(b.get('supporting_fact_ids', []))}
"""

    md += f"""
---

## 3. BROADCAST PRODUCTION SCRIPT (STAGE 4)
- **Duration:** `{script.get('estimated_duration', 'N/A')}` | **Words:** `{script.get('total_word_count', 'N/A')}`
- **QA Promise Delivery Match:** `{script.get('qa_report', {}).get('promise_delivery', {}).get('promise_match_score', 'N/A')}%`
"""
    for sc in script.get('scenes', []):
        md += f"""
---
### [{sc.get('timestamp_estimate')}] SCENE {sc.get('scene_number')}: {sc.get('section_title')}
- **Facts:** {', '.join(sc.get('supporting_fact_ids', []))} | **Loops:** {', '.join(sc.get('open_loop_ids', []))} ({sc.get('payoff_contribution')})
- **VISUAL:** {sc.get('visual_direction')}
- **AUDIO:** {sc.get('audio_sfx')}
- **VOICEOVER:**
> {sc.get('voiceover_script')}
"""

    md += f"""
---

## 4. PACKAGING & SEO (STAGE 5)
### High-CTR Titles:
"""
    for t in pkg.get('titles', []):
        md += f"- **[{t.get('predicted_ctr')}]** {t.get('title')} *({t.get('formula_type')} Formula)*\n"

    md += f"""
### Thumbnail Concepts:
"""
    for th in pkg.get('thumbnails', []):
        md += f"#### {th.get('concept_name')}\n- **Text Overlay:** `{th.get('text_overlay')}`\n- **Layout:** {th.get('visual_layout')}\n- **Prompt:** `{th.get('ai_image_prompt')}`\n\n"

    md += f"""
### YouTube SEO Description:
```
{pkg.get('seo_description', '')}
```
"""
    return PlainTextResponse(content=md, media_type="text/markdown")
