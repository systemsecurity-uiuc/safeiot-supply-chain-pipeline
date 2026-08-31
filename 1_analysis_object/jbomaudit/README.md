# JBomAudit — Analysis Object

`samples/` holds ten `(SBOM, JAR)` pairs, each laid out as
`<groupId>/<artifactId>/<version>/` with one JAR and one `*-cyclonedx.json` beside it.
The SBOM is the claim; the JAR is the evidence the claim is checked against.

Five come from the paper's artifact-evaluation set. Five were added here: two more real-world
dependency mismatches and a spread of clean baselines, so a run shows both a populated finding
and a clean result.

| Sample | Source | Expected result |
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
| `commons-validator/commons-validator/1.9.0` | added, clean baseline with real transitive deps | clean |

The paper's other §VII case study, `flight-sql-jdbc-driver` (missing `logback`), is not
included — it is a 35 MB shaded JAR, too large to vendor for a demo sample.

The BOM format these documents follow is CycloneDX; see
[`../general/specifications/`](../general/specifications/README.md).

## Using your own artifacts

The layout, not the location, is what matters. Any directory of
`<groupId>/<artifactId>/<version>/` subdirectories works:

```bash
python3 main.py --samples_dir /path/to/your/sboms
```
