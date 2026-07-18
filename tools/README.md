# Tools

This directory hosts the supply-chain security and compliance verification tools integrated into the SafeIoT pipeline. Each subdirectory is a self-contained tool with its own setup and usage instructions.

## Available Tools

| Tool | Description |
|------|-------------|
| [jbomaudit](jbomaudit/README.md) | Evaluates the completeness and accuracy of Java SBOMs against their JAR files _(integration pending)_ |

## Adding a New Tool

1. Create a subdirectory under `tools/` named after the tool.
2. Add a `README.md` with prerequisites, installation, and usage instructions.
3. Register the tool in the table above and in the root [README.md](../README.md).
