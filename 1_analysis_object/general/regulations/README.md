# SBOM / CBOM / AI-BOM Regulations & Policy

This directory tracks the legal and policy mandates that require producing, disclosing, or verifying Bills of Materials — as opposed to [specifications/](../specifications/), which covers the technical *formats* (CycloneDX, SPDX, etc.) those BOMs are encoded in. Understanding this side matters for the pipeline because tools like JBomAudit ultimately serve **compliance** with these mandates, not just format correctness.

> **Note:** This is a fast-moving policy area (especially AI regulation); entries below reflect our best understanding at time of writing and should be re-verified before being cited. Link-only for now — no documents vendored.

---

## SBOM

- [NTIA — Minimum Elements for a Software Bill of Materials (SBOM)](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom) (2021) — defines the baseline fields (supplier, component name, version, dependency relationships, etc.) a conformant SBOM must contain; the reference most SBOM tooling (including JBomAudit) is implicitly validated against
- [Executive Order 14028 — Improving the Nation's Cybersecurity](https://www.federalregister.gov/documents/2021/05/17/2021-10460/improving-the-nations-cybersecurity) (2021), §4 — directs NIST/NTIA to define SBOM requirements for software sold to the US federal government
- [NIST SP 800-218 — Secure Software Development Framework (SSDF)](https://csrc.nist.gov/pubs/sp/800/218/final) — practices referenced by EO 14028 self-attestation, includes SBOM production as a recommended practice
- [OMB M-22-18 — Enhancing the Security of the Software Supply Chain](https://www.whitehouse.gov/wp-content/uploads/2022/09/M-22-18.pdf) (2022) — requires federal agencies to collect self-attestations (and SBOMs on request) from software vendors
- [FDA — Cybersecurity in Medical Devices (Section 524B, FD&C Act)](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cybersecurity-medical-devices-quality-system-considerations-and-content-premarket-submissions) (2023) — mandates SBOM as part of premarket submissions for connected medical devices; directly relevant to IoT medical devices
- [EU Cyber Resilience Act (CRA) — Regulation (EU) 2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj) — requires SBOM (Annex I, Part II) for "products with digital elements" sold in the EU, explicitly covering consumer IoT; obligations phase in through 2027
- [CISA — SBOM Resources](https://www.cisa.gov/sbom) — ongoing US government clearinghouse for SBOM tooling, use cases, and guidance updates

## CBOM

- [OMB M-23-02 — Migrating to Post-Quantum Cryptography](https://www.whitehouse.gov/wp-content/uploads/2022/11/M-23-02-M-Memo-on-Migrating-to-Post-Quantum-Cryptography.pdf) (2022) — requires federal agencies to inventory cryptographic systems, i.e. produce a CBOM, as the first step of PQC migration
- [National Security Memorandum 10 (NSM-10)](https://www.whitehouse.gov/briefing-room/statements-releases/2022/05/04/national-security-memorandum-on-promoting-united-states-leadership-in-quantum-computing-while-mitigating-risks-to-vulnerable-cryptographic-systems/) (2022) — the underlying directive behind M-23-02's cryptographic inventory requirement

## AI-BOM

- [EU AI Act — Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj), Annex IV — technical documentation requirements for high-risk AI systems (training data, model architecture, dependencies) that an AI-BOM would help satisfy
- _US AI policy is currently in flux (EO 14110 was rescinded and replaced by EO 14179 in early 2025); no stable US federal AI-BOM mandate exists yet as of this writing — re-check before relying on this._

### Update Instructions

New entries go under the matching BOM-type section — real title, official link, one line on what it requires re: BOMs. This area moves fast (AI policy especially), so call out anything that's likely to be stale soon, the way the AI-BOM note above does.
