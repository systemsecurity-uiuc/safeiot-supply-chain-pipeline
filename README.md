# SafeIoT Pipeline — Supply Chain

Part of the **[SafeIoT Center](https://safe-iot.com/)** — the NSF-funded Center for Security and Privacy Assurance and Conformance in IoT Standards and Systems (supported by NSF, UIUC, UNC Charlotte, and Indiana University).

Consumers increasingly rely on IoT products for home safety, health, and everyday convenience, yet popular IoT standards and their implementations lack holistic, rigorous security and privacy verification. SafeIoT addresses this gap with a community-driven, open-source CI/CD infrastructure that continuously verifies IoT standards and vendor implementations, with an initial focus on the **Matter** standard and **SBOM** in the IoT context.

The SafeIoT pipeline is organized into two complementary tracks, each with its own repository:

| Track | Repository | Focus | Example Tool |
|---|---|---|---|
| 1 — IoT Vulnerability Detection | [safeiot-vuln-pipeline](https://github.com/systemsecurity-uiuc/safeiot-vuln-pipeline) | Vulnerabilities in IoT standards and their implementations, incl. commodity products such as Google Home, Apple Home, and SmartThings | [UMCCI Checker](https://github.com/systemsecurity-uiuc/safeiot-vuln-pipeline/tree/main/tools/umcci-checker) |
| 2 — IoT SBOM, CBOM, and AI-BOM Verification | **safeiot-supply-chain-pipeline** (this repo) | Supply-chain security, privacy, and compliance issues in Software/Cryptographic/AI Bills of Materials for IoT systems | [JBomAudit](tools/jbomaudit/) |

---

## This Repository — Track 2: IoT SBOM, CBOM, and AI-BOM Verification

This repository collects and organizes IoT ecosystem research artifacts for supply-chain and compliance verification, with an initial focus on **Software Bills of Materials (SBOM)** for Java-based IoT components, and planned expansion to **Cryptographic Bills of Materials (CBOM)** and **AI Bills of Materials (AI-BOM)**. It is designed to be cloned locally and run after environment setup.

## Repository Structure

```
safeiot-supply-chain-pipeline/
├── specifications/          # SBOM / CBOM / AI-BOM format specifications (CycloneDX, SPDX, ...)
├── regulations/             # SBOM / CBOM / AI-BOM legal & policy mandates (NTIA, EO 14028, CRA, ...)
└── tools/                   # Supply-chain verification tools integrated into the pipeline
    └── jbomaudit/           #   JBomAudit (example tool; more tools coming)
```

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

From here, head into [tools/](tools/) and follow the README for whichever tool you want to run — each one manages its own dependencies and setup. Currently that's just [JBomAudit](tools/jbomaudit/); more tools will land here over time.
