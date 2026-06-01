---
name: pilot
description: >-
  Post-implementation quality ritual based on Fabio Akita's PILOT method
  (Plan, Investigate, Polish, Operate, Test + Adjust). Run this AFTER a feature,
  fix, or refactor is working to answer "what can we improve now?" across BOTH
  backend and frontend — eliminate redundancy, tighten architecture, harden,
  then capture the lesson as an incremental rule. Use this skill whenever the
  user finishes implementing something and asks to review, polish, improve,
  refine, harden, or "make it production-grade"; whenever they say things like
  "what can we do better", "limpa esse código", "tira a redundância", "ficou
  bom?", "revisa o que fizemos", "melhora isso", "pilot", "/pilot", "lapida",
  or just finished writing code and quality matters. Triggers on post-impl
  review, refactor passes, DRY cleanup, quality gates before commit/PR, and
  any "we shipped it, now make it good" moment. Prefer this over an ad-hoc
  review when the user cares about well-crafted code with no duplication.
---

# PILOT — Post-Implementation Improvement Ritual

## Why this exists

AI is a mirror. It accelerates whoever is driving — a strong engineer 10x, a
sloppy one's technical debt 10x. The dangerous moment with AI-assisted coding
is not writing the code; it's the silence right after it works. "It runs" feels
like done. It isn't. The gap between "works" and "well-crafted" is where
duplication, leaky abstractions, N+1 queries, and untested edge cases quietly
accumulate — and they compound.

Fabio Akita's **PILOT** method closes that gap with a deliberate second pass:
treat the agent like a junior you mentor, and after every implementation ask
**"what can we improve now?"** — then actually do it. This skill is that pass,
on demand. It is not a linter and not a bug hunter (other tools own those). It
is the disciplined "polish + harden + learn" loop that turns working code into
code you'd be proud to put your name on.

