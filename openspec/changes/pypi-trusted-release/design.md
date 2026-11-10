# Design

The existing setuptools project and Python namespace remain unchanged. Add metadata and a license; verify wheel and sdist from a clean build. CI installs declared runtime and dev dependencies and runs unit tests on Python 3.12. A tag workflow validates the static version, tests, builds and checks distributions in an unprivileged job, then uploads the same artifacts in an OIDC-enabled `pypi` environment. The PyPI environment does not require a GitHub reviewer; a successful upload is public and cannot be treated as staging. No application code or dependency-layer direction changes. The library artifacts are affected; `mcp/` has a separate distribution and is excluded.

Knowledge: `knowledge/features/python-distribution.md`. PyPI name and trusted-publisher identity are external state; pending registration does not reserve the name.
