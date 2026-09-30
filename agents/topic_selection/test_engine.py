import json
from agents.topic_selection.models import ResearchPacket, CompetitorItem
from agents.topic_selection.engine import TopicSelectionEngine

def main():
    # WWII American Bombers Candidate Packet
    wwii_bomber_packet = ResearchPacket(
        topic_name="Why Did America Need So Many WWII Bombers?",
        main_keyword="WWII American bombers",
        related_keywords=["B-17 Flying Fortress", "B-24 Liberator", "B-25 Mitchell", "B-29 Superfortress"],
        search_demand_score=82.0,
        trend_momentum=75.0,
        competitor_examples=[
            CompetitorItem(title="The Legendary B-17 Bomber Explained", views=450000, channel_authority="HIGH"),
            CompetitorItem(title="B-17 vs B-24: Which Was Really Better?", views=280000, channel_authority="MEDIUM"),
        ],
        competitor_saturation_level=60.0,
        audience_signals=[
            "Why did the US make the B-24 if the B-17 was already great?",
            "How did theater requirements in the Pacific differ from Europe?"
        ],
        content_gaps=[
            "Explaining the strategic doctrine and production tradeoffs rather than simple speed/armor comparisons.",
            "Visualizing the Pacific vs European mission ranges."
        ],
        existing_angles=["The hidden strategic reason one bomber could not do every job."],
        topic_category="Military History / Aviation Strategy",
        related_topics=["Pacific bomber strategy", "B-24 twin-tail mystery", "US industrial doctrine 1941-1945"],
        potential_series_ideas=["WWII Bomber Evolution Series", "Aircraft That Failed vs Aircraft That Won"],
        source_links=["https://nationalww2museum.org/aircraft-strategy"],
        research_confidence=91.0,
        curiosity_factor=94.0,
        audience_fit_score=91.0,
        depth_score=85.0,
        visual_packaging_score=93.0,
        is_factually_verified=True
    )

    engine = TopicSelectionEngine()
    decision_output = engine.evaluate_topic(wwii_bomber_packet)
    
    print("=" * 60)
    print("TOPIC SELECTION AGENT — DECISION RESULT")
    print("=" * 60)
    print(json.dumps(decision_output.model_dump(), indent=2))

if __name__ == "__main__":
    main()
