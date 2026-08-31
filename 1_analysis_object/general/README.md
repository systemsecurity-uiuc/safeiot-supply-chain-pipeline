# Shared Analysis Objects

Material that is not tied to a single tool. Anything here is expected to be useful to
more than one tool in the pipeline, so it is maintained once and reused.

| Directory | Contents |
|---|---|
| [`specifications/`](specifications/) | The technical BOM formats — CycloneDX, SPDX, and related schemas — that describe how a BOM is written |
| [`regulations/`](regulations/) | The legal and policy mandates behind those BOMs — NTIA minimum elements, EO 14028, the EU CRA, and others |

`specifications/` describes what a valid BOM looks like; `regulations/` describes what a
vendor is required to produce and disclose. A compliance check usually needs both: the format
to parse against, and the mandate to judge against.

If your tool needs an object that another tool could plausibly reuse, add it here rather
than under your own tool directory, and say in your tool's stage-1 README that you depend
on it.
