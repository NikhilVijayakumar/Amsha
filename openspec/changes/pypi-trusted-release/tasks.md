# Tasks

- [x] Record distribution knowledge and requirements; validate OKF and OpenSpec.
- [x] Add Python metadata, license and consumer/release instructions; inspect distributions and installation.
- [x] Add CI and trusted publishing workflows; validate workflow structure and tag checks.
- [ ] Run unit tests, distribution checks and isolated consumer verification; record failures.
- [ ] Configure pending publisher and protected GitHub environment; approve and verify first PyPI upload.

## Verification evidence

- OKF linter and OpenSpec baseline and change validation passed. Wheel and sdist built, passed Twine and distribution audits; the wheel installed without dependencies in a clean environment and `amsha` imported from site-packages. Documented imports also resolved in a compatibility overlay; that overlay is not a clean dependency installation.
- Existing `.venv` has CrewAI 0.201.1 rather than the declared 1.15.18 and failed collection. A temporary overlay with CrewAI 1.15.18 and reused dependencies yielded 321 passed, 27 failed and 2 skipped. Failures include stale fixtures/expectations and possible runtime defects; they require independent investigation and a clean run. A complete clean dependency installation was stopped because of download size and speed.
- Publication is blocked until the full unit suite passes in a clean declared-dependency environment, the PyPI pending publisher is configured, and GitHub environment approval is enabled and verified. No registry upload has occurred.

### Follow-up: 3.0.0 readiness

- The complete declared dependency set was installed into a clean temporary environment with `uv`; `pip check` passed. The 3.0.0 wheel and sdist passed distribution auditing and Twine, and tests ran against the installed wheel.
- Full suite: 354 passed, 4 failed, 2 skipped. The failures expect `AmshaCrewFileApplication.execute_crew_with_retry` and `validate_execution`, which are absent; `FileCrewOrchestrator.run_crew` provides retry with a caller-supplied validator. The intended application API requires a product decision; tests have not been removed or suppressed.
- The `amsha` pending PyPI publisher was configured by the maintainer. The GitHub `pypi` environment has the maintainer as required reviewer and administrator bypass disabled. Actual tag upload and publication remain unverified and blocked by the four failing tests. MCP is a separate project and is not released by this workflow.
