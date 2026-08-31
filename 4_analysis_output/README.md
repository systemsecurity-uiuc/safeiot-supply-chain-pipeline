# Stage 4 — Analysis Output

What a run produces: reports, findings, logs, and any other evidence a reader needs to
judge the result.

Each tool gets a subdirectory named after the tool.

```
4_analysis_output/
└── <tool-name>/
```

Tools are not required to share an output format. Commit **one representative example
run** so a reader can see what your tool produces without setting it up, and describe in
your tool's README what the output means.

Keep large or per-run artifacts out of git; commit the example, ignore the rest.
