# Incremental CLAUDE.md rule format (Adjust phase)

A PILOT rule is a **narrow, earned, actionable** instruction that prevents a
recurring mistake. It is added one at a time, as the need appears — never a big
upfront wall (that wastes context and breeds contradictions). Delegate the
actual file write to `revise-claude-md`; this is just the shape of what you
hand it.

## Anatomy
```
- <imperative rule>. <trigger condition> → <required action>. (why: <1 phrase>)
```

## Good rules (earned, specific, checkable)
- Always add a regression test on a bug fix → write the failing test first,
  then fix. (why: bugs without a pinning test recur)
- Before commit, run `pnpm typecheck && pnpm test` → fix before committing.
  (why: cheap checks catch most regressions)
- When a Blade/JSX markup block repeats 3×, extract a component. (why: drift)
- Wrap multi-step writes in a DB transaction. (why: partial writes corrupt state)

## Bad rules (don't add these)
- "Write clean code." → not actionable, not checkable.
- "Use SOLID principles." → vague; the model already knows, adds noise.
- A rule for a one-off issue that won't recur → clutters context.

## When to propose a rule
Only when the same class of finding showed up **more than once** (this session,
or you recognize it from the existing CLAUDE.md). One occurrence → just fix it,
don't write a rule. If unsure whether it recurs, ask the user before persisting.
