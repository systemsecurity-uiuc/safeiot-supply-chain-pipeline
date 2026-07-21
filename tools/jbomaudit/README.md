# JBomAudit

**JBomAudit** is a tool to evaluate the completeness and accuracy of Java SBOMs (Software Bill of Materials). The tool analyzes SBOMs alongside their corresponding JAR files to detect discrepancies, categorized as either missing dependencies or incorrect dependencies.

Vendored from [code-genome/jbomaudit](https://github.com/code-genome/jbomaudit) for the SafeIoT supply-chain pipeline. Source is otherwise unmodified except where noted below.

## A Note on `jarpkgtags`

The pipeline depends on `jarpkgtags` (from IBM Research's [code-genome/jarpkginfo](https://github.com/code-genome/jarpkginfo)) to extract each JAR's declared packages, inter-package `uses` edges, and reflection/dynamic-load usage. `requirements.txt` normally installs this via `git+https://github.com/code-genome/jarpkginfo.git`, but that URL currently 404s, so it's vendored locally instead at [`vendor/jarpkginfo/`](vendor/jarpkginfo/) and installed from there.

## Quick Start

1. **Set up a virtual environment**
    ```bash
    cd tools/jbomaudit
    pip3 install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Prepare Target SBOM and JAR Files**

   Move the target SBOM file and its corresponding JAR file to the `./samples/` directory. Please organize them using the following structure: (Both the **SBOM** and **JAR** should be placed inside the following directory.)
   ```
   /samples/<groupId>/<artifactId>/<version>/
   ```

   Ten worked examples are already in place, five from the paper's own artifact-evaluation set and five added here for variety (two more real-world dependency mismatches plus a spread of clean baselines):

   | Sample | Source | Result |
   |---|---|---|
   | `org.opendaylight.aaa/aaa-cli-jar/0.15.2` | paper's artifact-evaluation set | 12 missing direct deps |
   | `com.hack23.sonar/sonar-cloudformation-plugin/3.0.11` | paper's artifact-evaluation set | 13 missing + 5 incorrect direct deps |
   | `dev.iabudiab/dependency-track-maven-plugin/2.4.1` | paper's artifact-evaluation set | 3 incorrect direct deps |
   | `gov.nist.secauto.oscal/liboscal-java/3.0.3` | paper's artifact-evaluation set | 1 incorrect direct dep |
   | `org.apache.hbase/hbase-examples/2.5.3` | paper §VII case study (falsely-listed `zookeeper`) | 1 missing, 2 incorrect direct, 6 incorrect transitive, 21 incorrect transitive-relationship |
   | `commons-io/commons-io/2.16.1` | added, clean baseline | clean |
   | `org.apache.commons/commons-lang3/3.14.0` | added, clean baseline | clean |
   | `org.apache.commons/commons-text/1.12.0` | added, clean baseline | clean |
   | `commons-codec/commons-codec/1.17.1` | added, clean baseline | clean |
   | `commons-validator/commons-validator/1.9.0` | added, clean baseline (has real transitive deps, still came back clean) | clean |

   The paper's other §VII case study, `flight-sql-jdbc-driver` (missing `logback`), isn't included here — it's a 35MB shaded jar, too large to be worth vendoring into this repo for a demo sample.

3. **Running the Analysis**

   Use the following command to analyze your Java project:

   ```bash
   python3 main.py --sbom_path [example-cyclonedx.json] \
                  --jar_path [example.jar]
   ```

   By default, the tool runs in **SearchMode.GLOBAL** mode. You can specify a different mode using the `-m` parameter.

   #### **Selecting a Comparison Mode (`-m` parameter)**
   JBomAudit supports two comparison modes for **missing dependency detection**, controlling the granularity and precision:

   - **`SearchMode.GLOBAL` (default)**:
      - Performs a **strict validation** by checking the entire SBOM dependency tree.
      - If a package is used in the project but not provided by any dependency at any level of the SBOM hierarchy, it is marked as missing.
      - This indicates a purely missing dependency, meaning the package is completely absent from the SBOM. Such cases are more severe, as they suggest the dependency was not disclosed anywhere in the SBOM dependency tree.

   - **`SearchMode.LAYER`**:
   - Performs a **layer-sensitive validation**, ensuring that dependencies are disclosed at the correct hierarchical levels in the SBOM.
   - Specifically, checks whether a directly used package is explicitly declared in the first layer of the SBOM dependency tree. Also verifies whether transitive dependencies of first-layer dependencies are correctly disclosed in the second layer, and so on.
   - This helps identify cases where dependency layers are mismatched. For example, if a package is directly used in the project but is only disclosed as a transitive dependency in a lower layer of the SBOM (instead of being explicitly listed as a direct dependency), it is marked as a missing direct dependency.

   #### **Example Usage**
   ```bash
   python3 main.py -m global --sbom_path [example-cyclonedx.json] \
                  --jar_path [example.jar]
   ```

   ```bash
   python3 main.py -m layer --sbom_path [example-cyclonedx.json] \
                  --jar_path [example.jar]
   ```

   If `-m` is not provided, **SearchMode.GLOBAL** is used by default.

   #### **Batch Mode: Auditing Multiple Samples at Once**

   To audit every sample under a folder in one run instead of one `--sbom_path`/`--jar_path` pair at a time, point `--samples_dir` at a folder of `<groupId>/<artifactId>/<version>/` subdirectories (each holding one jar and one `*-cyclonedx.json`):

   ```bash
   python3 main.py --samples_dir samples
   ```

   This isn't limited to `./samples/` — any folder with the same `<groupId>/<artifactId>/<version>/` layout works, e.g. `--samples_dir /path/to/other/sboms`. It runs the full pipeline for each sample found and finishes with a consolidated summary table of per-type finding counts. A failure on one sample (e.g. a dependency that's disappeared from Maven Central) is reported inline and doesn't abort the rest of the batch.

   The first run against a new set of samples downloads every dependency referenced in their SBOMs from Maven Central, with a short pause between each new download — so runtime scales with how many *distinct* dependencies your samples reference. Downloads are cached under `metaDB/` and shared across samples in the same run, so overlapping dependencies (e.g. `commons-logging` showing up in several samples) are only fetched once.

## Results

Once the analysis is complete, results are displayed in **two formats**:

- **Command Line Table**:
  - If the flag shows `Undetermined`: It means **manual verification** is required. Specifically:
   - **Incorrect Dependency**: Some classes contain **unresolved dynamically loaded dependencies** that need manual resolution.
   - **Missing Dependency**: The `Undetermined` flag appears when the tool cannot retrieve certain dependencies due to unavailability. In such cases, you must manually download and verify them.

- **JSON Report Output**:
  A detailed report is saved in:
  ```
  ./results/audit_results/compliance_result.json
  ```

## Citation
```bibtex
@inproceedings{jbomaudit,
  title={JBomAudit:Assessing the Landscape, Compliance, and Security Implications of Java SBOMs},
  author={Yue Xiao, Dhilung Kirat, Douglas Lee Schales, Jiyong Jang, Luyi Xing, Xiaojing Liao},
  booktitle={Proceeding of the ISOC Network and Distributed System Security Symposium (NDSS)},
  year={2025}
}
```
