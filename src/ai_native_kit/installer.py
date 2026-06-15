"""Copy and render the packaged assets into a target project.

Assets are organized in two layers:

* the asset root (shared across presets) — agents, commands, githooks, specs,
  module/claude templates, the shared wiki files (decisions.md, adr/), and the
  config example;
* ``presets/<preset>/`` — files that differ by architecture preset (the root
  ``CLAUDE.md`` plus ``docs/context/MAP.md`` and ``architecture.md``).

The preset layer is applied on top of the base layer: a preset file overrides a
base file mapped to the same destination.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

_VAR_PATTERN = re.compile(r"\{\{(\w+)\}\}")

# First path segment under a layer -> destination directory in the project.
SEGMENT_MAP: dict[str, str] = {
    "agents": "_agent_templates",
    "claude_templates": "_claude_templates",
    "module_templates": "_module_templates",
    "commands": ".claude/commands",
    "githooks": ".githooks",
    "docs_context": "docs/context",
    "specs": "docs/specs",
}

# Single files needing special destinations / install gates.
# value: (destination, gate)  — gate is checked against install() flags.
SPECIAL_FILES: dict[str, tuple[str, str]] = {
    "CLAUDE.root.md": ("CLAUDE.md", "root_claude"),
    "ai-native-kit.toml.example": ("ai-native-kit.toml", "config"),
}


def assets_dir() -> Path:
    """Absolute path to the packaged ``assets/`` directory."""
    return Path(__file__).resolve().parent / "assets"


def available_presets() -> list[str]:
    """Preset names discovered under ``assets/presets/``."""
    presets_root = assets_dir() / "presets"
    if not presets_root.is_dir():
        return []
    return sorted(p.name for p in presets_root.iterdir() if p.is_dir())


def render(text: str, variables: dict[str, str]) -> str:
    """Replace every ``{{VAR}}`` token with its value from ``variables``.

    Unknown tokens are left untouched so template authors get a visible signal.
    """

    def _sub(match: re.Match[str]) -> str:
        return variables.get(match.group(1), match.group(0))

    return _VAR_PATTERN.sub(_sub, text)


def _resolve(rel: str) -> tuple[str, bool, str | None] | None:
    """Map a layer-relative path to (dest, executable, gate).

    Returns None for paths that are not installable assets.
    """
    if rel in SPECIAL_FILES:
        dest, gate = SPECIAL_FILES[rel]
        return dest, False, gate
    seg, _, rest = rel.partition("/")
    base = SEGMENT_MAP.get(seg)
    if base is None:
        return None
    dest = f"{base}/{rest}" if rest else base
    return dest, seg == "githooks", None


@dataclass
class InstallResult:
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _collect(preset: str) -> dict[str, tuple[Path, bool, str | None]]:
    """Build dest -> (source, executable, gate), preset overriding base."""
    root = assets_dir()
    collected: dict[str, tuple[Path, bool, str | None]] = {}

    # Base layer: everything under assets/ except the presets/ subtree.
    for src in sorted(root.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(root).as_posix()
        if rel.startswith("presets/"):
            continue
        resolved = _resolve(rel)
        if resolved:
            dest, exe, gate = resolved
            collected[dest] = (src, exe, gate)

    # Preset layer: overrides + additions.
    preset_root = root / "presets" / preset
    if preset_root.is_dir():
        for src in sorted(preset_root.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(preset_root).as_posix()
            resolved = _resolve(rel)
            if resolved:
                dest, exe, gate = resolved
                collected[dest] = (src, exe, gate)

    return collected


def install(
    project_dir: Path,
    variables: dict[str, str],
    *,
    preset: str = "clean",
    force: bool = False,
    with_root_claude: bool = True,
    with_config: bool = False,
    configure_hook: bool = True,
) -> InstallResult:
    """Install assets into ``project_dir``, rendering ``{{VAR}}`` tokens.

    Existing files are preserved unless ``force`` is set.
    """
    result = InstallResult()
    gates = {"root_claude": with_root_claude, "config": with_config}

    for dest, (src, executable, gate) in _collect(preset).items():
        if gate is not None and not gates.get(gate, True):
            continue
        dst_path = project_dir / dest
        if dst_path.exists() and not force:
            result.skipped.append(dest)
            continue
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = render(src.read_text(encoding="utf-8"), variables)
        # Hooks must use LF endings even on Windows or bash chokes on them.
        newline = "\n" if executable else None
        dst_path.write_text(rendered, encoding="utf-8", newline=newline)
        if executable:
            dst_path.chmod(0o755)
        result.created.append(dest)

    if configure_hook:
        _configure_git_hook(project_dir, result)

    return result


def _configure_git_hook(project_dir: Path, result: InstallResult) -> None:
    if not (project_dir / ".git").exists():
        result.notes.append(
            "git repo not detected - run `git init` then "
            "`git config core.hooksPath .githooks` to enable branch scaffolding."
        )
        return
    try:
        current = subprocess.run(
            ["git", "-C", str(project_dir), "config", "--get", "core.hooksPath"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        if current == ".githooks":
            result.notes.append("git core.hooksPath already set to .githooks")
            return
        subprocess.run(
            ["git", "-C", str(project_dir), "config", "core.hooksPath", ".githooks"],
            check=True,
            capture_output=True,
            text=True,
        )
        result.notes.append("git core.hooksPath -> .githooks (branch scaffolding enabled)")
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        result.notes.append(f"could not set core.hooksPath automatically: {exc}")
