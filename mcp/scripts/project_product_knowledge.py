#!/usr/bin/env python3
"""Project Amsha product knowledge into an MCP-owned, packaged OKF bundle.

The product knowledge already exists, authored and maintained in the Amsha
repository:

    knowledge/features/<module>.md      one concept per runtime module
    openspec/specs/<module>/spec.md      the behavioural requirements
    README.md                            the Installation / Quick Start sections

This script *projects* that knowledge into `mcp/knowledge/product/` as a
self-contained, packaged bundle, so the MCP server can answer questions about
Amsha with no repository registered. It generates; it does not author. Every
emitted field is copied or mechanically derived from a source artifact.

The output is committed, because `mcp/` must stay copyable and buildable on its
own. `--check` re-projects in memory and fails on any difference, so a change to
the Amsha knowledge that is not carried across becomes a build failure rather
than silent drift.

Usage:
    python3 scripts/project_product_knowledge.py            # write
    python3 scripts/project_product_knowledge.py --check    # fail on drift
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MCP_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = MCP_ROOT.parent
SRC_KNOWLEDGE = REPO_ROOT / "knowledge"
SRC_SPECS = REPO_ROOT / "openspec" / "specs"
SRC_README = REPO_ROOT / "README.md"
MANIFEST_NAME = "manifest.json"
OUT = MCP_ROOT / "knowledge" / "product"

# The server serves these 8 modules. `common` is intentionally internal and
# unserved; `crew-gen` is retired and has no source module. Keeping this list
# here (not in the projection) is what makes a missing concept a hard error.
MODULES: tuple[str, ...] = (
    "configuration",
    "crew_forge",
    "crew_monitor",
    "execution_runtime",
    "execution_state",
    "llm_factory",
    "output_process",
    "utils",
)

# Knowledge and spec directories are kebab-case; the server names modules with
# Python identifiers.
KEBAB = {m: m.replace("_", "-") for m in MODULES}

README_SECTIONS = ("Installation", "Quick Start")

# Human-readable module titles, mirroring the loader's fallback table.
DISPLAY = {
    "configuration": "Configuration",
    "crew_forge": "Crew Forge",
    "crew_monitor": "Crew Monitor",
    "execution_runtime": "Execution Runtime",
    "execution_state": "Execution State",
    "llm_factory": "LLM Factory",
    "output_process": "Output Processing",
    "utils": "Utils",
}
SECTION_SLUG = {"Installation": "installation", "Quick Start": "quickstart"}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"project: cannot read {path}: {exc}") from exc


def frontmatter(raw: str) -> dict[str, str]:
    """Parse the trivial `key: value` frontmatter the root concepts use."""
    if not raw.startswith("---\n"):
        raise SystemExit("project: expected a frontmatter block")
    end = raw.find("\n---\n", 4)
    if end == -1:
        raise SystemExit("project: unterminated frontmatter block")
    out: dict[str, str] = {}
    for line in raw[4:end].split("\n"):
        if not line or line.startswith((" ", "\t", "-")):
            continue  # nested/collection fields are not needed for the projection
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"')
    return out


def concept_for(module: str) -> tuple[str, str]:
    """Return (filename, projected text) for one module concept."""
    kebab = KEBAB[module]
    src = SRC_KNOWLEDGE / "features" / f"{kebab}.md"
    if not src.is_file():
        raise SystemExit(
            f"project: no root concept for module {module!r} (expected {src}).\n"
            f"        Add the concept, or drop the module from MODULES."
        )
    meta = frontmatter(read(src))

    spec_rel = f"openspec/specs/{kebab}/spec.md"
    spec_path = REPO_ROOT / spec_rel
    if not spec_path.is_file():
        raise SystemExit(f"project: module {module!r} has no spec at {spec_rel}")
    spec_purpose = ""
    sm = re.search(r"## Purpose\s*\n+(.*?)(?=\n## |\Z)", read(spec_path), re.S)
    if sm:
        spec_purpose = " ".join(sm.group(1).split())
        # Root specs close their Purpose with a root-relative "Knowledge concept:"
        # link. It resolves inside the Amsha bundle but not from here, and the
        # concept is already cited below, so drop it rather than emit a dead link.
        spec_purpose = re.sub(r"\s*Knowledge concept:.*$", "", spec_purpose).strip()

    description = meta.get("description", "").strip()
    if not description:
        raise SystemExit(f"project: {src.name} has no description to project")

    # Real relative paths, so the projected concept is navigable on its own.
    spec_link = f"../../../{spec_rel}"
    concept_link = f"../../../knowledge/features/{kebab}.md"

    title = meta.get("title", kebab.replace("-", " ").title())
    lines = [
        "---",
        "type: Module",
        f'title: "{title}"',
        f'description: "{description}"',
        f"tags: [amsha, mcp, product, {kebab}]",
        "status: stable",
        f'module: "{module}"',
        f"kebab_name: {kebab}",
        f'spec: "{spec_rel}"',
        f'concept_source: "knowledge/features/{kebab}.md"',
        'generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }',
        "---",
        "",
        f"# {title}",
        "",
        description,
        "",
    ]
    if spec_purpose:
        lines += [
            "## Why it exists",
            "",
            spec_purpose,
            "",
        ]
    lines += [
        "## Provenance",
        "",
        f"Generated from the Amsha concept [`{kebab}`]({concept_link}) and the",
        f"behavioural requirements in [`{kebab}` spec]({spec_link}). Edit those sources,",
        "then re-run `scripts/project_product_knowledge.py`.",
        "",
        "## Source of truth",
        "",
        "The MCP server serves this concept for `list_amsha_modules` and",
        "`explain_module`. A registered target repository may additionally supply the",
        "module's real file list; it is not required to answer.",
        "",
    ]
    return f"{kebab}.md", "\n".join(lines)


def readme_section(title: str) -> str:
    text = read(SRC_README)
    m = re.search(rf"## {re.escape(title)}[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    if not m:
        raise SystemExit(f"project: README.md has no `## {title}` section")
    return m.group(1).strip()


def section_concept(title: str) -> tuple[str, str]:
    """Project a README section into a concept that is *only* servable content.

    The body is the README section verbatim, with no editorial preamble: the
    loader serves everything after the H1, so any prose added here would be
    served to the caller as if it were the procedure itself. Provenance lives in
    the frontmatter instead.
    """
    slug = SECTION_SLUG[title]
    body = readme_section(title)
    label = "Installation" if title == "Installation" else "Quick Start"

    lines = [
        "---",
        "type: Reference",
        f'title: "Amsha {label}"',
        f'description: "The {label.lower()} procedure for the Amsha library, served '
        f'standalone by the MCP server."',
        f"tags: [amsha, mcp, product, {slug}]",
        "status: stable",
        f'section: "{title}"',
        'source_file: "README.md"',
        'generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }',
    ]
    if title == "Installation":
        # Structured facts, so the server can answer without re-parsing prose.
        # requires-python comes from pyproject.toml, not the README: the README
        # never states it, and pyproject is the actual constraint.
        for key, value in install_facts(body).items():
            lines.append(f'{key}: "{value}"')
    lines += ["---", "", f"# Amsha {label}", "", body, ""]
    return f"{slug}.md", "\n".join(lines)


def install_facts(body: str) -> dict[str, str]:
    """Extract the install command, the optional extra, and the Python floor."""
    facts: dict[str, str] = {}
    commands = re.findall(r"^\s*pip install ([^\n#]+)", body, re.M)
    for command in commands:
        package = command.split()[0].strip()
        if package == "amsha" and "install_command" not in facts:
            facts["install_command"] = f"pip install {package}"
        elif package not in ("amsha",) and "optional_extra" not in facts:
            facts["optional_extra"] = f"pip install {package}"
    requires = read_requires_python()
    if requires:
        facts["requires_python"] = requires
    return facts


def read_requires_python() -> str:
    """`[project] requires-python` from the Amsha pyproject, via stdlib tomllib."""
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        return ""
    try:
        data = tomllib.loads(read(REPO_ROOT / "pyproject.toml"))
    except (OSError, ValueError):
        return ""
    return str(data.get("project", {}).get("requires-python", ""))


def index_concept(counts: dict[str, int]) -> str:
    rows = "\n".join(
        f"| `{m}` | [{k}]({k}.md) |" for m, k in ((m, KEBAB[m]) for m in MODULES)
    )
    return "\n".join(
        [
            "# Product knowledge",
            "",
            f"Generated projections of Amsha's own knowledge: **{counts['modules']}** runtime",
            f"module concepts and **{counts['sections']}** procedure references.",
            "",
            "## Runtime modules",
            "",
            "| Module | Concept |",
            "|---|---|",
            rows,
            "",
            "`common` is intentionally absent: it is cross-cutting internal",
            "infrastructure and the server does not serve it. `crew-gen` is retired and",
            "has no source module.",
            "",
            "## Procedures",
            "",
            "| Reference | Covers |",
            "|---|---|",
            "| [installation](installation.md) | Installing Amsha, including the optional docling extra |",
            "| [quickstart](quickstart.md) | The first runnable crew |",
            "",
            "## Generated, not authored",
            "",
            "Every field here is copied or mechanically derived from an existing",
            "Amsha artifact: `knowledge/features/*.md`, `openspec/specs/*/spec.md`, and the",
            "README's Installation and Quick Start sections. Nothing is written by hand,",
            "so this bundle cannot drift silently from the source:",
            "",
            "```bash",
            "python3 scripts/project_product_knowledge.py --check   # fails on drift",
            "```",
            "",
            "These concepts are packaged into the wheel, which is what lets the server",
            "answer product questions with no repository registered.",
            "",
        ]
    )


def product_manifest() -> dict:
    """Machine facts the runtime needs, in a form that survives frontmatter stripping.

    The build removes OKF frontmatter from packaged concepts, so `module:`,
    `section:`, and the install facts would be unreadable in a wheel. The
    requires-python constraint is worse: it comes from `pyproject.toml` and
    appears in no concept body, so it cannot be re-derived from the packaged
    Markdown at all. This manifest is the packaged fallback for that metadata.
    """
    entries: dict[str, dict[str, str]] = {}
    for module in MODULES:
        name, text = concept_for(module)
        entries[name] = {
            "module": module,
            "title": f"Amsha {DISPLAY[module]}",
            "purpose": first_prose_line(text),
        }
    for title in README_SECTIONS:
        name, text = section_concept(title)
        entry = {"section": title, "title": f"Amsha {title}"}
        # Install facts belong to the Installation section only; the Quick Start
        # is a procedure, and stamping a version constraint on it is noise.
        if title == "Installation":
            entry.update(install_facts(readme_section(title)))
        entries[name] = entry
    return {"generated_by": "process:project-product-knowledge", "documents": entries}


def first_prose_line(text: str) -> str:
    """First non-heading, non-blank line after the H1: a concept's one-line purpose."""
    body = re.split(r"\n#\s+[^\n]*\n", text, maxsplit=1)
    for line in (body[1] if len(body) > 1 else text).splitlines():
        line = line.strip()
        if line and not line.startswith(("#", ">", "-", "|", "*", "`")):
            return line
    return ""


