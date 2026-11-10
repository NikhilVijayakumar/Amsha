# Changelog

## 3.0.0 — Unreleased

- Remove Azure-specific LLM support. Azure-qualified `azure/` and `azure_ai/` model names now raise `UnsupportedProviderError`; migrate those configurations to another provider. Amsha no longer modifies global LiteLLM completion behavior.
- Do not force streaming for custom LLM endpoints; default endpoints continue to request streaming.
- Preserve valid falsy JSON outputs, including empty objects and arrays, without overwriting the input file.
- Prepare the Amsha library for PyPI distribution; the separate amsha-mcp distribution is not part of this release.
