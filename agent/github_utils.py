"""Git and GitHub operations via subprocess calls to git and gh CLI."""

import json
import os
import subprocess
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command, print it, and return the result."""
    print(f"[git] $ {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def setup_git_identity() -> None:
    """Configure a bot git identity (required for commits inside Actions)."""
    _run(["git", "config", "--global", "user.name", "Autonomous Agent"])
    _run(["git", "config", "--global", "user.email", "agent@github-actions.local"])


def create_branch(branch_name: str) -> None:
    """Create and switch to a new branch, or re-use if it already exists."""
    result = _run(["git", "branch", "--list", branch_name], check=False)
    if branch_name in (result.stdout or ""):
        _run(["git", "checkout", branch_name])
    else:
        _run(["git", "checkout", "-b", branch_name])


def write_files(files: list[dict[str, str]]) -> None:
    """Write a list of {path, content} dicts to disk, creating dirs as needed."""
    for f in files:
        path = Path(f["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f["content"], encoding="utf-8")
        print(f"[git] wrote {path}")


def commit_and_push(branch: str, message: str) -> None:
    """Stage all changes, commit, and push the branch to origin."""
    _run(["git", "add", "-A"])

    # Check if there is anything to commit
    status = _run(["git", "status", "--porcelain"], check=False)
    if not (status.stdout or "").strip():
        print("[git] nothing to commit — skipping.")
        return

    _run(["git", "commit", "-m", message])

    # Push; set upstream on first push
    result = _run(
        ["git", "push", "--set-upstream", "origin", branch],
        check=False,
    )
    if result.returncode != 0:
        # Retry once (handles transient network issues)
        time.sleep(5)
        _run(["git", "push", "--set-upstream", "origin", branch])


def get_ci_status(branch: str, repo: str, timeout_minutes: int = 20) -> dict:
    """Poll GitHub Actions for the most recent run on *branch*.

    Returns a dict:
      {
        "conclusion": "success" | "failure" | "skipped",
        "run_id": str,
        "logs": str,        # non-empty only on failure
      }

    If no run appears within 5 minutes, returns {"conclusion": "skipped"}.
    """
    deadline = time.time() + timeout_minutes * 60
    no_run_deadline = time.time() + 5 * 60  # give up waiting for run to appear after 5m

    print(f"[ci] polling for CI run on branch {branch!r}…")

    while time.time() < deadline:
        time.sleep(60)

        result = _run(
            [
                "gh", "run", "list",
                "--branch", branch,
                "--repo", repo,
                "--json", "status,conclusion,databaseId",
                "--limit", "5",
            ],
            check=False,
        )

        if result.returncode != 0 or not result.stdout.strip():
            if time.time() > no_run_deadline:
                print("[ci] no CI run found after 5 minutes — assuming no CI configured.")
                return {"conclusion": "skipped", "run_id": "", "logs": ""}
            continue

        try:
            runs = json.loads(result.stdout)
        except json.JSONDecodeError:
            continue

        if not runs:
            if time.time() > no_run_deadline:
                return {"conclusion": "skipped", "run_id": "", "logs": ""}
            continue

        # Reset the "no run" deadline once we see at least one run
        no_run_deadline = float("inf")

        # Find the most recent run that isn't still queued/waiting
        run = runs[0]
        run_id = str(run.get("databaseId", ""))
        status = run.get("status", "")
        conclusion = run.get("conclusion", "")

        print(f"[ci] run {run_id}: status={status!r} conclusion={conclusion!r}")

        if status == "completed":
            logs = ""
            if conclusion == "failure":
                logs = get_workflow_logs(run_id, repo)
            return {
                "conclusion": conclusion or "failure",
                "run_id": run_id,
                "logs": logs,
            }

    print("[ci] timeout reached waiting for CI.")
    return {"conclusion": "failure", "run_id": "", "logs": "CI polling timed out."}


def get_workflow_logs(run_id: str, repo: str) -> str:
    """Fetch failed step logs for a given workflow run ID."""
    result = _run(
        ["gh", "run", "view", run_id, "--repo", repo, "--log-failed"],
        check=False,
    )
    return (result.stdout or "") + (result.stderr or "")


def open_pr(branch: str, title: str, body: str, repo: str) -> str:
    """Open a pull request and return its URL."""
    result = _run(
        [
            "gh", "pr", "create",
            "--repo", repo,
            "--head", branch,
            "--base", "main",
            "--title", title,
            "--body", body,
        ],
        check=False,
    )

    # gh pr create outputs the PR URL on stdout
    url = (result.stdout or "").strip().splitlines()[-1] if result.stdout else ""
    if result.returncode != 0:
        # Try 'master' as base if 'main' doesn't exist
        result2 = _run(
            [
                "gh", "pr", "create",
                "--repo", repo,
                "--head", branch,
                "--base", "master",
                "--title", title,
                "--body", body,
            ],
            check=False,
        )
        url = (result2.stdout or "").strip().splitlines()[-1] if result2.stdout else ""

    print(f"[git] PR opened: {url}")
    return url


def list_repo_files(extensions: tuple[str, ...] | None = None) -> list[str]:
    """Return all tracked file paths in the repo, optionally filtered by extension."""
    result = _run(["git", "ls-files"], check=False)
    paths = [p for p in (result.stdout or "").splitlines() if p.strip()]
    if extensions:
        paths = [p for p in paths if any(p.endswith(ext) for ext in extensions)]
    return paths


def read_repo_files(paths: list[str], max_bytes: int = 200_000) -> dict[str, str]:
    """Read a list of file paths, returning {path: content}.

    Stops adding files once max_bytes is reached to avoid huge prompts.
    """
    contents: dict[str, str] = {}
    total = 0
    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
            total += len(text)
            if total > max_bytes:
                contents[path] = "<truncated — file too large>"
            else:
                contents[path] = text
        except OSError:
            pass
    return contents


def format_file_contents(contents: dict[str, str]) -> str:
    """Format a {path: content} dict for insertion into a prompt."""
    if not contents:
        return "None"
    parts = []
    for path, content in contents.items():
        parts.append(f"### {path}\n```\n{content}\n```")
    return "\n\n".join(parts)
