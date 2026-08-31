# JBomAudit — Security Analysis

Vendored from [`code-genome/jbomaudit`](https://github.com/code-genome/jbomaudit)
(Apache-2.0), the artifact for the NDSS 2025 paper "JBomAudit: Assessing the Landscape,
Compliance, and Security Implications of Java SBOMs."

JBomAudit evaluates whether a Java SBOM is complete and accurate. It takes the dependency
tree the SBOM declares, takes the packages actually present in the JAR and its resolved
dependencies, and reports where the two disagree. Findings fall into six types: **M1–M3**
for dependencies the SBOM should have declared and did not, and **N1–N3** for
dependencies it declared that are not really there, each split across direct, transitive,
and relationship levels.

## Comparison modes

`-m global` (default) checks the SBOM tree as a whole: a package used by the project but
absent from every level of the tree is missing outright, which is the more serious case.
`-m layer` checks that dependencies are declared at the *right* level — a directly used
package that only appears further down the tree is reported as a missing direct
dependency.

## Files

| File | Purpose |
|---|---|
| `main.py` | Entry point; orchestrates preprocessing and analysis, single-sample or batch |
| `crawl_deps.py` | Resolves and downloads declared dependencies (stage 2) |
| `generate_jar_pkg_tags.py`, `add_jar_to_pkg_dic.py` | Extract package inventories from JARs (stage 2) |
| `analyze_inconsistency.py` | Compares declared against actual and classifies discrepancies |
| `compliance_check.py` | Drives the checks and assembles the report |
| `utils_tool/` | Dependency-tree construction, downloads, shared helpers |
| `vendor/jarpkginfo/` | Vendored IBM Research package-inspection library |

`metaDB/` and `results/` are created at run time and gitignored.

## Running

Use the harness rather than calling this directly, so that samples and output resolve to
their stage directories:

```bash
./pipeline_harness/jbomaudit/run.sh
```

A finding flagged `Undetermined` means the tool could not decide on its own and manual
verification is needed — either a dynamically loaded dependency it could not resolve, or
an artifact it could not retrieve.
