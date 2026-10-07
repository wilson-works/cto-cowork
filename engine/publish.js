'use strict';

/**
 * engine/publish.js — check a composed run folder, then put it on fleet-ops main. Node built-ins only.
 *
 * check(runDir, o)   reads run/ and refuses (throws, in plain words) unless it is a whole run object:
 *   - only .md files, in run/ itself or run/prompts/, plain names, each under 200 KB, at most 40 files;
 *   - RUN.md whose first heading is "# <RUN-ID>" (and, for a training run, whose line 1 starts TRAINING);
 *   - BOARD.md with no posts in it;
 *   - PROMPTS.md with at least one "## Lane <X> · <title>" heading, each followed by one fenced block of at most 6
 *     lines, and a prompts/PROMPT-<X>.md for every lane it names;
 *   - no dollar figure in any file (owner fence: codes and counts only).
 *   Returns { files: [{ rel, data }], blocks: [{ lane, title, text, flags }], title }. flags name HELD-class words a
 *   block or its prompt carries (deploy, Railway, DNS, merge, push to main or master, delete, workflow, connector),
 *   shown beside its copy button; they are a reading aid, not a refusal.
 *
 * publish(o)   the board.py way (tools/board.py transact): fetch origin main into a private ref, build a tree in a
 *   private index (read-tree the base, hash-object each file, update-index --cacheinfo), commit-tree on the base with
 *   a message file, push <commit>:refs/heads/main. Refused when the folder is already on the base. On a rejected push
 *   it starts again from a fresh fetch (one loop, up to 6 tries). Success is read from the commit's subject carrying
 *   the marker and from ls-remote showing main at or past the commit, never from an exit code. Nothing is checked out
 *   and no working tree is touched; git runs with no prompts, no pager and no automatic gc.
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const FILE_MAX = 200 * 1024;
const MONEY = /\$\s?\d/;
const POST = /^## \d{4}-\d{2}-\d{2} \d{2}:\d{2} CDT · /m;
const LANE_HEAD = /^##\s+Lane\s+([A-Z][A-Z0-9]{0,3})\s*·\s*(.+?)\s*$/;
const HELD = [/\bdeploy/i, /\brailway\b/i, /\bdns\b/i, /\bmerge\b/i, /\bpush(?:es|ed)?\b[^.\n]{0,40}\b(?:main|master)\b/i,
  /\bdelet/i, /\bworkflow\b/i, /\bconnector\b/i, /--force\b/i];
const HELD_NAMES = ['deploy', 'Railway', 'DNS', 'merge', 'push to main/master', 'delete', 'workflow', 'connector', 'force'];
const GIT_ENV = { GIT_TERMINAL_PROMPT: '0', GCM_INTERACTIVE: 'never', GIT_PAGER: 'cat', PAGER: 'cat' };
const GIT_OPTS = ['-c', 'gc.auto=0', '-c', 'maintenance.auto=false', '-c', 'core.pager=cat', '-c', 'core.fsmonitor=false'];

const refuse = (m) => { throw Object.assign(new Error(m), { refused: true }); };

function listFiles(runDir) {
  const out = [];
  const walk = (dir, rel) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const r = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) {
        if (rel || e.name !== 'prompts') refuse(`The run folder holds a folder it should not: ${r}`);
        walk(path.join(dir, e.name), r);
      } else if (e.isFile()) out.push(r);
      else refuse(`The run folder holds something that is not a plain file: ${r}`);
    }
  };
  walk(runDir, '');
  return out;
}

/** The paste blocks in PROMPTS.md: [{ lane, title, text }]. */
function blocksOf(md) {
  const lines = md.replace(/\r\n/g, '\n').split('\n');
  const blocks = [];
  for (let i = 0; i < lines.length; i++) {
    const h = LANE_HEAD.exec(lines[i]);
    if (!h) continue;
    let j = i + 1;
    while (j < lines.length && !/^```/.test(lines[j]) && !LANE_HEAD.test(lines[j])) j++;
    if (j >= lines.length || !/^```/.test(lines[j])) refuse(`PROMPTS.md: Lane ${h[1]} has no fenced paste block.`);
    let k = j + 1;
    while (k < lines.length && !/^```\s*$/.test(lines[k])) k++;
    if (k >= lines.length) refuse(`PROMPTS.md: Lane ${h[1]}'s paste block is never closed.`);
    const body = lines.slice(j + 1, k);
    while (body.length && !body[body.length - 1].trim()) body.pop();
    if (!body.length) refuse(`PROMPTS.md: Lane ${h[1]}'s paste block is empty.`);
    if (body.length > 6) refuse(`PROMPTS.md: Lane ${h[1]}'s paste block is ${body.length} lines; a paste block is 3 to 5.`);
    blocks.push({ lane: h[1], title: h[2], text: body.join('\n') });
    i = k;
  }
  return blocks;
}

// A line that forbids or holds the act ("never deploy", "Railway is HELD") is a fence, not an ask: it raises no flag.
// Measured on CWT1006-2251: without this every prompt's fences flagged six words and the flag meant nothing.
const FORBIDS = /\b(never|not|no|nothing|don't|do not|nor|without|held|refuse[sd]?|forbid\w*|unless|off-limits|outside)\b/i;
const flagsOf = (...texts) => {
  const lines = texts.join('\n').split(/\r?\n/).filter((l) => !FORBIDS.test(l));
  return HELD.map((re, i) => (lines.some((l) => re.test(l)) ? HELD_NAMES[i] : null)).filter(Boolean);
};

function check(runDir, o) {
  let names;
  try { names = listFiles(runDir); } catch (e) { if (e.refused) throw e; refuse('The run folder is not there.'); }
  if (names.length > 40) refuse(`The run folder holds ${names.length} files; a run object is at most 40.`);
  const files = [];
  for (const rel of names) {
    if (!/^(prompts\/)?[A-Za-z0-9][A-Za-z0-9._-]{0,80}\.md$/.test(rel)) refuse(`Only Markdown files with plain names belong in a run: ${rel}`);
    const data = fs.readFileSync(path.join(runDir, ...rel.split('/')));
    if (data.length > FILE_MAX) refuse(`${rel} is over 200 KB.`);
    if (MONEY.test(data.toString('utf8'))) refuse(`${rel} carries a dollar figure (codes and counts only).`);
    files.push({ rel, data });
  }
  const text = (rel) => { const f = files.find((x) => x.rel === rel); return f ? f.data.toString('utf8').replace(/^﻿/, '') : null; };
  const run = text('RUN.md');
  if (run == null) refuse('There is no RUN.md.');
  if (o.training && !/^TRAINING\b/.test(run)) refuse('A training run says TRAINING on the first line of RUN.md, and this one does not.');
  const h1 = run.split(/\r?\n/).find((l) => /^# /.test(l)) || '';
  if (!h1.startsWith(`# ${o.runId}`)) refuse(`RUN.md's first heading should start "# ${o.runId}"; it is "${h1.slice(0, 60)}".`);
  const board = text('BOARD.md');
  if (board == null) refuse('There is no BOARD.md.');
  if (POST.test(board)) refuse('BOARD.md already has posts; a new run starts with an empty board.');
  const pm = text('PROMPTS.md');
  if (pm == null) refuse('There is no PROMPTS.md.');
  const blocks = blocksOf(pm);
  if (!blocks.length) refuse('PROMPTS.md has no "## Lane <X> · <title>" headings with paste blocks.');
  const seen = new Set();
  for (const b of blocks) {
    if (seen.has(b.lane)) refuse(`PROMPTS.md names Lane ${b.lane} twice.`);
    seen.add(b.lane);
    const p = text(`prompts/PROMPT-${b.lane}.md`);
    if (p == null) refuse(`Lane ${b.lane} has a paste block but no prompts/PROMPT-${b.lane}.md.`);
    b.flags = flagsOf(b.text, p);
  }
  return { files, blocks, title: h1.replace(/^#\s+/, '').trim() };
}

function git(repo, args, opts) {
  const o = opts || {};
  const r = spawnSync('git', [...GIT_OPTS, '-C', repo, ...args], {
    input: o.input, env: Object.assign({}, process.env, GIT_ENV, o.env || {}), windowsHide: true, timeout: 120000, maxBuffer: 16 * 1024 * 1024,
  });
  const out = r.stdout ? r.stdout.toString('utf8') : '';
  const err = r.stderr ? r.stderr.toString('utf8') : (r.error ? r.error.message : '');
  if (o.check !== false && r.status !== 0) throw new Error(`git ${args.slice(0, 2).join(' ')} failed: ${err.trim().split(/\r?\n/).slice(-2).join(' ')}`);
  return { status: r.status, out: out.trim(), err: err.trim() };
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** Fetch origin main into this run's own ref; returns the base sha. */
async function fetchBase(repo, ref) {
  let last = '';
  for (let i = 0; i < 4; i++) {
    const r = git(repo, ['fetch', '-q', '--no-write-fetch-head', 'origin', `+refs/heads/main:${ref}`], { check: false });
    if (r.status === 0) return git(repo, ['rev-parse', ref]).out;
    last = r.err;
    await sleep(3000);
  }
  throw new Error(`fetch failed 4 times: ${last.split(/\r?\n/).slice(-1)[0]}`);
}

/**
 * o { repo, ref, folder, files: [{ rel, data }], subject, msgFile, indexFile, log }
 * Resolves { sha, base, tries } or throws.
 */
async function publish(o) {
  const env = { GIT_INDEX_FILE: o.indexFile };
  fs.writeFileSync(o.msgFile, `${o.subject}\n`, 'utf8');
  try {
    for (let attempt = 1; attempt <= 6; attempt++) {
      const base = await fetchBase(o.repo, o.ref);
      const there = git(o.repo, ['ls-tree', '--name-only', base, '--', `${o.folder}/`]).out;
      if (there) refuse(`${o.folder} is already on fleet-ops main; nothing was published over it.`);
      git(o.repo, ['read-tree', base], { env });
      for (const f of o.files) {
        const p = `${o.folder}/${f.rel}`;
        const blob = git(o.repo, ['hash-object', '-w', '--stdin', '--path', p], { input: f.data }).out;
        git(o.repo, ['update-index', '--add', '--cacheinfo', `100644,${blob},${p}`], { env });
      }
      const changed = git(o.repo, ['diff-index', '--cached', '--name-status', base], { env }).out.split(/\r?\n/).filter(Boolean);
      const stray = changed.filter((l) => !/^A\t/.test(l) || !l.slice(2).startsWith(`${o.folder}/`));
      if (stray.length) refuse(`The commit would change more than the new folder (${stray[0]}); nothing was published.`);
      const tree = git(o.repo, ['write-tree'], { env }).out;
      const commit = git(o.repo, ['commit-tree', tree, '-p', base, '-F', o.msgFile]).out;
      const subject = git(o.repo, ['log', '-1', '--format=%s', commit]).out;
      if (!subject.includes(o.marker)) throw new Error('The commit was made without its marker; nothing was pushed.');
      const push = git(o.repo, ['push', '-q', 'origin', `${commit}:refs/heads/main`], { check: false });
      if (o.log) o.log(`publish try ${attempt}: base ${base.slice(0, 9)} commit ${commit.slice(0, 9)} push ${push.status === 0 ? 'accepted' : `rejected (${push.err.split(/\r?\n/).slice(-1)[0]})`}`);
      if (push.status === 0) {
        const head = (git(o.repo, ['ls-remote', 'origin', 'refs/heads/main']).out.split(/\s+/)[0] || '');
        if (head === commit) return { sha: commit, base, tries: attempt };
        await fetchBase(o.repo, o.ref);
        if (git(o.repo, ['merge-base', '--is-ancestor', commit, o.ref], { check: false }).status === 0) return { sha: commit, base, tries: attempt };
        throw new Error(`The push was accepted but main on GitHub does not hold ${commit.slice(0, 9)}.`);
      }
      await sleep(2000 + attempt * 1000);
    }
    throw new Error('fleet-ops main was busy: the push was turned back 6 times. Nothing was published; start the run again.');
  } finally {
    fs.rmSync(o.indexFile, { force: true });
  }
}

module.exports = { check, blocksOf, publish, fetchBase, flagsOf, git };
