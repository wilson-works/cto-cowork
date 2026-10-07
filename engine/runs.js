'use strict';

/**
 * engine/runs.js — start, stop and list the space's composing runs, from its dashboard. Node built-ins only.
 *
 * State, all in state/ (git-ignored):
 *   state/runs/<id>.json   one run: { id, runId, name, folder, training, direction, created, status, step, runner_pid,
 *                          claude_pid, session_id, beat, started, ended, reason, sha, blocks, result }
 *                          status: starting | running | finished | failed | stopped
 *   state/runs/<id>.log    the runner's notes and Claude Code's stream (what it read, wrote and said)
 *   state/lock             the run that is going: taken with open('wx'), so two starts can never both win
 *
 * start({ direction, training }) refuses (an error with .status and .reason) when a run is going (409 running),
 * Claude Code or fleet-ops is not on this computer (409 no-claude / no-fleet-ops), or the direction is empty or too
 * long (400). Otherwise it takes the lock, writes the run file and starts engine/run.js detached through
 * engine/detach.vbs (WScript.Shell.Run on Windows: the runner holds none of the server's handles), then waits up to
 * 15 s for the runner to say it is there. The direction goes into the run file, never onto a command line.
 *
 * A run whose runner has gone quiet (no heartbeat for a minute, or its pid gone) is marked failed, "runner lost",
 * and its lock released, the next time anyone looks.
 *
 * stop() stops only the Claude Code the runner recorded: its pid still alive, still claude.exe, started no earlier
 * than the run (the rule wake.js uses for Sleep), with taskkill /T /F. Nothing in a request names a pid.
 */

const fs = require('fs');
const path = require('path');
const { spawn, execFileSync } = require('child_process');
const compose = require('./compose');

const BEAT_STALE_MS = 60 * 1000;
const STARTING_MS = 30 * 1000;
const DIRECTION_MAX = 4000;
const ID_RE = /^\d{8}-\d{4}$/;

const dirs = (home) => ({ state: path.join(home, 'state'), runs: path.join(home, 'state', 'runs'), lock: path.join(home, 'state', 'lock') });
const runFile = (home, id) => path.join(dirs(home).runs, `${id}.json`);
const logFile = (home, id) => path.join(dirs(home).runs, `${id}.log`);
const refuse = (status, reason, message) => Object.assign(new Error(message), { status, reason });

