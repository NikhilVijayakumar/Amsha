from __future__ import annotations

from pathlib import Path
from typing import Optional


def _severity_counts(findings: list[dict]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0, "advisory": 0}
    for f in findings:
        s = f.get("severity", "")
        if s in counts:
            counts[s] += 1
    return counts


def _findings_as_list(raw) -> list[dict]:
    if isinstance(raw, dict):
        f = raw.get("findings")
        if isinstance(f, list):
            return [_normalize(x) for x in f]
        return []
    if hasattr(raw, "findings"):
        return [_normalize(x) for x in raw.findings]
    if isinstance(raw, list):
        return [_normalize(x) for x in raw]
    return []


def _normalize(f) -> dict:
    if isinstance(f, dict):
        return f
    return {
        "severity": getattr(f, "severity", ""),
        "rule_id": getattr(f, "rule_id", ""),
        "rule_source": getattr(f, "rule_source", ""),
        "message": getattr(f, "message", ""),
        "suggested_fix": getattr(f, "suggested_fix", ""),
    }


def _component_score(name: str, findings: list[dict]) -> dict:
    c = _severity_counts(findings)
    # each error -20, each warning -8, each advisory -2; floor 0
    score = max(0, 100 - c["error"] * 20 - c["warning"] * 8 - c["advisory"] * 2)
    verdict = "fail" if c["error"] else ("pass" if c["warning"] == 0 else "pass_with_warnings")
    return {"component": name, "score": score, "verdict": verdict,
            "errors": c["error"], "warnings": c["warning"], "advisories": c["advisory"]}


def _overall(components: list[dict]) -> dict:
    if not components:
        return {"score": 100, "verdict": "pass"}
    score = round(sum(c["score"] for c in components) / len(components))
    any_fail = any(c["verdict"] == "fail" for c in components)
    return {"score": score, "verdict": "fail" if any_fail else "pass"}


def score_crew(crew_dir: str | Path, smoke_output: Optional[dict] = None) -> dict:
    """Score a crew against the methodology rubric.

    Reuses Phase 3's verify engine (the rubric from implementation docs) and
    optionally blends in the outcome of a prior smoke_test/dry_run_parse.

    Args:
        crew_dir: path to the crew configuration directory.
        smoke_output: optional dict from smoke_test/dry_run_parse to account for.

    Returns:
        dict with {'overall': {score, verdict}, 'components': [...], 'summary'}.
    """
    from amsha_mcp.tools import verification

    result = verification.verify_crew_yaml(crew_dir)
    findings = _findings_as_list(result)

    by_rule: dict[str, list[dict]] = {}
    for f in findings:
        rule = f.get("rule_id", "misc").split(".")[0]
        by_rule.setdefault(rule, []).append(f)

    components = [_component_score(k, v) for k, v in sorted(by_rule.items())]
    overall = _overall(components)

    if smoke_output is not None and not smoke_output.get("ok", True):
        overall["score"] = max(0, overall["score"] - 20)
        overall["verdict"] = "fail"
        overall["smoke_failed"] = smoke_output.get("summary", "smoke test failed")

    return {"overall": overall, "components": components,
            "summary": f"score {overall['score']} ({overall['verdict']}) across {len(components)} component group(s)"}


def evaluate_design(prerequisite_artifacts: dict[str, dict], crew_dir: str | Path) -> dict:
    """Score whether the assembled crew faithfully realizes the validated design.

    Rolls the Phase 3 prerequisite + alignment + crew checks into design-quality
    scores.

    Args:
        prerequisite_artifacts: mapping of stage ("00"-"09") to filled artifact dict.
        crew_dir: path to the crew configuration directory.

    Returns:
        dict with {
            'design': {score, verdict},
            'realization': {score, verdict},
            'components': [...],
            'summary'
        }.
    """
    from amsha_mcp.tools import verification

    prereq = verification.verify_prerequisite_artifacts(prerequisite_artifacts)
    crew = verification.verify_crew_yaml(crew_dir)
    prereq_findings = _findings_as_list(prereq)
    crew_findings = _findings_as_list(crew)

    design = _component_score("design", prereq_findings)
    realization = _component_score("realization", crew_findings)

    # Alignment: requires structured agents/tasks lists. Best-effort; empty if unavailable.
    alignment_report = _alignment_eval(crew_findings)
    realization["score"] = max(0, realization["score"] - alignment_report["penalty"])
    if alignment_report["penalty"]:
        realization["verdict"] = realization["verdict"] if realization["verdict"] == "fail" else "pass_with_warnings"

    return {
        "design": design,
        "realization": realization,
        "alignment": alignment_report["report"],
        "components": [
            {"group": "design", **design},
            {"group": "realization", **realization},
        ],
        "summary": (f"design {design['score']} ({design['verdict']}), "
                    f"realization {realization['score']} ({realization['verdict']})"),
    }


def _alignment_eval(crew_findings: list[dict]) -> dict:
    """Best-effort alignment signal from crew findings; no structured lists
    means no penalty and an advisory note."""
    misaligned = sum(1 for f in crew_findings if f.get("rule_id", "").startswith("alignment."))
    penalty = min(20, misaligned * 7 if misaligned else 0)
    report = {
        "found": misaligned,
        "note": ("alignment agent/task lists not supplied; skipped" if not misaligned else
                 f"{misaligned} alignment issue(s) surfaced by crew checks"),
    }
    return {"penalty": penalty, "report": report}
