#!/usr/bin/env python3
"""Lint the Amsha knowledge bundle against OKF v0.2 conformance rules.

Usage:
    python3 scripts/okf_lint.py [BUNDLE_ROOT]     # default: knowledge/

Exits 0 when the bundle conforms, 1 on any finding.

Spec: https://openknowledge.sh/wiki/SPEC.html
Implements the three conformance conditions in section 11, plus the
navigational checks the spec describes but does not require, because a
bundle can be conformant and still unusable:

  1. every non-reserved .md file has a parseable YAML frontmatter block
  2. every frontmatter block has a non-empty `type`
  3. reserved filenames (index.md, log.md) follow their own structure
     -- which means index.md carries no frontmatter, except a bundle-root
     index.md may carry a single `okf_version` key

Beyond conformance, this reports:
  - `status` outside {draft, stable, deprecated}       (section 5.4)
  - `timestamp`, superseded by generated.at            (section 13.1)
  - non-ISO-8601 timestamps                            (section 5)
  - actors not matching the convention                 (section 7)
  - bundle-relative links that resolve to nothing      (advisory, section 6.1)

Deliberately tolerant: the spec says consumers MUST NOT reject a bundle for
unknown type values, unknown extra keys, or broken links. Those are reported
as advisory, never as errors.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:  # PyYAML ships with Amsha, but a bare checkout may lack it
    sys.exit("okf_lint: PyYAML is required (pip install pyyaml)")

RESERVED = {"index.md", "log.md"}
VALID_STATUS = {"draft", "stable", "deprecated"}
LEGACY_KEYS = {"timestamp"}
ISO_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# <producer>/<version> for tools, human:<id> for people, process:<id> for automation.
#
# `team:` is accepted for sources[].author only. Section 7 lists three forms
# and does not include it, but section 5.1 defers sources[].author to that
# same convention while the specification's own normative examples write
# `author: team:ga4-docs` (section 5.1) and `author: team:finance-fpa`
# (appendix A). Rejecting those would make the linter stricter than the
# document it implements, so the fourth form is permitted here. It is
# intentionally not accepted for generated.by or verified[].by, where
# section 7 applies without that exception.
ACTOR = re.compile(r"^(?:[\w.-]+/[\w.+-]+|human:[\w.@-]+|process:[\w.@-]+)$")
SOURCE_AUTHOR = re.compile(r"^(?:[\w.-]+/[\w.+-]+|human:[\w.@-]+|process:[\w.@-]+|team:[\w.@-]+)$")


class Finding:
    __slots__ = ("path", "level", "rule", "message")

    def __init__(self, path: Path, level: str, rule: str, message: str) -> None:
        self.path, self.level, self.rule, self.message = path, level, rule, message

    def __str__(self) -> str:
        return f"{self.path}: {self.level}: [{self.rule}] {self.message}"


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter_text, body). None when the block is absent."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, text
    return text[4:end + 1], text[end + 5:]


def check_iso(value: object, path: Path, field: str, out: list[Finding], date_only: bool = False) -> None:
    if not isinstance(value, str):
        return
    ok = ISO_DATE.match(value) if date_only else ISO_DATETIME.match(value)
    if not ok:
        out.append(Finding(path, "error", "iso8601", f"{field}: {value!r} is not ISO 8601"))
        return
    probe = value if date_only else value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(probe)
    except ValueError:
        out.append(Finding(path, "error", "iso8601", f"{field}: {value!r} is not a real instant"))


def check_actor(value: object, path: Path, field: str, out: list[Finding],
                pattern: re.Pattern[str] = ACTOR) -> None:
    if isinstance(value, str) and not pattern.match(value):
        out.append(Finding(
            path, "error", "actor-convention",
            f"{field}: {value!r} does not match '<producer>/<version>', 'human:<id>' or 'process:<id>'"))


def check_verified(data: dict, path: Path, out: list[Finding]) -> None:
    """`verified` is a list, or a bare {by, at} mapping a consumer must widen."""
    entries = data.get("verified")
    if entries is None:
        return
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        out.append(Finding(path, "error", "verified", "verified must be a mapping or a list of mappings"))
        return
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            out.append(Finding(path, "error", "verified", f"verified[{i}] is not a mapping"))
            continue
        if "by" not in entry:
            out.append(Finding(path, "error", "verified", f"verified[{i}] has no 'by'"))
        else:
            check_actor(entry["by"], path, f"verified[{i}].by", out)
        if "at" not in entry:
            out.append(Finding(path, "error", "verified", f"verified[{i}] has no 'at'"))
        else:
            check_iso(entry["at"], path, f"verified[{i}].at", out)


def check_generated(data: dict, path: Path, out: list[Finding]) -> None:
    gen = data.get("generated")
    if gen is None:
        return
    if not isinstance(gen, dict):
        out.append(Finding(path, "error", "generated", "generated must be a mapping"))
        return
    if "by" not in gen:
        out.append(Finding(path, "error", "generated", "generated has no 'by'"))
    else:
        check_actor(gen["by"], path, "generated.by", out)
    if "at" not in gen:
        out.append(Finding(path, "error", "generated", "generated has no 'at'"))
    else:
        check_iso(gen["at"], path, "generated.at", out)


def check_concept(path: Path, rel: str, text: str, out: list[Finding]) -> dict:
    raw, _ = split_frontmatter(text)
    if raw is None:
        out.append(Finding(path, "error", "frontmatter", "no YAML frontmatter block"))
        return {}
    try:
        data = yaml.safe_load(raw) or {}
    except (yaml.YAMLError, ValueError) as exc:
        out.append(Finding(path, "error", "frontmatter", f"unparseable YAML: {exc}"))
        return {}
    if not isinstance(data, dict):
        out.append(Finding(path, "error", "frontmatter", "frontmatter is not a mapping"))
        return {}

    kind = data.get("type")
    if not isinstance(kind, str) or not kind.strip():
        out.append(Finding(path, "error", "type", "missing or empty 'type' (the only required key)"))
    elif kind != kind.strip():
        out.append(Finding(path, "error", "type", f"type {kind!r} has surrounding whitespace"))

    status = data.get("status")
    if status is not None and status not in VALID_STATUS:
        out.append(Finding(
            path, "error", "status",
            f"status {status!r} is not one of {sorted(VALID_STATUS)}"))

    for legacy in sorted(LEGACY_KEYS & data.keys()):
        out.append(Finding(
            path, "error", "legacy-key",
            f"{legacy!r} was superseded in v0.2; use generated.at instead"))

    check_generated(data, path, out)
    check_verified(data, path, out)

    if "stale_after" in data:
        check_iso(data["stale_after"], path, "stale_after", out, date_only=True)

    for i, src in enumerate(data.get("sources") or []):
        if not isinstance(src, dict):
            out.append(Finding(path, "error", "sources", f"sources[{i}] is not a mapping"))
            continue
        if "resource" not in src:
            out.append(Finding(path, "error", "sources", f"sources[{i}] has no 'resource'"))
        if "author" in src:
            check_actor(src["author"], path, f"sources[{i}].author", out, SOURCE_AUTHOR)
        if "last_modified" in src:
            check_iso(src["last_modified"], path, f"sources[{i}].last_modified", out)

    for key in ("title", "description"):
        if key in data and not isinstance(data[key], str):
            out.append(Finding(path, "error", key, f"{key} must be a string"))
    if "tags" in data and not isinstance(data["tags"], list):
        out.append(Finding(path, "error", "tags", "tags must be a list"))

    return data


def check_index(path: Path, text: str, is_root: bool, out: list[Finding]) -> None:
    """index.md carries no frontmatter, except one okf_version key at the root."""
    raw, _ = split_frontmatter(text)
    if raw is None:
        return
    if not is_root:
        out.append(Finding(path, "error", "index", "index.md must not carry frontmatter (section 8)"))
        return
    try:
        data = yaml.safe_load(raw) or {}
    except (yaml.YAMLError, ValueError) as exc:
        out.append(Finding(path, "error", "index", f"unparseable YAML: {exc}"))
        return
    extra = set(data) - {"okf_version"}
    if extra:
        out.append(Finding(
            path, "error", "index",
            f"bundle-root index.md may carry only okf_version; found {sorted(extra)}"))


def check_log(path: Path, text: str, out: list[Finding]) -> None:
    _, body = split_frontmatter(text)
    for lineno, line in enumerate(body.splitlines(), 1):
        if not line.startswith("## "):
            continue
        stamp = line[3:].strip()
        if not ISO_DATE.match(stamp):
            out.append(Finding(
                path, "error", "log",
                f"line {lineno}: date heading {stamp!r} is not ISO 8601 YYYY-MM-DD (section 9)"))


def check_links(path: Path, text: str, root: Path, out: list[Finding]) -> None:
    _, body = split_frontmatter(text)
    for target in re.findall(r"\]\((/[^)#\s]+)\)", body):
        candidate = root / target.lstrip("/")
        if not candidate.exists():
            out.append(Finding(
                path, "advisory", "broken-link",
                f"bundle-relative link {target} resolves to nothing"))


def lint(root: Path) -> list[Finding]:
    out: list[Finding] = []
    if not root.is_dir():
        return [Finding(root, "error", "bundle", "bundle root is not a directory")]

    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(root))

        if path.name == "index.md":
            check_index(path, text, path.parent == root, out)
        elif path.name == "log.md":
            check_log(path, text, out)
        else:
            check_concept(path, rel, text, out)

        check_links(path, text, root, out)

    return out


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("knowledge")
    if not root.exists():
        print(f"okf_lint: {root} does not exist", file=sys.stderr)
        return 1

    findings = lint(root)
    errors = [f for f in findings if f.level == "error"]
    advisory = [f for f in findings if f.level == "advisory"]

    for f in findings:
        print(f, file=sys.stderr if f.level == "error" else sys.stdout)

    concepts = sum(1 for p in root.rglob("*.md") if p.name not in RESERVED)
    summary = f"{concepts} concepts"
    if errors:
        print(f"\nokf_lint: {summary}, {len(errors)} error(s), {len(advisory)} advisory", file=sys.stderr)
        return 1
    print(f"\nokf_lint: {summary}, conformant with OKF v0.2"
          + (f", {len(advisory)} advisory" if advisory else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
