"""Phase 2 Architecture Guidance tools (proposal 02).

These add *sequencing* over the read-only methodology content Phase 1 serves:
a session cursor, stage-by-stage structural acceptance, and gating that defers
capability selection (stage 07) until decomposition stages pass. Validation here
is structural only — existence + required fields + self-reported checklist — not
a judgment of design quality (that is Phase 3's job).
"""
from __future__ import annotations

from .. import docs_loader as dl
from .. import session as sess


# ---------------------------------------------------------------------------
# Per-stage required fields, grounded in each prerequisite doc's own
# "Required ..." / "Every ... should define" enumerations.
# ---------------------------------------------------------------------------
STAGE_FIELDS = {
    "00": ["problem", "start_condition", "desired_end_condition", "primary_objective", "constraints", "success_definition"],
    "01": ["start_boundary", "end_boundary", "scope", "completion_definition"],
    "02": ["start_state", "end_state", "processes", "relationships"],
    "03": ["contracts"],  # per-process inputs/outputs/atomicity; validated deeper in Phase 3
    "04": ["validation"], # process validation & human-review approval outcome
    "05": ["flow_order", "transitions", "state_requirements", "checkpoints"],
    "06": ["failures", "recovery", "unrecoverable_definition"],
    "07": ["capabilities"],  # least-powerful mechanism per requirement
    "08": ["architecture_yaml", "validation_outcome"],
    "09": ["handoff"],  # approved handoff artifact
}

_STAGE_DOC = {
    "00": "00-problem-definition.md", "01": "01-goal-and-boundary-definition.md",
    "02": "02-process-decomposition.md", "03": "03-process-contracts-and-atomicity.md",
    "04": "04-process-validation-and-human-review.md", "05": "05-flow-and-state-planning.md",
    "06": "06-corner-cases-and-failure-planning.md", "07": "07-capability-selection.md",
    "08": "08-architecture-validation.md", "09": "09-architecture-handoff-checklist.md",
}


def _artifact(artifact) -> dict:
    if isinstance(artifact, dict):
        return artifact
    raise ValueError("artifact must be a JSON/YAML mapping (a dict of fields).")


def _missing_fields(stage: str, artifact: dict) -> list[str]:
    required = STAGE_FIELDS.get(stage, [])
    return [f for f in required if not artifact.get(f)]


def _stage_content(stage: str) -> str:
    path = dl.repo_root() / "mcp" / "docs" / "prerequisite" / _STAGE_DOC[stage]
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _valid_stage_or_error(stage: str) -> str | None:
    if stage not in STAGE_FIELDS:
        known = ", ".join(sorted(sess.STAGE_ORDER))
        return f"Unknown architecture stage '{stage}'. Valid stages: {known}"


def begin_architecture_session(problem_statement: str) -> dict:
    """Start an architecture session with a problem statement. Returns session_id + first stage."""
    if not problem_statement or not problem_statement.strip():
        return {"error": "problem_statement is required and must be non-empty."}
    s = sess.create(problem_statement)
    first = sess.next_pending(s["id"])
    return {
        "session_id": s["id"],
        "problem": s["problem"],
        "current_stage": first,
        "current_stage_title": sess.STAGE_TITLES[first],
    }


def submit_stage_artifact(session_id: str, stage: str, artifact: dict, checklist: list[str] | None = None) -> dict:
    """Submit a filled artifact for a stage. Structurally validates and, if it passes,
    advances the session to the next pending stage (or reports the unmet fields)."""
    s = sess.get(session_id)
    if not s:
        return {"error": f"Unknown session '{session_id}'. Call begin_architecture_session first."}
    err = _valid_stage_or_error(stage)
    if err:
        return {"error": err}

    # Gating: a stage may only be submitted once its predecessors (for 04..09)
    # are accepted, except 00 which starts the session.
    d = sess.STAGE_ORDER.index(stage)
    preds = sess.STAGE_ORDER[:d]
    unmet = [p for p in preds if p not in s["submitted"]]
    if unmet and d > 0:
        return {
            "error": f"Stage '{stage}' blocked: submit these earlier stages first: {', '.join(unmet)}.",
            "required_order": sess.STAGE_ORDER,
        }

    try:
        art = _artifact(artifact)
    except ValueError as e:
        return {"error": str(e)}
    missing = _missing_fields(stage, art)
    if missing:
        return {
            "accepted": False,
            "stage": stage,
            "missing_fields": missing,
            "hint": "Provide these keys in the artifact (see the prerequisite doc below).",
            "doc": _stage_content(stage)[:1200],
        }

    # Checklist items self-reported. We only require that at least the stage's
    # checklist keys are claimed; the actual *quality* of the answers is Phase 3.
    checklist = checklist or []
    sess.accept_stage(session_id, stage, {**art, "checklist": checklist})

    nxt = sess.next_pending(session_id)
    return {
        "accepted": True,
        "stage": stage,
        "next_stage": nxt,
        "next_stage_title": sess.STAGE_TITLES[nxt] if nxt else None,
        "session_complete": nxt is None,
    }


def current_stage(session_id: str) -> dict:
    """Return where in the methodology the session is and which stages are done."""
    s = sess.get(session_id)
    if not s:
        return {"error": f"Unknown session '{session_id}'."}
    nxt = sess.next_pending(session_id)
    done = sorted(s["submitted"])
    return {
        "session_id": session_id,
        "problem": s["problem"],
        "completed_stages": done,
        "current_stage": nxt,
        "current_stage_title": sess.STAGE_TITLES[nxt] if nxt else None,
        "session_complete": nxt is None,
    }


def get_least_powerful_capability(session_id: str) -> dict:
    """After decomposition stages (00-06) pass, present capability selection as a
    conclusion: the least-powerful mechanism ladder, not a free menu."""
    s = sess.get(session_id)
    if not s:
        return {"error": f"Unknown session '{session_id}'."}
    if not sess.capability_open(session_id):
        pending = [st for st in sess.STAGE_ORDER[:7] if st not in s["submitted"]]
        return {
            "error": (
                "Capability selection (07) is deferred until decomposition stages are "
                "validated. Still pending: " + ", ".join(pending) + "."
            ),
            "required_order": sess.STAGE_ORDER,
        }
    return {
        "capability_ladder": [
            "Deterministic Python",
            "Task-only (single bounded operation)",
            "Agent wrapping genuine professional capability",
            "Crew (multi-specialist collaboration)",
            "Flow / CrewFlow (explicit orchestration + state)",
        ],
        "guidance": (
            "Select the least powerful mechanism that reliably satisfies the "
            "requirement; escalate only when the problem demands it."
        ),
    }