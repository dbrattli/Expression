"""Check the isolated generator spike and each marked invalid consumer."""

import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run positive checks and compare negative diagnostics to marked lines."""
    root = Path(__file__).resolve().parent
    pyright = shutil.which("pyright")
    if pyright is None:
        raise SystemExit("Pyright is required on PATH; use the repository-pinned version.")
    positive = subprocess.run([pyright, "--project", str(root / "pyrightconfig.json")], cwd=root, check=False)
    if positive.returncode:
        return positive.returncode
    fixture = root / "negative.py"
    expected = {number for number, line in enumerate(fixture.read_text().splitlines(), 1) if "# type-error" in line}
    negative = subprocess.run(
        [pyright, "--project", str(root / "pyrightconfig.negative.json"), "--outputjson"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    report = json.loads(negative.stdout)
    errors = [item for item in report["generalDiagnostics"] if item["severity"] == "error"]
    actual = {item["range"]["start"]["line"] + 1 for item in errors if Path(item["file"]) == fixture}
    unexpected_files = {item["file"] for item in errors if Path(item["file"]) != fixture}
    if actual != expected or unexpected_files or negative.returncode != 1:
        sys.stderr.write(negative.stdout + negative.stderr)
        sys.stderr.write(f"Missing rejection lines: {sorted(expected - actual)}\n")
        sys.stderr.write(f"Unexpected rejection lines: {sorted(actual - expected)}\n")
        return 1
    sys.stdout.write(f"Verified {len(expected)} invalid consumer expressions are rejected.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
