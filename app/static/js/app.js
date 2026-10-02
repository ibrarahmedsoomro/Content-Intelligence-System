// Content Intelligence System - 5-Stage Agent Pipeline with Story Intelligence & 11-Check QA
let radarChartInstance = null;
let currentLoadedPacket = null;
let currentPipelineData = null;

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  loadResearchPackets();
  loadConfigs();
  initRadarChart();
});

// Tab Switching
function initTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.getAttribute('data-tab');
      switchStageTab(targetId);
    });
  });
}

function switchStageTab(targetId) {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');

  const activeTab = document.querySelector(`.tab-btn[data-tab="${targetId}"]`);
  if (activeTab) activeTab.classList.add('active');

  const targetEl = document.getElementById(targetId);
  if (targetEl) targetEl.style.display = 'block';

  updateHeaderStepper(targetId);

  if (targetId === 'tab-batch') {
    runBatchEvaluation();
  }
}

function updateHeaderStepper(currentTabId) {
  const nodeMap = {
    'tab-creator': 1,
    'tab-studio': 2,
    'tab-story': 3,
    'tab-script': 4,
    'tab-packaging': 5
  };

  const activeStage = nodeMap[currentTabId] || 2;
  for (let i = 2; i <= 5; i++) {
    const el = document.getElementById(`pipe-node-${i}`);
    if (!el) continue;
    if (i < activeStage) {
      el.className = 'pipeline-node done';
    } else if (i === activeStage) {
      el.className = 'pipeline-node active';
    } else {
      el.className = 'pipeline-node';
    }
  }
}

// Fetch Candidate Research Packets
async function loadResearchPackets() {
  try {
    const res = await fetch('/api/research/list');
    const packets = await res.json();
    const container = document.getElementById('candidates-list');
    container.innerHTML = '';

    packets.forEach((p, idx) => {
      const item = document.createElement('div');
      item.className = `candidate-item ${idx === 0 ? 'selected' : ''}`;
      item.innerHTML = `
        <div class="candidate-title">${p.topic_name}</div>
        <div class="candidate-meta">
          <span>${p.category}</span>
          <span>Demand: ${p.demand} | Conf: ${p.confidence}%</span>
        </div>
      `;
      item.addEventListener('click', () => {
        document.querySelectorAll('.candidate-item').forEach(c => c.classList.remove('selected'));
        item.classList.add('selected');
        loadSinglePacket(p.filename);
      });
      container.appendChild(item);
    });

    if (packets.length > 0) {
      loadSinglePacket(packets[0].filename);
    }
  } catch (err) {
    console.error('Failed to load research packets:', err);
  }
}

// Load and evaluate a single packet
async function loadSinglePacket(filename) {
  try {
    const res = await fetch(`/api/research/${filename}`);
    const packet = await res.json();
    currentLoadedPacket = packet;
    runFullPipelineForCurrentTopic();
  } catch (err) {
    console.error('Failed to load packet details:', err);
  }
}

// Modal controls
function openPipelineModal() {
  const m = document.getElementById('pipeline-modal');
  if (m) m.classList.add('open');
}

function closePipelineModal() {
  const m = document.getElementById('pipeline-modal');
  if (m) m.classList.remove('open');
}

function jumpToStageFromModal(tabId) {
  closePipelineModal();
  switchStageTab(tabId);
}

