#!/usr/bin/env python3
"""Determine the review surface for /pilot: which files changed.

Prefers git (unstaged -> staged -> branch-vs-default). Falls back to
recently-modified files when not a git repo (heuristic for "this session"),
and finally to an empty set with source="none" so the skill knows to ask the
user for scope. Pure stdlib, cross-platform. Emits JSON to stdout.

Output: {"source": "...", "files": [...], "hint": "..."}
  source ∈ {git-unstaged, git-staged, git-branch, session, none}
"""
import json
import os
import subprocess
import sys
import time

IGNORE_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", ".next", "out",
    "__pycache__", ".venv", "venv", "env", ".mypy_cache", ".pytest_cache",
    "coverage", ".idea", ".vscode", "target", "tmp", "log", ".turbo",
    ".cache", "public/build", "storage",
}
SESSION_WINDOW_S = 90 * 60  # files touched in the last 90 min count as "session"
MAX_FILES = 400  # above this the surface is too big to auto-review


def _git(args):
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=15,
        )
        return out
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _is_git_repo():
    r = _git(["rev-parse", "--is-inside-work-tree"])
    return r is not None and r.returncode == 0 and r.stdout.strip() == "true"


def _lines(r):
    if r is None or r.returncode != 0:
        return []
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def _default_branch():
    # Try origin/HEAD, then common names.
    r = _git(["symbolic-ref", "refs/remotes/origin/HEAD"])
    if r is not None and r.returncode == 0:
        return r.stdout.strip().split("/")[-1]
    for name in ("main", "master", "develop"):
        if _git(["rev-parse", "--verify", name]) and \
           _git(["rev-parse", "--verify", name]).returncode == 0:
            return name
    return None


def from_git():
    # 1) Working-tree changes: modified (unstaged) + untracked new files.
    #    `git diff` omits untracked files, which are the most common case in
    #    fresh work, so add them explicitly via ls-files --others.
    modified = _lines(_git(["diff", "--name-only"]))
    untracked = _lines(_git(["ls-files", "--others", "--exclude-standard"]))
    files = sorted(set(modified) | set(untracked))
    if files:
        return "git-unstaged", files
    # 2) Staged changes.
    files = _lines(_git(["diff", "--cached", "--name-only"]))
    if files:
        return "git-staged", files
    # 3) Branch vs default (committed work on a feature branch).
    base = _default_branch()
    if base:
        cur = _git(["rev-parse", "--abbrev-ref", "HEAD"])
        cur_name = cur.stdout.strip() if cur and cur.returncode == 0 else ""
        if cur_name and cur_name != base:
            mb = _git(["merge-base", base, "HEAD"])
            if mb and mb.returncode == 0:
                files = _lines(_git(["diff", "--name-only", mb.stdout.strip(), "HEAD"]))
                if files:
                    return "git-branch", files
    return None, []


def from_mtime():
    now = time.time()
    found = []
    for root, dirs, names in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for n in names:
            p = os.path.join(root, n)
            try:
                if now - os.path.getmtime(p) <= SESSION_WINDOW_S:
                    found.append(os.path.relpath(p).replace("\\", "/"))
            except OSError:
                continue
            if len(found) > MAX_FILES:
                return found
    return found


def main():
    result = {"source": "none", "files": [], "hint": ""}

    if _is_git_repo():
        source, files = from_git()
        if source:
            result["source"], result["files"] = source, files
        else:
            result["hint"] = (
                "Git repo but no changes detected (clean tree). "
                "Ask the user which feature/files to review."
            )
    else:
        files = from_mtime()
        if files:
            result["source"], result["files"] = "session", files
            result["hint"] = (
                "Not a git repo. Files below were modified recently "
                "(last 90 min) — confirm scope with the user if unsure."
            )
        else:
            result["hint"] = (
                "Not a git repo and no recently-modified files found. "
                "Ask the user which files/feature to review."
            )

    if len(result["files"]) > MAX_FILES:
        result["hint"] = (
            f"{len(result['files'])} files — too broad to auto-review. "
            "Ask the user to narrow the scope."
        )

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
