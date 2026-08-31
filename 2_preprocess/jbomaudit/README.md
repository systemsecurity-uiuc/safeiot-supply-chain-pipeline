# JBomAudit — Preprocess

Before anything can be compared, JBomAudit has to know two things: what the SBOM *claims*
the dependency tree is, and what packages are *actually* inside the JARs. Building both is
this stage.

The code lives in
[`3_security_analysis/jbomaudit/`](../../3_security_analysis/jbomaudit/README.md): these
modules import each other and share a working directory with the analysis. The steps below run
as the first half of `main.py`.

**Resolving and downloading dependencies** — `crawl_deps.py`, with
`utils_tool/transitive_download.py` and `utils_tool/construct_transitive_deps.py`, walks
the dependency tree declared in the SBOM and fetches each artifact from Maven Central,
pausing briefly between new downloads.

**Extracting package tags** — `generate_jar_pkg_tags.py` opens each JAR and records which
Java packages it actually contains; `add_jar_to_pkg_dic.py` folds those into the lookup
dictionary the analysis queries.

Both write into `metaDB/` under the analysis directory, which is gitignored and shared
across samples in a run — a dependency that appears in several SBOMs is fetched once.
Runtime therefore scales with the number of *distinct* dependencies, and the first run
against a new sample set is much slower than later ones.

The `jarpkginfo` package that does the JAR inspection is vendored at
`3_security_analysis/jbomaudit/vendor/jarpkginfo/` and installed from a local path in
`requirements.txt`, because the upstream `git+https://` URL 404s.

The end-to-end command that runs this stage together with the rest is in
[`pipeline_harness/jbomaudit/`](../../pipeline_harness/jbomaudit/README.md).
