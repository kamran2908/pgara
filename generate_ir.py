import os
import sys
import subprocess
import re
from collections import Counter
import glob

CLANG = r"C:\LLVM-23.1.3\clang+llvm-23.1.3-x86_64-pc-windows-msvc\bin\clang.exe"
OPT = r"C:\LLVM-23.1.3\clang+llvm-23.1.3-x86_64-pc-windows-msvc\bin\opt.exe"

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"ERROR executing: {' '.join(cmd)}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)
    return result

def count_patterns(filepath, patterns):
    counts = {p: 0 for p in patterns}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            for p in patterns:
                if re.search(r'\b' + p + r'\b', line):
                    counts[p] += 1
    return counts

def main():
    benchmarks = glob.glob("benchmarks/*.c")
    if not benchmarks:
        print("No benchmarks found.")
        sys.exit(1)

    out_dir = os.path.join("results", "raw", "ir")
    os.makedirs(out_dir, exist_ok=True)

    opcode_inventory = Counter()

    for c_file in sorted(benchmarks):
        basename = os.path.basename(c_file).replace(".c", "")
        raw_ll = os.path.join(out_dir, f"{basename}.raw.ll")
        mem2reg_ll = os.path.join(out_dir, f"{basename}.mem2reg.ll")

        # 1. Clang -O0 -S -emit-llvm
        # We add -Xclang -disable-O0-optnone based on our earlier investigation
        # otherwise mem2reg does absolutely nothing.
        clang_cmd = [CLANG, "-O0", "-Xclang", "-disable-O0-optnone", "-S", "-emit-llvm", c_file, "-o", raw_ll]
        run_cmd(clang_cmd)

        # 2. Opt mem2reg
        # We use -passes=mem2reg for modern LLVM.
        opt_cmd = [OPT, "-passes=mem2reg", "-S", raw_ll, "-o", mem2reg_ll]
        run_cmd(opt_cmd)

        # 3. Verify
        verify_cmd = [OPT, "-passes=verify", mem2reg_ll]
        run_cmd(verify_cmd)

        # 4. Count alloca and phi
        raw_counts = count_patterns(raw_ll, ["alloca", "phi"])
        mem_counts = count_patterns(mem2reg_ll, ["alloca", "phi"])

        print(f"--- {basename} ---")
        print(f"  RAW     : alloca = {raw_counts['alloca']}, phi = {raw_counts['phi']}")
        print(f"  MEM2REG : alloca = {mem_counts['alloca']}, phi = {mem_counts['phi']}")

        # Parse mem2reg_ll for opcodes
        with open(mem2reg_ll, 'r', encoding='utf-8') as f:
            for line in f:
                # Basic heuristic to match LLVM instruction opcode
                match = re.match(r'^\s*(?:%[a-zA-Z0-9_.]+\s*=\s*)?([a-z]+)\b', line)
                if match:
                    opcode = match.group(1)
                    # Ignore common keywords that appear at start of line but aren't instructions
                    if opcode not in ["define", "declare", "attributes", "source_filename", "target", "!", "}", "entry"]:
                        opcode_inventory[opcode] += 1

    print("\n--- OPCODE INVENTORY ---")
    for opcode, count in opcode_inventory.most_common():
        print(f"{opcode}: {count}")

if __name__ == "__main__":
    main()
