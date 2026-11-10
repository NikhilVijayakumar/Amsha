# Design

Use a private parse-failure sentinel so JSON null can be distinguished from invalid input, preserving all valid JSON values. The output-process implementation ships in the library wheel; dependency direction and MCP distribution are unchanged.
