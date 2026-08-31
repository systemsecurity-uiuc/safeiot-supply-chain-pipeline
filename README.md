# SafeIoT Supply Chain Pipeline

Part of the **[SafeIoT Center](https://safe-iot.com/)** — the NSF-funded Center for Security and Privacy Assurance and Conformance in IoT Standards and Systems (supported by NSF, UIUC, UNC Charlotte, and Indiana University).

Consumers increasingly rely on IoT products for home safety, health, and everyday convenience, yet popular IoT standards and their implementations lack holistic, rigorous security and privacy verification. SafeIoT addresses this gap with a community-driven, open-source CI/CD infrastructure that continuously verifies IoT standards and vendor implementations.

The SafeIoT pipeline is organized into two complementary tracks, each with its own repository:

- **Track 1 — IoT Vulnerability Detection** — [safeiot-vuln-pipeline](https://github.com/systemsecurity-uiuc/safeiot-vuln-pipeline)
- **Track 2 — IoT SBOM, CBOM, and AI-BOM Verification** — **safeiot-supply-chain-pipeline** (this repository)

---

## Track 2 — IoT SBOM, CBOM, and AI-BOM Verification

Tools that check whether an IoT product's Software, Cryptographic, and AI Bills of Materials are complete, consistent, and supported by technical evidence from the artifacts they describe.

The repository is organized by the stages a verification run passes through, so that each tool's analysis object, preparation, analysis, and results sit in the part of the pipeline they belong to.

## Repository Structure

The four numbered directories are the stages of a verification run. Inside each one,
every tool has a subdirectory named after itself, so a tool's contribution appears in the
stages it actually uses. `pipeline_harness/` is what ties a tool's stages back together
into something runnable.

```
safeiot-supply-chain-pipeline/
├── 1_analysis_object/       # What gets analyzed
│   ├── general/             #   Shared: BOM format specs (CycloneDX, SPDX) and mandates (NTIA, EO 14028, CRA)
│   └── <tool-name>/         #   Objects specific to one tool
├── 2_preprocess/            # Dependency resolution, unpacking, normalization
│   └── <tool-name>/
├── 3_security_analysis/     # The verification logic itself
│   └── <tool-name>/
├── 4_analysis_output/       # Reports, findings, evidence
│   └── <tool-name>/
└── pipeline_harness/        # Per-tool end-to-end flow description and entry point
    └── <tool-name>/
```

The example tool is [JBomAudit](pipeline_harness/jbomaudit/README.md); start at its
harness README to see how one tool spans the stages.

---

## Getting Started

### Prerequisites

- Python 3.9+
- Git

### Clone and Setup

```bash
git clone https://github.com/systemsecurity-uiuc/safeiot-supply-chain-pipeline.git
cd safeiot-supply-chain-pipeline
```

Each tool manages its own dependencies. Pick a tool in
[`pipeline_harness/`](pipeline_harness/) and follow its README — it lists the
prerequisites and the single command that runs the tool end to end. Currently that is
just [JBomAudit](pipeline_harness/jbomaudit/README.md); more tools will land here over
time.

---

## Contribution Guidelines

Tools reach this pipeline through the [SafeIoT Hackathon](https://safe-iot.com/#hackathon)
and through course projects built on it. A contribution is a **tool**, and a tool is
described by where its parts sit in the four stages.

### How to contribute

1. **Fork** this repository and create a branch for your tool.
2. **Pick a name** for your tool. It becomes your subdirectory name in every stage. You only ever
   add files under directories named after your tool, so contributions do not collide.
3. **Add your content stage by stage**, under `<stage>/<your-tool>/`:

   | Stage | What goes here |
   |---|---|
   | `1_analysis_object/` | The BOM documents, JARs, firmware, container images, or model files your tool analyzes — or instructions for obtaining them |
   | `2_preprocess/` | Dependency resolution, unpacking, extraction, normalization |
   | `3_security_analysis/` | The verification, compliance checks, or risk analysis |
   | `4_analysis_output/` | One representative example run: report, findings, logs, evidence |

4. **Add a harness** at `pipeline_harness/<your-tool>/` containing a README that
   describes the flow and a runnable entry point that takes a clean checkout to a result.
5. **Open a pull request** against `main`.

### What is expected

- **Every stage directory you use gets a README.** One or two paragraphs: what this stage
  does for your tool, what it consumes, what it produces.
- **Skip the stages that do not apply.** Plenty of tools have no meaningful preprocessing
  step, and some have no analysis object that can be checked in. Add a short README in
  that stage's directory saying it does not apply and why.
- **The harness must run.** A script, a Makefile, or a documented sequence of commands —
  whatever form fits your tool, as long as someone else can go from a fresh clone to a
  result by following it. This doubles as the reproducibility instruction your project
  report needs.
- **Commit one example output.** Someone should be able to see what your tool produces
  without setting it up.
- **Keep large artifacts out of git.** Firmware images, container images, and build output
  belong behind a fetch script or a manifest, with the downloads gitignored.

### What is not required

There is no plugin interface to implement, no base class to subclass, and no shared
output format. Write your tool in whatever language and with whatever dependencies it
needs. What you follow is the structure: the stages, the naming, and a working entry point.

If your tool needs an analysis object or reference material that other tools could reuse
— a BOM format schema, a regulation, a benchmark corpus — put it in
[`1_analysis_object/general/`](1_analysis_object/general/) rather than under your own
tool directory.
