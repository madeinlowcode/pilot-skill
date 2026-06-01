# pilot 🛬 — Post-Implementation Quality Ritual for Claude Code

A [Claude Code](https://claude.com/claude-code) skill that runs **after** your
code works, to answer the one question that separates "it runs" from
"production-grade": **"what can we improve now?"** — across both backend and
frontend.

Based on **Fabio Akita's PILOT method** (*Plan · Investigate · Polish · Operate
· Test* + *Adjust*) from his talk
[*Minha Experiência com Agile Vibe Coding*](https://www.youtube.com/watch?v=U3bZavG8qQY).
The dangerous moment in AI-assisted coding isn't writing the code — it's the
silence right after it works, where duplication, leaky abstractions, N+1
queries, and untested edge cases quietly accumulate. PILOT is the deliberate
second pass that closes that gap.

## Core principle: orchestrate, never reimplement

Quality reviews should not be redundant either. Every review dimension has
exactly **one owner** — `pilot` delegates to mature tools and builds only what
nothing else covers:

| Dimension | Owner |
|-----------|-------|
| Bugs / correctness | `/code-review` (non-ultra) |
| Reuse / duplication / efficiency | `/simplify` |
| Security / OWASP | `security-review` *(only on sensitive surfaces)* |
| **Backend architecture & integrity** | **this skill** — layering, cohesion, N+1, transactions, contracts |
| **Frontend structure & UX integrity** | **this skill** — componentization, state, re-render, a11y, responsiveness |
| Capturing lessons → rules | `revise-claude-md` |

The two custom reviewers run as a **parallel fan-out**; findings are
deduplicated, ranked by severity (🔴 blocking · 🟠 important · 🟡 nit ·
🔵 suggestion), and split into Backend / Frontend sections.

## The flow

1. **Investigate** — detect the change surface (`git diff` → session files →
   ask) and the project's real `test`/`lint`/`typecheck` commands + stack.
2. **Polish** — fan out backend + frontend reviewers in parallel; delegate
   bugs/DRY/security to their owners.
3. **Synthesize** — one ranked list, two sections, deduplicated.
4. **Operate / Test** — apply accepted fixes (behavior-preserving), then run the
   project's real test/lint/typecheck and add regression tests.
5. **Adjust** — turn a *recurring* finding into a narrow, earned rule in
   `CLAUDE.md` so it never repeats.

## Install

Clone into your Claude Code skills directory as `pilot`:

```bash
# global (all projects)
git clone https://github.com/madeinlowcode/pilot-skill ~/.claude/skills/pilot

# or per-project
git clone https://github.com/madeinlowcode/pilot-skill .claude/skills/pilot
```

On Windows (PowerShell):

```powershell
git clone https://github.com/madeinlowcode/pilot-skill "$env:USERPROFILE\.claude\skills\pilot"
```

Restart Claude Code (or start a new session) so the skill is picked up.

## Usage

Invoke after you've implemented something and it works:

| Command | Effect |
|---------|--------|
| `/pilot` | Review the change surface, report only |
| `/pilot --fix` | Apply accepted fixes and verify |
| `/pilot --back` | Backend-only pass |
| `/pilot --front` | Frontend-only pass |
| `/pilot --severity 🟠` | Hide findings below the given severity |

Flags compose: `/pilot --back --fix --severity 🟠`.

It also triggers naturally on phrases like *"what can we improve"*,
*"revisa o que fizemos"*, *"tira a redundância"*, *"make it production-grade"*,
*"ficou bom?"*.

## Supported stacks

Thin per-stack guides (real command discovery + key gotchas) for:
**Node/TS + React/Next · Python · Rails/Ruby · PHP/Laravel · Go**.
The `detect_stack.py` script reads each project's actual commands, so it adapts
to whatever you have.

## Layout

```
SKILL.md                    # core: PILOT philosophy + flow + single-owner delegation
references/
  severity.md               # rating rubric
  backend.md  frontend.md   # the two custom reviewer prompts + checklists
  redundancy.md             # duplication catalog + DRY merge protocol
  stacks/*.md               # thin per-stack command/gotcha guides
assets/
  review-template.md        # output format
  claude-md-rule.md         # incremental-rule format for the Adjust phase
scripts/
  changed_files.py          # change-surface detection (git → session → ask)
  detect_stack.py           # detect stack + real test/lint/typecheck commands
```

## What it is *not*

- Not a linter or a bug hunter (those are delegated).
- Not a project bootstrapper or planner — it runs **after** code exists.
- It never launches `/code-review ultra` (that's a billed, user-triggered run).

---

*Method credit: [Fabio Akita](https://akitaonrails.com/). Skill scaffolding
built with Claude Code.*
