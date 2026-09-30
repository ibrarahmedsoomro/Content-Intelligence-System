import os
import sys
import json
import argparse
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from agents.topic_selection.models import ResearchPacket
from agents.topic_selection.engine import TopicSelectionEngine

def main():
    parser = argparse.ArgumentParser(description="Antigravity Topic Selection Agent CLI Orchestrator")
    parser.add_argument("--input", "-i", type=str, default="data/research/2026-09-30-bomber-research.json", help="Path to research packet JSON")
    parser.add_argument("--scoring", "-s", type=str, default="config/scoring.json", help="Path to scoring config JSON")
    parser.add_argument("--audience", "-a", type=str, default="config/audience.json", help="Path to audience config JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    packet = ResearchPacket(**data)
    engine = TopicSelectionEngine(scoring_config_path=args.scoring, audience_config_path=args.audience)
    
    decision, handoff, report = engine.evaluate(packet)

    # Directories
    outputs_decisions = Path("outputs/decisions")
    outputs_handoffs = Path("outputs/handoffs")
    outputs_decisions.mkdir(parents=True, exist_ok=True)
    outputs_handoffs.mkdir(parents=True, exist_ok=True)

    base_stem = input_path.stem.replace("-research", "")

    # Save Decision JSON
    decision_file = outputs_decisions / f"{base_stem}-decision.json"
    with open(decision_file, "w", encoding="utf-8") as f:
        json.dump(decision.model_dump(), f, indent=2)

    # Save Handoff JSON
    handoff_file = outputs_handoffs / f"{base_stem}-script-handoff.json"
    with open(handoff_file, "w", encoding="utf-8") as f:
        json.dump(handoff.model_dump(), f, indent=2)

    # Save Decision Report
    report_file = outputs_decisions / f"{base_stem}-report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print("=" * 60)
    print(f"TOPIC EVALUATION COMPLETED: {packet.topic_name}")
    print("=" * 60)
    print(report)
    print("\nGenerated Artifacts:")
    print(f"  • Decision JSON: {decision_file}")
    print(f"  • Handoff JSON:  {handoff_file}")
    print(f"  • Markdown Card: {report_file}")

if __name__ == "__main__":
    main()
