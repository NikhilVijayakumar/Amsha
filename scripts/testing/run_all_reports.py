#!/usr/bin/env python3
"""Run available test suites and generate report artifacts in one command."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SuiteResult:
    name: str
    path: str
    ran: bool
    returncode: int
    junit_xml: str
    coverage_xml: str
    summary_md: str
    summary_json: str


def run_command(cmd: list[str], cwd: Path) -> int:
    print("\n$", " ".join(cmd))
    completed = subprocess.run(cmd, cwd=str(cwd), check=False)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--skip-editable-install",
        action="store_true",
        help="Skip `pip install -e .` before running tests",
    )
    parser.add_argument(
        "--cov-target",
        default="src/nikhil/amsha",
        help="Coverage target for pytest --cov (default: src/nikhil/amsha)",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    output_dir = project_root / "output" / "testing"
    output_dir.mkdir(parents=True, exist_ok=True)

    python_exe = sys.executable
    summary_script = project_root / "scripts" / "testing" / "generate_module_summary.py"

    if not summary_script.exists():
        print(f"ERROR: Summary script not found: {summary_script}")
        return 2

    if not args.skip_editable_install:
        print("\nInstalling package in editable mode...")
        rc = run_command([python_exe, "-m", "pip", "install", "-e", "."], project_root)
        if rc != 0:
            print("ERROR: Editable install failed.")
            return rc

    suites = [
        ("unit", "tests/unit"),
        ("integration", "tests/integration"),
        ("e2e", "tests/e2e"),
    ]

    results: list[SuiteResult] = []
    any_ran = False
    any_failed = False

    for suite_name, suite_path in suites:
        suite_dir = project_root / suite_path
        junit_xml = output_dir / f"junit-{suite_name}.xml"
        coverage_xml = output_dir / f"coverage-{suite_name}.xml"
        summary_md = output_dir / f"module-summary-{suite_name}.md"
        summary_json = output_dir / f"module-summary-{suite_name}.json"

        if not suite_dir.exists():
            print(f"\nSkipping {suite_name}: {suite_path} not found")
            results.append(
                SuiteResult(
                    name=suite_name,
                    path=suite_path,
                    ran=False,
                    returncode=0,
                    junit_xml=str(junit_xml.relative_to(project_root)),
                    coverage_xml=str(coverage_xml.relative_to(project_root)),
                    summary_md=str(summary_md.relative_to(project_root)),
                    summary_json=str(summary_json.relative_to(project_root)),
                )
            )
            continue

        any_ran = True
        pytest_cmd = [
            python_exe,
            "-m",
            "pytest",
            suite_path,
            f"--junitxml={junit_xml}",
            f"--cov={args.cov_target}",
            f"--cov-report=xml:{coverage_xml}",
            "--cov-report=term",
        ]
        rc = run_command(pytest_cmd, project_root)
        any_failed = any_failed or rc != 0

        if junit_xml.exists():
            summary_cmd = [
                python_exe,
                str(summary_script),
                "--junit",
                str(junit_xml),
                "--coverage",
                str(coverage_xml),
                "--output-md",
                str(summary_md),
                "--output-json",
                str(summary_json),
            ]
            run_command(summary_cmd, project_root)
        else:
            print(f"WARNING: Missing JUnit XML for {suite_name}, summary generation skipped.")

        results.append(
            SuiteResult(
                name=suite_name,
                path=suite_path,
                ran=True,
                returncode=rc,
                junit_xml=str(junit_xml.relative_to(project_root)),
                coverage_xml=str(coverage_xml.relative_to(project_root)),
                summary_md=str(summary_md.relative_to(project_root)),
                summary_json=str(summary_json.relative_to(project_root)),
            )
        )

    if not any_ran:
        print("ERROR: No test suites found to run.")
        return 3

    manifest = {
        "python_executable": python_exe,
        "project_root": str(project_root),
        "results": [r.__dict__ for r in results],
        "overall_status": "failed" if any_failed else "passed",
    }
    manifest_path = output_dir / "report-run-summary.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("\nRun summary written to:", manifest_path)
    print("Overall status:", manifest["overall_status"])

    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
