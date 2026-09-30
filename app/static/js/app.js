// Main Frontend Application Logic for 5-Stage Agent Pipeline
let radarChartInstance = null;
let currentLoadedPacket = null;
let currentPipelineData = null;

// Initialize Application
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

  // Highlight header pipeline nodes
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

  // Open HUD Modal
  openPipelineModal();
  const bar = document.getElementById('pipeline-progress-bar');
  const sub = document.getElementById('pipeline-status-sub');
  
  // Reset HUD
  bar.style.width = '15%';
  sub.innerText = `Analyzing: "${currentLoadedPacket.topic_name}"`;

  setHudBadge('hud-stage-2-badge', 'RUNNING...', 'rgba(6,182,212,0.2)', 'var(--cyan-glow)');
  setHudBadge('hud-stage-3-badge', 'WAITING', 'rgba(255,255,255,0.05)', 'var(--text-muted)');
  setHudBadge('hud-stage-4-badge', 'WAITING', 'rgba(255,255,255,0.05)', 'var(--text-muted)');
  setHudBadge('hud-stage-5-badge', 'WAITING', 'rgba(255,255,255,0.05)', 'var(--text-muted)');

  try {
    const res = await fetch('/api/pipeline/run-full', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(currentLoadedPacket)
    });

    const data = await res.json();
    currentPipelineData = data;

    // Simulate animated stage-by-stage progression
    await delay(300);
    bar.style.width = '35%';
    setHudBadge('hud-stage-2-badge', `✓ ${data.decision.decision}`, 'rgba(16,185,129,0.2)', 'var(--emerald-glow)');
    renderDecisionUI(data.decision, data.handoff);

    if (data.story) {
      await delay(350);
      bar.style.width = '60%';
      setHudBadge('hud-stage-3-badge', '✓ 5 BEATS BUILT', 'rgba(16,185,129,0.2)', 'var(--emerald-glow)');
      renderStoryUI(data.story);
    }

    if (data.script) {
      await delay(350);
      bar.style.width = '85%';
      setHudBadge('hud-stage-4-badge', `✓ ${data.script.total_word_count} WORDS`, 'rgba(16,185,129,0.2)', 'var(--emerald-glow)');
      renderScriptUI(data.script);
    }

    if (data.packaging) {
      await delay(300);
      bar.style.width = '100%';
      setHudBadge('hud-stage-5-badge', '✓ 5 TITLES & SEO', 'rgba(16,185,129,0.2)', 'var(--emerald-glow)');
      renderPackagingUI(data.packaging);
    }

    sub.innerText = '⚡ Pipeline Execution Complete! All 5 Stages Ready.';
    
    // Light up all header stepper nodes
    for (let i = 2; i <= 5; i++) {
      const el = document.getElementById(`pipe-node-${i}`);
      if (el) el.className = 'pipeline-node done';
    }

    lucide.createIcons();
  } catch (err) {
    console.error('Pipeline execution failed:', err);
    sub.innerText = '⚠️ Pipeline execution error.';
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

// Render Stage 2: Decision UI
function renderDecisionUI(dec, handoff) {
  document.getElementById('display-topic-title').innerText = dec.topic;
  document.getElementById('display-topic-category').innerText = `${dec.topic_type} • Confidence: ${dec.confidence}%`;

  const scoreValEl = document.getElementById('hero-score-val');
  scoreValEl.innerText = dec.score;
  const progressCircle = document.getElementById('score-progress-ring');
  const circumference = 440;
  const offset = circumference - (dec.score / 100) * circumference;
  progressCircle.style.strokeDashoffset = offset;

  const badgeEl = document.getElementById('hero-decision-badge');
  badgeEl.className = `badge-decision badge-${dec.decision}`;
  badgeEl.innerText = dec.decision.replace('_', ' ');

  if (window.threeScene) {
    window.threeScene.setDecisionTheme(dec.decision);
  }

  updateRadarChart(dec.scores);
  renderHardGates(dec);

  document.getElementById('primary-angle-text').innerText = dec.primary_angle;
  document.getElementById('core-viewer-question').innerText = `"${dec.viewer_question}"`;
  document.getElementById('content-gap-text').innerText = dec.content_gap_reason;

  const altContainer = document.getElementById('alt-angles-container');
  altContainer.innerHTML = '';
  dec.alternative_angles.forEach((alt, i) => {
    const box = document.createElement('div');
    box.className = 'angle-box alt';
    box.innerHTML = `
      <div class="angle-label">Alternative Angle #${i + 1}</div>
      <div class="angle-text">${alt}</div>
    `;
    altContainer.appendChild(box);
  });

  document.getElementById('meta-format-badge').innerText = dec.recommended_format;
  document.getElementById('meta-timing-badge').innerText = dec.timing_action;
  document.getElementById('meta-effort-badge').innerText = dec.production_effort;
  document.getElementById('meta-reason-text').innerText = dec.reason;
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

// Render Stage 3: Story Dev UI
function renderStoryUI(story) {
  document.getElementById('story-thesis-text').innerText = story.core_thesis;
  document.getElementById('story-hook-text').innerText = story.hook_promise;

  const beatsContainer = document.getElementById('story-beats-container');
  beatsContainer.innerHTML = '';

  story.narrative_arc.forEach(b => {
    const card = document.createElement('div');
    card.className = 'glass-card';
    card.style.padding = '1rem';
    card.style.borderLeft = '3px solid var(--cyan-glow)';
    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
        <span style="font-weight:700; color:#fff; font-size:0.95rem;">Beat #${b.beat_number}: ${b.title}</span>
        <span class="badge-decision" style="font-size:0.7rem; padding:0.15rem 0.6rem; background:rgba(245,158,11,0.2); color:var(--amber-glow); border:1px solid var(--amber-glow);">
          ⚡ Tension: ${b.tension_level}/10
        </span>
      </div>
      <div style="font-size:0.85rem; color:#e2e8f0; margin-bottom:0.4rem;"><strong>Goal:</strong> ${b.narrative_goal}</div>
      <div style="font-size:0.82rem; color:#38bdf8; margin-bottom:0.4rem;"><strong>Key Revelation:</strong> ${b.key_revelation}</div>
      <div style="font-size:0.75rem; color:var(--text-muted); font-style:italic;"><strong>Visual Anchor:</strong> ${b.visual_anchor}</div>
    `;
    beatsContainer.appendChild(card);
  });
}

// Render Stage 4: Script UI
function renderScriptUI(script) {
  document.getElementById('script-duration').innerText = script.estimated_duration;
  document.getElementById('script-words').innerText = `${script.total_word_count} Words`;

  const container = document.getElementById('script-scenes-container');
  container.innerHTML = '';

  script.scenes.forEach(s => {
    const row = document.createElement('div');
    row.className = 'glass-card';
    row.style.padding = '1.2rem';
    row.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; padding-bottom:0.5rem; border-bottom:1px solid var(--border-subtle);">
        <span style="font-weight:700; color:#fff; font-size:0.9rem;">Scene ${s.scene_number}: ${s.section_title}</span>
        <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--cyan-glow); background:rgba(6,182,212,0.1); padding:0.2rem 0.6rem; border-radius:6px;">
          ⏱️ ${s.timestamp_estimate}
        </span>
      </div>
      <div style="display:grid; grid-template-columns: 1fr 1.2fr; gap:1.25rem;">
        <div>
          <div style="font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:0.2rem;">Visual Direction</div>
          <div style="font-size:0.8rem; color:#94a3b8; font-style:italic; margin-bottom:0.6rem;">${s.visual_direction}</div>
          <div style="font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:0.2rem;">SFX & Audio Track</div>
          <div style="font-size:0.78rem; color:#a855f7;">${s.audio_sfx}</div>
        </div>
        <div style="background:rgba(0,0,0,0.3); padding:0.85rem; border-radius:8px; border:1px solid var(--border-subtle);">
          <div style="font-size:0.72rem; color:var(--cyan-glow); text-transform:uppercase; font-weight:700; margin-bottom:0.3rem;">🎙️ Voiceover Script</div>
          <div style="font-size:0.88rem; color:#f1f5f9; line-height:1.5;">${s.voiceover_script}</div>
        </div>
      </div>
    `;
    container.appendChild(row);
  });
}

function copyFullScript() {
  if (!currentPipelineData || !currentPipelineData.script) return;
  const script = currentPipelineData.script;
  let text = `TOPIC: ${script.topic}\nDURATION: ${script.estimated_duration}\nWORD COUNT: ${script.total_word_count}\n\n`;
  script.scenes.forEach(s => {
    text += `[${s.timestamp_estimate}] SCENE ${s.scene_number}: ${s.section_title}\n`;
    text += `VISUAL: ${s.visual_direction}\n`;
    text += `AUDIO: ${s.audio_sfx}\n`;
    text += `VOICEOVER: ${s.voiceover_script}\n\n`;
  });

  navigator.clipboard.writeText(text).then(() => {
    alert('📋 Full Production Script copied to clipboard!');
  });
}

// Render Stage 5: Packaging UI
function renderPackagingUI(pkg) {
  // Titles
  const titlesContainer = document.getElementById('packaging-titles-container');
  titlesContainer.innerHTML = '';
  pkg.titles.forEach((t, i) => {
    const card = document.createElement('div');
    card.className = 'angle-box';
    card.style.display = 'flex';
    card.style.justifyContent = 'space-between';
    card.style.alignItems = 'center';
    card.innerHTML = `
      <div>
        <div class="angle-label">${t.formula_type} Formula</div>
        <div style="font-size:0.95rem; font-weight:700; color:#fff;">${t.title}</div>
        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.2rem;">${t.rationale}</div>
      </div>
      <div class="badge-decision" style="font-size:0.75rem; padding:0.2rem 0.7rem; background:rgba(16,185,129,0.2); color:var(--emerald-glow); border:1px solid var(--emerald-glow);">
        ${t.predicted_ctr} CTR
      </div>
    `;
    titlesContainer.appendChild(card);
  });

  // Thumbnails
  const thumbsContainer = document.getElementById('packaging-thumbnails-container');
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

  // Description & Tags
  document.getElementById('packaging-seo-desc').value = pkg.seo_description;
  const tagsContainer = document.getElementById('packaging-tags-container');
  tagsContainer.innerHTML = '';
  pkg.tags.forEach(tag => {
    const tagSpan = document.createElement('span');
    tagSpan.style.cssText = 'background:rgba(255,255,255,0.06); padding:0.2rem 0.5rem; border-radius:4px; font-size:0.72rem; color:#94a3b8; border:1px solid var(--border-subtle);';
    tagSpan.innerText = `#${tag}`;
    tagsContainer.appendChild(tagSpan);
  });

  document.getElementById('packaging-pinned-comment').innerText = pkg.pinned_comment_prompt;
}

// Chart.js Radar Initialization
function initRadarChart() {
  const ctx = document.getElementById('radarChart');
  if (!ctx) return;

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: [
        'Demand (20%)',
        'Curiosity (15%)',
        'Audience (15%)',
        'Competition Opp (15%)',
        'Content Gap (10%)',
        'Series (10%)',
        'Format (5%)',
        'Timing (5%)',
        'Feasibility (3%)',
        'Packaging (2%)'
      ],
      datasets: [{
        label: 'Candidate Score',
        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
          pointLabels: { color: '#94a3b8', font: { size: 10, family: 'Inter' } }
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

    document.getElementById(`count-${col.toLowerCase()}`).innerText = items.length;

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

    alert('✅ Configurations updated successfully!');
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
    related_keywords: [keyword, `${keyword} explained`, `${keyword} mystery`],
    search_demand_score: demand,
    trend_momentum: 75.0,
    competitor_examples: [],
    competitor_saturation_level: 50.0,
    audience_signals: [`Why is ${keyword} so significant?`],
    content_gaps: [`Comprehensive breakdown of ${keyword} from a fresh strategic angle.`],
    existing_angles: [`The untold story behind ${keyword}.`],
    topic_category: category,
    related_topics: [],
    potential_series_ideas: [`The ${category} Chronicles`],
    source_links: ["https://wikipedia.org"],
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
