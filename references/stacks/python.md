# Stack: Python (FastAPI / Django / Flask)

`detect_stack.py` reports the runner it found. Trust it over these defaults.

## Finding the commands
- Tests: `pytest` (look for `pytest.ini`/`pyproject.toml [tool.pytest]`) or
  `python -m pytest`. Django: `python manage.py test` or `pytest-django`.
- Lint/format: `ruff check .` (modern default), else `flake8`; format `ruff
  format`/`black` (formatting ≠ review finding).
- Typecheck: `mypy .` or `pyright` if configured (check `pyproject.toml` /
  `mypy.ini`). Many projects have none — note its absence as 🔵, don't invent.
- Env: prefer the project's `uv`/`poetry`/`venv`; check `uv.lock`,
  `poetry.lock`, `requirements.txt`.

## Gotchas worth flagging
1. **N+1 in Django ORM** — querying inside a loop; fix with
   `select_related`/`prefetch_related`. Same for SQLAlchemy lazy loads.
2. **Missing `@transaction.atomic`** (Django) / no `session.begin()` around a
   multi-step write.
3. **Blocking I/O inside an async view** (FastAPI/async Django) — a sync DB or
   `requests` call blocks the event loop. Use the async client or run in a
   threadpool.
4. **Mutable default arguments** (`def f(x=[])`) — classic shared-state bug.
5. **Pydantic/serializer validation bypassed** — trusting raw request data.
6. **Bare `except:` / swallowed exceptions** hiding failures.
7. **Settings/secrets** read from code instead of env/secrets manager.
