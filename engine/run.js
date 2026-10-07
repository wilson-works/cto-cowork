'use strict';

/**
 * engine/run.js — the runner for one composing run (engine/runs.js starts it detached). Node built-ins only.
 *
 *   node engine/run.js <id>
 *
 * In order, writing each step to the run file (a heartbeat every 10 s) and its log:
 *   1. makes the run's staging folder <rigs>/cowork-<id> with .rig-meta.json, context/ (copies of the Hub's CLAUDE.md
 *      and .claude/rules) and run/prompts/; refuses when the folder is already there;
 *   2. fetches fleet-ops main into its own ref refs/cowork/<id> (never FETCH_HEAD, never a checkout) and refuses when
 *      the run's folder is already on it;
 *   3. starts Claude Code with compose.args() in the staging folder, its stream in the run's log, under a hard cap
 *      (cap_minutes, default 40): past it the program and what it started are stopped, and nothing is published;
 *   4. when it ends cleanly, checks run/ (publish.check) and puts it on fleet-ops main (publish.publish);
 *   5. posts one short note to the office's group chat, as the run's own session, scoped to this run so no working
 *      session is interrupted; marks the run finished or failed, with the reason in plain words; releases the lock.
 * A run stopped from the dashboard, or one that ends with an error, publishes nothing. The staging folder stays (the
 * rig gate, not the space, removes rigs), so partial work can be read.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { spawn, execFileSync } = require('child_process');
const config = require('./config');
const compose = require('./compose');
const runs = require('./runs');
const publish = require('./publish');

const HOME = path.resolve(__dirname, '..');
const BEAT_MS = 10 * 1000;
// Set by a Claude Code session in what it starts; a run is its own session, so these are not passed on (Louise's list).
const SESSION_ENV = ['CLAUDECODE', 'CLAUDE_CODE_ENTRYPOINT', 'CLAUDE_CODE_SESSION_ID', 'CLAUDE_CODE_CHILD_SESSION',
  'CLAUDE_CODE_SESSION_ATTENDED', 'CLAUDE_CODE_MESSAGING_SOCKET', 'CLAUDE_CODE_MESSAGING_TOKEN', 'CLAUDE_CODE_EXECPATH',
  'CLAUDE_CODE_SSE_PORT', 'CLAUDE_PID', 'CLAUDE_AGENT_SDK_VERSION'];

function copyContext(cfg, dir) {
  fs.mkdirSync(path.join(dir, 'rules'), { recursive: true });
  const copied = [];
  const hubMd = path.join(cfg.hub || '', 'CLAUDE.md');
  if (cfg.hub && fs.existsSync(hubMd)) { fs.copyFileSync(hubMd, path.join(dir, 'CLAUDE.md')); copied.push('CLAUDE.md'); }
  const rules = path.join(cfg.hub || '', '.claude', 'rules');
  let names = [];
  try { names = fs.readdirSync(rules).filter((n) => /^[\w.-]+\.md$/.test(n)); } catch (_) { /* none */ }
  for (const n of names) { fs.copyFileSync(path.join(rules, n), path.join(dir, 'rules', n)); copied.push(`rules/${n}`); }
  return copied;
}

/** The final "result" line of the stream: { text, turns, ms, error } or null. */
function resultOf(logPath) {
  let tail = '';
  try {
    const st = fs.statSync(logPath);
    const fd = fs.openSync(logPath, 'r');
    const len = Math.min(st.size, 256 * 1024);
    const buf = Buffer.alloc(len);
    fs.readSync(fd, buf, 0, len, st.size - len);
    fs.closeSync(fd);
    tail = buf.toString('utf8');
  } catch (_) { return null; }
  const lines = tail.split(/\r?\n/).reverse();
  for (const l of lines) {
    if (!l.startsWith('{') || !l.includes('"type":"result"')) continue;
    try {
      const j = JSON.parse(l);
      return { text: String(j.result || '').slice(0, 600), turns: j.num_turns || null, ms: j.duration_ms || null, error: !!j.is_error };
    } catch (_) { /* a cut line */ }
  }
  return null;
}

