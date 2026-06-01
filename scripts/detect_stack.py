#!/usr/bin/env python3
"""Detect the project's stack(s) and the REAL test/lint/typecheck commands.

The PILOT skill should run the project's actual commands, not guessed ones.
This reads manifests (package.json, pyproject.toml, Gemfile, composer.json,
go.mod, Makefile) and reports per-stack commands. Pure stdlib, cross-platform.
Emits JSON to stdout: {"stacks": [{"stack","test","lint","typecheck","notes"}]}

A null command means "not found — ask or fall back to the stack guide default".
"""
import json
import os
import re
import sys

ROOT = "."


def read(path):
    try:
        with open(os.path.join(ROOT, path), "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def exists(path):
    return os.path.exists(os.path.join(ROOT, path))


def pkg_manager():
    if exists("pnpm-lock.yaml"):
        return "pnpm"
    if exists("yarn.lock"):
        return "yarn"
    if exists("bun.lockb"):
        return "bun"
    return "npm"


def script_cmd(scripts, name, runner):
    if name not in scripts:
        return None
    if runner == "npm":
        return f"npm run {name}"
    return f"{runner} {name}"  # pnpm/yarn/bun run a script by name directly


def detect_node():
    raw = read("package.json")
    if raw is None:
        return None
    try:
        pkg = json.loads(raw)
    except json.JSONDecodeError:
        return {"stack": "node-react", "test": None, "lint": None,
                "typecheck": None, "notes": "package.json present but unparseable"}
    scripts = pkg.get("scripts", {}) or {}
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    runner = pkg_manager()

    is_react = any(k in deps for k in ("react", "next", "vue", "svelte", "@angular/core"))
    stack = "node-react" if is_react else "node"

    test = script_cmd(scripts, "test", runner)
    lint = script_cmd(scripts, "lint", runner)
    typecheck = (script_cmd(scripts, "typecheck", runner)
                 or script_cmd(scripts, "type-check", runner)
                 or script_cmd(scripts, "tsc", runner))
    notes = []
    if typecheck is None and ("typescript" in deps or exists("tsconfig.json")):
        typecheck = "npx tsc --noEmit"
        notes.append("typecheck inferred (tsc --noEmit); no script found")
    notes.append(f"package manager: {runner}")
    return {"stack": stack, "test": test, "lint": lint,
            "typecheck": typecheck, "notes": "; ".join(notes)}


def detect_python():
    has = exists("pyproject.toml") or exists("requirements.txt") or exists("setup.py")
    if not has:
        return None
    pyproject = read("pyproject.toml") or ""
    django = exists("manage.py")
    test = "pytest"
    if django:
        test = "pytest" if "pytest" in pyproject else "python manage.py test"
    lint = "ruff check ." if ("ruff" in pyproject or exists("ruff.toml")) else "flake8"
    typecheck = None
    if "mypy" in pyproject or exists("mypy.ini"):
        typecheck = "mypy ."
    elif "pyright" in pyproject:
        typecheck = "pyright"
    notes = "django project" if django else ""
    return {"stack": "python", "test": test, "lint": lint,
            "typecheck": typecheck, "notes": notes}


def detect_rails():
    if not exists("Gemfile"):
        return None
    gem = read("Gemfile") or ""
    is_rails = "rails" in gem
    rspec = exists("spec") or "rspec" in gem
    test = "bundle exec rspec" if rspec else "bin/rails test"
    lint = "bundle exec rubocop" if "rubocop" in gem else None
    notes = []
    if "brakeman" in gem:
        notes.append("brakeman available (security)")
    if "simplecov" in gem:
        notes.append("simplecov available (coverage)")
    return {"stack": "rails", "test": test, "lint": lint,
            "typecheck": None, "notes": "; ".join(notes) if notes else
            ("rails" if is_rails else "ruby")}


def detect_laravel():
    raw = read("composer.json")
    if raw is None:
        return None
    try:
        comp = json.loads(raw)
    except json.JSONDecodeError:
        comp = {}
    deps = {**comp.get("require", {}), **comp.get("require-dev", {})}
    pest = exists("tests/Pest.php") or "pestphp/pest" in deps
    test = "./vendor/bin/pest" if pest else "php artisan test"
    typecheck = None
    if "phpstan/phpstan" in deps or "nunomaduro/larastan" in deps or exists("phpstan.neon"):
        typecheck = "./vendor/bin/phpstan analyse"
    lint = "./vendor/bin/pint --test" if "laravel/pint" in deps else None
    return {"stack": "laravel", "test": test, "lint": lint,
            "typecheck": typecheck, "notes": "laravel/php"}


def detect_go():
    if not exists("go.mod"):
        return None
    lint = "golangci-lint run" if exists(".golangci.yml") or exists(".golangci.yaml") else "go vet ./..."
    return {"stack": "go", "test": "go test ./...", "lint": lint,
            "typecheck": "go build ./...", "notes": "race: go test -race ./..."}


def main():
    detectors = [detect_node, detect_python, detect_rails, detect_laravel, detect_go]
    stacks = [s for s in (d() for d in detectors) if s]
    out = {"stacks": stacks}
    if not stacks:
        out["hint"] = ("No known stack manifest found. Ask the user, or read "
                       "the closest references/stacks/*.md guide.")
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
