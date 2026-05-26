from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"

PY_PATH_PATTERNS = [
    re.compile(r"Path\([^#\n]*https?://", re.IGNORECASE),
    re.compile(r"Path\([^#\n]*github\.com", re.IGNORECASE),
    re.compile(r"Path\([^#\n]*blob/main", re.IGNORECASE),
    re.compile(r"Path\([^#\n]*raw\.githubusercontent", re.IGNORECASE),
    re.compile(r"Path\([^#\n]*[A-Z]:\\\\", re.IGNORECASE),
    re.compile(r"I:\\\\My Drive\\\\UFO", re.IGNORECASE),
    re.compile(r"C:\\\\Users\\\\Dan", re.IGNORECASE),
]

PS_PATH_PATTERNS = [
    re.compile(r"Join-Path[^\n]*https?://", re.IGNORECASE),
    re.compile(r"Test-Path[^\n]*https?://", re.IGNORECASE),
    re.compile(r"Join-Path[^\n]*github\.com", re.IGNORECASE),
    re.compile(r"Test-Path[^\n]*github\.com", re.IGNORECASE),
    re.compile(r"Join-Path[^\n]*[A-Z]:\\\\", re.IGNORECASE),
    re.compile(r"Test-Path[^\n]*[A-Z]:\\\\", re.IGNORECASE),
    re.compile(r"I:\\\\My Drive\\\\UFO", re.IGNORECASE),
    re.compile(r"C:\\\\Users\\\\Dan", re.IGNORECASE),
]


def scan_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    patterns = PY_PATH_PATTERNS if path.suffix.lower() == ".py" else PS_PATH_PATTERNS
    for lineno, line in enumerate(text, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for pattern in patterns:
            if pattern.search(line):
                errors.append(f"{path}:{lineno}:{stripped}")
                break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for URL strings embedded in filesystem path constructors.")
    parser.add_argument("--scripts-dir", type=Path, default=SCRIPT_DIR)
    args = parser.parse_args()

    failures: list[str] = []
    for path in sorted(args.scripts_dir.glob("*.py")) + sorted(args.scripts_dir.glob("*.ps1")):
        failures.extend(scan_file(path))

    if failures:
        print("Found path hygiene issues:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print(f"Scanned {len(list(args.scripts_dir.glob('*.py')))} Python scripts and {len(list(args.scripts_dir.glob('*.ps1')))} PowerShell scripts.")
    print("No publication path hygiene issues found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

