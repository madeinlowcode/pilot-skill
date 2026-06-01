# Stack: PHP / Laravel

`detect_stack.py` reads `composer.json` scripts. Trust it over these defaults.

## Finding the commands
- Tests: `php artisan test` or `./vendor/bin/pest` / `./vendor/bin/phpunit`
  (presence of `tests/Pest.php` → Pest).
- Static analysis (typecheck-equivalent): `./vendor/bin/phpstan analyse` or
  Larastan if present (`phpstan.neon`). Note absence as 🔵.
- Style: `./vendor/bin/pint` (Laravel's formatter) — formatting ≠ finding.

## Gotchas worth flagging
1. **N+1 via lazy Eloquent relations** — fix with `with()` eager loading.
   Enable `Model::preventLazyLoading()` in dev to surface these.
2. **Fat controllers** — extract to form requests (validation), actions, or
   services. Business logic in controllers drifts and duplicates.
3. **Mass assignment** — `$fillable`/`$guarded` gaps; `Model::create($request->all())`
   on untrusted input.
4. **Missing DB transaction** (`DB::transaction()`) around multi-step writes.
5. **Validation in the controller body** instead of a `FormRequest`.
6. **Queries in Blade templates / loops** — move to the controller/view model.
7. **Missing index / `->get()` then filtering in PHP** what the DB should filter.
8. **Secrets in code** instead of `config()`/`.env`; never `env()` outside config.
