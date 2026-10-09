# EX1001-2100: Contact form and a faster home page

An example run, shipped with James and John's Coworking Space so a run on any computer has one to follow. It was
never launched. Every name, sha and time in it is made up. Of its three lane prompts only PROMPT-A.md is included;
B and G follow the same shape.

> The contact form drops messages when someone attaches a photo, and the home page takes forever on a phone. Fix both
> tonight. Don't deploy anything.

## How this direction reads

His words: "The contact form drops messages when someone attaches a photo" and "the home page takes forever on a
phone". Tonight that means two builders, one per problem, in the same repo, and a gate that judges both. "Don't deploy
anything" means every lane stops at a pull request; merging to main is his.

## Assumptions

- "Drops messages" means the message never arrives, not that the photo is lost. If it is the photo, lane A's row A2
  changes from "the message arrives" to "the photo arrives", and nothing else moves.
- "Takes forever on a phone" is measured on a 375 px wide screen with the browser's slow-4G setting.

## The lanes

| Lane | Job | Model | Writes | Prompt |
|---|---|---|---|---|
| A | Contact form: photos up to 10 MB, the message always arrives | Opus 5.5 | `site/src/contact/**`, `site/api/contact.js` | prompts/PROMPT-A.md |
| B | Home page under 3 s to first view on a slow phone | Opus 5.5 | `site/src/home/**`, `site/public/img/**` | prompts/PROMPT-B.md |
| G | Gate: judges A and B, runs the tests, marks VERIFIED | Fable 5.1 | `runs/EX1001-2100/evidence/**` only | prompts/PROMPT-G.md |

## Start state

- Repo `site`, main at `a1b2c3d` (measured with look log site main 1).
- Open pull requests: none (look branches site).
- The contact form's size limit: NOT MEASURED (the config file was not readable from here).

## Common rules

1. Each lane works on its own branch, `ex1001/<lane>`, in its own worktree. Never on main.
2. Each lane writes only the paths in its row of the lane table. A file outside them is the other lane's or nobody's.
3. A builder never grades its own work: it posts BUILT with its sha on BOARD.md, and only the gate posts VERIFIED.
4. Times a person reads are written in the owner's own time zone.
5. Nothing is deployed, merged to main, or published. Those are the owner's.
6. Two bounces on one row and the row is BLOCKED: post why and take the next row.

## John's call

"A and B both touch the site's shared stylesheet if B inlines critical CSS. Keep B's change in `site/src/home/` and
tell A not to touch `site/src/styles/`. Smallest fix: name the stylesheet as nobody's file tonight."

## HELD

- Merging to main and deploying: the owner's words would be "merge A and B" and "deploy the site".

## Close

The run closes when the gate has posted VERIFIED or BLOCKED for every row and both pull requests are open.
