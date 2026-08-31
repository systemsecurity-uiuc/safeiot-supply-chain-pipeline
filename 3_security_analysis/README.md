# Stage 3 — Security Analysis

The verification itself: the checks that compare what a BOM declares against what the
artifact actually contains, evaluate a BOM against a standard, or use BOM data to reason
about vulnerability and risk.

Each tool gets a subdirectory named after the tool.

```
3_security_analysis/
└── <tool-name>/
```

Every tool has this stage. Keep the verification logic here; collecting the object,
preparing it, and reporting the results belong to the other stages.
