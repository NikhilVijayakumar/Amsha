"""In-memory per-session architecture guidance state (Phase 2).

A session is a per-conversation cursor over the prerequisite stages. Intent is
in-memory only — no persistence across restarts. Each session tracks which
stages have been structurally accepted, so later stages (especially capability
selection, 07) can be gated until earlier ones pass.
"""
from __future__ import annotations

import itertools

STAGES = [
    ("00", "Problem Definition"),
    ("01", "Goal & Boundary Definition"),
    ("02", "Process Decomposition"),
    ("03", "Process Contracts & Atomicity"),
    ("04", "Process Validation & Human Review"),
    ("05", "Flow & State Planning"),
    ("06", "Corner Cases & Failure Planning"),
    ("07", "Capability Selection"),
    ("08", "Architecture Validation"),
    ("09", "Architecture Handoff Checklist"),
]
STAGE_ORDER = [s for s, _ in STAGES]
STAGE_TITLES = dict(STAGES)

_count = itertools.count(1)
_sessions: dict[str, dict] = {}


def create(problem: str, first_stage: str = "00") -> dict:
    sid = f"arch-{next(_count):03d}"
    _sessions[sid] = {
        "id": sid,
        "problem": problem,
        "first_stage": first_stage,
        "submitted": set(),   # stage ids accepted so far
        "artifacts": {},      # stage id -> the structurally-valid snapshot
    }
    return _sessions[sid]


def get(sid: str):
    return _sessions.get(sid)


def accept_stage(sid: str, stage: str, snapshot: dict):
    s = _sessions[sid]
    s["submitted"].add(stage)
    s["artifacts"][stage] = snapshot


def next_pending(sid: str) -> str:
    """First stage id (in 00..09 order) not yet accepted."""
    submitted = _sessions[sid]["submitted"]
    for stage in STAGE_ORDER:
        if stage not in submitted:
            return stage
    return None


def capability_open(sid: str) -> bool:
    """Whether stage 07 may be attempted: stages 00-06 all accepted."""
    return all(st in _sessions[sid]["submitted"] for st in STAGE_ORDER[:7])