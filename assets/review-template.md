# PILOT review output template

Use this exact structure when presenting the synthesized review. Two sections
(omit one if that side wasn't touched). Each finding is one line: severity ·
location · what & why · fix. Rank within each section by leverage, blockers first.

---

## 🛬 PILOT review — `<feature/change name>`

**Surface:** `<N files>` · stack: `<detected>` · scope source: `<git-staged | session | user-specified>`
**Delegated:** code-review ✓ · simplify ✓ · security-review `<✓ / skipped: not sensitive>`

### Backend
- 🔴 `path/file.rb:42` — <issue>. <why it bites>. → <concrete fix>.
- 🟠 `path/service.rb` — <issue>. → <fix>.
- 🟡 ...

### Frontend
- 🟠 `components/Foo.tsx:18` — <issue>. → <fix>.
- 🔵 ...

### Verification (if `--fix` ran)
- typecheck: `<cmd>` → ✅ / ❌ `<output>`
- lint: `<cmd>` → ✅ / ❌
- tests: `<cmd>` → ✅ N passed / ❌ `<failing test + output>`
- regression test added for `<bug>`: yes/no

### Adjust — proposed rule (only if a pattern recurred)
> `<one-line rule>` — recurred in `<where>`. Persist to CLAUDE.md? (y/n)

---

**Summary:** `<1 line: X blockers, Y important, what to do first>`
