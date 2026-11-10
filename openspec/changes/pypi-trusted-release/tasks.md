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
