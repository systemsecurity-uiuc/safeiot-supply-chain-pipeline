# JBomAudit — Analysis Output

A run produces output in two forms.

**A console table**, one row per finding type, with the counts for each sample and a
consolidated summary at the end of a batch run. A count shown as `Undetermined` means the
tool could not decide by itself: either a dynamically loaded dependency it could not
resolve, or an artifact it could not retrieve from Maven Central. Those rows need manual
verification and should not be read as either a pass or a finding.

**A JSON report** per sample, written to
`3_security_analysis/jbomaudit/results/audit_results/<groupId>/<artifactId>/<version>/compliance_result.json`.
That directory is gitignored, since it is regenerated on every run.

The report is keyed by the six finding types:

| Key | Meaning |
|---|---|
| `M1:Missing Direct Dependency` | Used directly by the project, declared nowhere in the SBOM |
| `M2:Missing Transitive Dependency` | Pulled in transitively, absent from the SBOM |
| `M3: Missing Transitive Relationship` | Present in the SBOM, but an edge in the dependency graph is not recorded |
| `N1:Incorrect Direct Dependency` | Declared as a direct dependency, not actually used |
| `N2:Incorrect Transitive Dependency` | Declared transitively, not actually present |
| `N3:Incorrect Transitive Relationship` | A declared edge that does not exist |

Each entry carries the validated findings plus the cases the tool could not settle
(`uncollected_first_level`, `unresolved_first_level`), and the `proof` field records the
binary evidence a finding was drawn from.

## Committed example

`example_run/com.hack23.sonar/sonar-cloudformation-plugin/3.0.11/compliance_result.json`
is a report for one of the samples in
[stage 1](../../1_analysis_object/jbomaudit/README.md) — the one with both missing and
incorrect direct dependencies, so it shows a populated finding alongside the types that came
back empty.

It was produced by the upstream JBomAudit artifact run against this sample, not by a run of
this repository.
