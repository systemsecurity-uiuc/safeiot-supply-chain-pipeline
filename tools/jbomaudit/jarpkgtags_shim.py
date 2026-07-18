#!/usr/bin/env python3
"""
Stand-in replacement for the upstream `jarpkgtags` CLI (from the
code-genome/jarpkginfo repo, which requirements.txt points at but which
is currently unavailable). See the commented-out line in requirements.txt.

Produces the same meta_info.json schema expected by generate_jar_pkg_tags.py
and analyze_inconsistency.py:

    {"packages": {"<pkg>": {"uses": ["<other_pkg>", ...]}, ...}}

Package list comes from the jar's own .class file layout; the "uses"
edges come from `jdeps -verbose:package` (ships with the JDK, no extra
install needed). This does NOT attempt reflection/dynamic-load
detection the way the real jarpkgtags tool reportedly does -- those
keys are simply omitted, and downstream code treats them as optional.

Swap back to the real jarpkgtags once code-genome/jarpkginfo is
available again: uncomment it in requirements.txt and revert the
command construction in generate_jar_pkg_tags.py to call `jarpkgtags`
directly instead of this script.
"""
import json
import re
import subprocess
import sys
import zipfile


def get_declared_packages(jar_path):
    packages = set()
    with zipfile.ZipFile(jar_path) as z:
        for name in z.namelist():
            if not name.endswith(".class"):
                continue
            if "/" not in name:
                continue
            if name.endswith("module-info.class") or name.endswith("package-info.class"):
                continue
            pkg = name.rsplit("/", 1)[0].replace("/", ".")
            packages.add(pkg)
    return packages


LINE_RE = re.compile(r"^\s+(\S+)\s+->\s+(\S+)\s+(\S+)\s*$")


def get_uses_edges(jar_path):
    uses = {}
    result = subprocess.run(
        ["jdeps", "-verbose:package", jar_path],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    for line in result.stdout.splitlines():
        if not line.startswith("   "):
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        src, tgt, _origin = m.groups()
        uses.setdefault(src, set()).add(tgt)
    return uses


def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    jar_path = sys.argv[1]

    declared = get_declared_packages(jar_path)
    uses = get_uses_edges(jar_path)

    packages = {}
    for pkg in declared:
        packages[pkg] = {"uses": sorted(uses.get(pkg, set()))}

    json.dump({"packages": packages}, sys.stdout)


if __name__ == "__main__":
    main()
