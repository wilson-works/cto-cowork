'use strict';

/**
 * engine/look.js — the one command a composing run may execute: read-only state of the Hub's repos and of fleet-ops.
 * Node built-ins only. A run cannot run git itself; it asks this script.
 *
 *   node engine/look.js repos                         the repos it can look at (the code zone's git repos, fleet-ops)
 *   node engine/look.js status <repo>                 branch, ahead/behind, changed files (first 80 lines)
 *   node engine/look.js log <repo> [ref] [n]          one line per commit (n up to 50, default 15)
 *   node engine/look.js branches <repo>               local and remote-tracking branches, newest first (40)
 *   node engine/look.js remote <repo>                 the branch heads on GitHub right now (git ls-remote)
 *   node engine/look.js ls <repo> <ref> [folder]      the names in a folder at a ref
 *   node engine/look.js show <repo> <ref>:<path>      a file at a ref (up to 256 KB)
 *   node engine/look.js fleet <path>                  a fleet-ops file at the run's fresh copy of origin/main
 *   node engine/look.js fleet-ls [folder]             the names in a fleet-ops folder there
 *
 * Fences: a repo is a NAME from the list, never a path; no argument may start with "-" (git log and show take
 * --output=<file>, which writes); a ref is letters, digits and . _ / - only. Every call runs git with no prompts, no
 * pager, no optional locks and no automatic gc, and writes nothing. fleet-ops is read at the ref the runner fetched
 * for this run (COWORK_FLEET_REF), because the shared clone's files on disk run behind GitHub.
 * Exit codes: 0 answered; 2 refused (the reason is printed); 1 git failed.
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const config = require('./config');

const OUT_MAX = 256 * 1024;
const NAME = /^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$/;
const REF = /^[A-Za-z0-9][A-Za-z0-9._\/-]{0,150}$/;
const GIT_ENV = { GIT_TERMINAL_PROMPT: '0', GCM_INTERACTIVE: 'never', GIT_PAGER: 'cat', PAGER: 'cat', GIT_OPTIONAL_LOCKS: '0' };
const GIT_OPTS = ['-c', 'gc.auto=0', '-c', 'maintenance.auto=false', '-c', 'core.pager=cat', '-c', 'core.fsmonitor=false', '--no-optional-locks'];

class Refused extends Error {}
const refuse = (m) => { throw new Refused(m); };

/** name -> folder, for every git repo the space may look at. */
function repoMap(cfg) {
  const map = new Map();
  if (cfg.codeZone) {
    let names = [];
    try { names = fs.readdirSync(cfg.codeZone); } catch (_) { /* none */ }
    for (const n of names) {
      const dir = path.join(cfg.codeZone, n);
      if (NAME.test(n) && fs.existsSync(path.join(dir, '.git'))) map.set(n, dir);
    }
  }
  if (cfg.fleetOps && fs.existsSync(path.join(cfg.fleetOps, '.git'))) map.set('fleet-ops', cfg.fleetOps);
  return map;
}

function git(dir, args, max) {
  const out = execFileSync('git', [...GIT_OPTS, '-C', dir, ...args], {
    env: Object.assign({}, process.env, GIT_ENV), encoding: 'utf8', windowsHide: true, timeout: 60000,
    maxBuffer: 8 * 1024 * 1024, stdio: ['ignore', 'pipe', 'pipe'],
  });
  return out.length > (max || OUT_MAX) ? `${out.slice(0, max || OUT_MAX)}\n[cut at ${Math.round((max || OUT_MAX) / 1024)} KB]` : out;
}
const firstLines = (s, n) => s.split(/\r?\n/).slice(0, n).join('\n');

