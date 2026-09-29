# Records

Superseded proposals, retained as `type: Record` / `status: deprecated`.

These are the design history of the `amsha-mcp` build. They are **not** current
methodology: each describes a phase that has since shipped in some form, and
several contain scope decisions later revised. Read them to understand *why* a
capability exists, not to learn what the server does now.

For current behaviour, see the sibling `methodology/` concepts and the
behavioural requirements in `../openspec/specs/`.

| # | Proposal | Subject |
|---|---|---|
| 00 | Overview and Roadmap | Scoping and phasing of the original build |
| 01 | MCP Server Foundation | Phase 1: the server as a knowledge server |
| 02 | Architecture Guidance | Phase 2: sequenced prerequisite/implementation tools |
| 03 | Plan and Crew Verification | Phase 3: read-only judges over plans and crew YAML |
| 04 | Improve / Test / Evaluate Loop | Phase 4: findings to reviewed fix drafts |
| 05 | User Plan Verification and Component Discovery | Phase 3 addendum: semantic plan checks, component discovery |
| 06 | Project Scaffolding | Generating a project from a validated session |
| 07 | Crew Lifecycle Verification | Phase 3 addendum: memory, tracing, checkpoint checks |
| 08 | Standalone, Repo-Agnostic Server | Removing the accidental Amsha dependency |

These records remain repository knowledge only. They are intentionally not part
of the runtime product plane and are not searched by the MCP server.