**Scope:** this skill is the post-implementation loop ONLY. It does not plan
new features or bootstrap projects (that is `anti-vibe-coding`'s job). It runs
after code exists.

## Core principle: orchestrate, never reimplement

The user values craftsmanship and *hates redundancy* — so this skill must not
be redundant either. Every review dimension has exactly **one owner**. We
delegate to mature tools and build only the two things nothing else covers
(backend & frontend design review) plus the Adjust loop.

| Dimension | Owner | How |
|-----------|-------|-----|
| Bugs / correctness | `/code-review` | Invoke the skill, **non-ultra only** (see below) |
| Reuse / duplication / efficiency | `/simplify` | Already fans out 3 DRY agents |
| Security / OWASP | `security-review` or `appsec-elite-auditor` | Only if the change touches auth, payments, input, uploads, secrets |
| Backend architecture & integrity | **this skill** | Custom `backend` reviewer (below) |
| Frontend structure & UX integrity | **this skill** | Custom `frontend` reviewer (below) |
| Capturing lessons → rules | `revise-claude-md` | For the durable rule write; we only decide *what* the rule is |

> **`/code-review` ultra is OFF-LIMITS.** Ultra is a billed, user-triggered
> cloud review. You cannot launch it. When delegating to `/code-review`, use the
> default (non-ultra) path. Never pass `ultra`, never attempt to start it.

## The flow (maps to P‑I‑L‑O‑T + Adjust)

`/pilot` runs these phases in order. Narrate each phase briefly so the user can
follow and interrupt.

### Investigate — define the surface
Figure out *what changed* — that is the review surface. Don't review the whole
repo; review the delta.

```bash
python "<skill-dir>/scripts/changed_files.py"
```

This returns the changed files with a `source` field telling you how it found
them (`git-unstaged`, `git-staged`, `git-branch`, `session`, or `none`). It
prefers git, and falls back gracefully when the environment is **not a git
repo** (which happens). If `source` is `none` or the list is empty/huge, **ask
the user for the scope** ("which files/feature should I review?") rather than
guessing. Then detect the stack:

```bash
python "<skill-dir>/scripts/detect_stack.py"
```

This returns detected stack(s) and the project's real `test` / `lint` /
`typecheck` commands (read from package.json scripts, Makefile, composer.json,
Gemfile, etc.). Read the matching `references/stacks/<stack>.md` for that
ecosystem's gotchas and command conventions. Read `references/severity.md` for
the rating rubric you'll use everywhere.

### Polish — fan out the review (parallel)
Spawn the review agents **in parallel** using the Agent tool (one message,
multiple tool calls — see `superpowers:dispatching-parallel-agents`). Do NOT
use the Workflow tool (it needs explicit user opt-in this skill doesn't have).

Run, concurrently:
1. **`backend` reviewer** — prompt in `references/backend.md`, scoped to changed
   backend files. Skip if no backend files changed.
2. **`frontend` reviewer** — prompt in `references/frontend.md`, scoped to
   changed frontend files. Skip if no frontend files changed.
3. **`/code-review`** (non-ultra) on the same diff — for correctness/bugs.
4. **`/simplify`** in review mode — for reuse/duplication/efficiency. (If the
   user passed `--fix`, `/simplify` may apply; otherwise have it only report.)
5. **`security-review`** — *only* if the change touches a sensitive surface
   (auth, authz, payments, file upload, raw SQL, secrets, deserialization).

`--back` runs only backend + code-review + simplify; `--front` runs only
frontend + code-review + simplify. Default runs everything applicable.

Read `references/redundancy.md` before synthesizing — it is the cross-cutting
duplication catalog (the user's top priority) and tells you how to merge the
DRY findings from `/simplify` with your own structural observations so they
aren't reported twice.

### Synthesize — one ranked list, two sections
Collect every finding. **Deduplicate** (the whole point of single-owner
dimensions is that you shouldn't get the same finding twice — if you do, keep
one). Then present using `assets/review-template.md`: a **Backend** section and
a **Frontend** section, each finding tagged with severity
(🔴 blocking · 🟠 important · 🟡 nit · 🔵 suggestion), a one-line rationale, and
a concrete fix. Apply the `--severity` cutoff if given (e.g. `--severity 🟠`
hides nits and suggestions). Lead with the highest-leverage fixes, not the
easiest.

### Operate / Test — apply & verify
If `--fix` was given (or the user picks fixes), apply them. Refactors must
**preserve behavior**: show the change, then verify. Run the project's real
commands from `detect_stack.py`:
- typecheck → lint → tests, in that order (fail fast on the cheap checks)
- if the change fixed a bug, ensure a **regression test** exists for it; if not,
  add one. A bug without a regression test will come back.

Report what passed and what failed with the actual output. Never claim green
without running.

### Adjust — capture the lesson (the compounding part)
This is what makes PILOT a *method* and not just a review. When a finding
reflects a **recurring** mistake (not a one-off), turn it into a durable,
incremental rule so neither you nor the agent repeats it. Examples: "always add
a regression test on bug fix", "extract a partial/component when a markup block
repeats", "run typecheck before commit".

Keep rules **narrow and earned** — add them as the need appears, never a giant
upfront wall (that wastes context and creates contradictory instructions). Use
`assets/claude-md-rule.md` for the format, then delegate the actual write to
`revise-claude-md` (it owns CLAUDE.md maintenance). Only propose a rule when the
pattern genuinely recurred — ask the user before persisting if unsure.

## Flags

| Flag | Effect |
|------|--------|
| `/pilot` | Full review of the change surface, report only |
| `/pilot --fix` | Apply the accepted fixes and verify |
| `/pilot --back` | Backend-only pass |
| `/pilot --front` | Frontend-only pass |
| `/pilot --severity 🟠` | Hide findings below the given severity |

Flags compose: `/pilot --back --fix --severity 🟠`.

## What NOT to do
- Don't review the whole repo — only the change surface.
- Don't reimplement bug-finding, DRY analysis, or security scanning — delegate.
- Don't attempt `/code-review ultra` — it's billed and user-only.
- Don't dump a 40-item flat list — rank by leverage, split back/front.
- Don't add CLAUDE.md rules for one-off issues — only recurring patterns.
- Don't claim tests pass without running the project's real commands.

## Reference files
- `references/severity.md` — the rating rubric (read every run)
- `references/backend.md` — backend reviewer prompt + checklist
- `references/frontend.md` — frontend reviewer prompt + checklist
- `references/redundancy.md` — duplication catalog + how to merge DRY findings
- `references/stacks/{node-react,python,rails,laravel,go}.md` — per-stack
  commands & gotchas (read only the detected one)
- `assets/review-template.md` — output format
- `assets/claude-md-rule.md` — incremental rule format for the Adjust phase
