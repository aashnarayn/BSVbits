/* ==========================================================================
   BSVbits Studio — Frontend Application Logic
   Includes:
     - Monaco Editor with custom Bluespec SystemVerilog (BSV) language & snippets
     - Mode 1: Guided 32-Problem Progression (HDLBits style)
     - Mode 2: Dynamic Competitive Hardware Programming (CP Arena)
     - Interactive SVG Digital Waveform Renderer (CLK, Inputs, Ref, Yours, Mismatch)
     - BSC Rule Schedule, Conflict Matrix & Synthesized Verilog RTL Viewers
     - Smart Semantic AST / LLM Code Review & Progressive Clues
   ========================================================================== */

const appState = {
  username: 'default',
  platformMode: 'curriculum', // 'curriculum' | 'cp'
  editorMode: 'snippet',      // 'snippet' | 'full'
  curriculumTracks: [],
  curriculumSearchQuery: '',
  curriculumStatusFilter: 'all', // 'all' | 'unsolved' | 'solved' | 'combo'
  collapsedTracks: {},
  cpCategories: [],
  cpQuestionFormats: [],
  solvedCurriculum: [],
  totalCurriculum: 342,
  cpRating: 1200,
  cpStreak: 0,
  dailyStreak: 0,
  activeSession: null,
  cpHistory: [],
  activeProblem: null,
  lastEvaluation: null,
  activeWorkbenchTab: 'wave',
  unlockedClueLevel: -1,
  monacoEditor: null,
  useFallbackEditor: false,
  timerSeconds: 0,
  timerInterval: null,
  cpDifficultyFilter: 'Medium',
  cpCategoryFilter: 'all',
  cpFormatFilter: 'all',
  cpTimeBudget: 20,
  cpTimeBudgetMin: 20,
  cpSessionCount: 0, // 0 = Auto-fit to time
  llmConfig: {
    apiKey: localStorage.getItem('bsvbits_llm_key') || '',
    apiBase: localStorage.getItem('bsvbits_llm_base') || 'https://api.openai.com/v1',
    model: localStorage.getItem('bsvbits_llm_model') || 'gpt-4o-mini',
  },
};

// Initialize Editor + Fetch Initial Platform State
window.addEventListener('DOMContentLoaded', async () => {
  initEditorEngine();
  startSpeedrunTimer();
  await loadInitialData();

  // Keyboard shortcut Ctrl+Enter / Cmd+Enter to compile & co-simulate
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      submitToBsc();
    }
  });
});

function initEditorEngine() {
  const fallback = document.getElementById('fallback-editor');
  const mount = document.getElementById('monaco-mount');

  if (typeof window.require === 'undefined') {
    enableFallbackEditor();
    return;
  }

  try {
    window.require.config({
      paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' },
    });
    window.require(['vs/editor/editor.main'], () => {
      registerBsvLanguageInMonaco(window.monaco);
      appState.monacoEditor = window.monaco.editor.create(mount, {
        value: '// Loading BSVbits...',
        language: 'bsv',
        theme: 'bsv-dark',
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        fontSize: 13.5,
        lineHeight: 21,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 4,
        insertSpaces: true,
        padding: { top: 12, bottom: 12 },
      });

      if (appState.activeProblem) {
        setEditorValue(appState.activeProblem.active_code || '');
      }
    }, () => {
      enableFallbackEditor();
    });
  } catch (err) {
    enableFallbackEditor();
  }
}

function enableFallbackEditor() {
  appState.useFallbackEditor = true;
  document.getElementById('monaco-mount').style.display = 'none';
  const fb = document.getElementById('fallback-editor');
  fb.style.display = 'block';
  if (appState.activeProblem) {
    fb.value = appState.activeProblem.active_code || '';
  }
}

