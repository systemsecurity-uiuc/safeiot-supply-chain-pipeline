from crawl_deps import crawl_assets
from generate_jar_pkg_tags import generate_jarpkgtags
from add_jar_to_pkg_dic import add_to_dic
from compliance_check import check_sbom_noncompliance
import argparse
import glob
import json
import os
from tabulate import tabulate

# Define available search modes
class SearchMode:
    GLOBAL = "global"
    LAYER = "layer"

def audit(sbom_path, jar_path, mode, sbom_dir='./samples/'):
    """
    Perform SBOM and JAR auditing based on the selected mode.
    """
    # Step 1: Download all dependencies
    root_path = "./metaDB/maven_asset_deps/"
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    crawl_assets(sbom_path, root_path)

    # Step 2: Run jarpkgtags to generate metadata and add to dictionary if not already stored
    generate_jarpkgtags(sbom_dir)
    add_to_dic()

    # Step 3: Check for non-compliance issues
    check_sbom_noncompliance(sbom_path, jar_path, mode)


def discover_samples(samples_dir):
    """
    Walk samples_dir for <groupId>/<artifactId>/<version>/ triples, each expected to
    hold exactly one JAR and one *-cyclonedx.json. Returns a list of (label, sbom_path, jar_path).
    """
    found = []
    for gid in sorted(get_immediate_subdirs(samples_dir)):
        for aid in sorted(get_immediate_subdirs(gid)):
            for ver in sorted(get_immediate_subdirs(aid)):
                jars = glob.glob(os.path.join(ver, '*.jar'))
                sboms = glob.glob(os.path.join(ver, '*cyclonedx*.json'))
                if len(jars) != 1 or len(sboms) != 1:
                    print(f"skipping {ver}: expected exactly one jar and one *-cyclonedx.json, "
                          f"found {len(jars)} jar(s) and {len(sboms)} sbom(s)")
                    continue
                label = "/".join(ver.rstrip("/").split("/")[-3:])
                found.append((label, sboms[0], jars[0]))
    return found


def get_immediate_subdirs(directory):
    return [os.path.join(directory, name) for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


def audit_batch(samples_dir, mode):
    """
    Run audit() over every sample found under samples_dir and print a consolidated summary.
    """
    samples = discover_samples(samples_dir)
    if not samples:
        print(f"No <groupId>/<artifactId>/<version> samples found under {samples_dir}")
        return

    summary_rows = []
    for label, sbom_path, jar_path in samples:
        print(f"\n=== {label} ===")
        try:
            audit(sbom_path, jar_path, mode, sbom_dir=samples_dir)
            counts = count_findings(label)
            summary_rows.append([label, "clean" if sum(counts) == 0 else "violations found", *counts])
        except Exception as e:
            print(f"error auditing {label}: {e}")
            summary_rows.append([label, "error", "-", "-", "-", "-", "-", "-"])

    headers = ["Sample", "Result", "M1", "M2", "M3", "N1", "N2", "N3"]
    print("\n\n=== Batch Summary ===")
    print(tabulate(summary_rows, headers=headers, tablefmt="grid"))


def count_findings(label):
    """
    Read back ./results/audit_results/<label>/compliance_result.json and count validated
    (non-Undetermined-only) findings per inconsistency type, in M1/M2/M3/N1/N2/N3 order.
    """
    result_path = f"./results/audit_results/{label}/compliance_result.json"
    with open(result_path) as f:
        result = json.load(f)
    keys = [
        ("M1:Missing Direct Dependency", "validate_missing_deps"),
        ("M2:Missing Transitive Dependency", "validate_missing_transitive_dependency"),
        ("M3: Missing Transitive Relationship", "validate_missing_transitive_relationship"),
        ("N1:Incorrect Direct Dependency", "validate_incorrect_deps"),
        ("N2:Incorrect Transitive Dependency", "validate_incorrect_transitive_deps"),
        ("N3:Incorrect Transitive Relationship", "validate_incorrect_transitive_relationship"),
    ]
    counts = []
    for top_key, sub_key in keys:
        entries = result[top_key][sub_key]
        counts.append(len([e for e in entries if e]) if isinstance(entries, list) else len(entries))
    return counts


if __name__ == '__main__':
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Run the SBOM and JAR audit tool.")

    # Add arguments for SBOM path and JAR path
    parser.add_argument('--sbom_path', type=str, help="Path to the SBOM JSON file")
    parser.add_argument('--jar_path', type=str, help="Path to the JAR file")

    # Batch mode: audit every <groupId>/<artifactId>/<version> sample under a folder
    parser.add_argument('--samples_dir', type=str,
                        help="Path to a folder of <groupId>/<artifactId>/<version> samples; "
                             "audits all of them in one run instead of a single --sbom_path/--jar_path pair")

    # Add the mode argument with default set to GLOBAL
    parser.add_argument('-m', '--mode', type=str, choices=[SearchMode.GLOBAL, SearchMode.LAYER],
                        default=SearchMode.GLOBAL, help="Comparison mode: 'global' (default) or 'layer'")

    # Parse the arguments from the command line
    args = parser.parse_args()

    if args.samples_dir:
        audit_batch(args.samples_dir, args.mode)
    elif args.sbom_path and args.jar_path:
        audit(args.sbom_path, args.jar_path, args.mode)
    else:
        parser.error("either --samples_dir, or both --sbom_path and --jar_path, are required")
