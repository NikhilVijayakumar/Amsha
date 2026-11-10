# Fix valid falsy JSON output

The output-process cleaner rejects valid JSON values that are falsy in Python. Preserve these values without changing invalid-input or collision behavior. This externally visible correction affects output-process only; see `knowledge/features/output-process.md`.
