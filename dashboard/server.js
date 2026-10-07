'use strict';

/**
 * dashboard/server.js — James and John's Coworking Space: its page and the JSON API the page reads. Node built-ins only.
 *
 *   node dashboard/server.js        (from the space's folder; "start" in agent.json says so)
 *
 * Who it answers, and what it may touch:
 *   - Listens on 127.0.0.1 only, on the port from engine/config.js (cowork.config.json, else probe.port in agent.json,
 *     else 7560). Writes its pid to dashboard/.pid while it runs and clears it when it stops.
 *   - Answers only Host 127.0.0.1, localhost, or the phone host in cowork.config.json (machine-local, never committed).
 *     Any other Host gets 403, so a page elsewhere cannot point a name of its own at this port.
 *   - A per-start token: made fresh each time the server starts, written into the page it serves, and required on
 *     every /api/ request as the X-Cowork-Token header. The door is / and the probes are /health and /mark.svg, so no
 *     address the office opens or probes ever carries the token (the trap Tony's /open set, HK1004-N I6).
 *   - A POST must be JSON and, when the browser says where it came from (Origin, Sec-Fetch-Site), from this page.
 *   - Starts one program: the runner (engine/run.js), which starts Claude Code with arguments fixed in engine/compose.js.
 *     Only the direction's text reaches the run, through its run file, never a command line. It stops only the run it
 *     recorded.
 *
 * Files it serves (GET and HEAD), never a dot-file:
 *   /                  dashboard/public/index.html, with this start's token in it
 *   /<file>            dashboard/public/<file>   (app.js, app.css)
 *   /art/<file>        art/<file>
 *   /art.svg, /mark.svg   the scene and the mark
 *
 * The API:
 *   GET  /health                    {"ok":true}, no token, ever: the office probes it
 *   GET  /api/state                 { name, running, runs: [...], scene, claude, fleetOps, capMinutes }; scene is which
 *                                   picture the page shows (engine/runs.js sceneOf), one of art/<scene>.svg
 *   POST /api/runs  { direction, training }   starts one run: 202 { run }; 409 with { error, reason } when it cannot
 *                                   (running | no-claude | no-fleet-ops); 400 (empty | long)
 *   POST /api/runs/stop  {}         stops the run that is going: 200 { run }; 409 (not-running | starting | not-ours)
 * An error is { "error": "<a plain sentence>" } with a 4xx status.
 *
 *   createServer(opts)   the server, not yet listening. opts { home, cfg, token, runs } (runs replaces engine/runs.js)
 */

const fs = require('fs');
const http = require('http');
const path = require('path');
const crypto = require('crypto');
const config = require('../engine/config');

const HOME = path.resolve(__dirname, '..');
const BODY_MAX = 16 * 1024;
const STATIC_MAX = 4 * 1024 * 1024;
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.json': 'application/json; charset=utf-8', '.ico': 'image/x-icon',
};
const PAGE_CSP = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; " +
  "connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'";
const SVG_CSP = "default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; sandbox";

function send(res, status, body, headers) {
  const buf = Buffer.isBuffer(body) ? body : Buffer.from(String(body));
  res.writeHead(status, Object.assign({
    'Content-Length': buf.length, 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer', 'Cache-Control': 'no-store',
  }, headers));
  res.end(res.req.method === 'HEAD' ? undefined : buf);
}
const json = (res, status, obj) => send(res, status, JSON.stringify(obj), { 'Content-Type': 'application/json; charset=utf-8' });
const fail = (res, status, message, extra) => json(res, status, Object.assign({ error: message }, extra || {}));

