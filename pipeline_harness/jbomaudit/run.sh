#!/usr/bin/env bash
#
# JBomAudit — end-to-end run.
#
# Drives stages 2 (preprocess) and 3 (security analysis) in a single invocation of
# main.py, against the samples in stage 1. Reports land under the analysis directory's
# results/ (gitignored); see 4_analysis_output/jbomaudit/ for a committed example.
#
# Usage: ./pipeline_harness/jbomaudit/run.sh [args passed to main.py]
#        default: --samples_dir <stage 1 samples>

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ANALYSIS_DIR="$REPO_ROOT/3_security_analysis/jbomaudit"
SAMPLES_DIR="$REPO_ROOT/1_analysis_object/jbomaudit/samples"

cd "$ANALYSIS_DIR"

if [ ! -d venv ]; then
  echo "==> Creating virtual environment"
  python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate

echo "==> Installing dependencies (includes the vendored jarpkginfo)"
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r requirements.txt

if [ "$#" -gt 0 ]; then
  echo "==> Running JBomAudit (stages 2 and 3): $*"
  python3 main.py "$@"
else
  echo "==> Running JBomAudit (stages 2 and 3) over all stage-1 samples"
  echo "    First run downloads every declared dependency from Maven Central; this is slow."
  python3 main.py --samples_dir "$SAMPLES_DIR"
fi

echo "==> Reports written to 3_security_analysis/jbomaudit/results/audit_results/"
