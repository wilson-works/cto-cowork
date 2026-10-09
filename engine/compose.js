'use strict';

/**
 * engine/compose.js — what one composing run is told and what it may touch. Node built-ins only.
 *
 * A run is Claude Code, headless (-p), in the run's own staging folder under the rigs folder:
 *   <rigs>/cowork-<id>/            the working folder (cwd)
 *     context/                     copies of the Hub's CLAUDE.md and the rules in .claude/rules (they do not load on
 *                                  their own under --restricted, measured on 2.1.263)
 *     run/                         the ONLY place it may write: RUN.md, prompts/PROMPT-<X>.md, BOARD.md, PROMPTS.md
 *     .rig-meta.json               what the rig is, for the rig gate
 * It never runs git, never writes outside run/, and never starts a lane: the runner (engine/run.js) checks run/ and
 * publishes it to fleet-ops after the session ends.
 *
 * The flags (ARGS), set with Victor (VP AI) and John (Chief Engineer), 2026-10-06:
 *   --restricted                 removes Bash/PowerShell/WebFetch unless --tools names them, ignores every settings
 *                                file (user, project, local), and confines the file tools to the working folders
 *   --strict-mcp-config          no MCP servers at all: without it the claude.ai connectors (Canva, Calendar, Drive,
 *                                with their write tools) were in the run's tool list (fence drill, 2026-10-06 22:48 CDT)
 *   --tools                      Read Glob Grep Edit Write Bash Agent, and nothing else
 *   --permission-prompts none    anything that would ask is refused at once; nobody is there to answer
 *   (permission mode default)    so a file write is allowed only by the one Edit rule below, never by acceptEdits
 *   --allowedTools               Edit on run/** only (an Edit rule covers Write too); Bash only for engine/look.js
 *   --disallowedTools            AskUserQuestion, CronCreate, WebFetch, WebSearch, and reads of secrets and data
 *   --add-dir                    read roots: the code zone (repos), the run-builder skill, the org's reference files
 *   --agents                     John (chief-engineer-john), whom --restricted would otherwise not find
 *   --model / --effort           Opus 5.5 at high: a compose is one careful pass (Victor)
 * Not given: --dangerously-skip-permissions, bypassPermissions, acceptEdits, any bare Bash, Edit or Write rule.
 *
 *   ids(now)                     { id, runId, folder (fleet-ops path), name } for a run started at now
 *   systemPrompt(o), message(o), agentsJson(cfg), args(o)
 */

const fs = require('fs');
const path = require('path');

const HOME = path.resolve(__dirname, '..');
const LOOK = path.join(HOME, 'engine', 'look.js');

const fwd = (p) => String(p).replace(/\\/g, '/');
/** D:\tmp\rigs\x -> //d/tmp/rigs/x , the absolute-path form a permission rule takes on Windows (measured). */
function rulePath(p) {
  const f = fwd(path.resolve(p));
  const m = /^([A-Za-z]):\/(.*)$/.exec(f);
  return m ? `//${m[1].toLowerCase()}/${m[2]}` : `/${f}`;
}

/** Central time parts for a Date (HQ runs on Central; the owner reads CDT). */
function cdt(d) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Chicago', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
  }).formatToParts(d).reduce((a, p) => Object.assign(a, { [p.type]: p.value }), {});
  return { y: parts.year, mo: parts.month, d: parts.day, h: parts.hour, mi: parts.minute };
}
const stamp = (d) => { const c = cdt(d); return `${c.y}-${c.mo}-${c.d} ${c.h}:${c.mi} CDT`; };

function ids(now, training) {
  const c = cdt(now);
  const name = `cowork-${c.y}-${c.mo}-${c.d}-${c.h}${c.mi}`;
  return {
    id: `${c.y}${c.mo}${c.d}-${c.h}${c.mi}`,
    runId: `${training ? 'CWT' : 'CW'}${c.mo}${c.d}-${c.h}${c.mi}`,
    name,
    folder: training ? `runs/training/${name}` : `runs/${name}`,
  };
}

/** Reads a run may never make, inside the folders it can read. */
const DENY_READ = ['**/.env', '**/.env.*', '**/*.db', '**/*.sqlite', '**/*.sqlite3', '**/*.pem', '**/*.key',
  '**/credentials*', '**/.credentials*', '**/uploads/**', '**/_Run8*/**', '**/_TonyLive/**', '**/BalncePro/member/**',
  '//d/Hub/10-Business/**', '//d/Hub/40-Personal/**', '//d/Hub/00-Inbox/**', '//d/Hub/90-Archive/**',
  '//c/Hub/10-Business/**', '//c/Hub/40-Personal/**', '//c/Hub/00-Inbox/**', '//c/Hub/90-Archive/**'];

