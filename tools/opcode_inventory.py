import os
import re
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from collections import Counter
from src.ir.parser import SUPPORTED_OPCODES

def scan_opcodes_in_files(files):
    counts = Counter()
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            in_fn = False
            for line in fp:
                clean = line.split(";", 1)[0].strip()
                if clean.startswith("define "):
                    in_fn = True
                    continue
                if clean == "}":
                    in_fn = False
                    continue
                if not in_fn or not clean:
                    continue
                if re.match(r"^[A-Za-z0-9_.]+:$", clean):
                    continue
                m = re.match(r"^(?:%[A-Za-z0-9_.]+\s*=\s*)?([a-z]+)\b", clean)
                if m:
                    op = m.group(1)
                    counts[op] += 1
    return counts

def generate_inventory():
    repo_root = Path(__file__).resolve().parent.parent
    ir_dir = repo_root / "results" / "raw" / "ir"
    doc_file = repo_root / "docs" / "OPCODE_INVENTORY.txt"

    raw_files = sorted(ir_dir.glob("*.raw.ll"))
    mem2reg_files = sorted(ir_dir.glob("*.mem2reg.ll"))

    raw_counts = scan_opcodes_in_files(raw_files)
    mem2reg_counts = scan_opcodes_in_files(mem2reg_files)

    lines = [
        "# PGARA Phase 1 LLVM IR Opcode Inventory",
        "# Note: Raw IR lists 'alloca' as unsupported by design, as the PGARA parser",
        "# operates exclusively on mem2reg-promoted IR where all allocas have been eliminated.",
        "",
        "=== RAW IR (results/raw/ir/*.raw.ll) ===",
        "Opcodes by frequency:",
    ]

    for op, cnt in sorted(raw_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"  {op:<15} : {cnt}")

    raw_unsupported = sorted([op for op in raw_counts if op not in SUPPORTED_OPCODES])
    raw_unseen = sorted([op for op in SUPPORTED_OPCODES if op not in raw_counts])

    lines.append("")
    lines.append("Present but unsupported in Raw IR:")
    for op in raw_unsupported:
        lines.append(f"  {op} ({raw_counts[op]})")
    if not raw_unsupported:
        lines.append("  (none)")

    lines.append("")
    lines.append("Supported but never seen in Raw IR:")
    for op in raw_unseen:
        lines.append(f"  {op}")
    if not raw_unseen:
        lines.append("  (none)")

    lines.append("")
    lines.append("=== MEM2REG IR (results/raw/ir/*.mem2reg.ll) ===")
    lines.append("Opcodes by frequency:")

    for op, cnt in sorted(mem2reg_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"  {op:<15} : {cnt}")

    mem_unsupported = sorted([op for op in mem2reg_counts if op not in SUPPORTED_OPCODES])
    mem_unseen = sorted([op for op in SUPPORTED_OPCODES if op not in mem2reg_counts])

    lines.append("")
    lines.append("Present but unsupported in Mem2Reg IR:")
    for op in mem_unsupported:
        lines.append(f"  {op} ({mem2reg_counts[op]})")
    if not mem_unsupported:
        lines.append("  (none)")

    lines.append("")
    lines.append("Supported but never seen in Mem2Reg IR:")
    for op in mem_unseen:
        lines.append(f"  {op}")
    if not mem_unseen:
        lines.append("  (none)")
    lines.append("")

    output_text = "\n".join(lines)
    with open(doc_file, "w", encoding="utf-8", newline="\n") as fp:
        fp.write(output_text)

    print(f"Opcode inventory generated at: {doc_file}")
    return output_text

if __name__ == "__main__":
    generate_inventory()