def project() -> dict[str, str]:
    out: dict[str, str] = {}
    for module in MODULES:
        name, text = concept_for(module)
        out[name] = text
    for title in README_SECTIONS:
        name, text = section_concept(title)
        out[name] = text
    out["index.md"] = index_concept(
        {"modules": len(MODULES), "sections": len(README_SECTIONS)}
    )
    out[MANIFEST_NAME] = json.dumps(product_manifest(), indent=2, sort_keys=True) + "\n"
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed bundle matches its sources; write nothing; "
             "exit non-zero on drift",
    )
    args = parser.parse_args(argv)
    expected = project()

    if args.check:
        if not OUT.is_dir():
            print(f"FAIL {OUT} does not exist", file=sys.stderr)
            return 1
        actual = {
            p.name: p.read_text(encoding="utf-8")
            for p in list(OUT.glob("*.md")) + list(OUT.glob(MANIFEST_NAME))
        }
        drifted = sorted(n for n, t in expected.items() if actual.get(n) != t)
        extra = sorted(set(actual) - set(expected))
        for name in drifted:
            print(f"FAIL stale or missing: {OUT / name}", file=sys.stderr)
        for name in extra:
            print(f"FAIL not produced from any source: {OUT / name}", file=sys.stderr)
        if drifted or extra:
            print(
                f"project --check: {len(drifted)} stale, {len(extra)} unexpected "
                f"(of {len(expected)} expected).\n"
                f"  Re-run: python3 scripts/project_product_knowledge.py",
                file=sys.stderr,
            )
            return 1
        print(f"project --check: {len(expected)} files match the Amsha sources")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    for name in sorted(
        set(p.name for p in list(OUT.glob("*.md")) + list(OUT.glob(MANIFEST_NAME)))
        - set(expected)
    ):
        (OUT / name).unlink()
    for name, text in sorted(expected.items()):
        path = OUT / name
        changed = not path.is_file() or path.read_text(encoding="utf-8") != text
        path.write_text(text, encoding="utf-8")
        if changed:
            print(f"  wrote {path.relative_to(MCP_ROOT)}")
    print(f"project: {len(expected)} product concepts in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
