# PGARA: Phase 1 Implementation

This repository contains the Phase 1 implementation of PGARA (Profile-Guided Adaptive Register Allocation). Phase 1 establishes the deterministic baseline, providing foundational compiler analysis required for structural optimization, strictly omitting profiling, heat-maps, and allocation decisions (which are deferred to Phases 2 and 3).

## What Phase 1 Does
- **IR Generation**: Compiles C code into LLVM IR (using `-O0 -Xclang -disable-O0-optnone`) and runs `mem2reg` to promote stack allocations to SSA register form.
- **Line-based IR Parsing**: Parses the resulting `.mem2reg.ll` LLVM IR text deterministically using a custom handwritten parser. No dependency on `llvmlite` or Python LLVM bindings.
- **CFG Construction**: Builds the control flow graph containing basic blocks, terminator instructions, and explicit predecessor and successor edges.
- **Loop Analysis**: Computes reachability and strict dominator trees to identify back-edges, merges natural loops sharing a header, and assigns block loop-nesting depths deterministically.
- **Liveness Analysis**: Computes backwards data-flow fixed points (using post-order traversal for rapid convergence; dump_liveness prints in reverse postorder for readability), maintaining exact LLVM phi semantics (values are live-out to specific incoming edges, not unconditionally live-in).
- **Interference Graph Construction**: Calculates a conflict graph (no move exemptions). It walks liveness sets instruction-by-instruction backwards and treats phi groupings simultaneously to synthesize per-block register pressure data (highest number of simultaneously live virtual registers).
- **Comprehensive Validation**: Every analysis is validated against path-based Oracle solvers across 9 functions and 60 basic blocks, tested with automated test suites.

## Phase 1 Pipeline

```text
  C benchmark
      ↓
  Clang LLVM IR (-O0 -disable-O0-optnone)
      ↓
  opt (mem2reg)
      ↓
  Custom LLVM IR Parser
      ↓
  CFG Construction
      ↓
  Dominator / Loop Analysis
      ↓
  Liveness Analysis
      ↓
  Interference Graph
      ↓
  Register Pressure
      ↓
  Phase 1 JSON Reports
```

## Benchmark Suite
The project validates on eight specific benchmarks designed to expose varying control flow complexity:
1. `b1_straight_line.c`: Pure sequential operations without branches.
2. `b2_array_sum.c`: A single flat array accumulation loop.
3. `b3_nested_loop.c`: Matrix operations testing depth and multiple back-edges.
4. `b4_recursive.c`: Factorial/Fibonacci style recursive call logic.
5. `b5_rare_error.c`: Loop containing an extremely rare error condition branch.
6. `b6_early_exit.c`: Loop exhibiting sudden termination and break.
7. `b7_switch_heavy.c`: High degree out-edge blocks modeling skewed path probabilities.
8. `b8_scanner.c`: String token scanning with data-dependent transitions.

## Where Files Live
- `results/raw/ir/`: **Source of truth for the test suite**. Committed `.raw.ll` and `.mem2reg.ll` IR files live here; unit tests and oracle tests read from these files directly.
- `results/raw/phase1/`: **Driver output directory**. When `python run_phase1.py` executes, generated IR files (`*.raw.ll`, `*.mem2reg.ll`), analysis reports (`*.report.json`), and DOT graphs (`*.dot`) are written here.
- `benchmarks/*.ll`: Earlier exploration artifacts. They are not referenced by any test, tool, or driver code (all tests read from `results/raw/ir/`), but are retained in the repository for historical reference.

## Installation & Requirements

