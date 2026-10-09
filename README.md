# James and John's Coworking Space

The CTO org's office. Wake it from the fleet office, tell James and John what you need, and they compose the run: the run
order, a prompt per lane and a short paste block for each, filed in fleet-ops. You paste the blocks to start the lanes.

## Start it

    node dashboard/server.js

It listens on http://127.0.0.1:7560/ . The fleet office's Wake button starts it the same way and Sleep stops it.

For the door on your phone, publish it on your tailnet and tell the space its own address:

    tailscale serve --bg --https=8446 http://127.0.0.1:7560

then put that address in cowork.config.json (copy cowork.config.example.json). That file stays on this computer.

## Needs

Node 20 or newer, Claude Code signed in on this computer, and a fleet-ops clone in the Hub (50-AI/fleet-ops). The run
reads the org's definitions for John from ~/.claude/agents.

## Install it

The space is free, and it is the front office of the WilsonWorks CTO org (the Dev Team pack): James, the CTO, plans
the work and John, the chief engineer, checks the plan. It runs best inside the free
[WilsonWorks Workspace](https://github.com/wilson-works/workspace), which brings everything it needs:

1. Install the Workspace (its `SETUP.md`), with its fleet (`fleet/README.md`) so you have a fleet repo at
   `<Hub>/50-AI/fleet-ops`.
2. Install the CTO org into your Hub folder from the Workspace (`org/INSTALL.md`:
   `node bin/install.js org --into "<your Hub folder>" --apply`). That puts James, John and their team in
   `<Hub>/.claude/agents`, where the space finds John (it also looks in `~/.claude/agents`).
3. Install the space: `node agents/bin/install-agent.js cowork` from the Workspace folder, or clone this repo and run
   `node dashboard/server.js`.
4. Open http://127.0.0.1:7560/, or Wake it from the office's Agents' wing.

Without a Workspace, it still runs: put `"hub"` (your Hub folder, the one with your CLAUDE.md) and, if your fleet repo
lives somewhere else, `"fleet_ops"` in `cowork.config.json`. It needs John's definition, `chief-engineer-john.md`
(from the CTO org), in `~/.claude/agents` or in the folder you name as `"agents_dir"`. Add `"owner": "<your name>"` and James will report to you
by name. The space ships an example run (`examples/run/`) that it reads when your fleet repo has none of its own.

## Make your own version

Everything that makes the space what it is lives in plain files: how James composes a run (`engine/compose.js`), what
he may read (`engine/look.js`) and the room itself (`art/build.py` draws every picture, `dashboard/public/`). Change
them, or ask Claude to. If you'd like a version built around your own team and the way you work, WilsonWorks builds
personalized versions: https://wilsonworks.studio/ai-consulting/agents

## A run

A direction starts one headless Claude Code session (Opus 5.5, effort high, 40-minute cap). It may read the Hub's repos
through engine/look.js and write only its own run folder. When it ends, the space checks the folder and publishes it to
fleet-ops main, then posts one line on the office's group chat. Training runs go under runs/training/.
