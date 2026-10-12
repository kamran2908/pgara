import sys
import os
import subprocess
import hashlib
import pathlib

def main():
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    checksums_file = repo_root / "docs" / "PHASE1_CHECKSUMS.txt"
    if not checksums_file.exists():
        print(f"Error: Checksums file not found at {checksums_file}", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: git executable is not available in PATH.", file=sys.stderr)
        sys.exit(1)

    lines = checksums_file.read_text(encoding="utf-8").splitlines()
    mismatches = []
    total = 0

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            print(f"Warning: malformed line {line_num} in {checksums_file}: {line}", file=sys.stderr)
            continue
        expected_hash, rel_path = parts
        rel_path = rel_path.replace("\\", "/")
        total += 1

        try:
            proc = subprocess.run(
                ["git", "show", f"HEAD:{rel_path}"],
                cwd=repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            blob_bytes = proc.stdout
            actual_hash = hashlib.sha256(blob_bytes).hexdigest()
            if actual_hash != expected_hash:
                mismatches.append((rel_path, expected_hash, actual_hash))
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode("utf-8", errors="replace").strip()
            mismatches.append((rel_path, expected_hash, f"git show failed: {err_msg}"))

    if mismatches:
        print(f"FAILED: {len(mismatches)} of {total} checksums mismatched:", file=sys.stderr)
        for rel_path, exp, act in mismatches:
            print(f"  {rel_path}: expected {exp}, got {act}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"OK: all {total} checksums match committed content.")
        sys.exit(0)

if __name__ == "__main__":
    main()
