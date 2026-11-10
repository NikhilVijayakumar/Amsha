# Design

The builder rejects `azure/` and `azure_ai/` model prefixes case-insensitively with a dedicated exception and does not construct a provider. Remove Azure-specific prefix stripping, argument suppression and global LiteLLM mutation; retain shared configuration fields and general provider arguments. This changes a distributed library artifact but not MCP or architecture layer direction. Non-Azure names that merely contain the word remain valid.

Existing executable tests require custom endpoints to avoid forcing streaming, while the default path requests it; correct the builder to retain that distinction.
