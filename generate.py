#!/usr/bin/env python3
"""AWS CLI Runbook generator.

Reads one or more runbook YAML files and renders Markdown using Jinja2
templates and snippets bundled in the same directory as this script.

Usage:
    python generate.py path/to/runbook.yaml [path...]

Output:
    Each <runbook>.yaml under <project>/runbooks/ is rendered to
    <project>/dist/runbooks/<basename>.md, where <project> is the parent
    of the runbooks/ directory.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


# Toolkit assets (templates/, snippets/) live next to this script.
TOOLKIT_ROOT = Path(__file__).resolve().parent


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TOOLKIT_ROOT)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def load_params_files(runbook_yaml_path: Path, params_files: list[str]) -> dict[str, Any]:
    """Load and merge param files referenced from a runbook YAML.

    Paths are resolved relative to the runbook YAML file. Later files
    override earlier ones (last write wins).
    """
    merged: dict[str, Any] = {}
    base_dir = runbook_yaml_path.parent
    for rel in params_files:
        params_path = (base_dir / rel).resolve()
        if not params_path.exists():
            raise FileNotFoundError(
                f"params file not found: {params_path} "
                f"(referenced by {runbook_yaml_path.name})"
            )
        data = load_yaml(params_path)
        params = data.get("params") or {}
        if not isinstance(params, dict):
            raise ValueError(
                f"params file must have a top-level 'params:' mapping: {params_path}"
            )
        merged.update(params)
    return merged


def dist_output_path(runbook_yaml_path: Path) -> Path:
    """Map a runbook YAML to its dist output path.

    e.g. <project>/runbooks/0101-create-vpc.yaml
       -> <project>/dist/runbooks/0101-create-vpc.md
    """
    project_root = runbook_yaml_path.parent.parent
    basename = runbook_yaml_path.stem
    return project_root / "dist" / "runbooks" / f"{basename}.md"


def render_runbook(runbook_yaml_path: Path, env: Environment) -> Path:
    data = load_yaml(runbook_yaml_path)
    if "runbook" not in data:
        raise ValueError(
            f"runbook YAML must have a top-level 'runbook:' key: {runbook_yaml_path}"
        )
    runbook = data["runbook"]

    template_name = runbook.get("template")
    if not template_name:
        raise ValueError(
            f"runbook.template is required: {runbook_yaml_path}"
        )

    params_files = runbook.get("params_files") or []
    runbook_params = runbook.get("params") or {}
    merged_params = {
        **load_params_files(runbook_yaml_path, params_files),
        **runbook_params,
    }

    template_path = f"templates/{template_name}.md.j2"
    try:
        template = env.get_template(template_path)
    except TemplateNotFound as e:
        raise FileNotFoundError(
            f"template not found: {template_path} "
            f"(referenced by {runbook_yaml_path.name})"
        ) from e

    context = {
        "runbook": runbook,
        "navigation": runbook.get("navigation") or {},
        **merged_params,
    }
    output = template.render(**context)

    out_path = dist_output_path(runbook_yaml_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate AWS CLI runbooks from YAML.",
    )
    parser.add_argument(
        "runbooks",
        nargs="+",
        help="Path(s) to runbook YAML file(s).",
    )
    args = parser.parse_args(argv)

    env = build_env()
    exit_code = 0
    for raw in args.runbooks:
        runbook_yaml = Path(raw).resolve()
        if not runbook_yaml.exists():
            print(f"error: runbook not found: {runbook_yaml}", file=sys.stderr)
            exit_code = 2
            continue
        try:
            out_path = render_runbook(runbook_yaml, env)
        except (FileNotFoundError, ValueError) as e:
            print(f"error: {e}", file=sys.stderr)
            exit_code = 1
            continue
        try:
            display = out_path.relative_to(Path.cwd())
        except ValueError:
            display = out_path
        print(f"generated: {display}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