### Dependencies
- Python 3.13 or 3.14 (tested and verified)
- [NetworkX](https://networkx.org/) (`pip install networkx`)
- [pytest](https://docs.pytest.org/) (`pip install pytest`)
- Clang & LLVM `opt`

Install Python dependencies with:
```bash
pip install -r requirements.txt
```

### LLVM Toolchain Configuration
The driver locates `clang` and `opt` binaries using the following priority order:
1. **Command-line flags**: `--clang <path>` and `--opt <path>` passed to `run_phase1.py`.
2. **Environment variables**: `PGARA_CLANG` and `PGARA_OPT`.
3. **System PATH**: standard `clang` and `opt` executables discovered via `shutil.which`.

For example, to configure paths via environment variables in PowerShell:
```powershell
$env:PGARA_OPT="C:\LLVM-23.1.3\clang+llvm-23.1.3-x86_64-pc-windows-msvc\bin\opt.exe"
```
Or pass them directly via the CLI:
```bash
python run_phase1.py --opt "C:\path\to\opt.exe" --clang "C:\path\to\clang.exe"
```

## Running the Driver

The end-to-end integration driver compiles benchmarks, generates IR, parses them, runs all Phase 1 analyses, and writes JSON reports and optional DOT graphs:

```bash
python run_phase1.py
```

### Real Output (Default Run)
```text
clang: C:\Program Files\LLVM\bin\clang.EXE (clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc))
opt  : C:\LLVM-23.1.3\clang+llvm-23.1.3-x86_64-pc-windows-msvc\bin\opt.exe (LLVM version 23.1.3)
Benchmark            | Funcs | Blocks | Back-Edges | Max Depth | IG Nodes | IG Edges | Max Pressure
-----------------------------------------------------------------------------------------------
b1_straight_line     | 1     | 1      | 0          | 0         | 11       | 21       | 4           
b2_array_sum         | 1     | 5      | 1          | 1         | 10       | 28       | 5           
b3_nested_loop       | 1     | 13     | 3          | 3         | 30       | 191      | 10          
b4_recursive         | 1     | 4      | 0          | 0         | 8        | 5        | 2           
b5_rare_error        | 2     | 8      | 1          | 1         | 20       | 71       | 6           
b6_early_exit        | 1     | 7      | 1          | 1         | 11       | 29       | 5           
b7_switch_heavy      | 1     | 10     | 0          | 0         | 12       | 4        | 3           
b8_scanner           | 1     | 12     | 1          | 1         | 25       | 85       | 6           
```

### Command-Line Interface (CLI)
`run_phase1.py` provides a full command-line interface:

```text
python run_phase1.py [BENCHMARK ...] [--bench-dir DIR] [--out-dir DIR] [--clang PATH] [--opt PATH]
                     [--dump {cfg,loops,liveness,interference} ...] [--function NAME] [--dot] [--quiet]
```

#### CLI Help Output
Running `python run_phase1.py --help`:
```text
usage: run_phase1.py [-h] [--bench-dir BENCH_DIR] [--out-dir OUT_DIR]
                     [--clang CLANG] [--opt OPT]
                     [--dump {cfg,loops,liveness,interference} [{cfg,loops,liveness,interference} ...]]
                     [--function FUNCTION] [--dot] [--quiet]
                     [benchmarks ...]

PGARA Phase 1 Analysis Pipeline Driver

positional arguments:
  benchmarks            Optional benchmark name(s) to run (e.g. b3_nested_loop
                        or b3_nested_loop.c). If omitted, all benchmarks are
                        run.

options:
  -h, --help            show this help message and exit
  --bench-dir BENCH_DIR
                        Directory containing benchmark .c files (default:
                        benchmarks)
  --out-dir OUT_DIR     Output directory for generated IR, reports, and DOT
                        graphs (default: results/raw/phase1)
  --clang CLANG         Explicit path to clang executable
  --opt OPT             Explicit path to opt executable
  --dump {cfg,loops,liveness,interference} [{cfg,loops,liveness,interference} ...]
                        Dump internal analysis representations to stdout
  --function FUNCTION   Filter analysis/dumps/dot to a specific function name
  --dot                 Export interference graph to <out-
                        dir>/<benchmark>.<function>.dot
  --quiet               Suppress startup toolchain info and summary table
```

#### CLI Example: Dumping Liveness to stdout
Running `python run_phase1.py b2_array_sum --dump liveness`:
```text
Function: sum_array
  Block: <implicit_entry>
    use:      []
    def:      [%0, %1]
    live_in:  []
    live_out: [%0, %1]
  Block: 3
    use:      [%0]
    def:      [%.0, %.01, %4]
    live_in:  [%0, %1]
    live_out: [%.0, %.01, %0, %1]
  Block: 5
    use:      [%.0, %.01, %1]
    def:      [%6, %7, %8, %9]
    live_in:  [%.0, %.01, %0, %1]
    live_out: [%.0, %0, %1, %9]
  Block: 10
    use:      [%.0]
    def:      [%11]
    live_in:  [%.0, %0, %1, %9]
    live_out: [%0, %1, %11, %9]
  Block: 12
    use:      [%.01]
    def:      []
    live_in:  [%.01]
    live_out: []
```

### JSON Report Structure
Reports are saved to `results/raw/phase1/<benchmark>.report.json` with deterministic sorted keys. Liveness sets are recorded per basic block (`live_in` and `live_out`):

```json
{
  "benchmark": "b1_straight_line",
  "functions": [
    {
      "back_edges": [],
      "blocks": [
        {
          "label": "<implicit_entry>",
          "live_in": [],
          "live_out": [],
          "loop_depth": 0,
          "pressure": 4
        }
      ],
      "edges": [],
      "interference": {
        "edge_count": 21,
        "max_pressure": 4,
        "node_count": 11
      },
      "is_irreducible": false,
      "name": "compute_arithmetic",
      "unreachable_blocks": []
    }
  ],
  "schema_version": 1
}
```

Top-level fields:
- `benchmark`: Benchmark name (string).
- `schema_version`: Schema version integer (`1`).
- `functions`: List of analyzed function objects.

Function fields:
- `name`: Function identifier string.
- `is_irreducible`: Boolean flag indicating whether the CFG contains irreducible loops.
- `unreachable_blocks`: Sorted list of labels for unreachable basic blocks.
- `edges`: List of directed CFG edges (`"src->dst"`).
- `back_edges`: List of loop back-edges (`"src->dst"`).
- `blocks`: List of basic block records containing `label`, `loop_depth`, `pressure`, `live_in` (sorted virtual register names), and `live_out` (sorted virtual register names).
- `interference`: Graph summary containing `node_count`, `edge_count`, and function-wide `max_pressure`.

## Running the Tests

The repository test suite is executed using `pytest`:

```bash
python -m pytest -v -s
```

All 51 tests execute deterministically against the committed IR and independent programmatic oracles.

## Proposal Decisions (D1-D8) Implemented

Phase 1 strictly respects the proposal boundaries:
- **D1 (Register Pressure Definition)**: Register pressure is defined as the maximum number of simultaneously live virtual registers at any point in a basic block, including at block entry and exit. Dead definitions (instructions whose results are never subsequently used) interfere with all variables live at their point of definition, but are not counted in register pressure at that definition point.
- **D2 (IR Generation Recipe)**: `clang -O0 -S -emit-llvm -Xclang -disable-O0-optnone` followed by `opt -passes=mem2reg -S`. The `-Xclang -disable-O0-optnone` flag is required because Clang attaches the `optnone` function attribute by default under `-O0`, which causes `opt`'s `mem2reg` pass to skip the function entirely without promoting stack allocas to SSA registers.
- **D3 (Nodes)**: Nodes in the interference graph correspond strictly to allocatable virtual registers (function arguments and instruction results). Constants, immediate values, and global labels are excluded.
- **D4 (DOT Export)**: Native textual DOT export via `src.analysis.interference.export_dot` without external Graphviz dependencies. Can be invoked from the CLI using `--dot`, writing `<out-dir>/<benchmark>.<function>.dot`.
- **D5 (Language & Graph Library)**: Implemented in Python (verified on Python 3.13 and 3.14) using [NetworkX](https://networkx.org/) for interference graph modeling.
- **D6 (Simultaneous Phi Semantics)**: The phi results defined at the top of a block are defined simultaneously, so they interfere with each other and with every other value live at that point.
- **D7 (Dominator-Based Loop Analysis & Nesting Depth)**: Loops and back-edges are identified using dominator tree analysis. Back-edges $(u \to v)$ are detected where $v$ dominates $u$. Loops sharing the same header block are merged into natural loops, and hierarchical loop nesting depth is assigned deterministically to each basic block.
- **D8 (Function Argument Interference at Entry)**: All function arguments are treated as simultaneously live and interfering with each other at function entry, even if an argument is unused in the body. This is a deliberate conservative design choice ensuring all incoming parameters are allocated distinct physical locations at entry.

## Reproducibility

- **Report Determinism**: Report JSON files and DOT graphs are byte-identical across runs for the same LLVM version.
- **LLVM Version Sensitivity**: Phi register names generated in LLVM IR depend on the LLVM compiler version (for example, an independent run with LLVM 18 produced the identical structural CFG and graph topology but different phi variable names in `b8_scanner`, such as `%.13` vs `%.24`). Consequently, report files are guaranteed byte-identical when run with the same LLVM version.
- **Committed IR Toolchain**: The committed IR in `results/raw/ir/` was generated using Clang/LLVM 23.1.3 on `x86_64-pc-windows-msvc`.

## Known Limitations & Not in Phase 1

- **Supported IR Opcodes**: The handwritten parser supports only the opcodes cataloged in `docs/OPCODE_INVENTORY.txt` (the opcodes emitted by Clang `-O0` and `mem2reg` on the benchmark suite). Unsupported opcodes trigger a clear `ParseError`.
- **Define-Line Argument Parsing**: Function argument parsing on `define` lines handles standard scalar and pointer parameters used by the benchmark suite; complex function signatures (e.g. varargs, complex struct byval) are not handled.
- **Single Function Scope**: Liveness and interference analyses operate strictly per function; inter-procedural optimization (IPO) and whole-program live ranges are out of scope.
- **Irreducible CFGs**: Handled by detection (`is_irreducible` flag set in report), but all Clang-generated benchmark loops are reducible.

### EXPLICITLY Not in Phase 1 (Deferred to Phase 2 & 3)
Phase 1 intentionally does NOT implement:
- profiling
- execution frequencies
- weights
- heat
- spill costs
- register allocation
- coloring
- coalescing
- adaptive allocation
