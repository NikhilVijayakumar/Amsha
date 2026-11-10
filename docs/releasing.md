# PyPI release

Amsha's distribution name is `Amsha` (normalized as `amsha`), and the import namespace is `amsha`. Confirm ownership of the package name, license rights and package contents before release. Check the current PyPI name again immediately before first publication; a pending publisher does not reserve it.

Build with `python -m build`, inspect the wheel and source archive, and run `python -m twine check dist/*`. Test the wheel in an isolated consumer with compatible Python and its declared dependencies. The package currently supports Python >=3.12,<3.14 and has substantial pinned runtime dependencies; review their download sizes and license requirements.

For a new PyPI project, configure a [pending trusted publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) using project `amsha`, GitHub owner `NikhilVijayakumar`, repository `Amsha`, workflow `publish.yml`, and environment `pypi`. Create the matching GitHub environment without required reviewers for direct automated releases. Do not add a long-lived PyPI token. Unlike npm staging, PyPI upload is public once the job runs.

Merge a reviewed version change, then create a matching `v<version>` tag from reviewed source and push it. The workflow validates the tag, runs unit tests, builds and checks the wheel and sdist, then uploads those exact artifacts to PyPI with OIDC after the checks pass, without a GitHub approval step. PyPI may perform its own validation. Confirm the workflow, package version, and clean installation afterward. PyPI versions cannot be overwritten.

The MCP server has its own package, workflow and lifecycle; it is not included in this library release.
