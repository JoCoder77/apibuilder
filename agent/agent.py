"""Main agent loop: plan → code → commit → CI → critique → PR."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from github_utils import (
    commit_and_push,
    create_branch,
    format_file_contents,
    get_ci_status,
    list_repo_files,
    open_pr,
    read_repo_files,
    setup_git_identity,
    write_files,
)
from llm import call_llm
from prompts import (
    CODING_SYSTEM,
    CODING_USER,
    CRITIQUE_SYSTEM,
    CRITIQUE_USER,
    PLAN_SYSTEM,
    PLAN_USER,
    PR_SYSTEM,
    PR_USER,
)
from state import AgentState

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_ITERATIONS = 8
MAX_CRITIQUE_LOOPS = 3
BRIEF_PATH = "agent-brief.md"

REPO_NAME = os.environ.get("REPO_NAME", "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_brief() -> str:
    brief_file = Path(BRIEF_PATH)
    if not brief_file.exists():
        sys.exit(
            f"[agent] ERROR: {BRIEF_PATH} not found. "
            "Create this file in the repo root with a description of what to build."
        )
    text = brief_file.read_text(encoding="utf-8").strip()
    if not text:
        sys.exit(f"[agent] ERROR: {BRIEF_PATH} is empty.")
    print(f"[agent] Brief loaded ({len(text)} chars).")
    return text


def plan(brief: str, existing_files: list[str], existing_contents: dict[str, str]) -> list[dict]:
    """Ask Gemini to produce a list of files to create/modify."""
    print("[agent] Planning…")
    user_prompt = PLAN_USER.format(
        brief=brief,
        existing_files="\n".join(existing_files) if existing_files else "None",
        existing_contents=format_file_contents(existing_contents),
    )
    raw = call_llm(PLAN_SYSTEM, user_prompt, json_mode=True)
    result = json.loads(raw)
    if not isinstance(result, list):
        raise ValueError(f"Plan prompt returned non-list: {raw[:200]}")
    print(f"[agent] Plan: {len(result)} file(s) to create/modify.")
    for item in result:
        print(f"  - {item.get('file', '?')}: {item.get('description', '')}")
    return result


def generate_code(
    brief: str,
    plan_items: list[dict],
    existing_contents: dict[str, str],
    state: AgentState,
) -> list[dict[str, str]]:
    """Ask Gemini to produce file contents implementing the plan."""
    print(f"[agent] Generating code (iteration {state.iteration})…")
    plan_text = "\n".join(
        f"- {p['file']}: {p.get('description', '')}" for p in plan_items
    )
    user_prompt = CODING_USER.format(
        brief=brief,
        plan=plan_text,
        existing_contents=format_file_contents(existing_contents),
        test_failures=state.format_errors(),
        critique_issues=state.format_critique_issues(),
    )
    raw = call_llm(CODING_SYSTEM, user_prompt, json_mode=True)
    files = json.loads(raw)
    if not isinstance(files, list):
        raise ValueError(f"Coding prompt returned non-list: {raw[:200]}")
    print(f"[agent] Generated {len(files)} file(s).")
    return files


def critique(brief: str, state: AgentState, ci_output: str) -> dict:
    """Ask Gemini to review the generated files and score them."""
    print(f"[agent] Critiquing (loop {state.critique_loop})…")
    user_prompt = CRITIQUE_USER.format(
        brief=brief,
        generated_files=state.format_generated_files(),
        test_output=ci_output or "No CI output available.",
    )
    raw = call_llm(CRITIQUE_SYSTEM, user_prompt, json_mode=True)
    result = json.loads(raw)
    score = int(result.get("score", 0))
    issues = result.get("issues", [])
    print(f"[agent] Critique score: {score}/10. Issues: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    return {"score": score, "issues": issues}


def build_pr_body(brief: str, state: AgentState, score: int, notes: list[str]) -> str:
    """Ask Gemini to draft a PR description."""
    file_paths = "\n".join(f"- {p}" for p in state.generated_files)
    notes_text = "\n".join(notes) if notes else "None"
    user_prompt = PR_USER.format(
        brief=brief,
        file_paths=file_paths or "None",
        score=score,
        notes=notes_text,
    )
    return call_llm(PR_SYSTEM, user_prompt, json_mode=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    setup_git_identity()

    brief = read_brief()

    # Create a timestamped branch for this run
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S")
    branch_name = f"agent/run-{timestamp}"
    create_branch(branch_name)

    state = AgentState.load()
    state.branch = branch_name
    state.iteration = 0
    state.critique_loop = 0
    state.save()

    # Gather repo context for the planner
    existing_files = list_repo_files()
    # Limit context: read source files only (skip images, large binaries, etc.)
    source_paths = list_repo_files(
        extensions=(".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".java",
                    ".rs", ".rb", ".sh", ".yml", ".yaml", ".json", ".toml",
                    ".md", ".txt", ".cfg", ".ini", ".env.example")
    )
    existing_contents = read_repo_files(source_paths)

    plan_items = plan(brief, existing_files, existing_contents)

    last_ci_output = ""
    pr_url = ""

    for iteration in range(1, MAX_ITERATIONS + 1):
        state.iteration = iteration
        state.save()
        print(f"\n{'='*60}")
        print(f"[agent] === ITERATION {iteration}/{MAX_ITERATIONS} ===")
        print(f"{'='*60}")

        # --- Code generation ---
        try:
            files = generate_code(brief, plan_items, existing_contents, state)
        except Exception as exc:
            print(f"[agent] Code generation failed: {exc}")
            state.add_error(str(exc))
            state.save()
            continue

        # --- Write files & commit ---
        write_files(files)
        state.update_files(files)
        state.save()

        commit_msg = f"agent: iteration {iteration} — code generation"
        commit_and_push(branch_name, commit_msg)

        # --- Wait for CI ---
        if REPO_NAME:
            ci_result = get_ci_status(branch_name, REPO_NAME)
            conclusion = ci_result["conclusion"]
            last_ci_output = ci_result.get("logs", "")

            if conclusion == "failure":
                print(f"[agent] CI failed on iteration {iteration}. Passing logs to next iteration.")
                state.add_error(f"CI failure (iteration {iteration}):\n{last_ci_output}")
                state.save()
                continue  # loop back to re-generate code

            if conclusion == "skipped":
                print("[agent] No CI configured — skipping CI wait.")
                last_ci_output = "No CI configured."
        else:
            print("[agent] REPO_NAME not set — skipping CI wait.")
            last_ci_output = "CI skipped (REPO_NAME not set)."

        # --- Critique loop ---
        critique_passed = False
        for critique_loop in range(1, MAX_CRITIQUE_LOOPS + 1):
            state.critique_loop = critique_loop
            state.save()

            result = critique(brief, state, last_ci_output)
            state.last_critique_score = result["score"]
            state.save()

            if result["score"] >= 8:
                print(f"[agent] Critique passed with score {result['score']}/10!")
                critique_passed = True
                break

            print(f"[agent] Score {result['score']}/10 — iterating on critique issues.")
            state.add_critique_issues(result["issues"])
            state.save()

            # Re-generate code addressing critique issues
            try:
                files = generate_code(brief, plan_items, existing_contents, state)
            except Exception as exc:
                print(f"[agent] Code re-generation failed: {exc}")
                state.add_error(str(exc))
                state.save()
                break

            write_files(files)
            state.update_files(files)
            state.save()

            commit_msg = f"agent: iteration {iteration} critique-loop {critique_loop} — fixes"
            commit_and_push(branch_name, commit_msg)

        if critique_passed:
            # Open PR with a clean description
            pr_body = build_pr_body(brief, state, state.last_critique_score, state.notes)
            pr_title = f"[Agent] {Path(BRIEF_PATH).stem} — auto-generated (score {state.last_critique_score}/10)"
            if REPO_NAME:
                pr_url = open_pr(branch_name, pr_title, pr_body, REPO_NAME)
            print(f"\n[agent] SUCCESS — PR opened: {pr_url}")
            return

    # --- Max iterations reached without passing critique ---
    print(f"\n[agent] Max iterations ({MAX_ITERATIONS}) reached without passing critique.")
    state.notes.append(
        f"Max iterations ({MAX_ITERATIONS}) reached. "
        f"Last critique score: {state.last_critique_score}/10. "
        "Opening PR with caveat."
    )
    state.save()

    notes = state.notes + [f"Last CI output:\n{last_ci_output[:2000]}"]
    pr_body = build_pr_body(brief, state, state.last_critique_score, notes)
    pr_body += (
        "\n\n---\n> **Note:** The agent hit its maximum iteration limit "
        f"({MAX_ITERATIONS}) without achieving a critique score of 8+. "
        "Manual review and follow-up are recommended."
    )
    pr_title = (
        f"[Agent] {Path(BRIEF_PATH).stem} — partial (score {state.last_critique_score}/10, "
        f"max iterations reached)"
    )
    if REPO_NAME:
        pr_url = open_pr(branch_name, pr_title, pr_body, REPO_NAME)
    print(f"[agent] PR opened (partial): {pr_url}")


if __name__ == "__main__":
    main()
