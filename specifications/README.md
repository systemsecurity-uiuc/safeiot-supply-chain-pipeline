# SBOM / CBOM / AI-BOM Specifications

This directory contains static specification documents and format references for Bill-of-Materials standards relevant to IoT supply-chain verification: **SBOM**, **CBOM**, and **AI-BOM**. See [regulations/](../regulations/) for the legal/policy mandates that require producing or consuming these BOMs — this directory is only about the technical formats.

> **Note:** These are currently link-only entries (no PDFs vendored yet). When a document is actually downloaded, place it under the matching subdirectory (`specifications/sbom/`, `specifications/cbom/`, `specifications/ai-bom/`) and update the Contents list below.

---

## SBOM (Software Bill of Materials)

The primary focus of the supply-chain pipeline's current verification efforts, and what [JBomAudit](../tools/jbomaudit/) evaluates.

### Contents

- [CycloneDX Specification](https://cyclonedx.org/specification/overview/) — OWASP-maintained BOM standard (JSON/XML/Protobuf); current version 1.6
- [SPDX Specification](https://spdx.dev/use/specifications/) — Linux Foundation / ISO 5962-standardized BOM format; current version 3.0
- [SWID Tags — ISO/IEC 19770-2](https://www.iso.org/standard/65666.html) — software identification tagging standard referenced by NTIA as an acceptable SBOM format

---

## CBOM (Cryptographic Bill of Materials)

Inventories the cryptographic assets (algorithms, keys, certificates, protocols) used by a piece of software — increasingly important for post-quantum cryptography (PQC) migration planning.

### Contents

- [CycloneDX CBOM](https://cyclonedx.org/capabilities/cbom/) — cryptographic-asset component type added in CycloneDX 1.6, originating from IBM Research's CBOM proposal
- [NIST IR 8547 (Draft) — Transition to Post-Quantum Cryptography Standards](https://csrc.nist.gov/pubs/ir/8547/ipd) — background on why cryptographic inventories (i.e., CBOMs) are needed for PQC migration

---

## AI-BOM (AI/ML Bill of Materials)

Inventories the models, datasets, and dependencies that make up an AI/ML component — relevant as IoT devices increasingly embed on-device ML models.

### Contents

- [CycloneDX ML-BOM](https://cyclonedx.org/capabilities/mlbom/) — AI/ML component profile in CycloneDX 1.5+ (model cards, datasets, training pipeline)
- [SPDX AI Profile](https://spdx.github.io/spdx-spec/v3.0.1/model/AI/) — AI/dataset metadata profile added in SPDX 3.0

### Update Instructions

1. Download the latest specification from the upstream source linked above.
2. Place the file(s) under `specifications/<sbom|cbom|ai-bom>/`.
3. Update the Contents list for that section.
4. Commit with a message referencing the spec version.
