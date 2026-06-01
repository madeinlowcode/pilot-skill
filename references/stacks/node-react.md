# Stack: Node/TS + React/Next

`detect_stack.py` reads the real commands from `package.json` `scripts`. Trust
its output over these defaults. This file is just the conventions + gotchas the
generic reviewers should keep in mind for this ecosystem.

## Finding the commands
- Look in `package.json` → `scripts` for: `test`, `lint`, `typecheck`
  (or `type-check`), `build`.
- Package manager: presence of `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn,
  else `package-lock.json` → npm. Use the matching runner (`pnpm test` etc).
- Typecheck is often not a script: fall back to `npx tsc --noEmit`.
- Lint: `eslint .` ; format: `prettier --check .` (formatting is not a review
  finding — leave it to the formatter).

## Gotchas worth flagging
1. **`useEffect` data fetching without cleanup/abort** → race + state-set after
   unmount. Prefer react-query/SWR for server state.
2. **Server vs client state conflation** (Next.js): fetching in a client
   component what should be a server component / server action. RSC boundary
   crossings that ship secrets or huge payloads to the client.
3. **`any` / `as` casts** added to silence TS instead of modeling the type —
   defeats the typecheck safety net.
4. **New object/array/arrow literal as a prop** every render → breaks memo,
   causes re-renders. Only matters on a hot or expensive subtree.
5. **`process.env` read on the client** / secret leaking into the bundle
   (Next: missing `NEXT_PUBLIC_` understanding, or the reverse — leaking a
   server secret). Flag for security-review.
6. **Floating promises** (unawaited async) and unhandled rejections in handlers.
