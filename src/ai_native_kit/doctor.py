"""Self-diagnostic for an installed AI_Native_Kit harness.

Run after install, or after a Claude Code version update, to confirm the harness
is intact and surface known version quirks.  The ``--drift`` flag adds a second
pass that detects staleness between docs/context wiki pages and the actual
codebase structure.
"""

from __future__ import annotations

import re
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


def _top_level_dirs(project: Path) -> set[str]:
    """Return names of top-level directories (excluding hidden/generated)."""
    skip = {".git", ".github", ".githooks", ".claude", "node_modules",
            "__pycache__", ".venv", "venv", ".mypy_cache", ".ruff_cache",
            ".pytest_cache", "out", "dist", "build", ".next"}
    return {
        p.name for p in project.iterdir()
        if p.is_dir() and p.name not in skip and not p.name.startswith(".")
    }


def _extract_map_dirs(map_path: Path) -> set[str]:
    """Extract directory names from a MAP.md code-fence tree diagram."""
    if not map_path.is_file():
        return set()
    text = map_path.read_text(encoding="utf-8", errors="ignore")
    in_fence = False
    dirs: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        m = re.search(r"(?:├──|└──|│\s+├──|│\s+└──|\s+)\s*(\w[\w.-]*)/", stripped)
        if m:
            dirs.add(m.group(1))
    return dirs


def _extract_claude_sections(claude_path: Path) -> set[str]:
    """Extract H2/H3 section headings from CLAUDE.md."""
    if not claude_path.is_file():
        return set()
    text = claude_path.read_text(encoding="utf-8", errors="ignore")
    return {
        m.group(1).strip()
        for m in re.finditer(r"^#{2,3}\s+(.+)$", text, re.MULTILINE)
    }


def _check_map_drift(project: Path) -> list[Check]:
    """Compare MAP.md's directory listing against the actual filesystem."""
    map_path = project / "docs" / "context" / "MAP.md"
    if not map_path.is_file():
        return [Check(WARN, "MAP.md drift", "MAP.md not found - skip drift check")]
    map_dirs = _extract_map_dirs(map_path)
    if not map_dirs:
        return [Check(WARN, "MAP.md drift", "no directory tree found in MAP.md code fence")]
    actual = _top_level_dirs(project)
    undocumented = actual - map_dirs
    stale = map_dirs - actual
    if not undocumented and not stale:
        return [Check(OK, "MAP.md drift", f"{len(map_dirs)} dirs match filesystem")]
    checks: list[Check] = []
    if undocumented:
        checks.append(Check(
            WARN, "MAP.md drift",
            f"dirs exist but not in MAP.md: {', '.join(sorted(undocumented))}",
        ))
    if stale:
        checks.append(Check(
            WARN, "MAP.md drift",
            f"dirs in MAP.md but missing on disk: {', '.join(sorted(stale))}",
        ))
    return checks


def _check_spec_drift(project: Path) -> list[Check]:
    """Check if docs/specs/ covers the modules that exist on disk."""
    specs_dir = project / "docs" / "specs"
    if not specs_dir.is_dir():
        return []
    spec_names = {
        p.stem for p in specs_dir.iterdir()
        if p.is_file() and p.suffix == ".md"
        and p.stem not in {"README", "SPEC_TEMPLATE"}
    }
    modules_dir = project / "modules"
    if not modules_dir.is_dir():
        return []
    module_names = {p.name for p in modules_dir.iterdir() if p.is_dir() and not p.name.startswith("_")}
    unspecced = module_names - spec_names
    orphan_specs = spec_names - module_names
    if not unspecced and not orphan_specs:
        return [Check(OK, "spec drift", f"{len(spec_names)} specs match modules/")]
    checks: list[Check] = []
    if unspecced:
        checks.append(Check(
            WARN, "spec drift",
            f"modules without spec: {', '.join(sorted(unspecced))}",
        ))
    if orphan_specs:
        checks.append(Check(
            WARN, "spec drift",
            f"specs without module dir: {', '.join(sorted(orphan_specs))}",
        ))
    return checks


def _check_claude_staleness(project: Path) -> list[Check]:
    """Detect CLAUDE.md referencing paths that don't exist."""
    claude = project / "CLAUDE.md"
    if not claude.is_file():
        return []
    text = claude.read_text(encoding="utf-8", errors="ignore")
    referenced_paths: list[str] = []
    for m in re.finditer(r"`((?:src|modules|packages|services|database|infra)/[^`]+)`", text):
        referenced_paths.append(m.group(1))
    if not referenced_paths:
        return []
    missing = [p for p in referenced_paths if not (project / p.rstrip("/")).exists()]
    if not missing:
        return [Check(OK, "CLAUDE.md paths", f"{len(referenced_paths)} referenced paths all exist")]
    return [Check(
        WARN, "CLAUDE.md paths",
        f"{len(missing)} path(s) in CLAUDE.md not found on disk: {', '.join(missing[:5])}",
    )]


def run(project: Path, *, drift: bool = False) -> tuple[list[Check], int]:
    """Run all checks. Returns (checks, exit_code). exit_code != 0 if any FAIL."""
    checks: list[Check] = []
    checks += _check_assets(project)
    checks += _check_git_hook(project)
    checks += _check_hook_file(project)
    checks += _check_gitignore(project)
    checks += _check_cc_version()
    if drift:
        checks += _check_map_drift(project)
        checks += _check_spec_drift(project)
        checks += _check_claude_staleness(project)
    exit_code = 1 if any(c.level == FAIL for c in checks) else 0
    return checks, exit_code
