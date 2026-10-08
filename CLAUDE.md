# James and John's Coworking Space

The CTO org's office in the fleet office's Agents' wing. The owner wakes it from the office (on HQ or his phone), types a
direction, and James (CTO) with John (Chief Engineer) compose a run for it, headless: they read the state, plan, and write
the run object (RUN.md, one prompt per lane, an empty BOARD.md, PROMPTS.md with one short paste block per lane). The space
publishes that folder to fleet-ops main and shows the paste blocks with a Copy button each.

Owner, 2026-10-06 ~21:10 CDT: "I would also in that same lane, would like to set another agent office up for the CTO org,
so it would be James and John's Coworking Space, and from there, they can launch CTO org work like we are doing right now."

## What it never does

It composes. It never starts a lane (lanes are Claude VS Code chats he pastes, his law of 2026-09-18), never merges,
deploys, writes a code repo, touches Railway or DNS, or posts as him. A training run (any proof) is filed under
runs/training/ with TRAINING on the first line of its RUN.md.

## How a run is fenced (engine/compose.js has the whole list and why)

- Claude Code runs with --restricted, --permission-prompts none and the default permission mode, in the run's own staging
  folder under the rigs folder. Nothing that would ask is ever allowed.
- The only writable place is that folder's run/. Bash runs one script, engine/look.js, which reads repo state with git and
  writes nothing. No WebFetch, WebSearch, AskUserQuestion or CronCreate. Reads of secrets and data files are refused.
- The model never runs git. engine/run.js checks run/ (engine/publish.js check) and publishes it the board.py way: a commit
  built in a private index on a fresh fetch of origin/main, pushed as <commit>:refs/heads/main, and confirmed by ls-remote.
- One run at a time, a hard cap (40 minutes), and anything that fails publishes nothing.

## Layout

- agent.json: the office's view of the space (door, probe, start, brand, jokes).
- dashboard/server.js: 127.0.0.1:7560, a per-start token carried by the page, Host and Origin checks, /health with no
  token, dashboard/.pid while it runs. The phone address lives in cowork.config.json, never committed.
- engine/: config.js, look.js, compose.js, runs.js (start, stop, list), run.js (the runner), publish.js, detach.vbs.
- art.svg (the scene), mark.svg, art/: every picture is drawn by art/build.py (edit it, never the SVGs). The look (owner
  2026-10-07): the CTO's office in a 1980s software startup at night, Mad Men meets Saturday-morning cartoon. Shirtsleeves
  rolled, ties loosened, whisky, two cigars, Chinese takeout, the org chart with the two of them at the top, one partners'
  desk with both nameplates. Kit: walnut, memo paper, brass, oxblood for the one action, phosphor green for the paste
  blocks. Type: Bodoni Moda, Courier Prime, VT323 (SIL OFL, dashboard/public/fonts/). Owner, same night: cartoon hands
  (three fingers and a thumb), the desk's front to us and the PC facing the chair, the two of them taking turns at the
  keys, pacing (drawn side-on, never slid) and on their feet together. The clock keeps Central time and the window
  follows the day (dashboard/public/app.js).
- state/: the runs, their logs and the lock. Git-ignored.

## Working here

Node built-ins only; CommonJS. Times a person reads are HH:MM CDT. Commit with an explicit pathspec and a -F message file.
