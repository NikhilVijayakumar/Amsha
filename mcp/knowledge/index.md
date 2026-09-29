---
okf_version: "0.2"
---

# amsha-mcp knowledge bundle

Durable, repo-side context for the `amsha-mcp` server, maintained as an
independent OKF v0.2 bundle. This is the **repository** knowledge plane and is
never shipped in the wheel.

## What lives here

| Kind | Contents | Role |
|---|---|---|
| `methodology/` | The 34 authored runtime methodology documents | Single source of truth for the product plane |
| `records/` | Historical proposal/archive records | Repo-side design history, not product runtime data |
| `specs` (sibling, `../openspec/specs/`) | Current-state behavioural requirements | What the server must do |

## Relationship to the product plane

The 34 runtime documents under `methodology/` are authored here **with OKF
frontmatter** and materialized at build time into the packaged
`amsha_mcp/docs/` tree by `scripts/sync_packaged_docs.py` and the build hook,
which strip the frontmatter.

```
mcp/knowledge/methodology/  (authored, frontmatter)
  --stage/build-->  mcp/build/package-docs/amsha_mcp/docs/  (body only)
  --package-->      wheel: amsha_mcp/docs/                  (body only)
```

The packaged form MUST stay frontmatter-free: the server's preview function
preserves every non-empty line, so frontmatter in a packaged file would leak
into agent-visible text. The reason frontmatter is therefore added on one side
and stripped on the other is a correctness requirement, not a preference.

Never hand-edit the staged or packaged product plane. In a source checkout the
server reads directly from `knowledge/`; builds materialize the product form.
Run:

```bash
python3 scripts/sync_packaged_docs.py          # regenerate the staged docs tree
python3 scripts/sync_packaged_docs.py --check  # validate generation; compare staged tree if present
```

## Metadata policy

These documents carry `type`, `title`, `description`, `tags`, `status`, and
`generated`. They deliberately omit three optional OKF fields:

- `stale_after` — methodology is stable, human-reviewed reference material with
  no expiry model. Inventing a date would imply a review cadence that does not
  exist.
- `verified[]` — reserved for concepts a deterministic tool can attest to. No
  tool verifies a prose document today.
- `sources[]` — the authoring source *is* this file. Pointing it at the
  generated artifact would be circular.

`status` is `stable` for the active methodology documents and `deprecated` for
the archived proposal records retained for reference.

## Conformance

```bash
python3 ../scripts/okf_lint.py knowledge     # from the mcp/ directory
```
