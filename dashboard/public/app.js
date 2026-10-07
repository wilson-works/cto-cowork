'use strict';

// The Coworking Space's page: one direction box, the runs, and each finished run's paste blocks with a Copy button.
(function () {
  const token = document.querySelector('meta[name="cowork-token"]').content;
  const $ = (id) => document.getElementById(id);
  const JOKES = [
    'James: "Easy does it. One lane at a time, and every lane gets a DONE-WHEN."',
    'John: "Relax. I read the diff. Twice."',
    'James: "Short version first. Then we earn the long one. We move."',
    'John: "Smallest correct change. Then coffee."',
    'James: "We plan it, you paste it. Nobody starts a lane behind your back."',
    'John: "Two lanes in one file is how Tuesdays get long."',
    'James: "The gate grades the work. We don\'t grade our own homework."',
    'John: "Clean diff, clean conscience."',
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
   * then James and John read, draw the flowchart, John makes his call, John draws the spec sheets, then done (or
   * didn't land). Each scene is art/<scene>.svg, drawn by art/build.py, put in the page as SVG so app.css can move its
   * parts, and crossfaded. ?scene=<name> shows one scene and holds it (for a look at each one). */
  const SCENES = ['idle', 'tim', 'reading', 'flowchart', 'consulting', 'spec', 'done', 'failed'];
  const CAPTIONS = {
    idle: "In the office. Dinner's on the table.",
    tim: 'Tim just walked in with a new direction.',
    reading: 'Reading the state. Takeout in hand.',
    flowchart: 'James is drawing the run on the board.',
    consulting: 'John is making his call.',
    spec: 'John is drawing the spec sheets.',
    done: 'Done. The paste blocks are up.',
    failed: "That one didn't land.",
  };
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
    layer.appendChild(svg);
    box.appendChild(layer);
    box.setAttribute('data-scene', name);
    $('scene-cap').textContent = CAPTIONS[name] || '';
    requestAnimationFrame(() => requestAnimationFrame(() => layer.classList.add('is-in')));
    setTimeout(() => { [...box.children].forEach((c) => { if (c !== layer) c.remove(); }); }, 700);
    shown = name;
  }

  const WORDS = { starting: 'Starting', running: 'Working', finished: 'Composed', failed: 'Did not publish', stopped: 'Stopped' };
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