function systemPrompt(o) {
  const look = `node ${fwd(LOOK)}`;
  // Portable (owner 2026-10-09: the space ships free with the CTO org dev pack): the Hub and the owner's name come from
  // this computer's config, and a fleet repo without our example run uses the one bundled in context/example.
  const hub = o.hub || 'the Hub folder';
  const owner = o.owner || 'the owner';
  const example = 'the example run (runs/go-2026-10-06 in the fleet repo when fleet-ls runs/go-2026-10-06 lists it, else context/example in your working folder)';
  return [
    `You are running headless in James and John's Coworking Space on this computer. The owner${o.owner ? `, ${o.owner},` : ''} woke the space from the office and gave it a direction. Nobody is at the keyboard and nobody can answer a question.`,
    '',
    '## What you produce',
    'Write these files inside the run folder named in the message, and nowhere else:',
    '- RUN.md. When the message says TRAINING, line 1 is exactly: TRAINING: a proof run of the Coworking Space. Never launch it. Then the first heading, "# <RUN-ID>: <title>", with the RUN-ID the message gives. Sections, in order: the owner\'s direction verbatim in a quote block; ## How this direction reads (his words, then what they mean tonight); ## Assumptions; ## The lanes (a table whose first column is Lane, with Job, Model, Writes and Prompt; letters A, B, C..., and the last lane is a non-building gate G); ## Start state (what you measured, with shas, and NOT MEASURED where you could not); ## Common rules (adapt the common rules of ' + example + '); ## John\'s call; ## HELD (what needs his own words, and the words); ## Close.',
    '- prompts/PROMPT-<X>.md for each lane: who the lane is, the owner\'s words, what to read first, its rows each with a DONE-WHEN, its fences, and how it finishes.',
    '- BOARD.md: the header of the example run\'s BOARD.md with the run id changed, and no posts.',
    '- PROMPTS.md: a one-line intro, then for each lane one "## Lane <X> · <title>" heading followed by one fenced text block of 3 to 5 lines. The owner pastes that block into a new Claude VS Code chat opened on ' + hub + '. It names the lane and points at RUN.md and the lane\'s prompt file by their fleet-ops paths (the folder\'s fleet-ops path is in the message). Nothing else.',
    'You are done when those files exist. Your last message is one line: COMPOSED <RUN-ID> <n> lanes. Then stop.',
    '',
    '## Fences',
    '- Write only inside the run folder. Every other write is refused; do not try.',
    '- You never run git, start a lane, merge, push, deploy, or touch Railway, DNS, a domain or a connector, and you never post to the office. The space publishes your folder to fleet-ops after you stop.',
    `- Bash runs one thing: ${look} <verb> ..., read-only repo state. Verbs: repos | status <repo> | log <repo> [ref] [n] | branches <repo> | remote <repo> | ls <repo> <ref> [folder] | show <repo> <ref>:<path> | fleet <path> | fleet-ls [folder]. "fleet" reads fleet-ops at a fresh copy of origin/main; the fleet-ops files on disk run behind, so never read them from disk.`,
    '- No dollar figures anywhere: codes and counts only. No client names, emails, amounts, memos or files; a client is named by a code, never by name.',
    '- Anything HELD (a deploy, a push or merge to a product repo\'s master or main that deploys, Railway, DNS, a connector write, work on another machine, a public repo, starting lanes headless) becomes a line under ## HELD naming the words he would need to say. It is never a lane\'s job.',
    `- A lane is a Claude VS Code chat opened on ${hub} that the owner pastes; the space never starts one. Builders run Opus 5.5; the gate runs Fable 5.1 and is the only lane that marks VERIFIED.`,
    '',
    '## Reading',
    `- First read context/CLAUDE.md and every file in context/rules/ in your working folder (the Hub's constitution and the owner's standing orders, where this computer has them; they do not load on their own here). Then ${example}: its RUN.md, its PROMPTS.md and one of its prompts (fleet files through ${look} fleet <path>). Then only what the direction names.`,
    '- You have read enough when every lane you plan can name its repo, base sha, territory and DONE-WHEN. A fact you could not measure goes in RUN.md as NOT MEASURED; it is never a reason to read more. Make at most 25 reads before your first Write.',
    '- Never Glob or Grep above a repo root. Repos are in the code zone named in the message.',
    '',
    '## John',
    'Consult John once, after your lane table and before any prompt: one Agent call (subagent_type chief-engineer-john) with the table and one question: which two lanes collide or fail, and what is the smallest fix? Write his answer under ## John\'s call. If you disagree, you decide and record both views.',
    '',
    '## When the direction reads two ways',
    'Take the reading closest to his words that does less. Write it under ## Assumptions: his words, your reading, and what changes if it is wrong. Never ask and never wait.',
    '',
    '## Time',
    `You have ${Math.round(o.capMs / 60000)} minutes before the space stops you, and a stopped run publishes nothing. Write RUN.md early and fill it in. Every time a person reads is HH:MM CDT, never UTC or Z.`,
    '',
    '## Who you are',
    `You are James, the CTO. You report to ${owner}. You speak in short sentences, warm but stern and fair, and you always give the team a way forward. John is your Chief Engineer: he calls the architecture and the risks. Here there is no comms bus and no Tim: this folder is the whole job.`,
  ].join('\n');
}