// Master Action: Execute full 5-stage pipeline with live animated HUD
async function runFullPipelineForCurrentTopic() {
  if (!currentLoadedPacket) {
    const list = document.querySelectorAll('.candidate-item');
    if (list.length > 0) {
      list[0].click();
      return;
    }
  }

  openPipelineModal();
  const bar = document.getElementById('pipeline-progress-bar');
  const sub = document.getElementById('pipeline-status-sub');
  
  bar.style.width = '15%';
  sub.innerText = `Analyzing: "${currentLoadedPacket.topic_name}"`;

  setHudBadge('hud-stage-2-badge', 'EVALUATING 12D...', 'rgba(6,182,212,0.2)', 'var(--cyan-glow)');
  setHudBadge('hud-stage-3-badge', 'WAITING', 'rgba(255,255,255,0.05)', 'var(--text-muted)');
  setHudBadge('hud-stage-4-badge', 'WAITING', 'rgba(255,255,255,0.05)', 'var(--text-muted)');
  setHudBadge('hud-stage-5-badge', 'WAITING', 'rgba(255,255,255,0.05)', 'var(--text-muted)');

  try {
    const res = await fetch('/api/pipeline/run-full', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(currentLoadedPacket)
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Server returned ${res.status}: ${errText}`);
    }

    const data = await res.json();
    currentPipelineData = data;

    await delay(250);
    bar.style.width = '35%';
    setHudBadge('hud-stage-2-badge', `✓ ${data.decision.decision} (${data.topic_opportunity_score}/100)`, 'rgba(16,185,129,0.2)', 'var(--emerald-glow)');
    renderDecisionUI(data.decision, data.handoff, data);

    if (data.story) {
      await delay(300);
      bar.style.width = '60%';
      setHudBadge('hud-stage-3-badge', `✓ STORY: ${data.story_intelligence_score}/100`, 'rgba(16,185,129,0.2)', 'var(--emerald-glow)');
      renderStoryUI(data.story, data.handoff, data);
    }

    if (data.script) {
      await delay(300);
      bar.style.width = '85%';
      const qScore = data.script_quality_score ?? data.script.qa_report.script_quality_score;
      setHudBadge('hud-stage-4-badge', `✓ SCRIPT: ${qScore}/100 (${data.script.qa_report.qa_verdict})`, 'rgba(16,185,129,0.2)', 'var(--emerald-glow)');
      renderScriptUI(data.script, data);
    }

    if (data.packaging) {
      await delay(250);
      bar.style.width = '100%';
      setHudBadge('hud-stage-5-badge', '✓ 5 TITLES & AI PROMPTS', 'rgba(16,185,129,0.2)', 'var(--emerald-glow)');
      renderPackagingUI(data.packaging);
    }

    sub.innerText = '⚡ Pipeline Execution Complete! All 5 Stages Ready.';
    
    for (let i = 2; i <= 5; i++) {
      const el = document.getElementById(`pipe-node-${i}`);
      if (el) el.className = 'pipeline-node done';
    }

    if (window.lucide) {
      lucide.createIcons();
    }
  } catch (err) {
    console.error('Pipeline execution failed:', err);
    sub.innerText = `⚠️ Pipeline error: ${err.message || 'Execution failed'}`;
  }
}

function setHudBadge(elId, text, bg, color) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.innerText = text;
  el.style.background = bg;
  el.style.color = color;
  el.style.borderColor = color;
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function advanceToNextStage(tabId) {
  switchStageTab(tabId);
}

// Render Stage 2: Decision UI (12 Dimensions)
function renderDecisionUI(dec, handoff, pipelineData) {
  try {
    const topicEl = document.getElementById('display-topic-title');
    if (topicEl) topicEl.innerText = dec.topic || 'Untitled Topic';

    const catEl = document.getElementById('display-topic-category');
    if (catEl) catEl.innerText = `${dec.topic_type || 'General'} • Confidence: ${dec.confidence ?? 80}%`;

    const scoreNum = dec.topic_opportunity_score ?? dec.score ?? 0;
    const scoreValEl = document.getElementById('hero-score-val');
    if (scoreValEl) scoreValEl.innerText = scoreNum;

    const progressCircle = document.getElementById('score-progress-ring');
    if (progressCircle) {
      const circumference = 440;
      const offset = circumference - (Math.min(100, Math.max(0, scoreNum)) / 100) * circumference;
      progressCircle.style.strokeDashoffset = isNaN(offset) ? 0 : offset;
    }

    const badgeEl = document.getElementById('hero-decision-badge');
    if (badgeEl) {
      const decStr = dec.decision || 'PENDING';
      badgeEl.className = `badge-decision badge-${decStr}`;
      badgeEl.innerText = decStr.replace('_', ' ');
    }

    if (window.threeScene && dec.decision) {
      window.threeScene.setDecisionTheme(dec.decision);
    }

    if (dec.scores) {
      updateRadarChart(dec.scores);
      renderHardGates(dec);
    }

    const primaryAngleEl = document.getElementById('primary-angle-text');
    if (primaryAngleEl) primaryAngleEl.innerText = dec.primary_angle || 'Strategic Tradeoff Analysis';

    const viewerQEl = document.getElementById('core-viewer-question');
    if (viewerQEl) viewerQEl.innerText = `"${dec.viewer_question || 'What is the real causation?'}"`;

    const gapEl = document.getElementById('content-gap-text');
    if (gapEl) gapEl.innerText = dec.content_gap_reason || 'Presents documented evidence missing from competitor coverage.';

    const altContainer = document.getElementById('alt-angles-container');
    if (altContainer) {
      altContainer.innerHTML = '';
      (dec.alternative_angles || []).forEach((alt, i) => {
        const box = document.createElement('div');
        box.className = 'angle-box alt';
        box.innerHTML = `
          <div class="angle-label">Alternative Angle #${i + 1}</div>
          <div class="angle-text">${alt}</div>
        `;
        altContainer.appendChild(box);
      });
    }

    const fmtBadge = document.getElementById('meta-format-badge');
    if (fmtBadge) fmtBadge.innerText = dec.recommended_format || 'LONG_FORM';

    const timingBadge = document.getElementById('meta-timing-badge');
    if (timingBadge) timingBadge.innerText = dec.timing_action || 'EVERGREEN';

    const effortBadge = document.getElementById('meta-effort-badge');
    if (effortBadge) effortBadge.innerText = dec.production_effort || 'MEDIUM';

    const reasonEl = document.getElementById('meta-reason-text');
    if (reasonEl) reasonEl.innerText = dec.reason || '-';
  } catch (err) {
    console.error('Error rendering Decision UI:', err);
  }
}

// Render Hard Gates status
function renderHardGates(dec) {
  const gates = [
    { name: 'Gate A: Evidence', pass: dec.confidence >= 60 },
    { name: 'Gate B: Audience', pass: dec.scores.audience_fit >= 40 },
    { name: 'Gate C: Curiosity', pass: dec.scores.curiosity >= 35 },
    { name: 'Gate D: Content Gap', pass: dec.scores.content_gap >= 30 },
    { name: 'Gate E: Depth/Format', pass: dec.scores.format_fit >= 60 },
    { name: 'Gate F: Fact Check', pass: dec.validation === 'VALID' }
  ];

  const container = document.getElementById('hard-gates-container');
  container.innerHTML = '';
  gates.forEach(g => {
    const pill = document.createElement('div');
    pill.className = `gate-pill ${g.pass ? 'pass' : 'fail'}`;
    pill.innerHTML = `
      <span>${g.name}</span>
      <strong>${g.pass ? '✓ PASS' : '✗ FAIL'}</strong>
    `;
    container.appendChild(pill);
  });
}

// Render Stage 3: Story Dev UI (Story Intelligence Blueprint)
function renderStoryUI(story, handoff, pipelineData) {
  try {
    const thesisEl = document.getElementById('story-thesis-text');
    if (thesisEl) thesisEl.innerText = story.core_thesis || 'Thesis generated.';

    const hookEl = document.getElementById('story-hook-text');
    if (hookEl) hookEl.innerText = `Target: ${story.payoff_target || 'Resolve primary contradiction'}`;

    // Render Archetype & Contamination Status Banner
    const storyBanner = document.getElementById('story-archetype-banner');
    if (storyBanner) {
      const arch = story.archetype || 'GENERAL_DOCUMENTARY';
      const isContaminated = story.contamination_check ? story.contamination_check.contamination_detected : false;
      const contamScore = story.contamination_check ? story.contamination_check.score : 0;
      const assump = story.audience_assumption || {};

      storyBanner.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(0,0,0,0.35); border:1px solid var(--border-subtle); border-radius:10px; padding:0.85rem 1.25rem; margin-bottom:1.25rem;">
          <div style="display:flex; gap:1.25rem; align-items:center;">
            <div>
              <span style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Story Archetype:</span>
              <div style="font-weight:700; color:var(--purple-glow); font-size:0.9rem;">🏛️ ${arch}</div>
            </div>
            <div style="border-left:1px solid var(--border-subtle); padding-left:1.25rem;">
              <span style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Template Contamination:</span>
              <div style="font-weight:700; color:${isContaminated ? 'var(--rose-glow)' : 'var(--emerald-glow)'}; font-size:0.9rem;">
                ${isContaminated ? `⚠️ ${contamScore}% Contamination` : '✓ 0% Contamination (Clean)'}
              </div>
            </div>
            <div style="border-left:1px solid var(--border-subtle); padding-left:1.25rem;">
              <span style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase;">Audience Assumption Source:</span>
              <div style="font-weight:700; color:var(--cyan-glow); font-size:0.85rem;">
                ${assump.source_type || 'POPULAR_NARRATIVE'} (${assump.confidence || 85}%)
              </div>
            </div>
          </div>
          <span class="badge-decision" style="font-size:0.75rem; padding:0.25rem 0.8rem; background:rgba(6,182,212,0.15); color:var(--cyan-glow); border:1px solid var(--cyan-glow); margin:0;">
            Story Intelligence: ${story.overall_story_intelligence_score}/100
          </span>
        </div>
      `;
    }

    // Render Open Loops Tracker Table with Entity Consistency & Payment Badges
    const loopsContainer = document.getElementById('story-loops-container');
    if (loopsContainer && story.open_loops) {
      loopsContainer.innerHTML = '';
      story.open_loops.forEach(l => {
        const row = document.createElement('div');
        const openedB = l.opened_at_beat ?? l.opened_beat ?? 1;
        const resolvedB = l.resolved_at_beat ?? l.resolved_beat ?? 5;
        const isConsistent = l.is_entity_consistent !== false;
        const resFacts = (l.resolution_fact_ids || []).join(', ');

        row.style.cssText = 'display:flex; justify-content:space-between; align-items:center; background:rgba(0,0,0,0.3); padding:0.6rem 0.85rem; border-radius:8px; border:1px solid var(--border-subtle); margin-bottom:0.5rem; font-size:0.8rem;';
        row.innerHTML = `
          <div>
            <strong style="color:var(--cyan-glow); font-family:var(--font-mono);">${l.loop_id}:</strong> 
            <span style="color:#cbd5e1; margin-left:0.3rem;">${l.question}</span>
            <div style="font-size:0.7rem; color:var(--text-muted); margin-top:0.2rem;">
              <span style="color:var(--emerald-glow);">Domain Verified: ${isConsistent ? '✓ Consistent' : '✗ Contaminated'}</span> | 
              <span>Resolution Facts: [${resFacts || 'FACT-001'}]</span>
            </div>
          </div>
          <div style="display:flex; gap:0.6rem; align-items:center;">
            <span style="font-size:0.7rem; color:var(--text-muted);">Beat ${openedB} ➔ Beat ${resolvedB}</span>
            <span class="badge-decision" style="font-size:0.68rem; padding:0.15rem 0.5rem; background:rgba(16,185,129,0.2); color:var(--emerald-glow); border:1px solid var(--emerald-glow); margin:0;">${l.status}</span>
          </div>
        `;
        loopsContainer.appendChild(row);
      });
    }

    // Render Beats with Beat Intelligence Score Breakdown & Dependency Audits
    const beatsContainer = document.getElementById('story-beats-container');
    if (beatsContainer && story.beats) {
      beatsContainer.innerHTML = '';

      story.beats.forEach(b => {
        const card = document.createElement('div');
        card.className = 'glass-card';
        card.style.padding = '1.25rem';
        card.style.borderLeft = '4px solid var(--cyan-glow)';
        
        const totalBeatScore = b.beat_score ? (b.beat_score.total_beat_score ?? 85) : 85;
        const depScore = b.narrative_dependency_score ?? 9;
        const rev = b.revelation || {};
        const infoGain = b.information_gain || {};
        const factIds = b.supporting_fact_ids || [];
        const loopIds = b.associated_open_loop_ids || [];
        const analogy = b.modern_analogy;

        card.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; padding-bottom:0.5rem; border-bottom:1px solid var(--border-subtle);">
            <div>
              <div style="font-size:0.7rem; font-family:var(--font-mono); color:var(--cyan-glow); text-transform:uppercase;">${b.slot_name || `BEAT #${b.beat_number}`}</div>
              <span style="font-weight:700; color:#fff; font-size:1rem;">Beat #${b.beat_number}: ${b.title}</span>
              <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.1rem;">${b.function_role || ''}</div>
            </div>
            <div style="display:flex; gap:0.5rem; align-items:center;">
              <span class="badge-decision" style="font-size:0.75rem; padding:0.2rem 0.7rem; background:rgba(6,182,212,0.15); color:var(--cyan-glow); border:1px solid var(--cyan-glow); margin:0;">
                ⚡ Beat Intelligence: ${totalBeatScore}/100
              </span>
              <span class="badge-decision" style="font-size:0.75rem; padding:0.2rem 0.7rem; background:rgba(245,158,11,0.15); color:var(--amber-glow); border:1px solid var(--amber-glow); margin:0;">
                Dependency: ${depScore}/10
              </span>
            </div>
          </div>

          <!-- Structured Revelation Box -->
          <div style="background:rgba(0,0,0,0.35); padding:0.85rem; border-radius:8px; border:1px solid var(--border-subtle); margin-bottom:0.75rem;">
            <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; color:var(--purple-glow); margin-bottom:0.3rem;">
              Structured Revelation Flow (Assumption ➔ Evidence ➔ Contradiction ➔ New Understanding)
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem; font-size:0.82rem;">
              <div><span style="color:var(--rose-glow); font-weight:700;">Premise / Assumption:</span> ${rev.assumption || 'Standard public view'}</div>
              <div><span style="color:var(--emerald-glow); font-weight:700;">Grounding Evidence:</span> ${rev.evidence || 'Documented records'}</div>
            </div>
            <div style="font-size:0.82rem; color:#f59e0b; margin-top:0.4rem;">
              <strong>Documented Contradiction:</strong> ${rev.contradiction || ''}
            </div>
            <div style="font-size:0.85rem; color:#38bdf8; margin-top:0.4rem; padding-top:0.4rem; border-top:1px dashed var(--border-subtle);">
              <strong>New Viewer Understanding:</strong> ${rev.new_understanding || 'Deeper strategic insight'}
            </div>
          </div>

          <!-- Modern Analogy Metadata if present -->
          ${analogy ? `
            <div style="background:rgba(244,63,94,0.08); border:1px solid rgba(244,63,94,0.25); border-radius:8px; padding:0.75rem; margin-bottom:0.75rem; font-size:0.75rem;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
                <strong style="color:var(--rose-glow);">🏷️ ${analogy.label} (${analogy.analogy_strength} Rigor)</strong>
                <span style="color:var(--text-muted);">${analogy.similarity_dimension}</span>
              </div>
              <div style="color:#cbd5e1; line-height:1.4;">
                <div><strong>Modern Analogy:</strong> ${analogy.modern_basis}</div>
                <div style="color:#94a3b8; font-size:0.7rem; margin-top:0.2rem;"><strong>Boundary Limitation:</strong> ${analogy.boundary_limit}</div>
              </div>
            </div>
          ` : ''}

          <!-- Information Gain Metric -->
          <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); padding:0.6rem 0.85rem; border-radius:6px; font-size:0.78rem; margin-bottom:0.5rem;">
            <div><strong style="color:var(--text-muted);">Information Gain:</strong> ${infoGain.genuine_change || 'Increases strategic clarity'}</div>
            <div style="display:flex; gap:0.4rem;">
              ${factIds.map(f => `<span style="background:rgba(6,182,212,0.2); color:var(--cyan-glow); padding:0.1rem 0.4rem; border-radius:4px; font-family:var(--font-mono); font-size:0.7rem;">${f}</span>`).join('')}
              ${loopIds.map(l => `<span style="background:rgba(139,92,246,0.2); color:var(--purple-glow); padding:0.1rem 0.4rem; border-radius:4px; font-family:var(--font-mono); font-size:0.7rem;">${l}</span>`).join('')}
            </div>
          </div>
        `;
        beatsContainer.appendChild(card);
      });
    }
  } catch (err) {
    console.error('Error rendering Story UI:', err);
  }
}

// Render Stage 4: Script UI (Traceable Scenes & 11-Check QA Report)
function renderScriptUI(script, pipelineData) {
  try {
    const durEl = document.getElementById('script-duration');
    if (durEl) durEl.innerText = script.estimated_duration || '8-10 Minutes';

    const wordsEl = document.getElementById('script-words');
    if (wordsEl) wordsEl.innerText = `${script.total_word_count || 1200} Words (${script.calculated_wpm || 145} WPM)`;

    // Render 11-Check QA Audit Matrix Banner
    const qaContainer = document.getElementById('script-qa-banner');
    if (qaContainer && script.qa_report) {
      const qa = script.qa_report;
      const matchScore = qa.promise_delivery ? (qa.promise_delivery.promise_match_score ?? 95) : 95;
      const scriptQuality = qa.script_quality_score ?? 92.5;
      const verdict = qa.qa_verdict || 'APPROVED_FOR_PRODUCTION';

      let verdictColor = 'var(--emerald-glow)';
      let verdictBg = 'rgba(16,185,129,0.2)';
      if (verdict === 'BLOCKED') {
        verdictColor = 'var(--rose-glow)';
        verdictBg = 'rgba(244,63,94,0.2)';
      } else if (verdict === 'REVISE_REQUIRED') {
        verdictColor = 'var(--amber-glow)';
        verdictBg = 'rgba(245,158,11,0.2)';
      }

      qaContainer.innerHTML = `
        <div style="background:rgba(0,0,0,0.4); border:1px solid var(--border-subtle); border-radius:12px; padding:1.25rem; margin-bottom:1.5rem;">
          <!-- Top QA Header -->
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; padding-bottom:0.75rem; border-bottom:1px solid var(--border-subtle);">
            <div style="display:flex; align-items:center; gap:0.75rem;">
              <span style="font-size:0.95rem; font-weight:700; color:#fff;">⚡ Production QA & Script Verification Matrix</span>
              <span class="badge-decision" style="font-size:0.75rem; padding:0.2rem 0.75rem; background:rgba(6,182,212,0.15); color:var(--cyan-glow); border:1px solid var(--cyan-glow); margin:0;">
                Script Quality Score: ${scriptQuality}/100
              </span>
            </div>
            <span class="badge-decision" style="font-size:0.75rem; padding:0.25rem 0.85rem; background:${verdictBg}; color:${verdictColor}; border:1px solid ${verdictColor}; margin:0;">
              ${verdict}
            </span>
          </div>

          <!-- 11-Check QA Audit Grid -->
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:0.6rem; margin-bottom:1rem;">
            ${(qa.checks || []).map(c => `
              <div style="background:rgba(255,255,255,0.03); border:1px solid ${c.status === 'PASS' ? 'rgba(16,185,129,0.25)' : (c.status === 'WARN' ? 'rgba(245,158,11,0.25)' : 'rgba(244,63,94,0.35)')}; border-radius:8px; padding:0.6rem 0.75rem; font-size:0.75rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                  <strong style="color:#f1f5f9;">${c.name}</strong>
                  <span style="font-size:0.68rem; font-weight:700; color:${c.status === 'PASS' ? 'var(--emerald-glow)' : (c.status === 'WARN' ? 'var(--amber-glow)' : 'var(--rose-glow)')};">
                    ${c.status === 'PASS' ? '✓ PASS' : (c.status === 'WARN' ? '⚠ WARN' : '✗ FAIL')}
                  </span>
                </div>
                <div style="color:var(--text-muted); font-size:0.7rem; line-height:1.3;">${c.details}</div>
                <div style="color:var(--cyan-glow); font-family:var(--font-mono); font-size:0.68rem; margin-top:0.25rem;">Value: ${c.calculated_value} (${c.threshold})</div>
              </div>
            `).join('')}
          </div>

          <!-- Promise Delivery Audit -->
          ${qa.promise_delivery ? `
            <div style="background:rgba(6,182,212,0.05); border:1px dashed var(--cyan-glow); border-radius:8px; padding:0.75rem 1rem; font-size:0.78rem;">
              <div style="font-weight:700; color:var(--cyan-glow); margin-bottom:0.3rem;">🎯 Promise-to-Delivery Verification: ${matchScore}% Alignment</div>
              <div style="color:#cbd5e1; line-height:1.4;">
                <strong>Story Thesis:</strong> ${qa.promise_delivery.title_promise || ''}<br>
                <strong>Delivery Payoff:</strong> ${qa.promise_delivery.script_delivery || ''}
              </div>
            </div>
          ` : ''}
        </div>
      `;
    }

    const container = document.getElementById('script-scenes-container');
    if (container && script.scenes) {
      container.innerHTML = '';

      script.scenes.forEach(s => {
        const row = document.createElement('div');
        row.className = 'glass-card';
        row.style.padding = '1.25rem';
        const facts = s.supporting_fact_ids || [];
        const loops = s.open_loop_ids || [];

        row.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; padding-bottom:0.5rem; border-bottom:1px solid var(--border-subtle);">
            <div style="display:flex; align-items:center; gap:0.6rem;">
              <span style="font-family:var(--font-mono); font-size:0.75rem; background:rgba(6,182,212,0.15); color:var(--cyan-glow); padding:0.2rem 0.5rem; border-radius:4px; font-weight:700;">${s.scene_id}</span>
              <span style="font-weight:700; color:#fff; font-size:0.92rem;">Scene ${s.scene_number}: ${s.section_title}</span>
            </div>
            <div style="display:flex; gap:0.5rem; align-items:center;">
              ${facts.map(f => `<span style="background:rgba(255,255,255,0.06); color:#94a3b8; font-family:var(--font-mono); font-size:0.7rem; padding:0.15rem 0.4rem; border-radius:4px;">${f}</span>`).join('')}
              ${loops.map(l => `<span style="background:rgba(139,92,246,0.2); color:var(--purple-glow); font-family:var(--font-mono); font-size:0.7rem; padding:0.15rem 0.4rem; border-radius:4px;">${l}</span>`).join('')}
              <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--cyan-glow); background:rgba(6,182,212,0.1); padding:0.2rem 0.6rem; border-radius:6px;">
                ⏱️ ${s.timestamp_estimate || '0:00 - 1:00'}
              </span>
            </div>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1.25fr; gap:1.25rem;">
            <div>
              <div style="font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:0.2rem;">Visual Direction</div>
              <div style="font-size:0.8rem; color:#94a3b8; font-style:italic; margin-bottom:0.6rem;">${s.visual_direction || ''}</div>
              <div style="font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:0.2rem;">SFX & Audio Track</div>
              <div style="font-size:0.78rem; color:#a855f7; margin-bottom:0.6rem;">${s.audio_sfx || ''}</div>
              ${s.retention_hook ? `
                <div style="background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.25); border-radius:6px; padding:0.4rem 0.6rem; font-size:0.72rem; color:var(--amber-glow);">
                  <strong>Retention Hook:</strong> ${s.retention_hook}
                </div>
              ` : ''}
            </div>
            <div style="background:rgba(0,0,0,0.3); padding:0.9rem; border-radius:8px; border:1px solid var(--border-subtle);">
              <div style="font-size:0.72rem; color:var(--cyan-glow); text-transform:uppercase; font-weight:700; margin-bottom:0.3rem;">🎙️ Grounded Voiceover Script</div>
              <div style="font-size:0.88rem; color:#f1f5f9; line-height:1.5;">${s.voiceover_script || ''}</div>
            </div>
          </div>
        `;
        container.appendChild(row);
      });
    }
  } catch (err) {
    console.error('Error rendering Script UI:', err);
  }
}