function within(base, parts) {
  if (!parts.length || parts.some((p) => !p || p.startsWith('.') || /[\\/:\0]/.test(p))) return null;
  const file = path.join(base, ...parts);
  let st;
  try { st = fs.lstatSync(file); } catch (_) { return null; }
  if (!st.isFile() || st.size > STATIC_MAX) return null;
  const rel = path.relative(base, file);
  return rel && !rel.startsWith('..') && !path.isAbsolute(rel) ? file : null;
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    let done = false;
    req.on('data', (c) => {
      if (done) return;
      size += c.length;
      if (size > BODY_MAX) { done = true; reject(Object.assign(new Error('That is more than the space takes in one go.'), { status: 413 })); return; }
      chunks.push(c);
    });
    req.on('end', () => { if (!done) { done = true; resolve(Buffer.concat(chunks).toString('utf8')); } });
    req.on('error', (e) => { if (!done) { done = true; reject(e); } });
  });
}

function sameToken(a, b) {
  const x = Buffer.from(String(a || ''));
  const y = Buffer.from(String(b || ''));
  return x.length === y.length && x.length > 0 && crypto.timingSafeEqual(x, y);
}

function createServer(opts) {
  const o = opts || {};
  const home = path.resolve(o.home || HOME);
  const cfg = o.cfg;
  const token = o.token;
  const runs = o.runs || require('../engine/runs');
  const hosts = new Set(['127.0.0.1', 'localhost']);
  if (cfg.phoneHost) hosts.add(cfg.phoneHost);
  const dirs = { public: path.join(home, 'dashboard', 'public'), art: path.join(home, 'art') };

  function postRefused(req) {
    if (!/^application\/json\b/i.test(String(req.headers['content-type'] || ''))) return 'Send this as JSON (Content-Type: application/json).';
    const site = String(req.headers['sec-fetch-site'] || '');
    if (site && site !== 'same-origin' && site !== 'none') return "Only the space's own page can ask for that.";
    const origin = req.headers.origin;
    if (origin === 'null') return "Only the space's own page can ask for that.";
    if (origin) {
      let h = null;
      try { h = new URL(origin).hostname.toLowerCase(); } catch (_) { /* refused below */ }
      if (!h || !hosts.has(h)) return "Only the space's own page can ask for that.";
    }
    return null;
  }

  async function api(req, res, url) {
    if (!sameToken(req.headers['x-cowork-token'], token)) return fail(res, 403, 'This page is out of date. Reload it.');
    const p = url.pathname;
    const m = req.method;
    if (p === '/api/state' && m === 'GET') {
      const list = runs.list(home);
      const cur = runs.current(home);
      return json(res, 200, {
        name: "James and John's Coworking Space", running: cur ? runs.summary(cur) : null, runs: list,
        scene: runs.sceneOf ? runs.sceneOf(home, cur, list) : 'idle',
        claude: !!cfg.claude, fleetOps: !!cfg.fleetOps, capMinutes: Math.round(cfg.capMs / 60000),
      });
    }
    if ((p === '/api/runs' || p === '/api/runs/stop') && m === 'POST') {
      const refused = postRefused(req);
      if (refused) return fail(res, 403, refused);
      let body;
      try { body = JSON.parse(await readBody(req) || '{}'); } catch (e) {
        if (e.status) throw e;
        return fail(res, 400, 'That was not readable JSON.');
      }
      if (!body || typeof body !== 'object' || Array.isArray(body)) return fail(res, 400, 'Send one JSON object.');
      try {
        if (p === '/api/runs') return json(res, 202, { run: await runs.start(home, cfg, body) });
        return json(res, 200, { run: runs.stop(home) });
      } catch (e) {
        if (e && e.reason) return fail(res, e.status, e.message, { reason: e.reason });
        throw e;
      }
    }
    if (['/api/state', '/api/runs', '/api/runs/stop'].includes(p)) return fail(res, 405, 'That address does not take that kind of request.');
    return fail(res, 404, 'Not found.');
  }

  function statics(req, res, url) {
    if (req.method !== 'GET' && req.method !== 'HEAD') return fail(res, 405, 'That address does not take that kind of request.');
    let parts;
    try { parts = url.pathname.split('/').slice(1).map(decodeURIComponent); } catch (_) { return fail(res, 400, 'That address is not readable.'); }
    if (url.pathname === '/') {
      const f = within(dirs.public, ['index.html']);
      if (!f) return fail(res, 404, 'Not found.');
      const page = fs.readFileSync(f, 'utf8').replace('__COWORK_TOKEN__', token);
      return send(res, 200, page, { 'Content-Type': TYPES['.html'], 'Content-Security-Policy': PAGE_CSP });
    }
    let file = null;
    if (url.pathname === '/art.svg' || url.pathname === '/mark.svg') file = within(home, [url.pathname.slice(1)]);
    else if (parts[0] === 'art') file = within(dirs.art, parts.slice(1));
    else if (parts[0] !== 'index.html') file = within(dirs.public, parts);
    if (!file) return fail(res, 404, 'Not found.');
    const ext = path.extname(file).toLowerCase();
    if (!TYPES[ext]) return fail(res, 404, 'Not found.');
    const headers = { 'Content-Type': TYPES[ext] };
    if (ext === '.svg') headers['Content-Security-Policy'] = SVG_CSP;
    return send(res, 200, fs.readFileSync(file), headers);
  }

  return http.createServer((req, res) => {
    const host = String(req.headers.host || '').toLowerCase().replace(/:\d+$/, '');
    if (!hosts.has(host)) { send(res, 403, 'unknown host', { 'Content-Type': 'text/plain; charset=utf-8' }); return; }
    let url;
    try { url = new URL(req.url, 'http://127.0.0.1'); } catch (_) { fail(res, 400, 'That address is not readable.'); return; }
    if (url.pathname === '/health') { json(res, 200, { ok: true }); return; }
    const handle = url.pathname.startsWith('/api/') ? api(req, res, url) : Promise.resolve(statics(req, res, url));
    handle.catch((e) => {
      if (res.headersSent) { res.destroy(); return; }
      if (e && e.status) { fail(res, e.status, e.message); return; }
      process.stderr.write(`${new Date().toISOString()} ${req.method} ${url.pathname}: ${(e && e.stack) || e}\n`);
      fail(res, 500, "Something went wrong on our end. Try again in a moment; if it keeps happening, the details are in the space's log.");
    });
  });
}