/** One short post on the office's group chat, as this run's session, scoped to the run (it fans out to no one). */
function officeNote(cfg, rec, text, note) {
  try {
    if (!cfg.fleetOffice || !rec.session_id) return;
    const C = require(path.join(cfg.fleetOffice, 'src', 'server', 'channel'));
    const geo = require(path.join(cfg.fleetOffice, 'src', 'server', 'geography'));
    const refusal = C.contentRefusal(text, false);
    if (refusal) { note(`office note not posted: ${refusal}`); return; }
    const home = process.env.FLEET_OFFICE_HOME || path.join(process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local'), 'FleetOffice');
    const now = Date.now();
    const post = {
      id: `g${now.toString(36)}${Math.random().toString(36).slice(2, 6)}`, at: now,
      from: { kind: 'session', callsign: 'James and John', machine: geo.thisMachine(), session_id: rec.session_id },
      scope: `run:${rec.runId.toLowerCase()}`, to: null, text, client_work: false,
    };
    fs.mkdirSync(path.join(home, 'channel'), { recursive: true });
    fs.appendFileSync(path.join(home, 'channel', 'outbox.jsonl'), `${JSON.stringify(post)}\n`, 'utf8');
    note(`office note posted ${post.id}`);
  } catch (e) { note(`office note not posted: ${e.message}`); }
}

function killTree(pid) {
  try {
    if (process.platform === 'win32') execFileSync('taskkill', ['/PID', String(pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore', timeout: 15000 });
    else process.kill(-pid, 'SIGTERM');
  } catch (_) { /* gone already */ }
}

async function main(id) {
  const home = HOME;
  let rec = runs.read(home, id);
  if (!rec || rec.status !== 'starting') return;
  const logPath = runs.logFile(home, id);
  const note = (m) => { try { fs.appendFileSync(logPath, `[${compose.stamp(new Date())}] ${m}\n`); } catch (_) { /* no log */ } };
  const set = (patch) => { rec = runs.update(home, id, patch); return rec; };
  set({ status: 'running', runner_pid: process.pid, beat: new Date().toISOString(), step: 'getting ready' });
  const timer = setInterval(() => { try { const r = runs.read(home, id); if (r && r.status === 'running') set({ beat: new Date().toISOString() }); } catch (_) { /* next beat */ } }, BEAT_MS);
  const fail = (reason) => { set({ status: 'failed', reason, ended: new Date().toISOString() }); note(`FAILED: ${reason}`); };
  let cfg;
  try {
    cfg = config.load(home);
    const staging = path.join(cfg.rigs, `cowork-${id}`);
    if (fs.existsSync(staging)) { fail(`Its staging folder is already there (${staging}); nothing was started.`); return; }
    const runDir = path.join(staging, 'run');
    fs.mkdirSync(path.join(runDir, 'prompts'), { recursive: true });
    fs.writeFileSync(path.join(staging, '.rig-meta.json'), `${JSON.stringify({
      rig: `cowork-${id}`, kind: 'cowork-staging', made_by: 'cto-cowork engine/run.js', run: rec.runId,
      created: rec.started, purpose: "James and John's Coworking Space: one composing run's working folder. Its run/ is what was published to fleet-ops.",
      remove: 'only through the rig gate',
    }, null, 2)}\n`, 'utf8');
    const copied = copyContext(cfg, path.join(staging, 'context'));
    set({ staging, step: 'reading fleet-ops' });
    note(`run ${rec.runId} (${rec.training ? 'TRAINING' : 'live'}) staging ${staging}; context ${copied.length} files`);

    const ref = `refs/cowork/${id}`;
    const base = await publish.fetchBase(cfg.fleetOps, ref);
    if (publish.git(cfg.fleetOps, ['ls-tree', '--name-only', base, '--', `${rec.folder}/`]).out) { fail(`${rec.folder} is already on fleet-ops main.`); return; }
    note(`fleet-ops main at ${base.slice(0, 9)} (${ref})`);

    const sessionId = crypto.randomUUID();
    const args = compose.args({
      cfg, training: rec.training, runId: rec.runId, folder: rec.folder, runDir, codeZone: cfg.codeZone,
      direction: rec.direction, started: rec.started, sessionId,
    });
    const env = Object.fromEntries(Object.entries(process.env).filter(([k]) => !SESSION_ENV.includes(k.toUpperCase())));
    Object.assign(env, { COWORK_FLEET_REF: ref, GIT_TERMINAL_PROMPT: '0', GCM_INTERACTIVE: 'never', GIT_PAGER: 'cat' });
    const out = fs.openSync(logPath, 'a');
    let child;
    try {
      child = spawn(cfg.claude, args, { cwd: staging, env, stdio: ['ignore', out, out], windowsHide: true, detached: process.platform !== 'win32' });
    } finally { fs.closeSync(out); }
    let capped = false;
    const exit = new Promise((resolve) => {
      child.on('error', (e) => resolve({ code: null, error: e.message }));
      child.on('exit', (code, signal) => resolve({ code, signal }));
    });
    if (child.pid) set({ claude_pid: child.pid, session_id: sessionId, step: 'James is reading and planning' });
    note(`Claude Code started, pid ${child.pid}, session ${sessionId}, cap ${cfg.capMs / 60000} min`);
    const cap = setTimeout(() => { capped = true; note('cap reached: stopping Claude Code'); killTree(child.pid); }, cfg.capMs);
    const ended = await exit;
    clearTimeout(cap);
    const result = resultOf(logPath);
    note(`Claude Code ended: code ${ended.code}${ended.signal ? ` signal ${ended.signal}` : ''}${ended.error ? ` error ${ended.error}` : ''}`);
    rec = runs.read(home, id);
    if (result) set({ result });
    if (rec.status === 'stopped') { note('stopped from the dashboard: nothing published'); officeNote(cfg, rec, `James and John stopped ${rec.runId} when you asked. Nothing was published.`, note); return; }
    if (capped) { fail(`They ran past the ${cfg.capMs / 60000}-minute cap and were stopped. Nothing was published; what they wrote is in the run's staging folder.`); officeNote(cfg, rec, `James and John ran out of time on ${rec.runId}. Nothing was published; the reason is on the Coworking Space door.`, note); return; }
    if (ended.code !== 0 || (result && result.error)) { fail(`Claude Code ended with ${ended.error || `code ${ended.code}`}. Nothing was published; the details are in the run's log.`); officeNote(cfg, rec, `James and John could not finish ${rec.runId}. Nothing was published; the reason is on the Coworking Space door.`, note); return; }

    set({ step: 'checking the run folder' });
    const checked = publish.check(runDir, { training: rec.training, runId: rec.runId });
    note(`checked: ${checked.files.length} files, ${checked.blocks.length} paste blocks`);
    set({ step: 'publishing to fleet-ops' });
    const marker = `[cowork][${rec.runId}]`;
    const res = await publish.publish({
      repo: cfg.fleetOps, ref, folder: rec.folder, files: checked.files, marker,
      subject: `${marker} COMPOSE: ${checked.title.replace(/^\S+:\s*/, '').slice(0, 120)}`,
      msgFile: path.join(staging, 'commit-msg.txt'), indexFile: path.join(runs.dirs(home).state, `idx-${id}`), log: note,
    });
    set({ status: 'finished', step: 'published', sha: res.sha, blocks: checked.blocks, ended: new Date().toISOString() });
    note(`PUBLISHED ${res.sha} (${res.tries} ${res.tries === 1 ? 'try' : 'tries'}) as ${rec.folder}`);
    const lanes = checked.blocks.map((b) => b.lane).join(', ');
    officeNote(cfg, rec, `James and John composed ${rec.runId}${rec.training ? ', a training run,' : ''} with ${checked.blocks.length} lane${checked.blocks.length === 1 ? '' : 's'} (${lanes}). Its paste blocks are on the Coworking Space door.`, note);
  } catch (e) {
    fail(e && e.refused ? `${e.message} Nothing was published.` : `Something went wrong: ${String(e && e.message).slice(0, 300)} Nothing was published.`);
    if (cfg && rec && rec.session_id) officeNote(cfg, rec, `James and John could not publish ${rec.runId}. The reason is on the Coworking Space door.`, note);
  } finally {
    clearInterval(timer);
    runs.releaseLock(home, id);
  }
}

if (require.main === module) {
  main(process.argv[2]).catch((e) => {
    try { runs.update(HOME, process.argv[2], { status: 'failed', reason: `The runner stopped: ${String(e && e.message).slice(0, 300)}`, ended: new Date().toISOString() }); } catch (_) { /* nothing more */ }
    runs.releaseLock(HOME, process.argv[2]);
  });
}

module.exports = { main, resultOf, copyContext };