function copyFullScript() {
  if (!currentPipelineData || !currentPipelineData.script) return;
  const script = currentPipelineData.script;
  let text = `TOPIC: ${script.topic}\nDURATION: ${script.estimated_duration}\nWORD COUNT: ${script.total_word_count}\n\n`;
  (script.scenes || []).forEach(s => {
    text += `[${s.timestamp_estimate}] ${s.scene_id}: ${s.section_title}\n`;
    text += `VISUAL: ${s.visual_direction}\n`;
    text += `AUDIO: ${s.audio_sfx}\n`;
    text += `VOICEOVER: ${s.voiceover_script}\n\n`;
  });

  navigator.clipboard.writeText(text).then(() => {
    alert('📋 Grounded Production Script copied to clipboard!');
  });
}

function downloadProductionBundle() {
  if (!currentLoadedPacket) return;
  const slug = currentLoadedPacket.topic_name.toLowerCase().replace(/[^a-z0-9]/g, '-').slice(0, 35);
  window.open(`/api/export/${slug}/markdown`, '_blank');
}

// Render Stage 5: Packaging UI
function renderPackagingUI(pkg) {
  try {
    const titlesContainer = document.getElementById('packaging-titles-container');
    if (titlesContainer && pkg.titles) {
      titlesContainer.innerHTML = '';
      pkg.titles.forEach((t, i) => {
        const card = document.createElement('div');
        card.className = 'angle-box';
        card.style.display = 'flex';
        card.style.justifyContent = 'space-between';
        card.style.alignItems = 'center';
        card.innerHTML = `
          <div>
            <div class="angle-label">${t.formula_type || 'Curiosity'} Formula</div>
            <div style="font-size:0.95rem; font-weight:700; color:#fff;">${t.title}</div>
            <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.2rem;">${t.rationale || ''}</div>
          </div>
          <div class="badge-decision" style="font-size:0.75rem; padding:0.2rem 0.7rem; background:rgba(16,185,129,0.2); color:var(--emerald-glow); border:1px solid var(--emerald-glow);">
            ${t.predicted_ctr || 'High'} CTR
          </div>
        `;
        titlesContainer.appendChild(card);
      });
    }

    const thumbsContainer = document.getElementById('packaging-thumbnails-container');
    if (thumbsContainer && pkg.thumbnails) {
      thumbsContainer.innerHTML = '';
      pkg.thumbnails.forEach(th => {
        const card = document.createElement('div');
        card.className = 'glass-card';
        card.style.padding = '1rem';
        card.innerHTML = `
          <div style="font-size:0.85rem; font-weight:700; color:var(--purple-glow); margin-bottom:0.4rem;">${th.concept_name}</div>
          <div style="font-size:0.78rem; color:#e2e8f0; margin-bottom:0.5rem;"><strong>Layout:</strong> ${th.visual_layout}</div>
          <div style="font-size:0.75rem; color:var(--amber-glow); margin-bottom:0.5rem;"><strong>Text Overlay:</strong> <span style="background:rgba(245,158,11,0.2); padding:0.1rem 0.4rem; border-radius:4px; font-weight:700;">${th.text_overlay}</span></div>
          <div style="background:rgba(0,0,0,0.4); padding:0.6rem; border-radius:6px; font-size:0.7rem; font-family:var(--font-mono); color:#38bdf8;">
            <strong>Prompt:</strong> ${th.ai_image_prompt}
          </div>
        `;
        thumbsContainer.appendChild(card);
      });
    }

    const seoEl = document.getElementById('packaging-seo-desc');
    if (seoEl) seoEl.value = pkg.seo_description || '';

    const tagsContainer = document.getElementById('packaging-tags-container');
    if (tagsContainer && pkg.tags) {
      tagsContainer.innerHTML = '';
      pkg.tags.forEach(tag => {
        const tagSpan = document.createElement('span');
        tagSpan.style.cssText = 'background:rgba(255,255,255,0.06); padding:0.25rem 0.6rem; border-radius:4px; font-size:0.75rem; color:#e2e8f0; border:1px solid var(--border-subtle); font-family:var(--font-mono);';
        tagSpan.innerText = tag;
        tagsContainer.appendChild(tagSpan);
      });
    }

    const pinnedEl = document.getElementById('packaging-pinned-comment');
    if (pinnedEl) pinnedEl.innerText = pkg.pinned_comment_prompt || '-';
  } catch (err) {
    console.error('Error rendering Packaging UI:', err);
  }
}

