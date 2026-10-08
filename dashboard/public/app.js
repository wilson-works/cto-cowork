'use strict';

// The Coworking Space's page: one direction box, the runs, and each finished run's paste blocks with a Copy button.
(function () {
  const token = document.querySelector('meta[name="cowork-token"]').content;
  const $ = (id) => document.getElementById(id);
  const JOKES = [
    'James: "Every lane gets an owner and a DONE-WHEN. That\'s the job."',
    'John: "I read the diff. Twice. Then I sign it."',
    'James: "Short version for the owner, long version for the lanes. We move."',
    'John: "Smallest correct change. Then we light the cigars."',
    'James: "We plan it, you paste it. Nobody starts a lane behind your back."',
    'John: "Two lanes in one file is how Tuesdays get long."',
    'James: "The gate grades the work. We don\'t grade our own homework."',
    'John: "Spec first, then code, then the good bottle."',
    'James: "My door is open. The run board is not a suggestion."',
  ];
  const open = new Set();
  let busy = false;

  async function call(method, url, body) {
    const res = await fetch(url, {
      method, headers: Object.assign({ 'X-Cowork-Token': token }, body ? { 'Content-Type': 'application/json' } : {}),
      body: body ? JSON.stringify(body) : undefined, cache: 'no-store',
    });
    let data = {};
    try { data = await res.json(); } catch (_) { /* below */ }
    if (!res.ok) throw new Error(data.error || `The space answered ${res.status}.`);
    return data;
  }

  /* ------------------------------------------------------------------ the scene
   * The picture follows the run (the server's `scene`, engine/runs.js sceneOf): Tim walks in with a new direction,
   * then James and John read, James draws the run on the board, John makes his call, John prints the spec, then a
   * toast (or didn't land). Each scene is art/<scene>.svg, drawn by art/build.py, put in the page as SVG so app.css can
   * move its parts, and crossfaded. ?scene=<name> shows one scene and holds it (for a look at each one). */
  const SCENES = ['idle', 'tim', 'reading', 'flowchart', 'consulting', 'spec', 'done', 'failed'];
  const CAPTIONS = {
    idle: "At the office. Takeout's on the desk.",
    tim: "Tim's in with your memo.",
    reading: 'James at the keys, John reading the memo.',
    flowchart: 'James is drawing the run on the board.',
    consulting: 'John is making his call.',
    spec: 'John is printing the spec.',
    done: 'Done. The paste blocks are up.',
    failed: "That one didn't land.",
  };

  /* ------------------------------------------------------------------ the clock and the window
   * Every scene is drawn at ten to eleven at night. Here the clock on the wall keeps Central time (its hands turn by
   * their transform about the clock's centre) and the city through the window follows the day: the sky's four bands,
   * the sun crossing between the towers, the moon and the stars after dark, the towers' windows lit at night. */
  const CLOCK = [317, 23];
  const NIGHT = { sky: ['#1B1638', '#231C45', '#2E2552', '#3C2C5C'], back: '#1E2040', front: '#15172E', dark: 1 };
  const DAY = { sky: ['#4A92D8', '#73B0E6', '#A0CBEE', '#CFE3F2'], back: '#7A8EA8', front: '#5A6C88', dark: 0 };
  const SKY = [
    [0, NIGHT], [5.25, NIGHT],
    [6.25, { sky: ['#2E3270', '#5B4C8A', '#C0708A', '#F2A26A'], back: '#2C2F55', front: '#1F2240', dark: 0.7 }],
    [7.5, { sky: ['#4F8FD0', '#79AEDF', '#A9CBE8', '#E5D9BE'], back: '#6F84A0', front: '#51627E', dark: 0.1 }],
    [9, DAY], [16.5, DAY],
    [18.25, { sky: ['#3F5A9C', '#7B6FA8', '#E08A78', '#F5B062'], back: '#4A5272', front: '#33395A', dark: 0.3 }],
    [19.5, { sky: ['#241E4A', '#3A2D63', '#7A4A7A', '#C0607A'], back: '#262848', front: '#1A1C36', dark: 0.8 }],
    [20.75, NIGHT], [24, NIGHT],
  ];
  const WINDOW_BY_DAY = '#A9BCD0';
  const hex = (c) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
  const mix = (a, b, t) => '#' + hex(a).map((v, i) => Math.round(v + (hex(b)[i] - v) * t).toString(16).padStart(2, '0')).join('');

  function chicago() {
    try {
      const p = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Chicago', hour: 'numeric', minute: 'numeric', second: 'numeric', hourCycle: 'h23' }).formatToParts(new Date());
      const g = (t) => Number((p.find((x) => x.type === t) || {}).value || 0);
      return { h: g('hour'), m: g('minute'), s: g('second') };
    } catch (_) {
      const d = new Date();
      return { h: d.getHours(), m: d.getMinutes(), s: d.getSeconds() };
    }
  }

  function skyAt(hour) {
    let i = 0;
    while (i < SKY.length - 2 && SKY[i + 1][0] <= hour) i++;
    const [h0, a] = SKY[i];
    const [h1, b] = SKY[i + 1];
    const t = h1 > h0 ? Math.min(1, Math.max(0, (hour - h0) / (h1 - h0))) : 0;
    return { sky: a.sky.map((c, k) => mix(c, b.sky[k], t)), back: mix(a.back, b.back, t), front: mix(a.front, b.front, t), dark: a.dark + (b.dark - a.dark) * t };
  }

  function setTime(svg, now) {
    const turn = (sel, deg) => { const el = svg.querySelector(sel); if (el) el.setAttribute('transform', `rotate(${deg.toFixed(2)} ${CLOCK[0]} ${CLOCK[1]})`); };
    turn('.clock .hour', ((now.h % 12) + now.m / 60) * 30);
    turn('.clock .minute', (now.m + now.s / 60) * 6);
    turn('.clock .second', now.s * 6);
  }

  function setDay(svg, now) {
    const hour = now.h + now.m / 60;
    const k = skyAt(hour);
    const all = (sel, attr, v) => svg.querySelectorAll(sel).forEach((el) => el.setAttribute(attr, typeof v === 'function' ? v(el) : v));
    all('.window .sky', 'fill', (el) => k.sky[Number(el.getAttribute('data-band')) || 0]);
    all('.window .bldg-back', 'fill', k.back);
    all('.window .bldg-front', 'fill', k.front);
    all('.window .lit', 'fill', (el) => mix(WINDOW_BY_DAY, el.getAttribute('data-c') || '#F2C14E', k.dark));
    all('.window .stars', 'opacity', (k.dark * k.dark).toFixed(2));
    all('.window .moon', 'opacity', k.dark.toFixed(2));
    // Sunrise to sunset in Chicago, near enough the year round; the sun arcs across the window between the towers.
    const t = (hour - 6.25) / (19.5 - 6.25);
    const up = t > 0 && t < 1;
    all('.window .sun', 'opacity', up ? Math.min(1, Math.min(t, 1 - t) * 8).toFixed(2) : '0');
    if (up) all('.window .sun', 'transform', `translate(${(420 + t * 176).toFixed(1)} ${(206 - Math.sin(Math.PI * t) * 108).toFixed(1)})`);
  }

  let lastMinute = -1;
  setInterval(() => {
    const now = chicago();
    const svgs = $('scene').querySelectorAll('svg');
    svgs.forEach((svg) => setTime(svg, now));
    if (now.m !== lastMinute) { lastMinute = now.m; svgs.forEach((svg) => setDay(svg, now)); }
  }, 1000);
  const pinned = (() => { try { const s = new URLSearchParams(location.search).get('scene'); return SCENES.includes(s) ? s : null; } catch (_) { return null; } })();
  const svgCache = new Map();
  let shown = null;
  let wanted = null;

  async function sceneSvg(name) {
    if (!svgCache.has(name)) {
      const res = await fetch(`/art/${name}.svg`, { cache: 'force-cache' });
      if (!res.ok) throw new Error('no scene');
      const doc = new DOMParser().parseFromString(await res.text(), 'image/svg+xml');
      const svg = doc.documentElement;
      if (!svg || svg.nodeName.toLowerCase() !== 'svg') throw new Error('bad scene');
      // Our own files; still, nothing scriptable goes into the page.
      svg.querySelectorAll('script, foreignObject').forEach((n) => n.remove());
      svg.querySelectorAll('*').forEach((n) => [...n.attributes].forEach((a) => { if (/^on/i.test(a.name) || /^\s*javascript:/i.test(a.value)) n.removeAttribute(a.name); }));
      svgCache.set(name, svg);
    }
    return document.importNode(svgCache.get(name), true);
  }

  async function showScene(name) {
    wanted = name;
    if (name === shown) return;
    let svg;
    try { svg = await sceneSvg(name); } catch (_) { return; }
    if (wanted !== name) return;
    const box = $('scene');
    const layer = document.createElement('div');
    layer.className = 'layer';
    const now = chicago();
    setTime(svg, now);
    setDay(svg, now);
    layer.appendChild(svg);
    box.appendChild(layer);
    box.setAttribute('data-scene', name);
    $('scene-cap').textContent = CAPTIONS[name] || '';
    requestAnimationFrame(() => requestAnimationFrame(() => layer.classList.add('is-in')));
    setTimeout(() => { [...box.children].forEach((c) => { if (c !== layer) c.remove(); }); }, 700);
    shown = name;
  }

  const WORDS = { starting: 'Starting', running: 'In session', finished: 'Composed', failed: 'Did not publish', stopped: 'Stopped' };
  const SHAPES = { starting: '◌', running: '●', finished: '■', failed: '▲', stopped: '◆' };

  function clock(iso) {
    if (!iso) return '';
    try {
      return new Intl.DateTimeFormat('en-US', { timeZone: 'America/Chicago', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(new Date(iso)) + ' CDT';
    } catch (_) { return ''; }
  }

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function copyText(text, pre, button) {
    const done = () => { $('live').textContent = 'Copied'; button.textContent = 'Copied'; setTimeout(() => { button.textContent = 'Copy'; }, 1500); };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, () => selectIn(pre));
    } else selectIn(pre);
  }
  function selectIn(pre) {
    const r = document.createRange();
    r.selectNodeContents(pre);
    const s = window.getSelection();
    s.removeAllRanges();
    s.addRange(r);
    $('live').textContent = 'Selected. Copy it from here.';
  }

  function runItem(r) {
    const li = el('li', `run is-${r.status}`);
    const head = el('button', 'run-head');
    head.type = 'button';
    head.setAttribute('aria-expanded', String(open.has(r.id)));
    const status = el('span', 'status');
    status.append(el('span', 'shape', SHAPES[r.status] || '·'), el('span', null, WORDS[r.status] || r.status));
    const first = String(r.direction || '').split('\n')[0];
    head.append(status, el('span', 'what', first.length > 140 ? `${first.slice(0, 140)}…` : first),
      el('span', 'when', `${r.runId}${r.training ? ' · training' : ''} · ${clock(r.created)}`));
    li.append(head);
    const body = el('div', 'run-body');
    body.hidden = !open.has(r.id);
    if (r.status === 'running' || r.status === 'starting') body.append(el('p', 'hint', `${r.step || 'Working'}.`));
    if (r.reason) body.append(el('p', 'reason', r.reason));
    if (r.status === 'finished') {
      body.append(el('p', 'hint', `On fleet-ops main as ${r.folder} (${String(r.sha || '').slice(0, 9)}). Paste each block into a new Claude chat opened on the Hub folder.`));
      for (const b of r.blocks || []) {
        const box = el('div', 'block');
        const bar = el('div', 'block-bar');
        bar.append(el('h3', null, `Lane ${b.lane} · ${b.title}`));
        const copy = el('button', 'copy', 'Copy');
        copy.type = 'button';
        const pre = el('pre', null, b.text);
        copy.addEventListener('click', () => copyText(b.text, pre, copy));
        bar.append(copy);
        box.append(bar);
        if (b.flags && b.flags.length) box.append(el('p', 'flags', `Mentions: ${b.flags.join(', ')}. Read it before you paste.`));
        box.append(pre);
        body.append(box);
      }
    }
    head.addEventListener('click', () => {
      const now = !open.has(r.id);
      if (now) open.add(r.id); else open.delete(r.id);
      head.setAttribute('aria-expanded', String(now));
      body.hidden = !now;
    });
    li.append(body);
    return li;
  }

  async function refresh() {
    let s;
    try { s = await call('GET', '/api/state'); } catch (e) { $('ask-msg').textContent = e.message; return; }
    showScene(pinned || (SCENES.includes(s.scene) ? s.scene : 'idle'));
    busy = !!s.running;
    $('go').disabled = busy;
    $('now').hidden = !busy;
    if (busy) $('now-text').textContent = `${s.running.runId}: ${s.running.step || 'working'}.`;
    const list = $('list');
    const keep = window.getSelection && window.getSelection().toString();
    if (!keep) list.replaceChildren(...s.runs.map(runItem));
    $('empty').hidden = s.runs.length > 0;
    if (!s.claude) $('ask-msg').textContent = 'Claude Code is not on this computer, so they cannot start.';
  }

  $('ask').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const direction = $('direction').value.trim();
    if (direction.length < 8) { $('ask-msg').textContent = 'Tell them what you need: a sentence or two is enough.'; $('direction').focus(); return; }
    $('go').disabled = true;
    $('ask-msg').textContent = 'Starting…';
    try {
      const { run } = await call('POST', '/api/runs', { direction, training: $('training').checked });
      $('ask-msg').textContent = `${run.runId} started. It takes a while: they read before they write.`;
      $('direction').value = '';
      open.add(run.id);
    } catch (e) { $('ask-msg').textContent = e.message; }
    refresh();
  });

  $('stop').addEventListener('click', async () => {
    try { await call('POST', '/api/runs/stop', {}); $('ask-msg').textContent = 'Stopped. Nothing was published.'; } catch (e) { $('ask-msg').textContent = e.message; }
    refresh();
  });

  $('joke').textContent = JOKES[Math.floor(Math.random() * JOKES.length)];
  refresh();
  setInterval(refresh, 5000);
}());
