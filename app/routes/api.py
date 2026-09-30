import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body

from agents.topic_selection.models import (
    ResearchPacket,
    MachineTopicDecision,
    ScriptHandoffPacket,
    DecisionType,
)
from agents.topic_selection.engine import TopicSelectionEngine
from agents.story_dev.engine import StoryDevEngine
from agents.script.engine import ScriptEngine
from agents.packaging.engine import PackagingEngine

router = APIRouter(prefix="/api", tags=["Content Intelligence Full Pipeline API"])

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

# Engines
topic_engine = TopicSelectionEngine()
story_engine = StoryDevEngine()
script_engine = ScriptEngine()
packaging_engine = PackagingEngine()

@router.get("/status")
def get_system_status():
    return {
        "system": "Content Intelligence System",
        "version": "2.1.0",
        "active_pipeline": [
            {"id": "research", "name": "1. Research Agent", "status": "COMPLETED", "stage": 1},
            {"id": "topic_selection", "name": "2. Topic Selection Agent", "status": "ACTIVE", "stage": 2},
            {"id": "story_dev", "name": "3. Story Dev Agent", "status": "ACTIVE", "stage": 3},
            {"id": "script", "name": "4. Script Agent", "status": "ACTIVE", "stage": 4},
            {"id": "packaging", "name": "5. Packaging Agent", "status": "ACTIVE", "stage": 5}
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
    topic_slug = packet_data.get("topic_name", "custom-topic").lower().replace(" ", "-").replace("?", "").replace(":", "")[:40]
    filename = f"custom-{topic_slug}.json"
    file_path = DATA_RESEARCH_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(packet_data, f, indent=2)
    return {"status": "SUCCESS", "filename": filename, "topic_name": packet_data.get("topic_name")}

@router.post("/evaluate")
def evaluate_single_topic(packet: ResearchPacket):
    decision, handoff, report = topic_engine.evaluate(packet)
    
    topic_slug = packet.topic_name.lower().replace(" ", "-").replace("?", "").replace(":", "")[:40]
    dec_path = OUTPUTS_DECISIONS_DIR / f"{topic_slug}-decision.json"
    rep_path = OUTPUTS_DECISIONS_DIR / f"{topic_slug}-report.md"
    hnd_path = OUTPUTS_HANDOFFS_DIR / f"{topic_slug}-script-handoff.json"

    with open(dec_path, "w", encoding="utf-8") as f:
        json.dump(decision.model_dump(), f, indent=2)
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write(report)
    with open(hnd_path, "w", encoding="utf-8") as f:
        json.dump(handoff.model_dump(), f, indent=2)

    return {
        "decision": decision.model_dump(),
        "handoff": handoff.model_dump(),
        "report_markdown": report
    }

# ==========================================
# ADVANCED MULTI-STAGE PIPELINE ENDPOINTS
# ==========================================

@router.post("/pipeline/run-full")
def run_full_pipeline(packet: ResearchPacket):
    """
    Executes all remaining pipeline stages end-to-end:
    Topic Selection -> Story Dev -> Script -> Packaging
    """
    topic_slug = packet.topic_name.lower().replace(" ", "-").replace("?", "").replace(":", "")[:40]

    # Stage 2: Topic Selection
    decision, handoff, report = topic_engine.evaluate(packet)
    
    # Save Stage 2
    with open(OUTPUTS_DECISIONS_DIR / f"{topic_slug}-decision.json", "w", encoding="utf-8") as f:
        json.dump(decision.model_dump(), f, indent=2)
    with open(OUTPUTS_HANDOFFS_DIR / f"{topic_slug}-script-handoff.json", "w", encoding="utf-8") as f:
        json.dump(handoff.model_dump(), f, indent=2)

    # Check if rejected by Hard Gate
    if decision.decision in [DecisionType.SKIP, DecisionType.NEED_MORE_RESEARCH]:
        return {
            "status": "STOPPED_AT_TOPIC_SELECTION",
            "decision": decision.model_dump(),
            "handoff": handoff.model_dump(),
            "story": None,
            "script": None,
            "packaging": None
        }

    # Stage 3: Story Dev
    story = story_engine.generate_story(handoff)
    with open(OUTPUTS_STORIES_DIR / f"{topic_slug}-story.json", "w", encoding="utf-8") as f:
        json.dump(story.model_dump(), f, indent=2)

    # Stage 4: Script Agent
    script = script_engine.generate_script(handoff, story)
    with open(OUTPUTS_SCRIPTS_DIR / f"{topic_slug}-script.json", "w", encoding="utf-8") as f:
        json.dump(script.model_dump(), f, indent=2)

    # Stage 5: Packaging Agent
    packaging = packaging_engine.generate_packaging(handoff, script)
    with open(OUTPUTS_PACKAGES_DIR / f"{topic_slug}-packaging.json", "w", encoding="utf-8") as f:
        json.dump(packaging.model_dump(), f, indent=2)

    return {
        "status": "PIPELINE_COMPLETE",
        "decision": decision.model_dump(),
        "handoff": handoff.model_dump(),
        "story": story.model_dump(),
        "script": script.model_dump(),
        "packaging": packaging.model_dump()
    }

@router.post("/pipeline/stage-story/{topic_slug}")
def advance_to_story(topic_slug: str):
    handoff_path = OUTPUTS_HANDOFFS_DIR / f"{topic_slug}-script-handoff.json"
    if not handoff_path.exists():
        raise HTTPException(status_code=404, detail="Topic Handoff packet not found. Run Topic Selection first.")
    
    with open(handoff_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        handoff = ScriptHandoffPacket(**data)

    story = story_engine.generate_story(handoff)
    with open(OUTPUTS_STORIES_DIR / f"{topic_slug}-story.json", "w", encoding="utf-8") as f:
        json.dump(story.model_dump(), f, indent=2)

    return story.model_dump()

@router.post("/pipeline/stage-script/{topic_slug}")
def advance_to_script(topic_slug: str):
    handoff_path = OUTPUTS_HANDOFFS_DIR / f"{topic_slug}-script-handoff.json"
    story_path = OUTPUTS_STORIES_DIR / f"{topic_slug}-story.json"
    
    if not handoff_path.exists() or not story_path.exists():
        raise HTTPException(status_code=404, detail="Prerequisite stages (Handoff / Story) missing.")

    with open(handoff_path, "r", encoding="utf-8") as f:
        handoff = ScriptHandoffPacket(**json.load(f))
    with open(story_path, "r", encoding="utf-8") as f:
        story_data = json.load(f)
        from agents.story_dev.models import StoryDevOutput
        story = StoryDevOutput(**story_data)

    script = script_engine.generate_script(handoff, story)
    with open(OUTPUTS_SCRIPTS_DIR / f"{topic_slug}-script.json", "w", encoding="utf-8") as f:
        json.dump(script.model_dump(), f, indent=2)

    return script.model_dump()

@router.post("/pipeline/stage-packaging/{topic_slug}")
def advance_to_packaging(topic_slug: str):
    handoff_path = OUTPUTS_HANDOFFS_DIR / f"{topic_slug}-script-handoff.json"
    script_path = OUTPUTS_SCRIPTS_DIR / f"{topic_slug}-script.json"
    
    if not handoff_path.exists():
        raise HTTPException(status_code=404, detail="Topic Handoff missing.")

    with open(handoff_path, "r", encoding="utf-8") as f:
        handoff = ScriptHandoffPacket(**json.load(f))

    script = None
    if script_path.exists():
        from agents.script.models import ProductionScriptOutput
        with open(script_path, "r", encoding="utf-8") as f:
            script = ProductionScriptOutput(**json.load(f))

    packaging = packaging_engine.generate_packaging(handoff, script)
    with open(OUTPUTS_PACKAGES_DIR / f"{topic_slug}-packaging.json", "w", encoding="utf-8") as f:
        json.dump(packaging.model_dump(), f, indent=2)

    return packaging.model_dump()

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
                
                topic_slug = packet.topic_name.lower().replace(" ", "-").replace("?", "").replace(":", "")[:40]
                with open(OUTPUTS_DECISIONS_DIR / f"{topic_slug}-decision.json", "w", encoding="utf-8") as out_f:
                    json.dump(decision.model_dump(), out_f, indent=2)
                with open(OUTPUTS_HANDOFFS_DIR / f"{topic_slug}-script-handoff.json", "w", encoding="utf-8") as out_f:
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