// Chart.js Radar Initialization (12 Exact Dimensions)
function initRadarChart() {
  const ctx = document.getElementById('radarChart');
  if (!ctx) return;

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: [
        '1. Demand (18%)',
        '2. Curiosity (14%)',
        '3. Audience (13%)',
        '4. Competition (13%)',
        '5. Content Gap (10%)',
        '6. Series (8%)',
        '7. Evidence (8%)',
        '8. Payoff (6%)',
        '9. Format (4%)',
        '10. Timing (3%)',
        '11. Feasibility (2%)',
        '12. Packaging (1%)'
      ],
      datasets: [{
        label: 'Candidate Score',
        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        backgroundColor: 'rgba(6, 182, 212, 0.25)',
        borderColor: '#06b6d4',
        borderWidth: 2,
        pointBackgroundColor: '#8b5cf6',
        pointBorderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { display: false, stepSize: 20 },
          grid: { color: 'rgba(255, 255, 255, 0.08)' },
          angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
          pointLabels: { color: '#94a3b8', font: { size: 9, family: 'Inter' } }
        }
      },
      plugins: { legend: { display: false } }
    }
  });
}

function updateRadarChart(scores) {
  if (!radarChartInstance) return;
  radarChartInstance.data.datasets[0].data = [
    scores.demand,
    scores.curiosity,
    scores.audience_fit,
    scores.competition_opportunity,
    scores.content_gap,
    scores.series_potential,
    scores.evidence_strength,
    scores.narrative_payoff_potential,
    scores.format_fit,
    scores.timing,
    scores.feasibility,
    scores.packaging
  ];
  radarChartInstance.update();
}

