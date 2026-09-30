# #5 — TOPIC SELECTION AGENT
## Final Production Architecture — Autonomous Topic Decision Engine

### 1. Agent Core Mission
Identify candidate topics from research that realistically hold audience attention, discoverability, retention, differentiation, and repeatable content potential — deciding final production format, angle, and timing.

---

### 2. Pipeline Position
```
Research Agent
      ↓
Topic Selection Agent  <--- [YOU ARE HERE]
      ↓
Topic Angle / Story Development Agent
      ↓
Script Agent
      ↓
SEO Agent
      ↓
Thumbnail / Packaging Agent
      ↓
Publishing / Analytics Agent
```

---

### 3. Input Data Contract

#### Required Input:
- `topic_name`: string
- `main_keyword`: string
- `related_keywords`: list[string]
- `search_demand_data`: object / metrics
- `trend_freshness_data`: object / metrics
- `competitor_examples`: list[object] (titles, views, dates, channel authority)
- `recent_performance`: object
- `audience_signals`: list[string] (comments, questions, sentiment)
- `content_gaps`: list[string]
- `existing_angles`: list[string]
- `topic_category`: string
- `related_topics`: list[string]
- `potential_series_ideas`: list[string]
- `source_links`: list[string]
- `research_confidence`: float (0–100)
- `research_date`: ISO timestamp string

#### Optional Channel-Specific Input:
- `avg_views`, `recent_10_video_perf`, `shorts_perf`, `long_form_perf`, `ctr`, `retention_rate`, `returning_viewers`, `audience_geography`, `audience_age`, `best_upload_format`

---

### 4. 12-Stage Evaluation Pipeline

1. **Stage 0: Input Normalization** — Normalize raw keyword into structured content opportunity (entities, intent, curiosities).
2. **Stage 1: Topic Validation** — Factual foundation check (`VALID`, `VALID WITH REFRAMING`, `INSUFFICIENT DATA`, `UNSTABLE`, `UNVERIFIED`, `SKIP`).
3. **Stage 2: Search Demand Analysis (Weight: 20)** — Stability, momentum, long-tail, and entity demand.
4. **Stage 3: Curiosity Analysis (Weight: 15)** — Tension, open questions, contradictions, knowledge gaps.
5. **Stage 4: Audience Fit (Weight: 15)** — Demographic, channel identity, and language alignment.
6. **Stage 5: Competition Opportunity (Weight: 15)** — Opportunity in spite of high competition (gaps & saturation level).
7. **Stage 6: Content Gap / Differentiation (Weight: 10)** — Why our version must be watched over existing videos.
8. **Stage 7: Series & Cluster Potential (Weight: 10)** — Expandability into topic clusters / content pillars.
9. **Stage 8: Format Selection Engine (Weight: 5)** — `SHORTS`, `LONG-FORM`, `BOTH`, `SERIES`, `NOT SUITABLE`.
10. **Stage 9: Timing & Freshness (Weight: 5)** — `MAKE NOW`, `MAKE SOON`, `EVERGREEN QUEUE`, `WAIT FOR EVENT`, `WATCH TREND`, `SKIP`.
11. **Stage 10: Production Feasibility (Weight: 3)** — Visual/animation/voiceover complexity assessment (`LOW`, `MEDIUM`, `HIGH`, `VERY HIGH`).
12. **Stage 11: Packaging Potential (Weight: 2)** — Visual subject clarity, title punchiness, contrast.
13. **Stage 12: Risk & Quality Gate** — Fact check necessity, duplicate risk, sensitivity check.

---

### 5. Hard Gates & Decision Matrix

#### Hard Gates:
- **Gate A (Evidence):** Research Confidence < 60 → `NEED MORE RESEARCH`
- **Gate B (Audience):** Audience Fit < 40 → `SKIP` or `REFRAME`
- **Gate C (Curiosity/Demand):** Curiosity < 35 AND Demand < 45 → `SKIP`
- **Gate D (Differentiation):** No gap AND Heavy saturation → `REFRAME`
- **Gate E (Depth):** Long-form chosen BUT shallow info → `SHIFT TO SHORTS`
- **Gate F (Reliability):** Unverifiable core premise → `DO NOT PRODUCE`

#### Score Matrix:
- **80–100:** `MAKE NOW`
- **68–79:** `MAKE`
- **55–67:** `TEST / REFRAME`
- **40–54:** `WATCHLIST`
- **0–39:** `SKIP`

---

### 6. Standard Output Schema (JSON)

```json
{
  "topic": "Why Did America Need So Many WWII Bombers?",
  "decision": "MAKE_NOW",
  "opportunity_score": 84,
  "confidence": 91,
  "research_status": "VALID",
  "demand": 82,
  "curiosity": 94,
  "audience_fit": 91,
  "competition_opportunity": 68,
  "content_gap": 87,
  "series_potential": 92,
  "format_fit": 88,
  "timing": "EVERGREEN",
  "production_effort": "MEDIUM",
  "packaging_potential": 93,
  "primary_angle": "The hidden reason one bomber could not do every job.",
  "alternative_angles": [
    "Why the B-17 Became America's Most Famous Bomber",
    "Why Did the B-17 Need the B-24?",
    "The WWII Bomber Problem the B-17 Couldn't Solve"
  ],
  "recommended_format": "BOTH",
  "core_viewer_question": "Why did the US military build multiple distinct heavy bombers simultaneously?",
  "main_risk": "Avoid oversimplifying aircraft comparisons into 'best bomber' debates.",
  "why_this_topic": "Strong contradiction, high curiosity, recognizable military aircraft, and clear cluster expansion.",
  "next_action": "HANDOFF_TO_SCRIPT_AGENT",
  "handoff_agent": "Script Agent"
}
```
