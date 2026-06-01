# Severity rubric

Every finding gets exactly one tag. Tag by **impact and certainty**, not by how
easy the fix is. A trivial-to-fix data-loss bug is still 🔴.

| Tag | Name | Meaning | Examples |
|-----|------|---------|----------|
| 🔴 | blocking | Correctness, data, or security risk. Must fix before merge/ship. | Data loss, auth bypass, money/precision bug, crash on common input, race on shared state |
| 🟠 | important | Real quality/maintainability cost. Should fix this pass. | Duplicated logic across files, N+1 query, leaky abstraction, missing regression test on a fixed bug, component that won't scale |
| 🟡 | nit | Minor, localized. Fix if cheap. | Naming, dead variable, small inconsistency, a magic number |
| 🔵 | suggestion | Optional improvement / future idea. | Possible extraction not yet earned, alternative pattern, perf idea with no current evidence |

## Calibration rules

- **Default down, not up.** If unsure between two levels, pick the lower one.
  Over-flagging trains the user to ignore you.
- **Duplication is 🟠 by default**, not 🟡 — it's the user's top concern and it
  compounds. Escalate to 🔴 only if the duplicated logic is security/correctness
  critical (e.g. the same auth check copy-pasted and drifting).
- **A bug fix without a regression test is 🟠.** It will regress.
- **"It works but..." is not automatically a finding.** Style preferences with
  no maintainability cost are noise — drop them.
- **One finding, one owner.** If `/code-review`, `/simplify`, and your own pass
  all surface the same issue, report it once at the highest justified severity.

## `--severity` cutoff
When the user passes `--severity X`, hide everything strictly below X:
`--severity 🟠` shows 🔴 and 🟠 only. `--severity 🔴` shows blockers only.
