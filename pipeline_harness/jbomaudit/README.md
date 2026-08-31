# JBomAudit — Pipeline Harness

**JBomAudit** evaluates the completeness and accuracy of Java SBOMs. It analyzes an SBOM
alongside the JAR it describes and reports the discrepancies, split into dependencies the
SBOM should have declared and did not, and dependencies it declared that are not really
there.

Vendored from [`code-genome/jbomaudit`](https://github.com/code-genome/jbomaudit)
(Apache-2.0), the artifact for the NDSS 2025 paper "JBomAudit: Assessing the Landscape,
Compliance, and Security Implications of Java SBOMs."

## Flow

| Stage | What happens |
|---|---|
| [1 — Analysis object](../../1_analysis_object/jbomaudit/README.md) | Ten `(SBOM, JAR)` pairs laid out as `<groupId>/<artifactId>/<version>/` |
| [2 — Preprocess](../../2_preprocess/jbomaudit/README.md) | Resolves and downloads declared dependencies from Maven Central, then extracts package inventories from every JAR |
| [3 — Security analysis](../../3_security_analysis/jbomaudit/README.md) | Compares declared against actual and classifies findings into the six M/N types |
| [4 — Analysis output](../../4_analysis_output/jbomaudit/README.md) | Console summary table plus a per-sample `compliance_result.json` |

Stages 2 and 3 run in one invocation of `main.py`: the analysis queries the package
dictionary the preprocessing builds, and both share the same working directory.

## Prerequisites

- Python 3.9+
- Network access to Maven Central — the first run downloads every dependency the sample
  SBOMs declare

## Running

From the repository root:

```bash
./pipeline_harness/jbomaudit/run.sh
```

This creates a virtual environment, installs dependencies including the vendored
`jarpkginfo`, and audits every sample in
[`1_analysis_object/jbomaudit/samples/`](../../1_analysis_object/jbomaudit/samples/),
finishing with a consolidated summary table.

To audit one pair instead of the whole set, or to point at your own artifacts:

```bash
cd 3_security_analysis/jbomaudit
source venv/bin/activate

python3 main.py --sbom_path <path/to/example-cyclonedx.json> --jar_path <path/to/example.jar>
python3 main.py --samples_dir /path/to/your/sboms
python3 main.py -m layer --samples_dir ../../1_analysis_object/jbomaudit/samples
```

`-m global` (the default) reports packages absent from the SBOM entirely; `-m layer`
reports packages declared at the wrong level of the tree.

**On runtime.** The first run against a new sample set is slow — it downloads every
distinct dependency referenced by the SBOMs, with a pause between fetches. Downloads are
cached in `metaDB/` and shared across samples, so later runs are much faster. A sample
that fails, typically because a dependency has disappeared from Maven Central, is
reported inline without aborting the batch.

## Citation

```bibtex
@inproceedings{jbomaudit,
  title={JBomAudit: Assessing the Landscape, Compliance, and Security Implications of Java SBOMs},
  author={Yue Xiao, Dhilung Kirat, Douglas Lee Schales, Jiyong Jang, Luyi Xing, Xiaojing Liao},
  booktitle={Proceeding of the ISOC Network and Distributed System Security Symposium (NDSS)},
  year={2025}
}
```
