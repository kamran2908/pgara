# PGARA Phase 1 Audit Report

## 1. Scope and Method
- **Audit Baseline**: Commit `24fe349`
- **Frozen Code Commit**: Commit `f101dd2bcf72835d5ffb86ecb6a0e32753c582be`
- **Methodology**: Static inspection of code changes, comparative verification of 51 test cases across Python 3.13 and Python 3.14, independent Oracle solver validation across all 9 functions and 60 basic blocks, toolchain configuration testing across multiple platforms and paths, and verification of strict Phase 1 scope boundaries (excluding profiling, weights, heat, costs, coloring, spilling, and coalescing).

## 2. Defects Found and How Each Was Fixed
- **Fix 1 (`48c2bed`)**: Fixed missing `Tuple` typing import in `src/analysis/liveness.py`, verified execution on Python 3.13 and 3.14, removed tracked compiled bytecode (`.pyc`), and established `.gitignore`.
- **Fix 2 (`46b88f2`)**: Removed hardcoded Windows binary paths, implementing configurable toolchain discovery prioritizing CLI flags (`--clang`, `--opt`), environment variables (`PGARA_CLANG`, `PGARA_OPT`), and system `PATH` with clear exit codes.
- **Fix 3 (`4e2f8d3`)**: Replaced silent error handling in handwritten IR parser with explicit `ParseError` on unsupported opcodes, added `docs/OPCODE_INVENTORY.txt` and `tools/opcode_inventory.py`, and verified zero silent test skips with oracle tests.
- **Fix 4 (`b8dd6bb` / `fcee0a0`)**: Implemented standalone CLI `run_phase1.py` with benchmark selection, `--dump` (cfg, loops, liveness, interference) and `--dot` export, additive report fields (`schema_version`, `is_irreducible`, `unreachable_blocks`), and working-directory-independent test fixtures.
- **Fix 5 (`724f9b1` / `c3c91e7`)**: Corrected documentation discrepancies across `README.md` and `docs/PGARA_Phase1_Final_Report.md` (project name, Python 3.13/3.14, decisions D1–D8, toolchain priority, per-block report structure, reproducibility, and accurate LLVM opt version banner extraction).
- **Fix 6 (`6984957`)**: Generated full verifiable evidence directory (`evidence/`) and `PHASE1_FIX_REPORT.md` backing all claims with untruncated command execution artifacts.
- **Fix 7 (`f101dd2`)**: Enhanced test helper portability (`os.chmod(..., 0o755)` in `tests/test_toolchain.py`), clarified post-order fixpoint traversal, updated simultaneous phi semantics description, and aligned total test count to 51.

## 3. Justified Deviations
- **Deterministic DOT Export (`src/analysis/interference.py`)**: `export_dot` sorts both graph nodes and undirected edges lexicographically prior to printing. The original implementation traversed unordered NetworkX graph structures whose iteration order depended on Python's dictionary hash seeding (`PYTHONHASHSEED`), which caused non-deterministic DOT file text across process invocations.

## 4. Design Decisions (D1 to D8)
- **D1 (Register Pressure Definition)**: Register pressure is defined as the maximum number of simultaneously live virtual registers at any point in a basic block, including at block entry and exit. Dead definitions (instructions whose results are never subsequently used) interfere with all variables live at their point of definition, but are not counted in register pressure at that definition point.
- **D2 (IR Generation Recipe)**: `clang -O0 -S -emit-llvm -Xclang -disable-O0-optnone` followed by `opt -passes=mem2reg -S`. The `-Xclang -disable-O0-optnone` flag is required because Clang attaches the `optnone` function attribute by default under `-O0`, which causes `opt`'s `mem2reg` pass to skip the function entirely without promoting stack allocas to SSA registers.
- **D3 (Nodes)**: Nodes in the interference graph correspond strictly to allocatable virtual registers (function arguments and instruction results). Constants, immediate values, and global labels are excluded.
- **D4 (DOT Export)**: Native textual DOT export via `src.analysis.interference.export_dot` without external Graphviz dependencies. Can be invoked from the CLI using `--dot`, writing `<out-dir>/<benchmark>.<function>.dot`.
- **D5 (Language & Graph Library)**: Implemented in Python (verified on Python 3.13 and 3.14) using NetworkX for interference graph modeling.
- **D6 (Simultaneous Phi Semantics)**: The phi results defined at the top of a block are defined simultaneously, so they interfere with each other and with every other value live at that point.
- **D7 (Dominator-Based Loop Analysis & Nesting Depth)**: Loops and back-edges are identified using dominator tree analysis. Back-edges $(u \to v)$ are detected where $v$ dominates $u$. Loops sharing the same header block are merged into natural loops, and hierarchical loop nesting depth is assigned deterministically to each basic block.
- **D8 (Function Argument Interference at Entry)**: All function arguments are treated as simultaneously live and interfering with each other at function entry, even if an argument is unused in the body. This is a deliberate conservative design choice ensuring all incoming parameters are allocated distinct physical locations at entry.

## 5. Known Limitations
- **Supported IR Opcodes**: The handwritten parser supports only the opcodes cataloged in `docs/OPCODE_INVENTORY.txt` (the opcodes emitted by Clang `-O0` and `mem2reg` on the benchmark suite). Unsupported opcodes trigger a clear `ParseError`.
- **Define-Line Argument Parsing**: Function argument parsing on `define` lines handles standard scalar and pointer parameters used by the benchmark suite; complex function signatures (e.g. varargs, complex struct byval) are not handled.
- **Single Function Scope**: Liveness and interference analyses operate strictly per function; inter-procedural optimization (IPO) and whole-program live ranges are out of scope.
- **Irreducible CFGs**: Handled by detection (`is_irreducible` flag set in report), but all Clang-generated benchmark loops are reducible.

## 6. Reproduction Commands

```bash
# 1. Clone repository
git clone https://github.com/kamran2908/pgara.git
cd pgara

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run complete test suite
python -m pytest -v -s

# 4. Run CLI on all benchmarks
python run_phase1.py

# 5. Run CLI individually on each benchmark
python run_phase1.py b1_straight_line
python run_phase1.py b2_array_sum
python run_phase1.py b3_nested_loop
python run_phase1.py b4_recursive
python run_phase1.py b5_rare_error
python run_phase1.py b6_early_exit
python run_phase1.py b7_switch_heavy
python run_phase1.py b8_scanner
```
