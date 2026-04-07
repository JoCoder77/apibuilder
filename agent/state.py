"""Lightweight in-run state management via a JSON file written to /tmp."""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any

STATE_PATH = "/tmp/agent-state.json"


@dataclass
class AgentState:
    branch: str = ""
    iteration: int = 0
    critique_loop: int = 0
    previous_errors: list[str] = field(default_factory=list)
    previous_critique_issues: list[str] = field(default_factory=list)
    # Mapping of path -> content for all files written so far
    generated_files: dict[str, str] = field(default_factory=dict)
    last_ci_run_id: str = ""
    last_critique_score: int = 0
    notes: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Persist state to STATE_PATH."""
        with open(STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, indent=2)

    @classmethod
    def load(cls) -> "AgentState":
        """Load state from STATE_PATH, or return a fresh instance."""
        if os.path.exists(STATE_PATH):
            try:
                with open(STATE_PATH, encoding="utf-8") as fh:
                    data: dict[str, Any] = json.load(fh)
                return cls(**data)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def add_error(self, error: str) -> None:
        self.previous_errors.append(error)
        # Keep only the last 5 to avoid bloating the prompt
        self.previous_errors = self.previous_errors[-5:]

    def add_critique_issues(self, issues: list[str]) -> None:
        self.previous_critique_issues.extend(issues)
        self.previous_critique_issues = self.previous_critique_issues[-20:]

    def update_files(self, files: list[dict[str, str]]) -> None:
        """Merge a list of {path, content} dicts into generated_files."""
        for f in files:
            self.generated_files[f["path"]] = f["content"]

    def format_errors(self) -> str:
        if not self.previous_errors:
            return "None"
        return "\n\n---\n\n".join(self.previous_errors)

    def format_critique_issues(self) -> str:
        if not self.previous_critique_issues:
            return "None"
        return "\n".join(f"- {issue}" for issue in self.previous_critique_issues)

    def format_generated_files(self) -> str:
        """Return all generated files formatted for prompt insertion."""
        parts = []
        for path, content in self.generated_files.items():
            parts.append(f"### {path}\n```\n{content}\n```")
        return "\n\n".join(parts) if parts else "None"
