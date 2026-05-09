#!/usr/bin/env python3
"""AWS CLI Runbook generator.

Reads a scenario YAML and the runbook YAMLs it references, then renders
Markdown using Jinja2 templates and snippets.

Usage:
    python generate.py \\
        --toolkit /path/to/runbook-toolkit \\
        --scenario examples/scenarios/0100-create-vpc.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


SCENARIO_TEMPLATE = "templates/scenario.md.j2"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_env(project_root: Path, toolkit_root: Path) -> Environment:
    search_paths: list[str] = [str(project_root)]
    if toolkit_root.resolve() != project_root.resolve():
        search_paths.append(str(toolkit_root))
    return Environment(
        loader=FileSystemLoader(search_paths),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def resolve_runbook_path(project_root: Path, runbook_id: str) -> Path:
    candidate = project_root / "runbooks" / f"{runbook_id}.yaml"
    if not candidate.exists():
        raise FileNotFoundError(f"Runbook YAML not found: {candidate}")
    return candidate


def render_runbook(
    runbook_yaml_path: Path,
    scenario_data: dict[str, Any],
    scenario_params: dict[str, Any],
    env: Environment,
) -> tuple[Path, dict[str, Any]]:
    runbook = load_yaml(runbook_yaml_path)["runbook"]
    template_name = runbook["template"]
    runbook_params = runbook.get("params") or {}
    merged_params = {**scenario_params, **runbook_params}

    template_path = f"templates/{template_name}.md.j2"
    try:
        template = env.get_template(template_path)
    except TemplateNotFound as e:
        raise FileNotFoundError(
            f"Template not found: {template_path} (referenced by {runbook_yaml_path.name})"
        ) from e

    context = {
        "runbook": runbook,
        "scenario": scenario_data,
        "navigation": runbook.get("navigation") or {},
        **merged_params,
    }
    output = template.render(**context)

    out_path = runbook_yaml_path.with_suffix(".md")
    out_path.write_text(output, encoding="utf-8")
    return out_path, runbook


def render_scenario(
    scenario_yaml_path: Path,
    scenario_data: dict[str, Any],
    runbook_summaries: list[dict[str, Any]],
    env: Environment,
) -> Path:
    template = env.get_template(SCENARIO_TEMPLATE)
    output = template.render(scenario=scenario_data, steps=runbook_summaries)
    out_path = scenario_yaml_path.with_suffix(".md")
    out_path.write_text(output, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate AWS CLI runbooks from YAML.")
    parser.add_argument(
        "--toolkit", required=True,
        help="Path to runbook-toolkit (directory containing snippets/ and templates/).",
    )
    parser.add_argument(
        "--scenario", required=True,
        help="Path to scenario YAML.",
    )
    parser.add_argument(
        "--project",
        help="Path to project root. Defaults to the parent of the scenario file's directory "
             "(e.g. scenarios/ → its parent).",
    )
    args = parser.parse_args(argv)

    toolkit_root = Path(args.toolkit).resolve()
    scenario_yaml_path = Path(args.scenario).resolve()
    project_root = (
        Path(args.project).resolve()
        if args.project
        else scenario_yaml_path.parent.parent
    )

    if not scenario_yaml_path.exists():
        print(f"error: scenario not found: {scenario_yaml_path}", file=sys.stderr)
        return 2

    scenario_data = load_yaml(scenario_yaml_path)["scenario"]
    scenario_params = scenario_data.get("params") or {}
    env = build_env(project_root, toolkit_root)

    runbook_summaries: list[dict[str, Any]] = []
    for step in scenario_data.get("steps") or []:
        runbook_id = step["runbook"]
        runbook_yaml = resolve_runbook_path(project_root, runbook_id)
        out_path, runbook = render_runbook(runbook_yaml, scenario_data, scenario_params, env)
        runbook_summaries.append({
            "id": runbook["id"],
            "title": runbook["title"],
            "link": f"../runbooks/{runbook_id}.md",
        })
        print(f"generated: {out_path.relative_to(project_root)}")

    scenario_out = render_scenario(scenario_yaml_path, scenario_data, runbook_summaries, env)
    print(f"generated: {scenario_out.relative_to(project_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
