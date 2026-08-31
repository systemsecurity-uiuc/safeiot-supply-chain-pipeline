# Stage 2 — Preprocess

Everything that turns raw BOM artifacts into something the verification can run against:
unpacking archives, resolving and downloading declared dependencies, extracting package
and class inventories, normalizing BOM documents into a common shape.

Each tool gets a subdirectory named after the tool.

```
2_preprocess/
└── <tool-name>/
```

Not every tool needs this stage. If yours does not, add a short README in your tool's
directory saying so and why.
