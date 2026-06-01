# Stack: Go

`detect_stack.py` checks for `go.mod` and a `Makefile`. Trust it over defaults.

## Finding the commands
- Tests: `go test ./...` (race detector for concurrent code: `go test -race ./...`).
- Vet/typecheck: `go vet ./...` (the compiler is the typecheck; `go build ./...`).
- Lint: `golangci-lint run` if configured (`.golangci.yml`); else `go vet`.
- Format: `gofmt`/`goimports` — formatting ≠ review finding.

## Gotchas worth flagging
1. **Ignored errors** — `_ = f()` or unchecked returns. Go's error handling is
   explicit for a reason; swallowing is 🟠 (🔴 if it hides a failed write).
2. **Goroutine leaks** — a goroutine with no exit path / blocked on a channel
   nobody closes. Missing `context` cancellation propagation.
3. **Data races** — shared map/slice/struct written from multiple goroutines
   without a mutex/channel. Run `-race`.
4. **`defer` in a loop** — defers pile up until function return (resource leak);
   move to a closure or explicit close.
5. **Missing `context.Context`** on calls that do I/O / can hang (no timeout).
6. **Nil pointer / nil map writes**; returning a struct where a pointer-or-error
   is the right contract.
7. **N+1 DB queries** in a loop; missing prepared statement reuse.