module.exports = { createServer };

if (require.main === module) {
  let cfg;
  try { cfg = config.load(HOME); } catch (e) { process.stderr.write(`${e.message}\nThe Coworking Space was not started.\n`); process.exit(2); }
  const pidFile = path.join(HOME, 'dashboard', '.pid');
  const server = createServer({ home: HOME, cfg, token: crypto.randomBytes(24).toString('hex') });
  const clearPid = () => {
    try { if (fs.readFileSync(pidFile, 'utf8').trim() === String(process.pid)) fs.rmSync(pidFile, { force: true }); } catch (_) { /* not ours, or gone */ }
  };
  server.on('error', (e) => {
    process.stderr.write(e.code === 'EADDRINUSE'
      ? `Port ${cfg.port} is already in use, so the Coworking Space did not start. Give it another: "port" in cowork.config.json.\n`
      : `${e.message}\n`);
    process.exit(1);
  });
  server.listen(cfg.port, '127.0.0.1', () => {
    fs.writeFileSync(pidFile, String(process.pid), 'utf8');
    process.stdout.write(`James and John's Coworking Space is on http://127.0.0.1:${cfg.port}/${cfg.phoneHost ? ` and ${cfg.phoneHost}` : ''}\n`);
    for (const n of cfg.notes) process.stdout.write(`Note: ${n}\n`);
  });
  for (const sig of ['SIGINT', 'SIGTERM']) process.on(sig, () => { clearPid(); server.close(() => process.exit(0)); setTimeout(() => process.exit(0), 1000).unref(); });
  process.on('exit', clearPid);
}