function registerBsvLanguageInMonaco(monaco) {
  monaco.languages.register({ id: 'bsv' });
  monaco.languages.setMonarchTokensProvider('bsv', {
    keywords: [
      'package', 'endpackage', 'import', 'export', 'module', 'endmodule',
      'interface', 'endinterface', 'rule', 'endrule', 'method', 'endmethod',
      'function', 'endfunction', 'typedef', 'struct', 'enum', 'tagged',
      'union', 'deriving', 'provisos', 'begin', 'end', 'if', 'else',
      'case', 'endcase', 'default', 'for', 'while', 'seq', 'endseq',
      'par', 'endpar', 'return', 'let', 'matches', 'valueOf', 'fromInteger',
      'zeroExtend', 'signExtend', 'truncate', 'pack', 'unpack', 'isValid',
      'fromMaybe', 'replicateM',
    ],
    typeKeywords: [
      'Bit', 'UInt', 'Int', 'Bool', 'Integer', 'Empty', 'Action', 'ActionValue',
      'Reg', 'Ehr', 'FIFO', 'FIFOF', 'Vector', 'Maybe', 'Valid', 'Invalid',
      'True', 'False', 'RWire', 'PulseWire', 'Stmt', 'FSM',
    ],
    tokenizer: {
      root: [
        [/\/\/.*$/, 'comment'],
        [/\/\*/, 'comment', '@comment'],
        [/\(\*.*?\*\)/, 'annotation'],
        [/\b\d+'[bBhHdDoO][0-9a-fA-F_xXzZ]+\b/, 'number.hex'],
        [/\b\d+\b/, 'number'],
        [/[A-Z][\w$]*/, {
          cases: {
            '@typeKeywords': 'type.identifier',
            '@default': 'type.identifier',
          },
        }],
        [/[a-z_$][\w$]*/, {
          cases: {
            '@keywords': 'keyword',
            '@default': 'identifier',
          },
        }],
        [/<=|<-|==|!=|&&|\|\||<<|>>/, 'operator'],
        [/".*?"/, 'string'],
      ],
      comment: [
        [/[^\/*]+/, 'comment'],
        [/\*\//, 'comment', '@pop'],
        [/[\/*]/, 'comment'],
      ],
    },
  });

  monaco.editor.defineTheme('bsv-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: '38bdf8', fontStyle: 'bold' },
      { token: 'type.identifier', foreground: '34d399' },
      { token: 'number', foreground: 'f59e0b' },
      { token: 'number.hex', foreground: 'fbbf24' },
      { token: 'annotation', foreground: '94a3b8', fontStyle: 'italic' },
      { token: 'comment', foreground: '64748b', fontStyle: 'italic' },
    ],
    colors: {
      'editor.background': '#0c1017',
      'editor.lineHighlightBackground': '#141c28',
      'editorLineNumber.foreground': '#475569',
    },
  });
}

function getEditorValue() {
  if (appState.monacoEditor && !appState.useFallbackEditor) {
    return appState.monacoEditor.getValue();
  }
  return document.getElementById('fallback-editor').value;
}

function setEditorValue(code) {
  if (appState.monacoEditor && !appState.useFallbackEditor) {
    appState.monacoEditor.setValue(code);
  }
  document.getElementById('fallback-editor').value = code;
}

async function loadInitialData() {
  const [statusRes, currRes] = await Promise.all([
    fetch('/api/status').then((r) => r.json()),
    fetch('/api/curriculum').then((r) => r.json()),
  ]);

  appState.username = statusRes.username || 'default';
  appState.curriculumTracks = currRes.tracks || [];
  appState.cpCategories = currRes.cp_categories || [];
  appState.cpQuestionFormats = currRes.cp_question_formats || statusRes.cp_question_formats || [];
  appState.solvedCurriculum = statusRes.solved_curriculum || [];
  appState.totalCurriculum = statusRes.total_curriculum || 79;
  appState.cpRating = statusRes.cp_rating || 1200;
  appState.cpStreak = statusRes.cp_streak || 0;
  appState.dailyStreak = statusRes.daily_streak || 0;
  appState.lastDailyDate = statusRes.last_daily_date || '';
  appState.activeSession = statusRes.active_session || null;
  appState.cpHistory = statusRes.cp_history || [];
  appState.platformMode = statusRes.active_mode || 'curriculum';
  appState.editorMode = statusRes.editor_mode || 'snippet';

  const modalPath = document.getElementById('modal-vscode-path');
  if (modalPath && statusRes.vscode_workspace_file) {
    modalPath.textContent = statusRes.vscode_workspace_file;
  }

  updateHeaderIndicators();
  renderSidebar();
  if (statusRes.active_problem) {
    loadProblemIntoView(statusRes.active_problem);
  }
  if (statusRes.last_eval_result && statusRes.last_eval_result.result) {
    appState.lastEvaluation = statusRes.last_eval_result.result;
    renderWorkbench();
  }
}

function updateHeaderIndicators() {
  const solvedCount = appState.solvedCurriculum.length;
  const totalCount = appState.totalCurriculum || 79;
  document.getElementById('curriculum-progress-pill').textContent = `${solvedCount} / ${totalCount}`;
  document.getElementById('cp-rating-pill').textContent = `${appState.cpRating} ELO`;
  document.getElementById('cp-streak-display').textContent = `${appState.cpStreak} 🔥`;

  const userBtn = document.getElementById('active-user-display');
  if (userBtn) {
    userBtn.textContent = `🗄 User: ${appState.username}`;
  }

  document.getElementById('btn-mode-curriculum').classList.toggle('active', appState.platformMode === 'curriculum');
  document.getElementById('btn-mode-cp').classList.toggle('active', appState.platformMode === 'cp');

  document.getElementById('btn-editor-snippet').classList.toggle('active', appState.editorMode === 'snippet');
  document.getElementById('btn-editor-full').classList.toggle('active', appState.editorMode === 'full');

  const pct = Math.round((solvedCount / Math.max(1, totalCount)) * 100);
  const bar = document.getElementById('sidebar-progress-bar');
  const lbl = document.getElementById('sidebar-progress-label');
  if (bar) bar.style.width = `${pct}%`;
  if (lbl) lbl.textContent = `${solvedCount}/${totalCount} Solved (${pct}%)`;
}

function filterCurriculumSidebar(query) {
  appState.curriculumSearchQuery = (query || '').trim().toLowerCase();
  renderSidebar();
}

function setCurriculumStatusFilter(filterMode) {
  appState.curriculumStatusFilter = filterMode || 'all';
  ['all', 'unsolved', 'solved', 'combo'].forEach((k) => {
    const el = document.getElementById(`cfilt-${k}`);
    if (el) el.classList.toggle('active', k === appState.curriculumStatusFilter);
  });
  renderSidebar();
}

function toggleTrackCollapse(trackId) {
  appState.collapsedTracks[trackId] = !appState.collapsedTracks[trackId];
  renderSidebar();
}

async function reinforceTrackInCp(trackId, evt) {
  if (evt) evt.stopPropagation();
  appState.platformMode = 'cp';
  appState.cpCategoryFilter = trackId;
  appState.cpFormatFilter = 'spiral_reinforcement';
  appState.cpDifficultyFilter = 'Mixed';
  appState.cpTimeBudget = 15;
  appState.cpTimeBudgetMin = 15;
  appState.cpSessionCount = 3;
  updateHeaderIndicators();
  await startCpSession();
}

function renderSidebar() {
  const container = document.getElementById('sidebar-content');
  const header = document.getElementById('sidebar-curriculum-header');

  if (appState.platformMode === 'curriculum') {
    header.style.display = 'flex';
    const solvedSet = new Set(appState.solvedCurriculum);
    const activeId = appState.activeProblem ? appState.activeProblem.id : '';
    const q = appState.curriculumSearchQuery || '';
    const stFilter = appState.curriculumStatusFilter || 'all';

    let html = '';
    for (const track of appState.curriculumTracks) {
      const filteredProbs = track.problems.filter((p) => {
        const isSolved = solvedSet.has(p.id);
        if (stFilter === 'unsolved' && isSolved) return false;
        if (stFilter === 'solved' && !isSolved) return false;
        if (stFilter === 'combo') {
          const tLower = p.title.toLowerCase();
          const tagsLower = (p.tags || []).map((t) => t.toLowerCase());
          const isComboOrReinforce =
            tLower.includes('combo') ||
            tLower.includes('reinforce') ||
            tLower.includes('revision') ||
            tLower.includes('capstone') ||
            tLower.includes('bug hunt') ||
            tagsLower.some((t) => t.includes('combo') || t.includes('reinforce') || t.includes('revision') || t.includes('bug hunt'));
          if (!isComboOrReinforce) return false;
        }
        if (!q) return true;
        return (
          p.title.toLowerCase().includes(q) ||
          p.id.toLowerCase().includes(q) ||
          (p.tags || []).some((t) => t.toLowerCase().includes(q))
        );
      });
      if (filteredProbs.length === 0) continue;

      const trackSolved = track.problems.filter((p) => solvedSet.has(p.id)).length;
      const isCollapsed = Boolean(appState.collapsedTracks[track.id]) && !q && stFilter === 'all';
      html += `<div class="track-group">`;
      html += `<div class="track-header" title="${escapeHtml(track.subtitle)}" onclick="toggleTrackCollapse('${track.id}')" style="display:flex;justify-content:space-between;align-items:center;cursor:pointer;gap:4px;">
        <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${isCollapsed ? '▸' : '▾'} ${escapeHtml(track.title)}</span>
        <span style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
          <button class="btn" onclick="reinforceTrackInCp('${track.id}', event)" title="Practice &amp; reinforce this track in the Competitive Arena" style="padding:1px 5px;font-size:9.5px;color:var(--accent-cyan);border-color:rgba(56,189,248,0.35);">🎯 CP Drill</button>
          <span style="font-size:10px;color:var(--text-muted);">${trackSolved}/${track.problems.length}</span>
        </span>
      </div>`;
      if (!isCollapsed) {
        for (const p of filteredProbs) {
          const isSolved = solvedSet.has(p.id);
          const isActive = p.id === activeId;
          html += `
            <button class="problem-item ${isActive ? 'active' : ''}" id="nav-prob-${p.id}" onclick="selectCurriculumProblem('${p.id}')">
              <span class="prob-left">
                <span class="status-icon ${isSolved ? 'solved' : ''}">${isSolved ? '✓' : p.number}</span>
                <span style="overflow:hidden;text-overflow:ellipsis;">${escapeHtml(p.title.replace(/^\d+\.\s*/, ''))}</span>
              </span>
              <span class="diff-badge diff-${p.difficulty}">${p.difficulty}</span>
            </button>
          `;
        }
      }
      html += `</div>`;
    }
    container.innerHTML = html || `<div style="padding:12px;color:var(--text-muted);font-size:12px;">No curriculum problems match your current filter.</div>`;
  } else {
    header.style.display = 'none';
    const catOptions = appState.cpCategories
      .map((c) => `<option value="${c.id}" ${c.id === appState.cpCategoryFilter ? 'selected' : ''}>${escapeHtml(c.name)}</option>`)
      .join('');

    const fmtOptions = (appState.cpQuestionFormats.length
      ? appState.cpQuestionFormats
      : [
          { id: 'all', name: 'All 7 Question Formats (Mixed)' },
          { id: 'design_from_spec', name: '1. RTL Module Design from Spec' },
          { id: 'bug_fix_rtl', name: '2. Hardware Bug Hunt & RTL Repair' },
          { id: 'fill_in_blanks', name: '3. Fill-in-the-Blanks Microarchitecture' },
          { id: 'verification_monitor', name: '4. Verification & Spec Compliance' },
          { id: 'reverse_engineer_mystery', name: '5. Reverse-Engineer Mystery Spec' },
          { id: 'spiral_reinforcement', name: '6. Spiral Track Reinforcement & Revision' },
          { id: 'speed_coding_sprint', name: '7. 90-Second Blitz Speed-Coding Sprint' },
        ]
    )
      .map((f) => `<option value="${f.id}" ${f.id === appState.cpFormatFilter ? 'selected' : ''}>${escapeHtml(f.name)}</option>`)
      .join('');

    const activeId = appState.activeProblem ? appState.activeProblem.id : '';
    let sessionCardHtml = '';
    if (appState.activeSession && appState.activeSession.problems && appState.activeSession.problems.length > 0) {
      const sess = appState.activeSession;
      const solvedInSess = sess.problems.filter((p) => p.solved).length;
      const itemsHtml = sess.problems
        .map((p, idx) => {
          const isAct = p.id === activeId;
          return `
            <button class="problem-item ${isAct ? 'active' : ''}" onclick="selectCpProblem('${p.id}')" style="margin-top:3px;">
              <span class="prob-left">
                <span class="status-icon ${p.solved ? 'solved' : ''}">${p.solved ? '✓' : idx + 1}</span>
                <span style="overflow:hidden;text-overflow:ellipsis;">${escapeHtml(p.title.replace(/^\[Session #\d+\]\s*/, ''))}</span>
              </span>
              <span class="diff-badge diff-${p.difficulty}">${p.difficulty}</span>
            </button>
          `;
        })
        .join('');
      sessionCardHtml = `
        <div class="section-card" style="padding:10px;border-color:var(--accent-cyan);">
          <div class="section-card-title" style="margin-bottom:4px;">
            <span>🎯 Active Session (${solvedInSess}/${sess.problems.length})</span>
            <span style="color:var(--accent-amber);">${sess.time_budget_minutes}m budget</span>
          </div>
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:6px;">
            Est. Time: ~${sess.estimated_total_minutes || sess.time_budget_minutes} min | Mode: ${escapeHtml(sess.difficulty)}
          </div>
          <div>${itemsHtml}</div>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="section-card" style="padding:11px;border-color:rgba(245, 158, 11, 0.45);background:linear-gradient(180deg, rgba(245, 158, 11, 0.08), rgba(17, 23, 34, 0.95));">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
          <span style="font-weight:700;font-size:12.5px;color:var(--accent-amber);">🌟 Daily Hardware Challenge</span>
          <span class="tag-chip" style="color:var(--accent-amber);">${appState.dailyStreak || 0}d Daily Streak</span>
        </div>
        <div style="font-size:11.5px;color:var(--text-secondary);margin-bottom:8px;">
          Deterministic daily hardware, DSP, memory, CDC, verification, or architecture challenge shared across all users today.
        </div>
        <button class="btn btn-amber" onclick="startDailyChallenge()" style="width:100%;justify-content:center;padding:6px 10px;">
          🌟 Launch Today's Daily Challenge
        </button>
      </div>

      ${sessionCardHtml}

      <div class="cp-gen-box">
        <div style="font-weight:700;font-size:13px;color:var(--accent-cyan);">
          ⚡ Practice Pack &amp; Problem Synthesizer
        </div>
        <div style="font-size:11.5px;color:var(--text-secondary);">
          80 procedural hardware, DSP, memory, CDC, verification &amp; computer architecture families across 7 question styles (including Track Reinforcement!).
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
          <div>
            <label class="form-label" for="cp-time-select">Time Budget</label>
            <select class="form-select" id="cp-time-select" onchange="appState.cpTimeBudget = parseInt(this.value, 10); appState.cpTimeBudgetMin = appState.cpTimeBudget;">
              <option value="10" ${appState.cpTimeBudget === 10 ? 'selected' : ''}>10 mins (Sprint)</option>
              <option value="15" ${appState.cpTimeBudget === 15 ? 'selected' : ''}>15 mins (Reinforce)</option>
              <option value="20" ${appState.cpTimeBudget === 20 ? 'selected' : ''}>20 mins (Standard)</option>
              <option value="30" ${appState.cpTimeBudget === 30 ? 'selected' : ''}>30 mins (Deep)</option>
              <option value="45" ${appState.cpTimeBudget === 45 ? 'selected' : ''}>45 mins (Contest)</option>
              <option value="60" ${appState.cpTimeBudget === 60 ? 'selected' : ''}>60 mins (Marathon)</option>
            </select>
          </div>
          <div>
            <label class="form-label" for="cp-count-select">Problem Count</label>
            <select class="form-select" id="cp-count-select" onchange="appState.cpSessionCount = parseInt(this.value, 10)">
              <option value="0" ${appState.cpSessionCount === 0 ? 'selected' : ''}>Auto-Fit to Time</option>
              <option value="2" ${appState.cpSessionCount === 2 ? 'selected' : ''}>2 Problems</option>
              <option value="3" ${appState.cpSessionCount === 3 ? 'selected' : ''}>3 Problems</option>
              <option value="5" ${appState.cpSessionCount === 5 ? 'selected' : ''}>5 Problems</option>
              <option value="8" ${appState.cpSessionCount === 8 ? 'selected' : ''}>8 Problems</option>
            </select>
          </div>
        </div>

        <div>
          <label class="form-label" for="cp-diff-select">Difficulty Tier</label>
          <select class="form-select" id="cp-diff-select" onchange="appState.cpDifficultyFilter = this.value">
            <option value="Mixed" ${appState.cpDifficultyFilter === 'Mixed' ? 'selected' : ''}>Progressive Mix (Easy → Hard)</option>
            <option value="Easy" ${appState.cpDifficultyFilter === 'Easy' ? 'selected' : ''}>Easy (+25 ELO / ~5m)</option>
            <option value="Medium" ${appState.cpDifficultyFilter === 'Medium' ? 'selected' : ''}>Medium (+45 ELO / ~10m)</option>
            <option value="Hard" ${appState.cpDifficultyFilter === 'Hard' ? 'selected' : ''}>Hard (+75 ELO / ~18m)</option>
          </select>
        </div>

        <div>
          <label class="form-label" for="cp-fmt-select">Question Format (7 Styles)</label>
          <select class="form-select" id="cp-fmt-select" onchange="appState.cpFormatFilter = this.value">
            ${fmtOptions}
          </select>
        </div>

        <div>
          <label class="form-label" for="cp-cat-select">Track Reinforce / Hardware Family (80 Families)</label>
          <select class="form-select" id="cp-cat-select" onchange="appState.cpCategoryFilter = this.value">
            ${catOptions}
          </select>
        </div>

        <div style="display:flex;gap:6px;flex-direction:column;">
          <button class="btn btn-primary" id="btn-start-cp-session" onclick="startCpSession()" style="width:100%;justify-content:center;padding:7px;">
            🎯 Start Timed Practice / Track Reinforce Session
          </button>
          <button class="btn btn-cyan" id="btn-generate-cp-now" onclick="generateNewCpChallenge()" style="width:100%;justify-content:center;padding:7px;">
            ⚡ Generate Single CP Problem
          </button>
        </div>
      </div>

      <div class="section-card" style="padding:12px;">
        <div class="section-card-title"><span>Competitive Mastery Stats</span></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-family:var(--font-mono);font-size:12px;">
          <div style="background:var(--bg-root);padding:8px;border-radius:4px;">
            <div style="color:var(--text-muted);font-size:10.5px;">RATING</div>
            <div style="color:var(--accent-cyan);font-size:16px;font-weight:700;">${appState.cpRating}</div>
          </div>
          <div style="background:var(--bg-root);padding:8px;border-radius:4px;">
            <div style="color:var(--text-muted);font-size:10.5px;">SOLVE STREAK</div>
            <div style="color:var(--accent-amber);font-size:16px;font-weight:700;">${appState.cpStreak} 🔥</div>
          </div>
        </div>
      </div>
    `;
  }
}

async function switchPlatformMode(mode) {
  appState.platformMode = mode;
  if (mode === 'cp' && (!appState.activeProblem || appState.activeProblem.mode_type !== 'cp')) {
    await generateNewCpChallenge();
    return;
  }
  if (mode === 'curriculum' && (!appState.activeProblem || appState.activeProblem.mode_type === 'cp')) {
    await selectCurriculumProblem('01_wire_zero');
    return;
  }
  updateHeaderIndicators();
  renderSidebar();
}

async function selectCurriculumProblem(problemId) {
  const res = await fetch('/api/select', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      problem_id: problemId,
      mode_type: 'curriculum',
      editor_mode: appState.editorMode,
    }),
  }).then((r) => r.json());

  appState.platformMode = 'curriculum';
  loadProblemIntoView(res.problem);
  updateHeaderIndicators();
  renderSidebar();
}

async function selectCpProblem(problemId) {
  const res = await fetch('/api/select', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      problem_id: problemId,
      mode_type: 'cp',
      editor_mode: appState.editorMode,
    }),
  }).then((r) => r.json());

  appState.platformMode = 'cp';
  loadProblemIntoView(res.problem);
  updateHeaderIndicators();
  renderSidebar();
}

async function startDailyChallenge() {
  const res = await fetch('/api/cp/daily', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  }).then((r) => r.json());

  appState.platformMode = 'cp';
  appState.cpRating = res.cp_rating || appState.cpRating;
  appState.cpStreak = res.cp_streak || appState.cpStreak;
  appState.dailyStreak = res.daily_streak || appState.dailyStreak;
  loadProblemIntoView(res.problem);
  updateHeaderIndicators();
  renderSidebar();
}

async function startCpSession() {
  const timeEl = document.getElementById('cp-time-select');
  const countEl = document.getElementById('cp-count-select');
  const diffEl = document.getElementById('cp-diff-select');
  const catEl = document.getElementById('cp-cat-select');
  const fmtEl = document.getElementById('cp-fmt-select');

  const time_budget_minutes = timeEl ? parseInt(timeEl.value, 10) : appState.cpTimeBudget;
  const countVal = countEl ? parseInt(countEl.value, 10) : appState.cpSessionCount;
  const difficulty = diffEl ? diffEl.value : appState.cpDifficultyFilter;
  const category = catEl ? catEl.value : appState.cpCategoryFilter;
  const question_format = fmtEl ? fmtEl.value : appState.cpFormatFilter;

  const res = await fetch('/api/cp/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      time_budget_minutes,
      problem_count: countVal > 0 ? countVal : null,
      difficulty,
      category,
      question_format,
    }),
  }).then((r) => r.json());

  appState.platformMode = 'cp';
  appState.activeSession = res.session || null;
  if (res.problem) {
    loadProblemIntoView(res.problem);
  }
  updateHeaderIndicators();
  renderSidebar();
}

async function generateNewCpChallenge() {
  const diffEl = document.getElementById('cp-diff-select');
  const catEl = document.getElementById('cp-cat-select');
  const fmtEl = document.getElementById('cp-fmt-select');
  const rawDiff = diffEl ? diffEl.value : appState.cpDifficultyFilter;
  const difficulty = rawDiff === 'Mixed' ? 'Medium' : rawDiff;
  const category = catEl ? catEl.value : appState.cpCategoryFilter;
  const question_format = fmtEl ? fmtEl.value : appState.cpFormatFilter;

  const res = await fetch('/api/cp/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty, category, question_format }),
  }).then((r) => r.json());

  appState.platformMode = 'cp';
  appState.cpRating = res.cp_rating || appState.cpRating;
  appState.cpStreak = res.cp_streak || appState.cpStreak;
  loadProblemIntoView(res.problem);
  updateHeaderIndicators();
  renderSidebar();
}

function loadProblemIntoView(prob) {
  appState.activeProblem = prob;
  appState.unlockedClueLevel = -1;
  appState.timerSeconds = 0;

  document.getElementById('prob-title').textContent = prob.title;
  const fmtBadge = prob.question_format_label ? ` | Format: ${prob.question_format_label}` : '';
  const estBadge = prob.estimated_minutes ? ` | ~${prob.estimated_minutes}m` : '';
  document.getElementById('prob-id-label').textContent = `ID: ${prob.id} | Module: ${prob.module_name}${fmtBadge}${estBadge}`;
  const diffBadge = document.getElementById('prob-diff-badge');
  diffBadge.textContent = prob.difficulty;
  diffBadge.className = `diff-badge diff-${prob.difficulty}`;

  const tagRow = document.getElementById('prob-tag-row');
  tagRow.innerHTML = (prob.tags || [])
    .map((t) => `<span class="tag-chip">${escapeHtml(t)}</span>`)
    .join('');

  document.getElementById('prob-diagram').textContent = prob.diagram || '';
  document.getElementById('prob-description').innerHTML = renderMarkdownSimple(prob.description || '');
  document.getElementById('prob-bsv-vs-verilog').innerHTML = renderMarkdownSimple(prob.bsv_vs_verilog || '');
  document.getElementById('prob-ifc-name').textContent = prob.interface_name || '';
  document.getElementById('prob-interface-def').textContent = prob.interface_def || '';

  document.getElementById('clue-step-counter').textContent = `0/${prob.hints_count || 3}`;
  document.getElementById('clues-output-area').innerHTML =
    'Click <strong>Unlock Clue</strong> for progressive hints and live structural comparison against the Golden Solution.';

  const codeToShow = appState.editorMode === 'snippet' ? prob.user_code_snippet : prob.user_code_full;
  setEditorValue(codeToShow || prob.active_code || '');
}

function setEditorMode(mode) {
  if (!appState.activeProblem) return;
  appState.editorMode = mode;
  updateHeaderIndicators();
  const prob = appState.activeProblem;
  const nextCode = mode === 'snippet' ? prob.user_code_snippet : prob.user_code_full;
  setEditorValue(nextCode || '');
}

function resetProblemTemplate() {
  if (!appState.activeProblem) return;
  const prob = appState.activeProblem;
  const tmpl = appState.editorMode === 'snippet' ? prob.snippet_template : prob.full_template;
  setEditorValue(tmpl);
}

async function submitToBsc() {
  if (!appState.activeProblem) return;
  const btn = document.getElementById('btn-submit-bsc');
  const origLabel = btn.innerHTML;
  btn.innerHTML = '⏳ Compiling &amp; Simulating in bsc...';
  btn.disabled = true;

  try {
    const code = getEditorValue();
    if (appState.editorMode === 'snippet') {
      appState.activeProblem.user_code_snippet = code;
    } else {
      appState.activeProblem.user_code_full = code;
    }

    const res = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        problem_id: appState.activeProblem.id,
        code,
        editor_mode: appState.editorMode,
        llm_api_key: appState.llmConfig.apiKey,
        llm_api_base: appState.llmConfig.apiBase,
        llm_model: appState.llmConfig.model,
      }),
    }).then((r) => r.json());

    appState.lastEvaluation = res.evaluation;
    appState.solvedCurriculum = res.solved_curriculum || appState.solvedCurriculum;
    appState.cpRating = res.cp_rating || appState.cpRating;
    appState.cpStreak = res.cp_streak || appState.cpStreak;
    appState.dailyStreak = res.daily_streak || appState.dailyStreak;
    if (res.active_session) {
      appState.activeSession = res.active_session;
    }

    if (!res.evaluation.compiled) {
      appState.activeWorkbenchTab = 'compiler';
    } else if (appState.activeWorkbenchTab === 'compiler') {
      appState.activeWorkbenchTab = 'wave';
    }

    updateHeaderIndicators();
    renderSidebar();
    renderWorkbench();
  } finally {
    btn.innerHTML = origLabel;
    btn.disabled = false;
  }
}

async function requestProgressiveHint() {
  if (!appState.activeProblem) return;
  const maxHints = appState.activeProblem.hints_count || 3;
  appState.unlockedClueLevel = Math.min(maxHints - 1, appState.unlockedClueLevel + 1);

  const res = await fetch('/api/hint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      problem_id: appState.activeProblem.id,
      code: getEditorValue(),
      hint_level: appState.unlockedClueLevel,
    }),
  }).then((r) => r.json());

  document.getElementById('clue-step-counter').textContent = `${appState.unlockedClueLevel + 1}/${res.total_hints}`;
  const cluesHtml = (res.all_unlocked_hints || [])
    .map((h, i) => `<div class="clue-card"><strong>Clue #${i + 1}:</strong> ${renderMarkdownSimple(h)}</div>`)
    .join('');

  const tipsHtml = (res.live_structural_tips || [])
    .map((t) => `<li style="margin-bottom:4px;">${renderMarkdownSimple(t)}</li>`)
    .join('');

  document.getElementById('clues-output-area').innerHTML = `
    ${cluesHtml}
    <div style="margin-top:10px;padding:8px 10px;background:var(--bg-root);border-radius:4px;border:1px solid var(--border-subtle);">
      <div style="font-weight:700;font-size:11.5px;color:var(--accent-cyan);margin-bottom:4px;">
        LIVE AST STRUCTURAL COMPARISON VS. GOLDEN MODEL
      </div>
      <ul style="padding-left:18px;margin:0;">${tipsHtml}</ul>
    </div>
  `;
}

async function revealGoldenSolution() {
  if (!appState.activeProblem) return;
  const res = await fetch(`/api/solution/${appState.activeProblem.id}`).then((r) => r.json());
  const area = document.getElementById('clues-output-area');
  const codeToCopy = appState.editorMode === 'snippet' ? res.reference_snippet : res.reference_full;
  window._lastGoldenCode = codeToCopy;

  area.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
      <strong style="color:var(--accent-emerald);">Golden Reference BSV Solution (${escapeHtml(res.title)})</strong>
      <button class="btn" style="padding:3px 8px;font-size:11px;" onclick="setEditorValue(window._lastGoldenCode)">
        Load Golden Code into Editor
      </button>
    </div>
    <pre class="diagram-pre" style="color:var(--text-primary);">${escapeHtml(res.reference_full)}</pre>
  `;
}

async function pullFromVsCode() {
  const res = await fetch('/api/vscode/pull').then((r) => r.json());
  if (res.code) {
    setEditorValue(res.code);
  }
  if (res.last_eval_result && res.last_eval_result.result) {
    appState.lastEvaluation = res.last_eval_result.result;
    renderWorkbench();
  }
}

function switchWorkbenchTab(tab) {
  appState.activeWorkbenchTab = tab;
  renderWorkbench();
}

function renderWorkbench() {
  const tabs = ['wave', 'review', 'sched', 'verilog', 'compiler'];
  for (const t of tabs) {
    const el = document.getElementById(`wbtab-${t}`);
    if (el) el.classList.toggle('active', appState.activeWorkbenchTab === t);
  }

  const banner = document.getElementById('wb-verdict-banner');
  const body = document.getElementById('workbench-content');
  const ev = appState.lastEvaluation;

  if (!ev) {
    banner.style.display = 'none';
    return;
  }

  banner.style.display = 'inline-block';
  if (ev.passed) {
    banner.className = 'wb-status-banner wb-status-pass';
    banner.textContent = `✓ ACCEPTED (${ev.passed_tests}/${ev.total_tests} cycles • ${ev.execution_time_ms}ms)`;
  } else if (ev.compiled) {
    banner.className = 'wb-status-banner wb-status-fail';
    banner.textContent = `✗ MISMATCH (${ev.passed_tests}/${ev.total_tests} cycles • First mismatch @ cycle ${ev.first_mismatch_cycle})`;
  } else {
    banner.className = 'wb-status-banner wb-status-fail';
    banner.textContent = `✗ BSC COMPILE ERROR`;
  }

  if (appState.activeWorkbenchTab === 'wave') {
    body.innerHTML = renderWaveformView(ev);
  } else if (appState.activeWorkbenchTab === 'review') {
    body.innerHTML = renderSemanticReviewView(ev);
  } else if (appState.activeWorkbenchTab === 'sched') {
    body.innerHTML = renderScheduleView(ev);
  } else if (appState.activeWorkbenchTab === 'verilog') {
    body.innerHTML = renderVerilogView(ev);
  } else {
    body.innerHTML = renderCompilerView(ev);
  }
}

function renderWaveformView(ev) {
  if (!ev.compiled) {
    return `<div style="color:var(--accent-coral);font-family:var(--font-mono);">Compilation did not succeed. Switch to the <strong>BSC Compiler Diagnostics</strong> tab to fix syntax/type errors first.</div>`;
  }
  const wave = ev.waveform || [];
  if (wave.length === 0) {
    return `<div style="color:var(--text-secondary);">No waveform cycles recorded.</div>`;
  }

  const svgHtml = buildDigitalWaveformSvg(wave);
  const rowsHtml = wave
    .map((w) => {
      const inStr = Object.entries(w.signals || {}).map(([k, v]) => `${k}=${v}`).join(', ');
      const refStr = Object.entries(w.ref_outputs || {}).map(([k, v]) => `${k}=${v}`).join(', ');
      const usrStr = Object.entries(w.user_outputs || {}).map(([k, v]) => `${k}=${v}`).join(', ');
      return `
        <tr class="${w.match ? '' : 'row-mismatch'}">
          <td>#${w.cycle}</td>
          <td>${escapeHtml(inStr)}</td>
          <td style="color:var(--accent-emerald);">${escapeHtml(refStr)}</td>
          <td style="color:${w.match ? 'var(--accent-cyan)' : 'var(--accent-coral)'};">${escapeHtml(usrStr)}</td>
          <td>${w.match ? '<span style="color:var(--accent-emerald);">✓ Match</span>' : '<strong style="color:var(--accent-coral);">✗ Mismatch</strong>'}</td>
        </tr>
      `;
    })
    .join('');

  return `
    <div class="wave-svg-wrap">${svgHtml}</div>
    <table class="wave-table">
      <thead>
        <tr>
          <th>Cycle</th>
          <th>Stimulus Inputs</th>
          <th>Golden Reference Output</th>
          <th>Your Module Output</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  `;
}

function buildDigitalWaveformSvg(wave) {
  const n = wave.length;
  const colW = 68;
  const labelW = 130;
  const width = labelW + n * colW + 20;
  const rowH = 30;
  const rows = [
    { name: 'CLK', type: 'clock' },
    { name: 'Inputs', type: 'bus', getter: (w) => Object.values(w.signals || {}).join(',') },
    { name: 'Ref Output', type: 'bus', color: '#10b981', getter: (w) => Object.values(w.ref_outputs || {}).join(',') },
    { name: 'Your Output', type: 'bus', color: '#38bdf8', getter: (w) => Object.values(w.user_outputs || {}).join(',') },
    { name: 'Mismatch', type: 'mismatch' },
  ];
  const height = rows.length * rowH + 28;

  let svg = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg" style="font-family:'JetBrains Mono',monospace;font-size:11px;">`;

  // Cycle header ticks
  for (let i = 0; i < n; i++) {
    const x = labelW + i * colW;
    const isErr = !wave[i].match;
    if (isErr) {
      svg += `<rect x="${x}" y="0" width="${colW}" height="${height}" fill="rgba(244,63,94,0.12)" />`;
    }
    svg += `<line x1="${x}" y1="0" x2="${x}" y2="${height}" stroke="#1f2a3a" stroke-dasharray="2,2" />`;
    svg += `<text x="${x + colW / 2}" y="14" fill="#9fb0c7" text-anchor="middle">c${wave[i].cycle}</text>`;
  }

  rows.forEach((row, rIdx) => {
    const yTop = 22 + rIdx * rowH;
    const yMid = yTop + rowH / 2;
    const yBot = yTop + rowH - 6;
    const yHi = yTop + 6;

    svg += `<text x="8" y="${yMid + 4}" fill="#e6edf5" font-weight="600">${row.name}</text>`;

    if (row.type === 'clock') {
      let path = '';
      for (let i = 0; i < n; i++) {
        const x0 = labelW + i * colW;
        const xMid = x0 + colW / 2;
        const x1 = x0 + colW;
        path += `${i === 0 ? 'M' : 'L'} ${x0} ${yBot} L ${x0} ${yHi} L ${xMid} ${yHi} L ${xMid} ${yBot} L ${x1} ${yBot} `;
      }
      svg += `<path d="${path}" fill="none" stroke="#f59e0b" stroke-width="1.6" />`;
    } else if (row.type === 'mismatch') {
      let path = '';
      for (let i = 0; i < n; i++) {
        const x0 = labelW + i * colW;
        const x1 = x0 + colW;
        const yVal = wave[i].match ? yBot : yHi;
        path += `${i === 0 ? `M ${x0} ${yVal}` : `L ${x0} ${yVal}`} L ${x1} ${yVal} `;
      }
      svg += `<path d="${path}" fill="none" stroke="#f43f5e" stroke-width="2" />`;
    } else {
      const strokeColor = row.color || '#9fb0c7';
      for (let i = 0; i < n; i++) {
        const x0 = labelW + i * colW;
        const x1 = x0 + colW;
        const val = String(row.getter(wave[i]) || '0');
        const boxColor = row.name === 'Your Output' && !wave[i].match ? '#f43f5e' : strokeColor;
        svg += `<polygon points="${x0 + 3},${yMid} ${x0 + 7},${yHi} ${x1 - 7},${yHi} ${x1 - 3},${yMid} ${x1 - 7},${yBot} ${x0 + 7},${yBot}" fill="rgba(16,22,31,0.85)" stroke="${boxColor}" stroke-width="1.3" />`;
        const shortVal = val.length > 7 ? val.slice(0, 7) : val;
        svg += `<text x="${x0 + colW / 2}" y="${yMid + 4}" fill="#e6edf5" text-anchor="middle" font-size="10.5px">${escapeHtml(shortVal)}</text>`;
      }
    }
  });

  svg += `</svg>`;
  return svg;
}

function renderSemanticReviewView(ev) {
  const ai = ev.ai_review || {};
  const acceptedList = (ai.approaches_accepted || [])
    .map((a) => `<li style="color:var(--accent-emerald);margin-bottom:4px;">✓ ${ renderMarkdownSimple(a) }</li>`)
    .join('');

  const cluesList = (ai.clues || [])
    .map((c) => `<div class="clue-card">💡 ${ renderMarkdownSimple(c) }</div>`)
    .join('');

  const uc = ai.user_constructs || {};
  const rc = ai.ref_constructs || {};

  return `
    <div class="review-grid">
      <div class="score-box">
        <div style="font-size:11px;color:var(--text-secondary);text-transform:uppercase;">Idiomatic BSV Score</div>
        <div class="score-value">${ai.idiomatic_score ?? 0}<span style="font-size:14px;color:var(--text-muted);">/100</span></div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">${ai.verdict || ''}</div>
      </div>
      <div>
        <div style="font-weight:700;font-size:13.5px;margin-bottom:6px;color:var(--accent-cyan);">
          Smart Semantic &amp; Golden Model Co-Simulation Analysis
        </div>
        <div style="font-size:13px;color:var(--text-primary);margin-bottom:8px;">
          ${renderMarkdownSimple(ai.summary || '')}
        </div>
        ${acceptedList ? `<ul style="list-style:none;padding:0;margin-bottom:8px;">${acceptedList}</ul>` : ''}
        <div style="font-family:var(--font-mono);font-size:11.5px;color:var(--text-secondary);background:var(--bg-panel);padding:8px 10px;border-radius:5px;border:1px solid var(--border-subtle);">
          <strong>Construct Comparison (Yours vs. Golden Reference):</strong>
          Regs: ${uc.registers ?? 0} vs ${rc.registers ?? 0} |
          Ehrs: ${uc.ehrs ?? 0} vs ${rc.ehrs ?? 0} |
          FIFOs: ${uc.fifos ?? 0} vs ${rc.fifos ?? 0} |
          Rules: ${uc.rules ?? 0} vs ${rc.rules ?? 0} |
          Methods: ${uc.methods ?? 0} vs ${rc.methods ?? 0}
        </div>
        ${cluesList}
      </div>
    </div>
  `;
}

function renderScheduleView(ev) {
  const sched = ev.schedule || {};
  const rulesHtml = (sched.rules || [])
    .map(
      (r) => `
      <tr>
        <td style="color:var(--accent-cyan);font-weight:600;">${escapeHtml(r.name)}</td>
        <td><code>${escapeHtml(r.predicate)}</code></td>
        <td>${escapeHtml(r.blocking_rules)}</td>
      </tr>`
    )
    .join('');

  return `
    <div style="margin-bottom:10px;font-size:12.5px;color:var(--text-secondary);">
      <strong>Logical Execution Order:</strong>
      <code style="color:var(--accent-emerald);">${escapeHtml((sched.execution_order || []).join('  →  ') || 'Combinational / Direct Methods')}</code>
    </div>
    ${
      rulesHtml
        ? `<table class="wave-table" style="margin-bottom:12px;">
            <thead><tr><th>Rule / Method</th><th>CAN_FIRE Predicate</th><th>Blocking Rules</th></tr></thead>
            <tbody>${rulesHtml}</tbody>
          </table>`
        : ''
    }
    <pre class="diagram-pre" style="color:var(--text-secondary);">${escapeHtml(sched.raw_schedule || 'No schedule output.')}</pre>
  `;
}

function renderVerilogView(ev) {
  const m = ev.metrics || {};
  return `
    <div style="display:flex;gap:14px;margin-bottom:10px;font-family:var(--font-mono);font-size:12px;color:var(--text-secondary);">
      <span>Verilog Lines: <strong style="color:var(--text-primary);">${m.verilog_lines || 0}</strong></span>
      <span>Synthesized Regs: <strong style="color:var(--accent-emerald);">${m.reg_count || 0}</strong></span>
      <span>Synthesized Wires: <strong style="color:var(--accent-cyan);">${m.wire_count || 0}</strong></span>
      <span>CAN_FIRE Signals: <strong style="color:var(--accent-amber);">${(m.can_fire_signals || []).length}</strong></span>
    </div>
    <pre class="diagram-pre" style="color:#cbd5e1;">${escapeHtml(ev.verilog_code || '// Compile a valid module to inspect generated BSC Verilog RTL.')}</pre>
  `;
}

function renderCompilerView(ev) {
  const diags = ev.diagnostics || [];
  const diagCards = diags
    .map(
      (d) => `
      <div class="clue-card" style="border-left-color:${d.severity === 'error' ? 'var(--accent-coral)' : 'var(--accent-amber)'};">
        <div style="font-family:var(--font-mono);font-weight:700;color:${d.severity === 'error' ? 'var(--accent-coral)' : 'var(--accent-amber)'};">
          [${d.severity.toUpperCase()} ${d.code}] Line ${d.line}, Col ${d.column}
        </div>
        <div style="margin:4px 0;">${escapeHtml(d.message)}</div>
        ${d.friendly_hint ? `<div style="color:var(--accent-cyan);font-size:12px;"><strong>💡 BSV Guide:</strong> ${escapeHtml(d.friendly_hint)}</div>` : ''}
      </div>`
    )
    .join('');

  return `
    ${diagCards || '<div style="color:var(--accent-emerald);margin-bottom:8px;">✓ Zero BSC compiler errors or warnings!</div>'}
    <pre class="diagram-pre" style="color:var(--text-secondary);margin-top:8px;">${escapeHtml(ev.compiler_output || '')}</pre>
  `;
}

function startSpeedrunTimer() {
  if (appState.timerInterval) clearInterval(appState.timerInterval);
  appState.timerInterval = setInterval(() => {
    appState.timerSeconds += 1;
    const mins = String(Math.floor(appState.timerSeconds / 60)).padStart(2, '0');
    const secs = String(appState.timerSeconds % 60).padStart(2, '0');
    const el = document.getElementById('cp-timer-display');
    if (el) el.textContent = `${mins}:${secs}`;
  }, 1000);
}

async function promptSwitchUser() {
  const nextUser = window.prompt(
    'Enter shared BSVbits username (stored in SQLite workspace/bsvbits.db and synced with VS Code):',
    appState.username || 'default'
  );
  if (!nextUser || !nextUser.trim()) return;
  await fetch('/api/user/switch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: nextUser.trim() }),
  });
  await loadInitialData();
}

function openSettingsModal() {
  const userEl = document.getElementById('input-username');
  if (userEl) userEl.value = appState.username || 'default';
  document.getElementById('input-llm-key').value = appState.llmConfig.apiKey;
  document.getElementById('input-llm-base').value = appState.llmConfig.apiBase;
  document.getElementById('input-llm-model').value = appState.llmConfig.model;
  document.getElementById('settings-modal').classList.add('open');
}

function closeSettingsModal() {
  document.getElementById('settings-modal').classList.remove('open');
}

async function saveSettingsModal() {
  const userEl = document.getElementById('input-username');
  const nextUser = userEl ? userEl.value.trim() : '';
  appState.llmConfig.apiKey = document.getElementById('input-llm-key').value.trim();
  appState.llmConfig.apiBase = document.getElementById('input-llm-base').value.trim();
  appState.llmConfig.model = document.getElementById('input-llm-model').value.trim();
  localStorage.setItem('bsvbits_llm_key', appState.llmConfig.apiKey);
  localStorage.setItem('bsvbits_llm_base', appState.llmConfig.apiBase);
  localStorage.setItem('bsvbits_llm_model', appState.llmConfig.model);
  closeSettingsModal();
  if (nextUser && nextUser !== appState.username) {
    await fetch('/api/user/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: nextUser }),
    });
    await loadInitialData();
  }
}

function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderMarkdownSimple(md) {
  let html = escapeHtml(md);
  // Code blocks ```bsv ... ```
  html = html.replace(/```(?:\w+)?\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  // Markdown tables
  html = html.replace(/((?:^\|.*\|\s*\n)+)/gm, (tableBlock) => {
    const rows = tableBlock.trim().split('\n');
    if (rows.length < 2) return tableBlock;
    let t = '<table>';
    rows.forEach((r, idx) => {
      if (/^\|[\s\-:|]+\|$/.test(r.trim())) return;
      const cells = r.trim().replace(/^\||\|$/g, '').split('|');
      const tag = idx === 0 ? 'th' : 'td';
      t += '<tr>' + cells.map((c) => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>';
    });
    t += '</table>';
    return t;
  });
  // Headings
  html = html.replace(/^###\s+(.*)$/gm, '<h3>$1</h3>');
  // Bold & inline code
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bullet lists
  html = html.replace(/^- (.*)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
  // Paragraphs
  html = html.replace(/\n\n+/g, '</p><p>');
  return `<p>${html}</p>`;
}
