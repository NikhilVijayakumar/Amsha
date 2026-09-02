#!/usr/bin/env python3
"""Generate module-wise testing summary from pytest JUnit XML and coverage XML."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET


def parse_junit(junit_path: Path) -> tuple[dict, dict]:
    tree = ET.parse(junit_path)
    root = tree.getroot()

    suite_node = root.find("testsuite") if root.tag == "testsuites" else root
    if suite_node is None:
        raise ValueError("No testsuite node found in JUnit XML")

    totals = {
        "tests": int(suite_node.attrib.get("tests", 0)),
        "failures": int(suite_node.attrib.get("failures", 0)),
        "errors": int(suite_node.attrib.get("errors", 0)),
        "skipped": int(suite_node.attrib.get("skipped", 0)),
        "time": float(suite_node.attrib.get("time", 0.0)),
    }
    totals["passed"] = max(
        0,
        totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"],
    )

    stats: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "total": 0}
    )

    for testcase in suite_node.findall("testcase"):
        name = testcase.attrib.get("name", "")
        classname = testcase.attrib.get("classname", "")
        ref = classname or name
        suite_name, module_name = infer_suite_module(ref)

        status = "passed"
        if testcase.find("error") is not None:
            status = "errors"
        elif testcase.find("failure") is not None:
            status = "failed"
        elif testcase.find("skipped") is not None:
            status = "skipped"

        key = (suite_name, module_name)
        stats[key][status] += 1
        stats[key]["total"] += 1

    return totals, stats


def infer_suite_module(ref: str) -> tuple[str, str]:
    parts = [p for p in ref.replace("/", ".").split(".") if p]
    if len(parts) >= 3 and parts[0] == "tests":
        return parts[1], parts[2]
    if len(parts) >= 2 and parts[0] == "tests":
        return parts[1], "unknown"
    return "unknown", "unknown"


def parse_coverage(coverage_path: Path) -> dict[str, float]:
    if not coverage_path.exists():
        return {}

    tree = ET.parse(coverage_path)
    root = tree.getroot()

    weighted: dict[str, dict[str, int]] = defaultdict(lambda: {"covered": 0, "valid": 0})

    for class_node in root.findall(".//class"):
        filename = class_node.attrib.get("filename", "")
        if not filename:
            continue
        module_name = filename.split("/", 1)[0] if "/" in filename else "."

        for line_node in class_node.findall("./lines/line"):
            hits = int(line_node.attrib.get("hits", 0))
            weighted[module_name]["valid"] += 1
            if hits > 0:
                weighted[module_name]["covered"] += 1

    coverage_pct: dict[str, float] = {}
    for module_name, counts in weighted.items():
        valid = counts["valid"]
        coverage_pct[module_name] = (counts["covered"] / valid * 100.0) if valid else 0.0

    return coverage_pct


def build_summary(stats: dict, coverage_pct: dict[str, float]) -> list[dict]:
    modules = set()
    for _, module_name in stats.keys():
        modules.add(module_name)
    modules.update(coverage_pct.keys())

    summary_rows = []
    for module_name in sorted(modules):
        unit = stats.get(("unit", module_name), {"passed": 0, "failed": 0, "skipped": 0, "errors": 0})
        integ = stats.get(("integration", module_name), {"passed": 0, "failed": 0, "skipped": 0, "errors": 0})
        e2e = stats.get(("e2e", module_name), {"passed": 0, "failed": 0, "skipped": 0, "errors": 0})

        summary_rows.append(
            {
                "module": module_name,
                "unit": unit,
                "integration": integ,
                "e2e": e2e,
                "coverage_pct": round(coverage_pct.get(module_name, 0.0), 2),
            }
        )

    return summary_rows


def render_markdown(rows: list[dict]) -> str:
    lines = [
        "| Module | Unit (P/F/S/E) | Integration (P/F/S/E) | E2E (P/F/S/E) | Coverage (%) |",
        "| --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        unit = row["unit"]
        integ = row["integration"]
        e2e = row["e2e"]
        lines.append(
            "| {module} | {up}/{uf}/{us}/{ue} | {ip}/{iff}/{is_}/{ie} | {ep}/{ef}/{es}/{ee} | {cov:.2f} |".format(
                module=row["module"],
                up=unit["passed"],
                uf=unit["failed"],
                us=unit["skipped"],
                ue=unit["errors"],
                ip=integ["passed"],
                iff=integ["failed"],
                is_=integ["skipped"],
                ie=integ["errors"],
                ep=e2e["passed"],
                ef=e2e["failed"],
                es=e2e["skipped"],
                ee=e2e["errors"],
                cov=row["coverage_pct"],
            )
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--junit", required=True, help="Path to pytest JUnit XML")
    parser.add_argument("--coverage", required=False, help="Path to coverage XML")
    parser.add_argument("--output-md", required=False, help="Path to write markdown table")
    parser.add_argument("--output-json", required=False, help="Path to write summary JSON")
    args = parser.parse_args()

    junit_path = Path(args.junit)
    coverage_path = Path(args.coverage) if args.coverage else None

    totals, stats = parse_junit(junit_path)
    coverage_pct = parse_coverage(coverage_path) if coverage_path else {}
    rows = build_summary(stats, coverage_pct)

    markdown = render_markdown(rows)

    if args.output_md:
        out_md = Path(args.output_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(markdown, encoding="utf-8")

    payload = {
        "overall": totals,
        "module_summary": rows,
    }

    if args.output_json:
        out_json = Path(args.output_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Overall:")
    print(json.dumps(totals, indent=2))
    print("\nModule summary:")
    print(markdown)


if __name__ == "__main__":
    main()