function message(o) {
  return [
    o.training ? 'TRAINING' : null,
    `James and John's Coworking Space · run ${o.runId} · started ${o.started}`,
    `Run folder (write only here): ${o.runDir}`,
    `Its fleet-ops path: ${o.folder}/`,
    `Code zone (the repos, read-only): ${o.codeZone}`,
    '',
    "The owner's direction, verbatim:",
    ...String(o.direction).split(/\r?\n/).map((l) => `> ${l}`),
  ].filter((l) => l !== null).join('\n');
}

/** John, from his own definition in ~/.claude/agents, told where his reference file is and what this consult is. */
function agentsJson(cfg) {
  const file = path.join(cfg.agentsDir, 'chief-engineer-john.md');
  const text = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '');
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(text);
  if (!m) throw new Error('chief-engineer-john.md has no frontmatter.');
  const desc = (/^description:\s*"?(.*?)"?\s*$/m.exec(m[1]) || [])[1] || 'John, Chief Engineer.';
  const ref = path.join(cfg.agentsDir, 'references', 'chief-engineer-john.md');
  const prompt = `${m[2].trim()}\n\n## In the Coworking Space\nJames consults you once while he composes a run for the owner. ` +
    `${fs.existsSync(ref) ? `Your reference file is ${ref}. ` : ''}There is no comms bus here and you write nothing. Read what you need (repo state: ` +
    `node ${fwd(LOOK)} <verb> ...), then answer his one question in under 300 words: which lanes collide or fail, and the smallest fix.`;
  return JSON.stringify({ 'chief-engineer-john': { description: desc, prompt, tools: ['Read', 'Grep', 'Glob', 'Bash'], model: 'opus' } });
}

/** The office's own hooks, so the run shows on the office floor (--restricted reads no settings file but this one). */
function officeSettings(cfg) {
  if (!cfg.fleetOffice) return null;
  const hook = path.join(cfg.fleetOffice, '.claude', 'hooks', 'office-hook.js');
  if (!fs.existsSync(hook)) return null;
  const h = (ev) => [{ hooks: [{ type: 'command', command: `node "${fwd(hook)}" ${ev}`, timeout: 10 }] }];
  return JSON.stringify({ hooks: { SessionStart: h('SessionStart'), UserPromptSubmit: h('UserPromptSubmit'), PreToolUse: h('PreToolUse'), Stop: h('Stop'), SessionEnd: h('SessionEnd') } });
}

/** The fixed arguments. Only the folders, the session id and the texts vary, and none of them comes from a request. */
function args(o) {
  const cfg = o.cfg;
  const reads = [cfg.codeZone, path.join(cfg.skillsDir, 'run-builder'), path.join(cfg.agentsDir, 'references')].filter((d) => d && fs.existsSync(d));
  const settings = o.officeHooks === false ? null : officeSettings(cfg);
  return [
    '-p', message(o),
    '--append-system-prompt', systemPrompt({ capMs: cfg.capMs, hub: cfg.hub, owner: cfg.owner }),
    '--restricted', '--strict-mcp-config',
    '--tools', 'Read', 'Glob', 'Grep', 'Edit', 'Write', 'Bash', 'Agent',
    '--permission-prompts', 'none',
    '--model', cfg.model, '--effort', cfg.effort,
    '--session-id', o.sessionId,
    '--add-dir', ...reads,
    '--allowedTools', 'Agent', `Edit(${rulePath(o.runDir)}/**)`, `Bash(node ${fwd(LOOK)} *)`,
    '--disallowedTools', 'AskUserQuestion', 'CronCreate', 'WebFetch', 'WebSearch', ...DENY_READ.map((p) => `Read(${p})`),
    '--agents', agentsJson(cfg),
    ...(settings ? ['--settings', settings] : []),
    '--output-format', 'stream-json', '--verbose',
  ];
}

module.exports = { ids, stamp, cdt, systemPrompt, message, agentsJson, officeSettings, args, rulePath, DENY_READ, LOOK };