// Batch Evaluation Runner
async function runBatchEvaluation() {
  const loadingEl = document.getElementById('batch-loading');
  if (loadingEl) loadingEl.style.display = 'block';

  try {
    const res = await fetch('/api/evaluate/batch', { method: 'POST' });
    const data = await res.json();
    renderKanban(data.queue);
  } catch (err) {
    console.error('Batch evaluation failed:', err);
  } finally {
    if (loadingEl) loadingEl.style.display = 'none';
  }
}

function renderKanban(queue) {
  const cols = ['NOW', 'NEXT', 'TEST', 'WATCHLIST', 'SKIP'];
  cols.forEach(col => {
    const container = document.getElementById(`kanban-col-${col.toLowerCase()}`);
    if (!container) return;
    container.innerHTML = '';
    const items = queue[col] || [];

    const countEl = document.getElementById(`count-${col.toLowerCase()}`);
    if (countEl) countEl.innerText = items.length;

    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'kanban-card';
      card.innerHTML = `
        <div style="font-size: 0.82rem; font-weight: 600; color: #fff; margin-bottom: 0.3rem;">${item.topic}</div>
        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #94a3b8;">
          <span style="color: #06b6d4; font-weight: 700;">Score: ${item.score}</span>
          <span>${item.recommended_format}</span>
        </div>
      `;
      card.addEventListener('click', () => {
        switchStageTab('tab-studio');
        loadSinglePacket(item.filename);
      });
      container.appendChild(card);
    });
  });
}

