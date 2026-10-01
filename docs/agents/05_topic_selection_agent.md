# #5 — TOPIC SELECTION & STORY INTELLIGENCE ARCHITECTURE
## Autonomous Content Intelligence, Decision Engine & Narrative Planning System

### 1. Complete Architecture Pipeline
```
┌──────────────────────────────┐
│       RESEARCH AGENT         │
│ Demand / Competition / Facts │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│   EVIDENCE & CLAIM ENGINE    │
│ Facts / Sources / Confidence │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│    TOPIC SELECTION AGENT     │
│ 12 Dimensions + Hard Gates   │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ CONTENT INTELLIGENCE LAYER   │
│ Contradiction / Gap / Angle  │
│ Curiosity / Information Gain │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      STORY DEV AGENT         │
│ Open Loops / Beats / Payoff  │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│    SCRIPT GENERATION AGENT   │
│ Scene / VO / Visual / SFX    │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       SCRIPT QA AGENT        │
│ Fact / Retention / Payoff    │
│ Repetition / Promise Match   │
└──────────────┬───────────────┘
               ↓
          PASS / REVISE
               ↓
┌──────────────────────────────┐
│       SEO + PACKAGING        │
│ Titles / Thumbnail / SEO     │
└──────────────────────────────┘
```

---

### 2. Exact 12-Dimensional Scoring Matrix (100% Total)

| # | Dimension | Weight | Operational Evaluation |
|---|---|:---:|---|
| 1 | **Search Demand** | **18%** | Search volume, historical stability, related query momentum |
| 2 | **Curiosity & Knowledge Gap** | **14%** | Immediate unanswered questions, surprise, and contradiction tension |
| 3 | **Audience & Channel Fit** | **13%** | Alignment with target demographics (13-35, UK/USA/Global) and tone |
| 4 | **Competition Opportunity** | **13%** | Market saturation separated from genuine unmet opportunity |
| 5 | **Content Gap & Differentiation** | **10%** | "Why watch our version over existing videos?" |
| 6 | **Series & Cluster Potential** | **8%** | Content pillar expandability and recurring video clusters |
| 7 | **Evidence Strength** | **8%** | Verified archival source density and research confidence |
| 8 | **Narrative / Payoff Potential** | **6%** | Depth to sustain curiosity through to the final revelation |
| 9 | **Format Suitability** | **4%** | Fast-paced Shorts vs in-depth Long-form documentary calibration |
| 10 | **Freshness & Timing** | **3%** | Evergreen consistency vs Trending momentum window |
| 11 | **Production Feasibility** | **2%** | Visual availability, 3D/animation complexity, fact check effort |
| 12 | **Packaging Potential** | **1%** | Recognizable visual subject, high contrast, instant focal point |
| **TOTAL** | **Opportunity Score** | **100%** | **Combined Weighted Score (0–100)** |

---

### 3. Stage 2 $\rightarrow$ Stage 3: Topic Intelligence Handoff Contract

Topic Selection Agent outputs the comprehensive `TopicIntelligenceHandoff` packet:
- **`core_facts`**: Fact Registry (`FACT-001`, `FACT-002`, `FACT-003`) with claim text, sources, and verification status.
- **`core_contradiction`**: What appears contradictory or unresolved.
- **`common_assumption`**: What the audience commonly assumes.
- **`evidence_base`**: Data that proves/disproves the assumption.
- **`content_gap`**: What existing coverage failed to address.
- **`unique_angle`**: Why this specific version must exist.
- **`primary_curiosity_question`** & **`secondary_questions`**.
- **`key_reveal`** & **`payoff_target`**.
- **`factual_risks`** & **`forbidden_claims`** (hard-blocks invented quotes or unverified conspiracy).
- **`visual_opportunities`** & **`packaging_promise`**.

---

### 4. Stage 3: Story Intelligence Blueprint & 100-Point Beat Score

Shallow "Tension 1-10" has been replaced with the **Beat Intelligence Scoring Model**:

$$\text{Beat Score} = (\text{Curiosity } 15\%) + (\text{Info Gain } 15\%) + (\text{Narrative Necessity } 15\%) + (\text{Evidence } 15\%) + (\text{Payoff } 10\%) + (\text{Novelty } 10\%) + (\text{Retention } 10\%) + (\text{Visual } 5\%) + (\text{Stakes } 5\%)$$

- **Tension:** Purely qualitative descriptive attribute (`LOW`, `MEDIUM`, `HIGH`, `EXTREME`).
- **Structured Revelation Blueprint:**
  $$\text{Assumption} \longrightarrow \text{Evidence} \longrightarrow \text{Contradiction} \longrightarrow \text{Explanation} \longrightarrow \text{New Understanding}$$
- **Information Gain Tracking:** Tracks *Viewer Knowledge Before* vs *Viewer Knowledge After* vs *Genuine Change*.
- **Narrative Dependency Metric (0–10):** Automatically identifies and eliminates padding beats.
- **Open-Loop Tracking (`LOOP-001`, `LOOP-002`):** Tracks opening, expansion, and resolution with a **Zero Unpaid Loops Rule** at the ending.
- **Drama Integrity Rule:** Hard-blocks sensational words (`secret`, `classified document reveals`, `dangerously incomplete`, `insurmountable`) unless directly grounded in registered facts.

---

### 5. Stage 4: Traceable Script & QA Promise-Delivery Audit

- Every scene (`SCENE-001` to `SCENE-005`) explicitly maps to `associated_beat_id`, `supporting_fact_ids` (`FACT-001`, `FACT-002`), `open_loop_ids`, and `payoff_contribution`.
- **Script QA Promise-Delivery Audit:**
  $$\text{Title Promise} \longrightarrow \text{Hook Promise} \longrightarrow \text{Story Promise} \longrightarrow \text{Script Delivery} \longrightarrow \text{Ending Payoff}$$
- Calculates Fact Coverage Rate (%), Unresolved Loops (0), Drama Integrity (Passed), and Promise Match Score (98%).

---

### 6. Stage 5: Packaging & SEO

- **5 High-CTR Title Formulas** (Curiosity, Structural Truth, Pivotal Moment, Extreme Constraint, Authority).
- **3 Visual Thumbnail Concepts** with Midjourney-ready AI prompts, color contrast, and text overlays.
- **YouTube SEO Description** with Chapters/Timestamps, 15 high-ranking tags, and Pinned Comment prompt.
