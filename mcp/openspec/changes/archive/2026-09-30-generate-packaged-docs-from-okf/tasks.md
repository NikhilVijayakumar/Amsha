# Tasks: Generate Packaged Methodology Docs from an MCP-Local OKF Bundle

All tasks complete. Verification results are recorded against the commands that
were actually run.

## 1. Establish the MCP-local OKF bundle — done

- [x] 1.1 Create `mcp/knowledge/` with the documents as OKF concepts, bodies
      byte-identical to the originals.
      **Verified:** 43 concepts written; body comparison against the source
      reported 0 mismatches.
- [x] 1.2 Frontmatter with `type` (`Methodology` / `Record`), `status`
      (`stable` / `deprecated`), `title`, `description`, `tags`, and
      `generated.by` in the linter's actor convention.
      **Verified:** `python3 scripts/okf_lint.py mcp/knowledge` → 43 concepts,
      conformant. An initial pass used `team:amsha` for `generated.by`, which
      is the *source author* convention; the linter requires
      `<producer>/<version>`, `human:<id>`, or `process:<id>`, so it was
      corrected to `process:okf-migration`.
- [x] 1.3 Omit `stale_after`, `verified[]`, and `sources[]` rather than invent
      them (design D5 in the original draft; rationale retained in
      `knowledge/index.md`).
- [x] 1.4 Add `knowledge/index.md`, `methodology/index.md`, `records/index.md`.
      **Verified:** linter reports 43 concepts, 0 errors.

## 2. Build-time materialization — done

- [x] 2.1 Implement `_build_hooks.py` with the explicit mapping and frontmatter
      stripping, raising on missing or unterminated frontmatter.
      **Verified:** a malformed block aborts the build rather than producing
      corrupt output.
- [x] 2.2 Wire it through `[tool.setuptools.cmdclass]` in `mcp/pyproject.toml`.
      **Verified:** `pip wheel ./mcp` produced a wheel containing
      `amsha_mcp/_build_hooks.py` and 34 docs.
- [x] 2.3 Declare generated files in `get_outputs()` so setuptools tracks them.
- [x] 2.4 `scripts/sync_packaged_docs.py` imports the mapping and renderer from
      `_build_hooks` rather than re-implementing them; `--check` verifies a
      staged tree and treats an absent staging tree as build-ready.
- [x] 2.5 Idempotence and determinism: repeated runs report no change; mapping
      is built from `sorted()` globs, so output does not depend on filesystem
      iteration order.

## 3. Remove the product plane from `src/` — done

- [x] 3.1 Untrack `mcp/src/amsha_mcp/docs` and add `mcp/.gitignore` covering
      `build/package-docs/`.
      **Verified:** `git ls-tree HEAD -- mcp/src/amsha_mcp/docs` → 0 entries.
- [x] 3.2 The regenerated wheel matches the authored bodies exactly.
      **Verified:** 0 packaged documents begin with `---`.

  Incidental finding: the tracked tree was already inconsistent before this
  change — git tracked `docs/proposal/08-…md` as a direct child while its 8
  siblings sat in `archive/`, and `archive/08-…md` existed only on disk. The
  index is now consistent, and no content was lost (byte-compared against
  `HEAD`).

## 4. Source-checkout fallback — done

- [x] 4.1 `docs_loader._AUTHORED_DOCS` resolves `mcp/knowledge/methodology/`;
      `_read()` strips frontmatter for paths beneath it.
      **Verified:** with `PYTHONPATH=mcp/src` and no build, 10 prerequisite and
      24 implementation documents are served.
- [x] 4.2 Remove `read_proposal()` and every call site.
      **Verified:** `grep -rn 'read_proposal' mcp/src mcp/tests` → no matches.

## 5. Specify the server — done

- [x] 5.1 `mcp/openspec/specs/packaged-documentation/spec.md`
- [x] 5.2 `mcp/openspec/specs/documentation-build/spec.md`
- [x] 5.3 `mcp/openspec/specs/documentation-discovery/spec.md`
- [x] 5.4 Rewrite `mcp/openspec/config.yaml`; its former rule forbidding
      frontmatter on packaged docs is inverted, since the *source* now carries
      it and the packaged output does not.
      **Verified:** `cd mcp && openspec validate --all --strict` → 5 passed,
      0 failed.

## 6. Governing documents — done

- [x] 6.1 `AGENTS.md` §14 describes the MCP-local bundle, the build hook, and
      the generated product plane.
- [x] 6.2 `docs/proposal/openspec-okf/proposal.md` restated: the product plane
      is generated at build time, not hand-authored.
- [x] 6.3 The `read_proposal()` defect is recorded as **resolved by removal**
      (design D2) rather than deferred.

## 7. Whole-system verification — done

- [x] 7.1 Both OKF bundles conform: 21 concepts (root) + 43 (`mcp/knowledge`).
- [x] 7.2 Both OpenSpec roots pass strict validation: 11 root specs, 3 MCP
      specs, 2 MCP changes.
- [x] 7.3 Wheel carries 34 docs, 0 with frontmatter, 0 `knowledge/`, 0
      `openspec/`.
      **Note:** this is a reduction from 43. Intended, per design D2.
- [x] 7.4 Product plane serves 10 + 24 with no repository registered.
- [x] 7.5 No frontmatter token in `get_preview()` output.
      **Note:** an initial scan reported `---`, which turned out to be a
      horizontal rule in the document body, not leaked frontmatter. `_read()`
      output was confirmed to start at the `# ` heading.
- [x] 7.6 No new failures against the 25-failed MCP test baseline (which is
      dominated by the absent MCP SDK).