// Config Load & Save
async function loadConfigs() {
  try {
    const [resScoring, resAudience] = await Promise.all([
      fetch('/api/config/scoring'),
      fetch('/api/config/audience')
    ]);

    const scoring = await resScoring.json();
    const audience = await resAudience.json();

    document.getElementById('config-scoring-raw').value = JSON.stringify(scoring, null, 2);
    document.getElementById('config-audience-raw').value = JSON.stringify(audience, null, 2);
  } catch (err) {
    console.error('Failed to load configs:', err);
  }
}

async function saveConfigs() {
  try {
    const scoringRaw = document.getElementById('config-scoring-raw').value;
    const audienceRaw = document.getElementById('config-audience-raw').value;

    await Promise.all([
      fetch('/api/config/scoring', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: scoringRaw }),
      fetch('/api/config/audience', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: audienceRaw })
    ]);

    alert('✅ 12-Dimensional Configurations updated successfully!');
    if (currentLoadedPacket) {
      runFullPipelineForCurrentTopic();
    }
  } catch (err) {
    alert('Failed to save configs. Check JSON syntax.');
  }
}

// Quick New Topic Form Submission
async function submitNewTopic(e) {
  e.preventDefault();
  const title = document.getElementById('new-topic-title').value;
  const keyword = document.getElementById('new-topic-keyword').value;
  const category = document.getElementById('new-topic-category').value;
  const demand = parseFloat(document.getElementById('new-topic-demand').value) || 85;
  const curiosity = parseFloat(document.getElementById('new-topic-curiosity').value) || 90;
  const confidence = parseFloat(document.getElementById('new-topic-confidence').value) || 92;

  const newPacket = {
    topic_name: title,
    main_keyword: keyword,
    related_keywords: [keyword, `${keyword} doctrine`, `${keyword} history`],
    search_demand_score: demand,
    trend_momentum: 75.0,
    competitor_examples: [],
    competitor_saturation_level: 50.0,
    audience_signals: [`Why is ${keyword} so significant in military doctrine?`],
    content_gaps: [`Comprehensive breakdown of ${keyword} from a documented doctrinal angle.`],
    existing_angles: [`The operational tradeoffs behind ${keyword}.`],
    topic_category: category,
    related_topics: [],
    potential_series_ideas: [`The ${category} Chronicles`],
    source_links: ["https://nationalww2museum.org/archives"],
    research_confidence: confidence,
    curiosity_factor: curiosity,
    audience_fit_score: 88.0,
    depth_score: 80.0,
    visual_packaging_score: 90.0,
    is_factually_verified: true
  };

  await fetch('/api/research/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newPacket)
  });

  await loadResearchPackets();
  switchStageTab('tab-studio');
}
