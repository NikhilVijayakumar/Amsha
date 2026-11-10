# Tasks

- [x] Record distribution knowledge and requirements; validate OKF and OpenSpec.
- [x] Add Python metadata, license and consumer/release instructions; inspect distributions and installation.
- [x] Add CI and trusted publishing workflows; validate workflow structure and tag checks.
- [x] Run unit tests, distribution checks and isolated consumer verification; record failures.
- [x] Configure the trusted publisher and GitHub environment; verify first PyPI upload.

## Initial verification evidence (historical)

- OKF linter and OpenSpec baseline and change validation passed. Wheel and sdist built, passed Twine and distribution audits; the wheel installed without dependencies in a clean environment and `amsha` imported from site-packages. Documented imports also resolved in a compatibility overlay; that overlay is not a clean dependency installation.
- Existing `.venv` has CrewAI 0.201.1 rather than the declared 1.15.18 and failed collection. A temporary overlay with CrewAI 1.15.18 and reused dependencies yielded 321 passed, 27 failed and 2 skipped. Failures include stale fixtures/expectations and possible runtime defects; they require independent investigation and a clean run. A complete clean dependency installation was stopped because of download size and speed.
- Publication is blocked until the full unit suite passes in a clean declared-dependency environment, the PyPI pending publisher is configured, and GitHub environment approval is enabled and verified. No registry upload has occurred.

### 3.0.0 pre-release readiness (historical)

- The complete declared dependency set was installed into a clean temporary environment with `uv`; `pip check` passed. The 3.0.0 wheel and sdist passed distribution auditing and Twine, and tests ran against the installed wheel.
- Full suite: 354 passed, 4 failed, 2 skipped. The failures expect `AmshaCrewFileApplication.execute_crew_with_retry` and `validate_execution`, which are absent; `FileCrewOrchestrator.run_crew` provides retry with a caller-supplied validator. The intended application API requires a product decision; tests have not been removed or suppressed.
- The `amsha` pending PyPI publisher was configured by the maintainer. The GitHub `pypi` environment has the maintainer as required reviewer and administrator bypass disabled. Actual tag upload and publication remain unverified and blocked by the four failing tests. MCP is a separate project and is not released by this workflow.

### Release verification after retry API decision

- The maintainer selected the existing `FileCrewOrchestrator.run_crew` API. Obsolete application-level retry tests now exercise the documented orchestrator with caller-provided validators, preserving success, retry and exhaustion checks.
- In an isolated Python 3.12 environment with the declared dependencies, the installed 3.0.0 wheel passed the unit suite: 358 passed, 2 existing skips, 4 subtests passed. The two skipped tests document strict CrewAI Pydantic validation incompatibilities; integration tests requiring services were not run. `pip check`, Twine and distribution audits passed.
- A pending `amsha` publisher and a `pypi` GitHub environment requiring maintainer approval are configured. PyPI upload and post-publication installation remain pending. Only the Amsha library is in scope; amsha-mcp is not released.

### Direct PyPI publishing policy

- The maintainer selected direct PyPI uploads after successful checks, without GitHub reviewer approval. The `pypi` environment reviewer requirement was removed. Release 3.0.0 completed via OIDC; its published wheel was installed with `--no-deps` and its top-level import and version verified. Full runtime dependency installation remains covered by the clean pre-release environment, not this no-dependency PyPI smoke test.
