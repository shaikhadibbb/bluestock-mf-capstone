# TODO: verify if environment has all libraries before running
# FIXME: subprocess.run can fail if python executable is not resolved
# WIP: pipeline runner works for now, will refactor to use a formal orchestration tool later

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    'scripts/data_ingestion.py',
    'scripts/clean_data.py',
    'scripts/load_database.py',
    'scripts/compute_metrics.py',
    'scripts/generate_eda_charts.py',
    'scripts/generate_report.py',
    'scripts/generate_presentation.py',
]

def run_step(script: str) -> bool:
    """Run a pipeline step, return True if successful."""
    print(f"\n{'='*60}")
    print(f"Running: {script}")
    print('='*60)
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"FAILED: {script}")
        return False
    print(f"DONE: {script}")
    return True

if __name__ == '__main__':
    print("Bluestock MF Capstone - Full Pipeline")
    print(f"Python: {sys.version}")
    success = all(run_step(s) for s in SCRIPTS)
    print(f"\n{'='*60}")
    print("Pipeline complete." if success else "Pipeline failed - check logs above.")
    sys.exit(0 if success else 1)