function main(argv, cfg) {
  const [verb, ...rest] = argv;
  for (const a of rest) {
    if (typeof a !== 'string' || !a || a.startsWith('-') || /[\0\r\n]/.test(a) || a.length > 300) refuse(`"${String(a).slice(0, 40)}" is not an argument this script takes.`);
  }
  const repos = repoMap(cfg);
  const repoOf = (name) => {
    if (!name || !NAME.test(name) || !repos.has(name)) refuse(`${name ? `"${name}" is not a repo here` : 'Name a repo'}. Run: node engine/look.js repos`);
    return repos.get(name);
  };
  const refOf = (r) => { if (!REF.test(r)) refuse(`"${r}" is not a ref name.`); return r; };
  const fleetRef = process.env.COWORK_FLEET_REF && REF.test(process.env.COWORK_FLEET_REF) ? process.env.COWORK_FLEET_REF : 'origin/main';

  switch (verb) {
    case 'repos': {
      const lines = [];
      for (const [n, dir] of repos) {
        let head = '';
        try { head = git(dir, ['rev-parse', '--abbrev-ref', 'HEAD']).trim(); } catch (_) { head = '?'; }
        lines.push(`${n}  (${head})`);
      }
      return lines.join('\n');
    }
    case 'status': return firstLines(git(repoOf(rest[0]), ['status', '--short', '--branch', '--untracked-files=normal']), 80);
    case 'log': {
      const n = rest[2] == null ? 15 : Number(rest[2]);
      if (!Number.isInteger(n) || n < 1 || n > 50) refuse('n is a whole number from 1 to 50.');
      return git(repoOf(rest[0]), ['log', '--oneline', '--decorate=short', '-n', String(n), refOf(rest[1] || 'HEAD'), '--']);
    }
    case 'branches':
      return git(repoOf(rest[0]), ['for-each-ref', '--sort=-committerdate', '--count=40',
        '--format=%(refname:short)  %(objectname:short)  %(committerdate:short)  %(subject)', 'refs/heads', 'refs/remotes']);
    case 'remote': return git(repoOf(rest[0]), ['ls-remote', '--heads', 'origin']);
    case 'ls': {
      const dir = repoOf(rest[0]);
      const ref = refOf(rest[1] || 'HEAD');
      return git(dir, ['ls-tree', '--name-only', ref, '--', rest[2] ? `${rest[2].replace(/\\/g, '/').replace(/\/+$/, '')}/` : '.']);
    }
    case 'show': {
      const dir = repoOf(rest[0]);
      const m = /^([^:]+):(.+)$/.exec(rest[1] || '');
      if (!m) refuse('Give <ref>:<path>, for example origin/main:README.md');
      return git(dir, ['show', `${refOf(m[1])}:${m[2].replace(/\\/g, '/')}`]);
    }
    case 'fleet': {
      if (!repos.has('fleet-ops')) refuse('fleet-ops is not on this computer.');
      if (!rest[0]) refuse('Give a fleet-ops path, for example runs/go-2026-10-06/RUN.md');
      return git(repos.get('fleet-ops'), ['show', `${fleetRef}:${rest[0].replace(/\\/g, '/')}`]);
    }
    case 'fleet-ls': {
      if (!repos.has('fleet-ops')) refuse('fleet-ops is not on this computer.');
      return git(repos.get('fleet-ops'), ['ls-tree', '--name-only', fleetRef, '--', rest[0] ? `${rest[0].replace(/\\/g, '/').replace(/\/+$/, '')}/` : '.']);
    }
    default:
      return refuse('Use one of: repos | status <repo> | log <repo> [ref] [n] | branches <repo> | remote <repo> | ls <repo> <ref> [folder] | show <repo> <ref>:<path> | fleet <path> | fleet-ls [folder]');
  }
}

module.exports = { main, repoMap, Refused };

if (require.main === module) {
  try {
    process.stdout.write(`${main(process.argv.slice(2), config.load())}\n`);
  } catch (e) {
    if (e instanceof Refused) { process.stdout.write(`REFUSED: ${e.message}\n`); process.exit(2); }
    process.stdout.write(`git could not answer: ${String((e.stderr || e.message || e)).trim().split(/\r?\n/).slice(0, 3).join(' ')}\n`);
    process.exit(1);
  }
}
