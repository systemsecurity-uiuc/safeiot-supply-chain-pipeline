# JBomAudit

**JBomAudit** is a tool to evaluate the completeness and accuracy of Java SBOMs (Software Bill of Materials). The tool analyzes SBOMs alongside their corresponding JAR files to detect discrepancies, categorized as either missing dependencies or incorrect dependencies.

Vendored from [code-genome/jbomaudit](https://github.com/code-genome/jbomaudit) for the SafeIoT supply-chain pipeline. Source is otherwise unmodified except where noted below.

## A Note on `jarpkgtags`

`requirements.txt` normally installs `jarpkgtags` from `git+https://github.com/code-genome/jarpkginfo.git`, a dependency the pipeline uses to extract each JAR's declared packages and their inter-package `uses` edges. That repo is currently unavailable, so the line is commented out in `requirements.txt` and `generate_jar_pkg_tags.py` instead calls the bundled [`jarpkgtags_shim.py`](jarpkgtags_shim.py), which reproduces the same `meta_info.json` schema using `zipfile` (declared packages) and `jdeps -verbose:package` (uses edges, ships with the JDK). It does not attempt reflection/dynamic-load detection the way the real tool reportedly does, so the `Undetermined` flag described below won't currently trigger from that path.

Once `code-genome/jarpkginfo` is reachable again, uncomment it in `requirements.txt` and point `generate_jar_pkg_tags.py` back at the real `jarpkgtags` command.

## Quick Start

1. **Set up a virtual environment**
    ```bash
    cd tools/jbomaudit
    pip3 install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    Also requires a JDK on `PATH` (for `jdeps`).

2. **Prepare Target SBOM and JAR Files**

   Move the target SBOM file and its corresponding JAR file to the `./samples/` directory. Please organize them using the following structure: (Both the **SBOM** and **JAR** should be placed inside the following directory.)
   ```
   /samples/<groupId>/<artifactId>/<version>/
   ```
   A worked example is already in place at `samples/org.opendaylight.aaa/aaa-cli-jar/0.15.2/`.

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
