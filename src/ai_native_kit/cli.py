"""Command-line interface: ``ai-native-kit`` / ``aink``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_native_kit import __version__
from ai_native_kit import doctor as doctor_mod
from ai_native_kit.config import build_vars, load_config
from ai_native_kit.installer import assets_dir, available_presets, install


def _cmd_init(args: argparse.Namespace) -> int:
    project_dir = Path(args.path).resolve()
    if not project_dir.is_dir():
        print(f"error: {project_dir} is not a directory", file=sys.stderr)
        return 1

    config = load_config(project_dir)
    variables = build_vars(config)

    # --preset overrides the config's architecture.preset.
    preset = args.preset or variables["ARCH_PRESET"]
    presets = available_presets()
    if preset not in presets:
        print(f"error: unknown preset '{preset}'. available: {', '.join(presets)}", file=sys.stderr)
        return 1
    variables["ARCH_PRESET"] = preset

    print(f"AI_Native_Kit v{__version__}")
    print(f"target: {project_dir}")
    print(f"project: {variables['PROJECT_NAME']}  |  preset: {preset}")
    print("-" * 60)

    result = install(
        project_dir,
        variables,
        preset=preset,
        force=args.force,
        with_root_claude=not args.no_claude,
        with_config=args.with_config,
        configure_hook=not args.no_hook,
    )

    for path in sorted(result.created):
        print(f"  created  {path}")
    for path in sorted(result.skipped):
        print(f"  skipped  {path} (exists - use --force to overwrite)")
    if result.notes:
        print("-" * 60)
        for note in result.notes:
            print(f"  note: {note}")

    print("-" * 60)
    print(f"done: {len(result.created)} written, {len(result.skipped)} skipped")
    if result.skipped and not args.force:
        print("tip: re-run with --force to overwrite skipped files.")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    project_dir = Path(args.path).resolve()
    if not project_dir.is_dir():
        print(f"error: {project_dir} is not a directory", file=sys.stderr)
        return 1

    print(f"AI_Native_Kit doctor v{__version__}")
    print(f"target: {project_dir}")
    print("-" * 60)

    checks, exit_code = doctor_mod.run(project_dir)
    symbol = {doctor_mod.OK: "[ OK ]", doctor_mod.WARN: "[WARN]", doctor_mod.FAIL: "[FAIL]"}
    for c in checks:
        print(f"  {symbol[c.level]} {c.label}: {c.detail}")

    print("-" * 60)
    n_fail = sum(c.level == doctor_mod.FAIL for c in checks)
    n_warn = sum(c.level == doctor_mod.WARN for c in checks)
    print(f"result: {n_fail} fail, {n_warn} warn")

    print("\nknown version quirks (advisory):")
    for q in doctor_mod.KNOWN_QUIRKS:
        print(f"  - {q}")

    if exit_code:
        print("\nfix the [FAIL] items above (often: re-run `ai-native-kit init --force`).")
    return exit_code


def _cmd_list(_args: argparse.Namespace) -> int:
    src = assets_dir()
    print(f"AI_Native_Kit assets (from {src}):\n")
    print(f"  presets: {', '.join(available_presets())}\n")
    for group in sorted(p for p in src.iterdir() if p.is_dir()):
        print(f"  {group.name}/")
        for f in sorted(group.rglob("*")):
            if f.is_file():
                print(f"      {f.relative_to(group).as_posix()}")
    print("\n  top-level:")
    for f in sorted(p for p in src.iterdir() if p.is_file()):
        print(f"      {f.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    # Windows consoles default to a legacy code page (e.g. cp949) that cannot
    # encode some status glyphs; force UTF-8 so output never crashes.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass

    parser = argparse.ArgumentParser(
        prog="ai-native-kit",
        description="Bootstrap AI-Native Engineering setup into a project.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="install assets into a project")
    p_init.add_argument("path", nargs="?", default=".", help="target project dir (default: cwd)")
    p_init.add_argument("--preset", help=f"architecture preset (default from config). one of: {', '.join(available_presets())}")
    p_init.add_argument("--force", action="store_true", help="overwrite existing files")
    p_init.add_argument("--no-claude", action="store_true", help="skip the root CLAUDE.md skeleton")
    p_init.add_argument("--no-hook", action="store_true", help="skip configuring git core.hooksPath")
    p_init.add_argument(
        "--with-config",
        action="store_true",
        help="also write an ai-native-kit.toml you can edit and re-run",
    )
    p_init.set_defaults(func=_cmd_init)

    p_doctor = sub.add_parser("doctor", help="diagnose an installed harness (run after a CC update)")
    p_doctor.add_argument("path", nargs="?", default=".", help="target project dir (default: cwd)")
    p_doctor.set_defaults(func=_cmd_doctor)

    p_list = sub.add_parser("list", help="list bundled assets")
    p_list.set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)
