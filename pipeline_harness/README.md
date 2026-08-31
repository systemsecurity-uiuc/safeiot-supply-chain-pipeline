# Pipeline Harness

One subdirectory per tool, holding the description of how that tool's four stages fit
together and the entry point that runs them end to end.

```
pipeline_harness/
└── <tool-name>/
    ├── README.md    # The flow: what runs, in what order, what comes out
    └── run.sh       # A single command that executes the flow
```

Every tool needs a runnable entry point here — a script, a Makefile, or a documented
sequence of commands — that takes a reader from a clean checkout to a result in
[`4_analysis_output/`](../4_analysis_output/).

This doubles as the reproducibility instruction your project report needs.
