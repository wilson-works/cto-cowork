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

## A run

A direction starts one headless Claude Code session (Opus 5.5, effort high, 40-minute cap). It may read the Hub's repos
through engine/look.js and write only its own run folder. When it ends, the space checks the folder and publishes it to
fleet-ops main, then posts one line on the office's group chat. Training runs go under runs/training/.
