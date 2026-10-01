---
name: topic-selection
description: Transform researched topic candidates into evidence-based production decisions, evaluating demand, curiosity, audience fit, competition gaps, format, and series potential.
---

# TOPIC SELECTION SKILL

## Purpose
Transform researched topic candidates into evidence-based production decisions.
Determines whether to make a topic, which angle to use, which format to produce (Shorts, Long-form, Both, Series), when to produce it, and creates the handoff packet for the Script Agent.

---

## INPUT CONTRACT
Accept one of the following:
1. **SINGLE TOPIC**: A researched topic object.
2. **BATCH**: A list of researched topic objects.
3. **RAW RESEARCH**: Research Agent output containing structured or semi-structured research.

---

## WORKFLOW STEPS

### STEP 1 — NORMALIZE INPUT
Extract the following fields from the research packet:
- `topic`
- `primary_keyword`
- `related_keywords`
- `search_signals`
- `competitors`
- `audience_signals`
- `content_gaps`
- `existing_angles`
- `sources`
- `research_confidence`
- `channel_context`

> **Rule:** If necessary fields are missing, mark them `UNKNOWN`. Do NOT invent values.

---

### STEP 2 — VALIDATE
Evaluate:
- Factual basis
- Source availability
- Topic clarity
- Audience relevance
- Content depth

**Return validation status:**
- `VALID`
- `VALID_WITH_REFRAMING`
- `INSUFFICIENT`
- `UNVERIFIED`
- `SKIP`

---

### STEP 3 — DEMAND ANALYSIS
Evaluate:
- Primary keyword demand
- Related keyword demand
- Trend movement & topic momentum
- Query diversity & evergreen value

**Return:**
- `demand_score` (0–100)
- `demand_reason`

---

### STEP 4 — CURIOSITY ANALYSIS
Identify:
- Unanswered questions
- Contradictions & surprises
- Mysteries & hidden causes
- Unexpected outcomes & comparison tension

**Return:**
- `curiosity_score` (0–100)
- `core_viewer_question`

---

### STEP 5 — AUDIENCE FIT
Compare the topic against `config/audience.json`.
Evaluate:
- Demographic fit & interest fit
- Channel identity & style fit
- Language fit & viewer intent
- Existing audience retention vs new viewer acquisition potential

**Return:**
- `audience_fit_score` (0–100)

---

### STEP 6 — COMPETITION ANALYSIS
Analyze competitors using:
- Topic saturation & angle saturation
- Competitor recency & quality
- Average view performance
- Authority concentration
- Title & thumbnail repetition patterns

> **Rule:** Do NOT simply count competitors. Separate saturation from opportunity.

**Return:**
- `competition_opportunity_score` (0–100) *(Higher = better opportunity)*

---

### STEP 7 — CONTENT GAP
Identify:
- `information_gap`
- `angle_gap`
- `visual_gap`
- `storytelling_gap`
- `comparison_gap`
- `unanswered_question`

**Return:**
- `content_gap_score` (0–100)
- Answer to: *"Why would someone watch our version over existing videos?"*

---

### STEP 8 — DIFFERENTIATION
Determine whether the topic can be made meaningfully distinct:
- `FRESH`
- `FRESH_WITH_ANGLE`
- `MODERATELY_DIFFERENT`
- `REPETITIVE`
- `DUPLICATE`

> If repetitive, trigger autonomous reframing.

---

### STEP 9 — SERIES POTENTIAL
Determine:
- Content pillar & topic cluster
- Possible sub-episodes & follow-up subjects
- Shorts extensions & long-form expansions

**Return:**
- `series_potential_score` (0–100)

---

### STEP 10 — FORMAT SELECTION
Evaluate:
- `shorts_fit`: Immediate hook in 3s, single reveal, 20–60s duration.
- `long_form_fit`: Deep narrative arc, evidence points, multi-section development.
- `series_fit`: Multi-episode cluster potential.

**Select format:**
- `SHORTS`
- `LONG_FORM`
- `BOTH`
- `TEST_SHORT`
- `SERIES`
- `WATCHLIST`

---

### STEP 11 — TIMING
Classify topic freshness:
- `EVERGREEN`
- `TRENDING`
- `SEASONAL`
- `EVENT_DRIVEN`
- `ANNIVERSARY_DRIVEN`
- `REVIVING`
- `DECLINING`
- `TOO_EARLY`

Select timing action (`MAKE_NOW`, `MAKE_SOON`, `EVERGREEN`, `WAIT_FOR_EVENT`, `WATCH_TREND`, `SKIP`).

---

### STEP 12 — PRODUCTION FEASIBILITY
Evaluate production effort:
- Research, visual, animation, editing, and fact-checking effort.
- Copyright risk and thumbnail creation difficulty.

**Return:**
- `LOW`
- `MEDIUM`
- `HIGH`
- `VERY_HIGH`

