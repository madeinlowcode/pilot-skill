# Redundancy — the duplication catalog & merge protocol

Eliminating duplication is the user's #1 craftsmanship priority. But `/simplify`
already fans out agents for reuse/duplication/efficiency. This file's job is to
**prevent double-reporting** and to give you the vocabulary to merge findings
cleanly — not to run a second DRY scan.

## Merge protocol (read before synthesizing)

1. `/simplify` returns reuse/duplication findings. Take those as the **primary**
   duplication source.
2. The `backend`/`frontend` reviewers may independently notice a repeated block.
   When they do, **match it against `/simplify`'s list and keep one entry** (the
   one with the better-located fix). Do not list the same duplication twice.
3. Only add a duplication finding of your own when it's **structural** and likely
   missed by a line-diff tool — e.g. the same *concept* implemented two
   different ways in two files (semantic duplication), which `/simplify` may not
   catch because the text differs.

## What counts as worth-fixing duplication

Not all repetition is bad. Flag it when removing it genuinely helps:

| Pattern | Fix | Notes |
|---------|-----|-------|
| Same logic copy-pasted in 2+ places | Extract function/service/util | 🟠 — drifts over time |
| Same markup block repeated | Extract component/partial | 🟠 — user's top concern |
| Same validation/rule in front and back, drifting | Single source of truth (shared schema, codegen, or one canonical place) | 🟠 |
| Magic value repeated | Named constant | 🟡 |
| Two functions, same shape, different types | Generic/parametrized — only if it doesn't obscure intent | 🔵 |
| Boilerplate the framework expects (e.g. similar CRUD controllers) | Often leave it | The rule of three: don't abstract on the 2nd occurrence |

## The rule of three (and when to break it)

Two occurrences is a coincidence; three is a pattern. Don't extract a shared
abstraction on the second occurrence unless the duplicated thing is
**correctness-critical** (e.g. an auth/permission check, a money calculation) —
there, even two drifting copies is a 🔴, because divergence is a security or
data bug, not just a smell.

## The opposite failure: over-abstraction

A premature or wrong abstraction is worse than duplication — it couples
unrelated things and every change fights it. If the change under review
introduced an abstraction that serves only one real caller, or a "flexible"
helper with five flags, flag *that* (🟠): inline it back until a third caller
actually appears. Akita's point cuts both ways — craftsmanship is the right
amount of structure, not the most.
