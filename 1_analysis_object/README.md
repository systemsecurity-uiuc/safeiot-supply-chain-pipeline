# Stage 1 — Analysis Object

What a tool analyzes: the BOM artifacts and the software they claim to describe —
CycloneDX or SPDX documents, JARs, firmware images, container images, model files — plus
the standards and mandates a compliance check evaluates them against.

Each tool gets a subdirectory named after the tool. Objects that more than one tool can
reuse live in [`general/`](general/) instead of being duplicated per tool.

```
1_analysis_object/
├── general/          # Objects and reference material shared across tools
└── <tool-name>/      # Objects specific to one tool
```

Large binaries should not be committed. Provide a fetch script, a manifest, or
instructions for obtaining the object, and keep the downloads out of git. The JBomAudit samples are an exception: they are small JARs, committed so the tool has
something to run against out of the box.

If a tool has no analysis object that can be checked in, describe what the object
actually is and how it comes into existence.
