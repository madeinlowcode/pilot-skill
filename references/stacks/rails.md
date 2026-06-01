# Stack: Rails / Ruby

This is Akita's home stack; his quality gate is `SimpleCov` (coverage) +
`Brakeman` (security) + `RuboCop` (style), run before every commit. Suggest
adding any that are missing as an Adjust-phase rule.

## Finding the commands
- Tests: `bin/rails test` or `bundle exec rspec` (presence of `spec/` →
  RSpec; `test/` → Minitest).
- Lint/style: `bundle exec rubocop` (style ≠ review finding, but RuboCop also
  catches real smells — let it run).
- Security: `bundle exec brakeman -q` — delegate the reading of its output to
  security-review when the change is sensitive.
- Coverage: `SimpleCov` (emits `coverage/`); use it to spot untested new code.

## Gotchas worth flagging
1. **N+1 queries** — the canonical Rails issue. `includes`/`preload`/`eager_load`.
   The `bullet` gem catches these if present.
2. **Fat controllers / fat models** — logic that belongs in a service object,
   query object, or concern. Business rules in views/helpers.
3. **Missing DB index** on a new `where`/`join`/foreign key.
4. **Callbacks doing too much** — `after_save` side effects that should be
   explicit; callback chains that are hard to test/reason about.
5. **Mass-assignment / strong params** gaps; trusting `params` directly.
6. **Migration safety** — adding a column with a default or an index on a large
   table without `disable_ddl_transaction!`/`algorithm: :concurrently`.
7. **N+1 of partials** in views (render per item) — extract/collection-render.
