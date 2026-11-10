# Remove Azure-specific LLM support

Amsha no longer supports Azure LLM providers. Remove special Azure parameter handling and global LiteLLM monkeypatching, and report an explicit error for Azure-qualified model names before provider creation. Other providers keep their existing behavior. This is an externally visible breaking change to the llm-factory and requires a major version. Knowledge: `knowledge/features/llm-factory.md`. MCP is out of scope.
