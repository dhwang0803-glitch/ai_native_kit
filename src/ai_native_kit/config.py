"""Configuration loading and the variable map used to render assets.

A project may drop an ``ai-native-kit.toml`` at its root to override defaults.
Anything not specified falls back to :data:`DEFAULTS`. The resulting flat
mapping (see :func:`build_vars`) is what the installer substitutes into every
``{{VAR}}`` placeholder found in the packaged assets.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

CONFIG_FILENAME = "ai-native-kit.toml"

# ── Default configuration ─────────────────────────────────────────────────────
# Mirrors the shape of ai-native-kit.toml. Override any subset in the project's
# own config file; unspecified keys keep these values.
DEFAULTS: dict[str, Any] = {
    "project": {
        "name": "My Project",
    },
    "git": {
        # PRs target the integration branch; releases flow integration -> base.
        "base_branch": "main",
        "integration_branch": "development",
    },
    "stack": {
        # Which language ecosystems this project uses. Drives which test/lint
        # commands appear in the agent templates.
        "languages": ["python", "javascript"],
        "python": {
            "min_version": "3.12",
            "test": "pytest",
            "lint": "ruff check",
            "line_length": 120,
        },
        "javascript": {
            "test": "npm run test",
            "lint": "npm run lint",
        },
    },
    "architecture": {
        # "clean" keeps the Clean Architecture preset (domain/application/adapters
        # layering, dependency-direction rules, SSOT). "generic" drops the
        # layering language for a plain src/tests/scripts layout.
        "preset": "clean",
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` onto a copy of ``base``."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(project_dir: Path) -> dict[str, Any]:
    """Load ``ai-native-kit.toml`` from ``project_dir`` merged over defaults."""
    config_path = project_dir / CONFIG_FILENAME
    if not config_path.is_file():
        return _deep_merge(DEFAULTS, {})
    with config_path.open("rb") as fh:
        user_config = tomllib.load(fh)
    return _deep_merge(DEFAULTS, user_config)


def build_vars(config: dict[str, Any]) -> dict[str, str]:
    """Flatten a config dict into the ``{{VAR}}`` substitution map."""
    project = config["project"]
    git = config["git"]
    stack = config["stack"]
    py = stack["python"]
    js = stack["javascript"]
    arch = config["architecture"]

    return {
        "PROJECT_NAME": str(project["name"]),
        "BASE_BRANCH": str(git["base_branch"]),
        "INTEGRATION_BRANCH": str(git["integration_branch"]),
        "PYTHON_MIN": str(py["min_version"]),
        "PY_TEST": str(py["test"]),
        "PY_LINT": str(py["lint"]),
        "PY_LINE_LENGTH": str(py["line_length"]),
        "JS_TEST": str(js["test"]),
        "JS_LINT": str(js["lint"]),
        "ARCH_PRESET": str(arch["preset"]),
    }


def languages(config: dict[str, Any]) -> list[str]:
    """Return the normalized list of enabled language ecosystems."""
    return [str(lang).lower() for lang in config["stack"]["languages"]]
