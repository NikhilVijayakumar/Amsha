# Tasks: Generate Packaged Methodology Docs from an MCP-Local OKF Bundle

## 1. Establish the MCP-local OKF bundle

- [ ] 1.1 Create `mcp/knowledge/` with all 43 product-plane documents as OKF
      concepts, bodies byte-identical to the current packaged files.
      **Verify:** `mcp/scripts/sync_packaged_docs.py --check` fails with a diff
      listing all 43 as missing, and no other error.
- [ ] 1.2 Add frontmatter: `type` (`Methodology` / `Record`), `status`
      (`stable` for stages and topics, `deprecated` for archived proposals),
      `created` and `updated` as ISO dates, actor convention `Amsha MCP
      maintainers`.
      **Verify:** `python3 scripts/okf_lint.py mcp/knowledge` → conformant.
- [ ] 1.3 Omit `stale_after` and `verified[]` on methodology files (design D4).
      **Verify:** `grep -rl 'stale_after\|verified:' mcp/knowledge` returns
      nothing.
- [ ] 1.4 Add `mcp/knowledge/index.md` (bundle root, `okf_version` only) plus
      `methodology/index.md` and `records/index.md`.
      **Verify:** `python3 scripts/okf_lint.py mcp/knowledge` reports 43
      concepts and 0 errors.

## 2. Build the generator

- [ ] 2.1 Write `mcp/scripts/sync_packaged_docs.py` with the explicit mapping
      in design D2 and frontmatter stripping per D1.
      **Verify:** `python3 mcp/scripts/sync_packaged_docs.py --check` against
      the still-committed `docs/` tree exits 0 and reports 43 files matching.
- [ ] 2.2 Add `--check` mode: compare only, write nothing, non-zero exit on any
      drift, addition, or deletion.
      **Verify:** mutate one packaged file by hand; `--check` exits non-zero
      naming that file; restore it; `--check` exits 0.
- [ ] 2.3 Make the generator idempotent and order-independent.
      **Verify:** run twice; second run reports no changes.

## 3. Move the product plane out of `src/`

- [ ] 3.1 `git rm -r mcp/src/amsha_mcp/docs` and add the path to
      `mcp/.gitignore`.
      **Verify:** `git status` shows 43 deletions plus one `.gitignore` edit,
      and no packaged doc remains tracked.
- [ ] 3.2 Regenerate the tree and confirm the result is byte-identical to the
      pre-removal content captured in 1.1.
      **Verify:** `diff -r` against a saved copy of the old tree reports no
      differences.

## 4. Wire the build

- [ ] 4.1 Invoke the generator from `mcp/packaging/build_standalone.py` before
      packaging, in both build and standalone paths.
      **Verify:** inspect the call sites; a build from a clean tree produces
      `src/amsha_mcp/docs/` with 43 files.
- [ ] 4.2 Add a build-time `--check` so a stale tree fails the build.
      **Verify:** corrupt a packaged file, run the build, confirm non-zero exit
      and a clear message.

## 5. Specify the server itself

- [ ] 5.1 Add `mcp/openspec/specs/packaged-documentation/spec.md` covering the
      product-plane contract: filenames, no frontmatter, standalone operation.
      **Verify:** `cd mcp && openspec validate --specs --strict`.
- [ ] 5.2 Add `mcp/openspec/specs/documentation-build/spec.md` covering
      authoring, generation, and drift detection.
      **Verify:** `cd mcp && openspec validate --specs --strict`.
- [ ] 5.3 Rewrite `mcp/openspec/config.yaml`: the rule forbidding frontmatter
      is inverted. The source carries frontmatter; the packaged output does not.
      **Verify:** no rule in `config.yaml` contradicts the new specs.

## 6. Update the governing documents

- [ ] 6.1 Update `AGENTS.md` §14 to describe `mcp/knowledge/`, the generator,
      and the two-step local workflow.
      **Verify:** the two-step workflow matches `mcp/docs/PACKAGING.md`.
- [ ] 6.2 Update `docs/proposal/openspec-okf/proposal.md` — the "product plane
      ships byte-identical, is never hand-edited" invariant needs restating in
      terms of generation rather than manual authorship.
      **Verify:** no claim in the proposal contradicts the implemented model.
- [ ] 6.3 Record the `read_proposal()` reachability defect as a deferred
      follow-up.
      **Verify:** named in this change's proposal and in proposal 15.

## 7. Verify the whole system

- [ ] 7.1 `python3 scripts/okf_lint.py knowledge` and
      `python3 scripts/okf_lint.py mcp/knowledge` both pass.
      **Verify:** both exit 0.
- [ ] 7.2 Both OpenSpec roots pass strict validation.
      **Verify:** root `openspec validate --specs --strict`; `cd mcp &&
      openspec validate --all --strict`.
- [ ] 7.3 The wheel still carries 43 files with identical names and bytes.
      **Verify:** build the wheel; list members; diff extracted `docs/` against
      the pre-change tree.
- [ ] 7.4 The product plane still serves 10 prerequisite and 24 implementation
      documents with no repository registered.
      **Verify:** run the loaders with `AMSHA_MCP_TARGET_REPO` unset.
- [ ] 7.5 `get_preview()` output is unchanged for all 43 files.
      **Verify:** capture previews before and after; assert equality.
- [ ] 7.6 MCP test suite shows no new failures against its 25-failed baseline.
      **Verify:** record the before/after counts.
