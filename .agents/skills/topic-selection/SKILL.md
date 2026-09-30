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
Extract: `topic`, `primary_keyword`, `related_keywords`, `search_signals`, `competitors`, `audience_signals`, `content_gaps`, `existing_angles`, `sources`, `research_confidence`, `channel_context`.
If necessary fields are missing, mark them `UNKNOWN`. Do NOT invent values.

### STEP 2 — VALIDATE
Check factual basis, source availability, clarity, audience relevance, and content depth. Return: `VALID`, `VALID_WITH_REFRAMING`, `INSUFFICIENT`, `UNVERIFIED`, `SKIP`.

### STEP 3 — DEMAND ANALYSIS
Evaluate primary & related keyword demand, trend movement, topic momentum, query diversity, evergreen value. Return `demand_score` (0–100) and `demand_reason`.

### STEP 4 — CURIOSITY ANALYSIS
Identify unanswered question, contradiction, mystery, surprise, hidden cause, unexpected outcome, comparison tension. Return `curiosity_score` (0–100) and `core_viewer_question`.

### STEP 5 — AUDIENCE FIT
Compare topic against `config/audience.json`. Return `audience_fit_score` (0–100).

### STEP 6 — COMPETITION
Analyze topic saturation, angle saturation, competitor quality, recency, view performance. Return `competition_opportunity_score` (0–100).

### STEP 7 — CONTENT GAP
Identify information, angle, visual, storytelling, and comparison gaps. Return `content_gap_score` (0–100) and answer *"Why would someone watch our version?"*.

### STEP 8 — DIFFERENTIATION
Classify as `FRESH`, `FRESH_WITH_ANGLE`, `MODERATELY_DIFFERENT`, `REPETITIVE`, `DUPLICATE`. Reframe if repetitive.

### STEP 9 — SERIES POTENTIAL
Identify content pillar, cluster, episodes, Shorts/Long-form expansions. Return `series_potential_score` (0–100).

### STEP 10 — FORMAT SELECTION
Select `SHORTS`, `LONG_FORM`, `BOTH`, `TEST_SHORT`, `SERIES`, or `WATCHLIST`.

### STEP 11 — TIMING
Classify freshness and assign timing action (`MAKE_NOW`, `MAKE_SOON`, `EVERGREEN`, `WAIT_FOR_EVENT`, `WATCH_TREND`, `SKIP`).

### STEP 12 — PRODUCTION FEASIBILITY
Evaluate research, visual, animation, editing, fact-check efforts and copyright risk. Return `LOW`, `MEDIUM`, `HIGH`, or `VERY_HIGH`.

### STEP 13 — PACKAGING POTENTIAL
Evaluate visual contrast, recognizable subject, curiosity gap in packaging. Return `packaging_score` (0–100).

### STEP 14 — SCORE
Apply dynamic weights from `config/scoring.json` to calculate total `opportunity_score`.

### STEP 15 — HARD GATES
Apply Hard Gates A through F (Evidence, Audience, Curiosity, Depth, Differentiation, Reliability).

### STEP 16 — REFRAME
Generate alternative angles if topic is viable but saturated.

### STEP 17 — BATCH OPTIMIZATION
Normalize, deduplicate, cluster, score, and build priority queue without adjacent repetitive topics.

### STEP 18 — FINAL DECISION
Return `MAKE_NOW`, `MAKE`, `REFRAME`, `TEST_SHORT`, `LONG_FORM`, `BOTH`, `SERIES`, `WATCHLIST`, `WAIT`, `NEED_MORE_RESEARCH`, or `SKIP`.

### STEP 19 — PRODUCTION HANDOFF
Generate handoff object for Script Agent.