function readJson(f) { try { return JSON.parse(fs.readFileSync(f, 'utf8').replace(/^﻿/, '')); } catch (_) { return null; } }
function writeJson(f, obj) {
  fs.mkdirSync(path.dirname(f), { recursive: true });
  const tmp = `${f}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, `${JSON.stringify(obj, null, 2)}\n`, 'utf8');
  try { fs.renameSync(tmp, f); } catch (_) { fs.writeFileSync(f, `${JSON.stringify(obj, null, 2)}\n`, 'utf8'); fs.rmSync(tmp, { force: true }); }
}
const read = (home, id) => (ID_RE.test(String(id)) ? readJson(runFile(home, id)) : null);
function update(home, id, patch) {
  const r = read(home, id) || {};
  const next = Object.assign(r, patch);
  writeJson(runFile(home, id), next);
  return next;
}

function alive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return false;
  try { process.kill(pid, 0); return true; } catch (e) { return e.code === 'EPERM'; }
}

/** { image, created } of a live pid on Windows, or null. */
function inspect(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return null;
  try {
    const ps = `$p = Get-CimInstance Win32_Process -Filter "ProcessId=${pid}"; if ($p) { $p.CreationDate.ToUniversalTime().ToString('o'); $p.Name }`;
    const out = execFileSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', ps], { encoding: 'utf8', windowsHide: true, timeout: 20000 });
    const [when, name] = out.split(/\r?\n/);
    const created = Date.parse(when);
    return Number.isFinite(created) ? { created, image: String(name || '').trim().toLowerCase() } : null;
  } catch (_) { return null; }
}

function releaseLock(home, id) {
  const f = dirs(home).lock;
  try { if (fs.readFileSync(f, 'utf8').trim() === id) fs.rmSync(f, { force: true }); } catch (_) { /* not ours, or gone */ }
}

/** The run that is going, or null. A run whose runner went quiet is marked failed here and its lock released. */
function current(home, now) {
  const at = now || Date.now();
  let id;
  try { id = fs.readFileSync(dirs(home).lock, 'utf8').trim(); } catch (_) { return null; }
  const r = read(home, id);
  const lost = (why) => { if (r) update(home, id, { status: 'failed', reason: why, ended: new Date(at).toISOString() }); releaseLock(home, id); return null; };
  if (!r) return lost('runner lost');
  if (!['starting', 'running'].includes(r.status)) { releaseLock(home, id); return null; }
  if (r.status === 'starting') return at - Date.parse(r.created) < STARTING_MS ? r : lost('The run never started. The details are in its log.');
  if (!(at - Date.parse(r.beat) < BEAT_STALE_MS) || !alive(r.runner_pid)) return lost('runner lost: the run stopped reporting. The details are in its log.');
  return r;
}

/** What the dashboard shows of a run (never the log, never a pid). */
function summary(r) {
  return {
    id: r.id, runId: r.runId, folder: r.folder, training: !!r.training, status: r.status, step: r.step || null,
    direction: r.direction, created: r.created, started: r.started || null, ended: r.ended || null,
    reason: r.reason || null, sha: r.sha || null, blocks: r.blocks || [], result: r.result || null,
  };
}

function list(home) {
  current(home);
  let names = [];
  try { names = fs.readdirSync(dirs(home).runs).filter((n) => /^\d{8}-\d{4}\.json$/.test(n)); } catch (_) { /* none yet */ }
  return names.map((n) => readJson(path.join(dirs(home).runs, n))).filter(Boolean)
    .sort((a, b) => String(b.created).localeCompare(String(a.created))).slice(0, 50).map(summary);
}

/** Start the runner detached, holding nothing of ours. */
function launchDetached(home, id) {
  const runner = path.join(__dirname, 'run.js');
  const out = fs.openSync(logFile(home, id), 'a');
  fs.closeSync(out);
  if (process.platform === 'win32') {
    const w = spawn('wscript.exe', ['//B', '//Nologo', path.join(__dirname, 'detach.vbs'), process.execPath, runner, id],
      { cwd: home, detached: true, stdio: 'ignore', windowsHide: true });
    w.on('error', () => { /* seen below: the runner never reports */ });
    w.unref();
    return;
  }
  const c = spawn(process.execPath, [runner, id], { cwd: home, detached: true, stdio: 'ignore' });
  c.on('error', () => { /* seen below */ });
  c.unref();
}

async function start(home, cfg, body, opts) {
  const o = opts || {};
  const direction = typeof body.direction === 'string' ? body.direction.replace(/\r\n/g, '\n').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, '').trim() : '';
  if (direction.length < 8) throw refuse(400, 'empty', 'Tell James and John what you need: a sentence or two is enough.');
  if (direction.length > DIRECTION_MAX) throw refuse(400, 'long', `That is more than ${DIRECTION_MAX} characters. Say it shorter, or point at a file in fleet-ops.`);
  if (!cfg.claude) throw refuse(409, 'no-claude', 'Claude Code is not on this computer, so James and John cannot start.');
  if (!cfg.fleetOps || !fs.existsSync(path.join(cfg.fleetOps, '.git'))) throw refuse(409, 'no-fleet-ops', 'fleet-ops is not on this computer, so there is nowhere to write a run.');
  if (current(home)) throw refuse(409, 'running', 'James and John are already working on one. One run at a time.');

  const now = new Date();
  const training = body.training === true;
  const n = compose.ids(now, training);
  if (read(home, n.id)) throw refuse(409, 'running', 'A run started this same minute. Try again in a minute.');
  fs.mkdirSync(dirs(home).runs, { recursive: true });
  let fd;
  try { fd = fs.openSync(dirs(home).lock, 'wx'); } catch (_) { throw refuse(409, 'running', 'James and John are already working on one. One run at a time.'); }
  fs.writeSync(fd, n.id);
  fs.closeSync(fd);
  writeJson(runFile(home, n.id), {
    id: n.id, runId: n.runId, name: n.name, folder: n.folder, training, direction,
    created: now.toISOString(), started: compose.stamp(now), status: 'starting', step: 'getting ready',
  });
  (o.launch || launchDetached)(home, n.id);
  const until = Date.now() + (o.waitMs || 15000);
  for (;;) {
    const r = read(home, n.id);
    if (r && (r.runner_pid || r.status !== 'starting')) return summary(r);
    if (Date.now() > until) break;
    await new Promise((res) => setTimeout(res, 200));
  }
  update(home, n.id, { status: 'failed', reason: 'The run did not start. The details are in its log.', ended: new Date().toISOString() });
  releaseLock(home, n.id);
  throw refuse(500, 'not-started', "James and John couldn't get started. The details are in the run's log.");
}

function stop(home) {
  const r = current(home);
  if (!r) throw refuse(409, 'not-running', 'Nothing is running.');
  if (!r.claude_pid) throw refuse(409, 'starting', 'They are only just sitting down. Try again in a moment.');
  const info = alive(r.claude_pid) ? inspect(r.claude_pid) : null;
  if (!info || !/^claude(\.exe)?$/.test(info.image) || info.created < Date.parse(r.created) - 10000) {
    throw refuse(409, 'not-ours', 'The program this run recorded is not running any more, so nothing was stopped.');
  }
  update(home, r.id, { status: 'stopped', reason: 'Stopped from the dashboard. Nothing was published.', ended: new Date().toISOString() });
  try { execFileSync('taskkill', ['/PID', String(r.claude_pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore', timeout: 15000 }); } catch (_) { /* checked by the runner */ }
  return summary(read(home, r.id));
}

module.exports = { start, stop, list, current, read, update, summary, runFile, logFile, releaseLock, alive, dirs };
