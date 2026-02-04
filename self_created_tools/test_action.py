import os
import sys
import tempfile
import json
from pathlib import Path

# Mock GitHub Action environment
os.environ['INPUT_PROMPT'] = "This is a test prompt"
os.environ['INPUT_OUTPUT'] = "This is a test output. Introduction. Step 1. Step 2. Step 3."
os.environ['INPUT_ASSERTIONS-CONFIG'] = "validators/sales_plan.yaml"
os.environ['INPUT_PASS-THRESHOLD'] = "50"
os.environ['INPUT_FAIL-ON-WARNING'] = "false"
os.environ['GITHUB_OUTPUT'] = "github_output.txt"

# Add repository root to python path (so entrypoint can be imported)
sys.path.insert(0, os.getcwd())

# Import entrypoint
try:
    import entrypoint
except ImportError:
    print("Could not import entrypoint. Make sure you are in the repo root.")
    sys.exit(1)

try:
    print("Running entrypoint.main()...")
    entrypoint.main()
except SystemExit as e:
    print(f"Entrypoint exited with code: {e.code}")
    if e.code != 0:
        print("FAIL: Entrypoint failed")
        sys.exit(1)

# Check output
if os.path.exists("github_output.txt"):
    with open("github_output.txt", "r") as f:
        print("GitHub Output:")
        print(f.read())
else:
    print("FAIL: No output file created")
    sys.exit(1)

print("SUCCESS: Action completed successfully")
