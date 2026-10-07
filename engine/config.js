'use strict';

/**
 * engine/config.js — where the Coworking Space finds the Hub, fleet-ops, its rigs folder, Claude Code and its own
 * port. Node built-ins only.
 *
 * Everything has a default worked out on this computer; cowork.config.json in the space's folder (never committed,
 * it is machine-local) overrides any of it:
 *   {
 *     "port": 7560,                       the dashboard's port (keep it the same as probe.port in agent.json)
 *     "phone": "https://<this computer's tailnet name>:8446/",   its phone address; the dashboard answers that host
 *     "hub": "D:\\Hub",                   else the first of D:\Hub, C:\Hub that holds CLAUDE.md
 *     "fleet_ops": "<hub>\\50-AI\\fleet-ops",
 *     "rigs": "D:\\tmp\\rigs",            where each run's staging folder goes (else <hub drive>\tmp\rigs)
 *     "claude": "<path to claude.exe>",   else the VS Code extension's newest, else claude.exe or claude.cmd on the PATH
 *     "model": "claude-opus-5-5", "effort": "high", "cap_minutes": 40
 *   }
 * The code zone is found by probing both of the Hub's names for it (20-Coding\Projects on HQ, 20-Coding\Active on
 * ENGINE and FIELD), never assumed.
 *
 *   load(home)   { home, port, phoneHost, hub, codeZone, fleetOps, fleetOffice, rigs, claude, model, effort, capMs,
 *                  agentsDir, skillsDir, notes }   Throws in plain words when cowork.config.json cannot be read.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');

const HOME = path.resolve(__dirname, '..');
const DEFAULT_PORT = 7560;

const isFile = (p) => { try { return fs.statSync(p).isFile(); } catch (_) { return false; } };
const isDir = (p) => { try { return fs.statSync(p).isDirectory(); } catch (_) { return false; } };
const readJson = (f) => JSON.parse(fs.readFileSync(f, 'utf8').replace(/^\uFEFF/, ''));

function findHub() {
  for (const root of ['D:\\Hub', 'C:\\Hub']) if (isFile(root + '\\CLAUDE.md')) return root;
  return null;
}

function codeZoneOf(hub) {
  if (!hub) return null;
  for (const name of ['Projects', 'Active']) {
    const z = path.join(hub, '20-Coding', name);
    if (isDir(z)) return z;
  }
  return null;
}

/** The newest Claude Code the VS Code extension carries (it updates itself; the npm one on the PATH may lag), or null. */
function extensionClaude() {
  const root = path.join(os.homedir(), '.vscode', 'extensions');
  let names = [];
  try { names = fs.readdirSync(root).filter((n) => /^anthropic\.claude-code-\d+\.\d+\.\d+/.test(n)); } catch (_) { return null; }
  const ver = (n) => /(\d+)\.(\d+)\.(\d+)/.exec(n).slice(1).map(Number);
  names.sort((a, b) => { const x = ver(a); const y = ver(b); return (y[0] - x[0]) || (y[1] - x[1]) || (y[2] - x[2]); });
  for (const n of names) {
    const exe = path.join(root, n, 'resources', 'native-binary', process.platform === 'win32' ? 'claude.exe' : 'claude');
    if (isFile(exe)) return exe;
  }
  return null;
}

/**
 * Claude Code: the configured path; else the VS Code extension's own (measured 2026-10-06: the npm claude on HQ's PATH
 * was 2.1.263, and Opus 5.5 needs 2.1.280 or newer, while the extension carried 2.1.289); else the PATH. An .exe runs as
 * it is; npm's claude.cmd is read for the claude.exe it starts (never run through cmd).
 */
function findClaude(configured) {
  if (configured) return isFile(configured) ? path.resolve(configured) : null;
  const ext = extensionClaude();
  if (ext) return ext;
  const dirs = String(process.env.PATH || process.env.Path || '').split(path.delimiter).filter(Boolean);
  dirs.push(path.join(os.homedir(), '.local', 'bin'));
  for (const d of dirs) {
    const dir = d.replace(/^"|"$/g, '');
    if (isFile(path.join(dir, 'claude.exe'))) return path.join(dir, 'claude.exe');
    const shim = path.join(dir, 'claude.cmd');
    if (isFile(shim)) {
      const m = /"%dp0%\\([^"%]+claude\.exe)"/i.exec(fs.readFileSync(shim, 'utf8'));
      if (m && isFile(path.join(dir, m[1]))) return path.join(dir, m[1]);
    }
  }
  return null;
}

function phoneHostOf(v) {
  if (v == null) return null;
  const s = String(v).trim();
  try { return new URL(/^https?:\/\//i.test(s) ? s : `https://${s}`).hostname.toLowerCase(); } catch (_) {
    throw new Error('"phone" in cowork.config.json is not an address. Use the one tailscale serve printed, like https://desk.example.ts.net:8446/');
  }
}

function load(home) {
  const h = path.resolve(home || HOME);
  const file = path.join(h, 'cowork.config.json');
  let cfg = {};
  if (isFile(file)) {
    try { cfg = readJson(file); } catch (e) { throw new Error(`cowork.config.json could not be read (${e.message}). Fix it, or remove it to use the defaults.`); }
    if (!cfg || typeof cfg !== 'object' || Array.isArray(cfg)) throw new Error('cowork.config.json must hold one JSON object.');
  }
  const notes = [];
  let port = DEFAULT_PORT;
  try { port = readJson(path.join(h, 'agent.json')).probe.port || port; } catch (_) { /* default */ }
  if (cfg.port != null) {
    if (!Number.isInteger(cfg.port) || cfg.port < 1024 || cfg.port > 65535) throw new Error('"port" in cowork.config.json must be a whole number from 1024 to 65535.');
    port = cfg.port;
  }
  const hub = cfg.hub || findHub();
  if (!hub) notes.push('No Hub found (D:\\Hub or C:\\Hub with a CLAUDE.md). Name it as "hub" in cowork.config.json.');
  const codeZone = codeZoneOf(hub);
  const fleetOps = cfg.fleet_ops || (hub ? path.join(hub, '50-AI', 'fleet-ops') : null);
  const fleetOffice = codeZone ? path.join(codeZone, 'fleet-office') : null;
  const rigs = cfg.rigs || (hub ? path.join(path.parse(hub).root, 'tmp', 'rigs') : path.join(os.tmpdir(), 'cowork-rigs'));
  const claude = findClaude(cfg.claude);
  if (!claude) notes.push('Claude Code was not found on the PATH. Name its program as "claude" in cowork.config.json.');
  const capMinutes = cfg.cap_minutes == null ? 40 : cfg.cap_minutes;
  if (!Number.isInteger(capMinutes) || capMinutes < 2 || capMinutes > 120) throw new Error('"cap_minutes" must be a whole number from 2 to 120.');
  return {
    home: h, port, phoneHost: phoneHostOf(cfg.phone), hub, codeZone, fleetOps, fleetOffice, rigs, claude,
    model: String(cfg.model || 'claude-opus-5-5'), effort: String(cfg.effort || 'high'), capMs: capMinutes * 60 * 1000,
    agentsDir: path.join(os.homedir(), '.claude', 'agents'), skillsDir: path.join(os.homedir(), '.claude', 'skills'),
    notes,
  };
}

module.exports = { load, findClaude, findHub, codeZoneOf, phoneHostOf, DEFAULT_PORT };

if (require.main === module) {
  const c = load();
  process.stdout.write(`${JSON.stringify(Object.assign({}, c, { capMinutes: c.capMs / 60000 }), null, 2)}\n`);
}
