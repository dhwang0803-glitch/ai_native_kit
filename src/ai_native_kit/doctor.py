"""Self-diagnostic for an installed AI_Native_Kit harness.

Run after install, or after a Claude Code version update, to confirm the harness
is intact and surface known version quirks.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

OK = "OK"
WARN = "WARN"
FAIL = "FAIL"

# Things that recent Claude Code updates have been known to break. Shown as
# advisories so a user hitting them mid-session knows the workaround.
KNOWN_QUIRKS: list[str] = [
    "AskUserQuestion tool can start failing after a CC update - fall back to "
    "asking questions in plain text.",
    "If slash commands stop loading, confirm `.claude/commands/*.md` are present "
    "and re-open the session.",
]

# .gitignore entries the harness expects (SECURITY_AUDITOR S07).
REQUIRED_GITIGNORE = [".env", "*.pem", "*.key", "credentials.json", "settings.local.json"]


@dataclass
class Check:
    level: str
    label: str
    detail: str


def _check_assets(project: Path) -> list[Check]:
    checks: list[Check] = []
    markers = {
        "agent templates": project / "_agent_templates",
        "slash commands": project / ".claude" / "commands",
        "wiki (docs/context)": project / "docs" / "context",
        "specs (docs/specs)": project / "docs" / "specs",
    }
    for label, path in markers.items():
        if path.is_dir() and any(path.iterdir()):
            n = sum(1 for _ in path.rglob("*") if _.is_file())
            checks.append(Check(OK, label, f"{n} file(s) at {path.name}/"))
        else:
            checks.append(Check(FAIL, label, f"missing or empty: {path} - run `ai-native-kit init`"))

    claude = project / "CLAUDE.md"
    checks.append(
        Check(OK, "CLAUDE.md", "present")
        if claude.is_file()
        else Check(WARN, "CLAUDE.md", "missing (run init without --no-claude)")
    )
    return checks


def _check_git_hook(project: Path) -> list[Check]:
    if not (project / ".git").exists():
        return [Check(WARN, "git repo", "not a git repo - branch scaffolding disabled")]
    try:
        path = subprocess.run(
            ["git", "-C", str(project), "config", "--get", "core.hooksPath"],
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        return [Check(WARN, "git hooksPath", f"could not read git config: {exc}")]
    if path == ".githooks":
        return [Check(OK, "git hooksPath", "= .githooks")]
    return [Check(FAIL, "git hooksPath", f"= {path or '(unset)'} - run `git config core.hooksPath .githooks`")]


def _check_hook_file(project: Path) -> list[Check]:
    hook = project / ".githooks" / "post-checkout"
    if not hook.is_file():
        return [Check(FAIL, "post-checkout hook", "missing")]
    raw = hook.read_bytes()
    if b"\r\n" in raw:
        return [Check(FAIL, "post-checkout hook", "has CRLF line endings - bash will fail; reinstall with --force")]
    if not raw.startswith(b"#!"):
        return [Check(WARN, "post-checkout hook", "missing shebang")]
    return [Check(OK, "post-checkout hook", "present, LF, shebang OK")]


def _check_gitignore(project: Path) -> list[Check]:
    gi = project / ".gitignore"
    if not gi.is_file():
        return [Check(WARN, ".gitignore", "missing - add .env/*.pem/*.key/credentials.json/settings.local.json")]
    text = gi.read_text(encoding="utf-8", errors="ignore")
    missing = [e for e in REQUIRED_GITIGNORE if e not in text]
    if missing:
        return [Check(WARN, ".gitignore", f"missing entries: {', '.join(missing)}")]
    return [Check(OK, ".gitignore", "required entries present")]


def _check_cc_version() -> list[Check]:
    exe = shutil.which("claude")
    if not exe:
        return [Check(WARN, "Claude Code", "`claude` not on PATH - cannot read version")]
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
        return [Check(OK, "Claude Code", out or "version reported")]
    except (subprocess.SubprocessError, OSError) as exc:
        return [Check(WARN, "Claude Code", f"could not run `claude --version`: {exc}")]


def run(project: Path) -> tuple[list[Check], int]:
    """Run all checks. Returns (checks, exit_code). exit_code != 0 if any FAIL."""
    checks: list[Check] = []
    checks += _check_assets(project)
    checks += _check_git_hook(project)
    checks += _check_hook_file(project)
    checks += _check_gitignore(project)
    checks += _check_cc_version()
    exit_code = 1 if any(c.level == FAIL for c in checks) else 0
    return checks, exit_code