> **Rule:** Do not automatically reject high-effort topics if opportunity is exceptionally high.

---

### STEP 13 — PACKAGING POTENTIAL
Estimate whether the topic has:
- Recognizable subject / focal point
- Visual contrast or conflict
- Strong curiosity gap in title/thumbnail

**Return:**
- `packaging_score` (0–100)

---

### STEP 14 — SCORE CALCULATION
Load weights dynamically from `config/scoring.json` (Exact 12 Dimensions):
1. Demand: 18%
2. Curiosity: 14%
3. Audience Fit: 13%
4. Competition Opportunity: 13%
5. Content Gap: 10%
6. Series Potential: 8%
7. Evidence Strength: 8%
8. Narrative Payoff Potential: 6%
9. Format Fit: 4%
10. Timing: 3%
11. Feasibility: 2%
12. Packaging: 1%

$$\text{Opportunity Score} = \sum_{i=1}^{12} (\text{Dimension Score}_i \times \text{Weight}_i) = 100\%$$

---

### STEP 15 — HARD GATE CHECK
Apply strict hard gates before issuing the final decision:
1. **Gate A (Evidence):** Research Confidence < 60 $\rightarrow$ `NEED_MORE_RESEARCH`
2. **Gate B (Audience):** Audience Fit < 40 $\rightarrow$ `SKIP` or `REFRAME`
3. **Gate C (Curiosity & Demand):** Curiosity < 35 AND Demand < 45 $\rightarrow$ `SKIP`
4. **Gate D (Differentiation):** Heavy saturation + zero content gap $\rightarrow$ `REFRAME`
5. **Gate E (Depth):** Long-form chosen but insufficient depth $\rightarrow$ `SHIFT TO SHORTS`
6. **Gate F (Reliability):** Unverifiable core premise $\rightarrow$ `DO NOT PRODUCE`

---

### STEP 16 — AUTONOMOUS REFRAMING
When a topic is viable but generic or crowded:
- Generate up to 3 alternative angles.
- For each angle, evaluate: `angle`, `viewer_question`, `curiosity`, `differentiation`, `audience_fit`, `format`, `score`.
- Approve the strongest viable angle.

---

### STEP 17 — BATCH OPTIMIZATION
When processing multiple candidates:
1. Normalize & validate all candidates.
2. Deduplicate against channel history.
3. Group into clusters.
4. Score and reframe.
5. Create priority production queue: `NOW`, `NEXT`, `TEST`, `WATCHLIST`, `SKIP`.
6. Ensure no two repetitive topics are scheduled adjacently.

---

### STEP 18 — FINAL DECISION
Assign exactly one action:
- `MAKE_NOW` (Score 80–100)
- `MAKE` (Score 68–79)
- `REFRAME` / `TEST_SHORT` (Score 55–67)
- `LONG_FORM`
- `BOTH`
- `SERIES`
- `WATCHLIST` (Score 40–54)
- `WAIT`
- `NEED_MORE_RESEARCH`
- `SKIP` (Score 0–39)

---

### STEP 19 — PRODUCTION HANDOFF
Create a clean handoff object for the Script Agent with all required production context.

---

## OUTPUT CONTRACT

### 1. Human-Readable Decision Report
Provide a clean summary card with score breakdowns, angle reasoning, format selection, and risk notes.

### 2. Machine-Readable Output (JSON)
```json
{
  "topic": "Why Did America Need So Many WWII Bombers?",
  "decision": "MAKE_NOW",
  "score": 87.3,
  "confidence": 91.0,
  "validation": "VALID",
  "scores": {
    "demand": 82.0,
    "curiosity": 94.0,
    "audience_fit": 91.0,
    "competition_opportunity": 70.0,
    "content_gap": 100.0,
    "series_potential": 100.0,
    "format_fit": 90.0,
    "timing": 80.0,
    "feasibility": 75.0,
    "packaging": 93.0
  },
  "topic_type": "Historical explanation / Aviation Strategy",
  "recommended_format": "BOTH",
  "primary_angle": "The hidden strategic reason one bomber could not do every job.",
  "alternative_angles": [
    "Why WWII American bombers solved a crisis everyone ignored",
    "The hidden truth behind WWII American bombers",
    "How one fatal design flaw redefined WWII American bombers"
  ],
  "viewer_question": "Why did America need the B-24 when it already had the legendary B-17?",
  "content_gap_reason": "Competitors compare technical specs; our version uncovers theater doctrine and production tradeoffs.",
  "timing_action": "EVERGREEN",
  "production_effort": "HIGH",
  "risk_status": "CLEAR_WITH_CAUTION",
  "reason": "Strong demand, exceptional curiosity, verified historical sources, and massive topic cluster potential.",
  "next_action": "HANDOFF_TO_SCRIPT_AGENT",
  "handoff_agent": "Script Agent"
}
```
