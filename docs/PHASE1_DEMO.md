# PGARA Phase 1: Faculty Demonstration Script

This document provides a 10-minute demonstration script for showcasing the Phase 1 static analysis pipeline to faculty using only the existing command-line interface.

Phase 1 establishes the deterministic compiler analysis foundation: LLVM IR parsing, CFG construction, dominator-based loop analysis, backwards dataflow liveness analysis, interference graph construction, and register pressure estimation. Phase 1 intentionally contains **no execution profiling**, **no cost model**, and **no register allocation** (which are deferred to Phases 2 and 3).

---

## 1. Setup

Run this single setup block from the terminal:

```bash
git clone https://github.com/kamran2908/pgara.git
cd pgara
pip install -r requirements.txt
python tools/verify_checksums.py
python -m pytest -q
```

Expected setup verification output:
```
OK: all 80 checksums match committed content.
```
```
...................................................                      [100%]
51 passed in 3.23s
```

---

## 2. Demo Flow

### Step 2a: CFG Construction on Straight-Line Code
- **Command**:
  ```bash
  python run_phase1.py b1_straight_line --dump cfg
  ```
- **What faculty should see**: A single basic block (`<implicit_entry>`) with no predecessors and no successors (`succ:[none] (pred:[none])`).
- **What it proves**: Proves that straight-line code with no branching is parsed into a minimal single-block control flow graph with explicit boundary termination.
- **Actual Output**:
```
Function: compute_arithmetic
  Block: <implicit_entry> -> succ:[none] (pred:[none])
```

---

### Step 2b: Single Loop and Dominator Back-Edge Detection
- **Command**:
  ```bash
  python run_phase1.py b2_array_sum --dump loops
  ```
- **What faculty should see**: Exactly one back-edge (`10->3`), a natural loop with header block `3` and body `[10, 3, 5]`, and loop nesting depth 1 for blocks in the loop while entry and exit blocks have depth 0.
- **What it proves**: Proves dominator tree analysis correctly identifies back-edges $(u \to v)$ where $v$ dominates $u$ and computes structural block depths.
- **Actual Output**:
```
Function: sum_array
  Back-edges: [10->3]
  Loop 3: body=[10, 3, 5]
  Block 10: depth=1
  Block 12: depth=0
  Block 3: depth=1
  Block 5: depth=1
  Block <implicit_entry>: depth=0
```

---

### Step 2c: Deeply Nested Multi-Level Loops
- **Command**:
  ```bash
  python run_phase1.py b3_nested_loop --dump loops
  ```
- **What faculty should see**: Three detected back-edges (`26->11`, `33->8`, `36->5`), three nested natural loops, and hierarchical loop nesting depths from depth 0 up to depth 3 (`Block 11: depth=3`, `Block 13: depth=3`, `Block 26: depth=3`).
- **What it proves**: Proves dominator-based loop analysis accurately discovers deeply nested loops and properly assigns multi-level nesting depths.
- **Actual Output**:
```
Function: matrix_multiply
  Back-edges: [26->11, 33->8, 36->5]
  Loop 11: body=[11, 13, 26]
  Loop 5: body=[10, 11, 13, 26, 28, 33, 35, 36, 5, 7, 8]
  Loop 8: body=[10, 11, 13, 26, 28, 33, 8]
  Block 10: depth=2
  Block 11: depth=3
  Block 13: depth=3
  Block 26: depth=3
  Block 28: depth=2
  Block 33: depth=2
  Block 35: depth=1
  Block 36: depth=1
  Block 38: depth=0
  Block 5: depth=1
  Block 7: depth=1
  Block 8: depth=2
  Block <implicit_entry>: depth=0
```

---

### Step 2d: Backwards Dataflow Liveness and SSA Phi Semantics
- **Command**:
  ```bash
  python run_phase1.py b3_nested_loop --dump liveness --function matrix_multiply
  ```
- **What faculty should see**: Per-block `use`, `def`, `live_in`, and `live_out` variable sets, demonstrating that phi operands are live-out of their specific incoming predecessor blocks rather than unconditionally live-in to the loop header.
- **What it proves**: Proves backwards fixed-point dataflow analysis accurately resolves live intervals and enforces LLVM SSA edge-specific phi semantics.
- **Actual Output**:
```
Function: matrix_multiply
  Block: <implicit_entry>
    use:      []
    def:      [%0, %1, %2, %3]
    live_in:  []
    live_out: [%0, %1, %2, %3]
  Block: 5
    use:      [%0]
    def:      [%.03, %6]
    live_in:  [%0, %1, %2, %3]
    live_out: [%.03, %0, %1, %2, %3]
  Block: 7
    use:      []
    def:      []
    live_in:  [%.03, %0, %1, %2, %3]
    live_out: [%.03, %0, %1, %2, %3]
  Block: 8
    use:      [%0]
    def:      [%.02, %9]
    live_in:  [%.03, %0, %1, %2, %3]
    live_out: [%.02, %.03, %0, %1, %2, %3]
  Block: 35
    use:      []
    def:      []
    live_in:  [%.03, %0, %1, %2, %3]
    live_out: [%.03, %0, %1, %2, %3]
  Block: 36
    use:      [%.03]
    def:      [%37]
    live_in:  [%.03, %0, %1, %2, %3]
    live_out: [%0, %1, %2, %3, %37]
  Block: 10
    use:      []
    def:      []
    live_in:  [%.02, %.03, %0, %1, %2, %3]
    live_out: [%.02, %.03, %0, %1, %2, %3]
  Block: 11
    use:      [%0]
    def:      [%.0, %.01, %12]
    live_in:  [%.02, %.03, %0, %1, %2, %3]
    live_out: [%.0, %.01, %.02, %.03, %0, %1, %2, %3]
  Block: 28
    use:      [%.01, %.02, %.03, %0, %3]
    def:      [%29, %30, %31, %32]
    live_in:  [%.01, %.02, %.03, %0, %1, %2, %3]
    live_out: [%.02, %.03, %0, %1, %2, %3]
  Block: 33
    use:      [%.02]
    def:      [%34]
    live_in:  [%.02, %.03, %0, %1, %2, %3]
    live_out: [%.03, %0, %1, %2, %3, %34]
  Block: 13
    use:      [%.0, %.01, %.02, %.03, %0, %1, %2]
    def:      [%14, %15, %16, %17, %18, %19, %20, %21, %22, %23, %24, %25]
    live_in:  [%.0, %.01, %.02, %.03, %0, %1, %2, %3]
    live_out: [%.0, %.02, %.03, %0, %1, %2, %25, %3]
  Block: 26
    use:      [%.0]
    def:      [%27]
    live_in:  [%.0, %.02, %.03, %0, %1, %2, %25, %3]
    live_out: [%.02, %.03, %0, %1, %2, %25, %27, %3]
  Block: 38
    use:      []
    def:      []
    live_in:  []
    live_out: []
```

---

### Step 2e: Interference Graph Construction and Register Pressure
- **Command**:
  ```bash
  python run_phase1.py b3_nested_loop --dump interference --function matrix_multiply
  ```
- **What faculty should see**: Graph topology metrics (30 nodes, 191 conflict edges, maximum register pressure 10), node conflict degrees, edge pairs, and per-block peak pressures.
- **What it proves**: Proves simultaneous phi resolution and instruction-by-instruction backward live range traversal synthesize exact conflict graphs and detect peak register pressure.
- **Actual Output**:
```
Function: matrix_multiply
  Max Pressure: 10
  Nodes & Degrees:
    %.0: 20
    %.01: 23
    %.02: 26
    %.03: 28
    %0: 29
    %1: 29
    %12: 8
    %14: 8
    %15: 8
    %16: 8
    %17: 8
    %18: 13
    %19: 9
    %2: 29
    %20: 9
    %21: 9
    %22: 9
    %23: 9
    %24: 8
    %25: 8
    %27: 7
    %29: 7
    %3: 29
    %30: 7
    %31: 7
    %32: 7
    %34: 5
    %37: 4
    %6: 5
    %9: 6
  Edges:
    %.0 -- %.01
    %.0 -- %.02
    %.0 -- %.03
    %.0 -- %0
    %.0 -- %1
    %.0 -- %12
    %.0 -- %14
    %.0 -- %15
    %.0 -- %16
    %.0 -- %17
    %.0 -- %18
    %.0 -- %19
    %.0 -- %2
    %.0 -- %20
    %.0 -- %21
    %.0 -- %22
    %.0 -- %23
    %.0 -- %24
    %.0 -- %25
    %.0 -- %3
    %.01 -- %.02
    %.01 -- %.03
    %.01 -- %0
    %.01 -- %1
    %.01 -- %12
    %.01 -- %14
    %.01 -- %15
    %.01 -- %16
    %.01 -- %17
    %.01 -- %18
    %.01 -- %19
    %.01 -- %2
    %.01 -- %20
    %.01 -- %21
    %.01 -- %22
    %.01 -- %23
    %.01 -- %24
    %.01 -- %29
    %.01 -- %3
    %.01 -- %30
    %.01 -- %31
    %.01 -- %32
    %.02 -- %.03
    %.02 -- %0
    %.02 -- %1
    %.02 -- %12
    %.02 -- %14
    %.02 -- %15
    %.02 -- %16
    %.02 -- %17
    %.02 -- %18
    %.02 -- %19
    %.02 -- %2
    %.02 -- %20
    %.02 -- %21
    %.02 -- %22
    %.02 -- %23
    %.02 -- %24
    %.02 -- %25
    %.02 -- %27
    %.02 -- %29
    %.02 -- %3
    %.02 -- %30
    %.02 -- %31
    %.02 -- %32
    %.02 -- %9
    %.03 -- %0
    %.03 -- %1
    %.03 -- %12
    %.03 -- %14
    %.03 -- %15
    %.03 -- %16
    %.03 -- %17
    %.03 -- %18
    %.03 -- %19
    %.03 -- %2
    %.03 -- %20
    %.03 -- %21
    %.03 -- %22
    %.03 -- %23
    %.03 -- %24
    %.03 -- %25
    %.03 -- %27
    %.03 -- %29
    %.03 -- %3
    %.03 -- %30
    %.03 -- %31
    %.03 -- %32
    %.03 -- %34
    %.03 -- %6
    %.03 -- %9
    %0 -- %1
    %0 -- %12
    %0 -- %14
    %0 -- %15
    %0 -- %16
    %0 -- %17
    %0 -- %18
    %0 -- %19
    %0 -- %2
    %0 -- %20
    %0 -- %21
    %0 -- %22
    %0 -- %23
    %0 -- %24
    %0 -- %25
    %0 -- %27
    %0 -- %29
    %0 -- %3
    %0 -- %30
    %0 -- %31
    %0 -- %32
    %0 -- %34
    %0 -- %37
    %0 -- %6
    %0 -- %9
    %1 -- %12
    %1 -- %14
    %1 -- %15
    %1 -- %16
    %1 -- %17
    %1 -- %18
    %1 -- %19
    %1 -- %2
    %1 -- %20
    %1 -- %21
    %1 -- %22
    %1 -- %23
    %1 -- %24
    %1 -- %25
    %1 -- %27
    %1 -- %29
    %1 -- %3
    %1 -- %30
    %1 -- %31
    %1 -- %32
    %1 -- %34
    %1 -- %37
    %1 -- %6
    %1 -- %9
    %12 -- %2
    %12 -- %3
    %14 -- %2
    %14 -- %3
    %15 -- %2
    %15 -- %3
    %16 -- %2
    %16 -- %3
    %17 -- %2
    %17 -- %3
    %18 -- %19
    %18 -- %2
    %18 -- %20
    %18 -- %21
    %18 -- %22
    %18 -- %23
    %18 -- %3
    %19 -- %2
    %19 -- %3
    %2 -- %20
    %2 -- %21
    %2 -- %22
    %2 -- %23
    %2 -- %24
    %2 -- %25
    %2 -- %27
    %2 -- %29
    %2 -- %3
    %2 -- %30
    %2 -- %31
    %2 -- %32
    %2 -- %34
    %2 -- %37
    %2 -- %6
    %2 -- %9
    %20 -- %3
    %21 -- %3
    %22 -- %3
    %23 -- %3
    %24 -- %3
    %25 -- %27
    %25 -- %3
    %27 -- %3
    %29 -- %3
    %3 -- %30
    %3 -- %31
    %3 -- %32
    %3 -- %34
    %3 -- %37
    %3 -- %6
    %3 -- %9
  Block Pressures:
    Block 10: max=6, |live_in|=6, |live_out|=6
    Block 11: max=9, |live_in|=6, |live_out|=8
    Block 13: max=10, |live_in|=8, |live_out|=8
    Block 26: max=8, |live_in|=8, |live_out|=8
    Block 28: max=8, |live_in|=7, |live_out|=6
    Block 33: max=6, |live_in|=6, |live_out|=6
    Block 35: max=5, |live_in|=5, |live_out|=5
    Block 36: max=5, |live_in|=5, |live_out|=5
    Block 38: max=0, |live_in|=0, |live_out|=0
    Block 5: max=6, |live_in|=4, |live_out|=5
    Block 7: max=5, |live_in|=5, |live_out|=5
    Block 8: max=7, |live_in|=5, |live_out|=6
    Block <implicit_entry>: max=4, |live_in|=0, |live_out|=4
```

---

### Step 2f: Standalone DOT Graph Export
- **Command**:
  ```bash
  python run_phase1.py b3_nested_loop --dot --out-dir demo_out
  ```
- **What faculty should see**: CLI summary table and the generated DOT file `demo_out/b3_nested_loop.matrix_multiply.dot`. *(Note: The DOT graph can optionally be rendered with Graphviz if installed via `dot -Tpng demo_out/b3_nested_loop.matrix_multiply.dot -o ig.png`, but Graphviz is not required).*
- **What it proves**: Proves native textual DOT export (D4) generates visualization-ready conflict graphs without external Graphviz binary dependencies.
- **Actual Output**:
```
clang: C:\Program Files\LLVM\bin\clang.EXE (clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc))
opt  : C:\LLVM-23.1.3\clang+llvm-23.1.3-x86_64-pc-windows-msvc\bin\opt.exe (LLVM version 23.1.3)
Benchmark            | Funcs | Blocks | Back-Edges | Max Depth | IG Nodes | IG Edges | Max Pressure
-----------------------------------------------------------------------------------------------
b3_nested_loop       | 1     | 13     | 3          | 3         | 30       | 191      | 10
```

---

### Step 2g: Complete Benchmark Suite Processing and JSON Telemetry
- **Command**:
  ```bash
  python run_phase1.py --out-dir demo_out --quiet
  ```
- **What faculty should see**: Command exits silently with code 0 and populates `demo_out/` with `.report.json` telemetry files for all benchmarks. Showing `demo_out/b1_straight_line.report.json`:
- **What it proves**: Proves batch CLI processing across the entire benchmark suite produces deterministic, strictly typed schema version 1 JSON reports.
- **Actual Output (`demo_out/b1_straight_line.report.json`)**:
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

---

### Step 2h: Byte-Level Determinism Across Invocations
- **Command**:
  ```bash
  PYTHONHASHSEED=0 python run_phase1.py b3_nested_loop --dot --out-dir demo_out/seed0
  PYTHONHASHSEED=42 python run_phase1.py b3_nested_loop --dot --out-dir demo_out/seed42
  ```
- **What faculty should see**: SHA256 hashes of the resulting `.dot` files are byte-identical regardless of Python dictionary hash seed randomization.
- **What it proves**: Proves lexicographical sorting of nodes and undirected edges guarantees 100% deterministic, reproducible output.
- **Actual Output**:
```
PYTHONHASHSEED=0  hash: 633583B13C6F459210075463603997CC8D69781A68050C24CD0E1C395F120EDA
PYTHONHASHSEED=42 hash: 633583B13C6F459210075463603997CC8D69781A68050C24CD0E1C395F120EDA
Identical: True
```

---

## 3. Summary Table Across All 8 Benchmarks

The following table summarizes the structural analyses computed across the benchmark suite:

| Benchmark | Functions | Basic Blocks | Back-Edges | Max Depth | Nodes | Edges | Max Pressure |
|---|---|---|---|---|---|---|---|
| b1_straight_line | 1 | 1 | 0 | 0 | 11 | 21 | 4 |
| b2_array_sum | 1 | 5 | 1 | 1 | 10 | 28 | 5 |
| b3_nested_loop | 1 | 13 | 3 | 3 | 30 | 191 | 10 |
| b4_recursive | 1 | 4 | 0 | 0 | 8 | 5 | 2 |
| b5_rare_error | 2 | 8 | 1 | 1 | 20 | 71 | 6 |
| b6_early_exit | 1 | 7 | 1 | 1 | 11 | 29 | 5 |
| b7_switch_heavy | 1 | 10 | 0 | 0 | 12 | 4 | 3 |
| b8_scanner | 1 | 12 | 1 | 1 | 25 | 85 | 6 |

---

## 4. Likely Faculty Questions & Answers

1. **Why run `mem2reg` instead of analyzing unoptimized Clang IR directly?**
   - *Answer*: Unoptimized Clang IR (`-O0`) allocates every C local variable on the stack via `alloca`, reading with `load` and writing with `store`. This hides dataflow live ranges inside memory locations. Running `opt -passes=mem2reg` lifts allocas into SSA virtual registers and phi nodes, making true dataflow dependencies and live intervals visible for register allocation analysis (Decision D2).

2. **Why are phi operands live-out of predecessor blocks rather than unconditionally live-in to the phi block?**
   - *Answer*: In SSA form, each phi operand corresponds to a specific incoming control-flow edge. The value is only needed along that specific incoming transition. Treating it as live-in to the destination block would artificially inflate live ranges across other incoming edges where the value is neither used nor defined.

3. **Why do phi results defined at the top of a basic block interfere with each other?**
   - *Answer*: Phi instructions at the start of a block are defined simultaneously as a parallel group. Because their values come into existence at the exact same program point, they are concurrently live and therefore interfere with each other and with every other value live at that point (Decision D6).

4. **How are back-edges and loops discovered?**
   - *Answer*: Natural loops are detected using strict dominator tree analysis. A control flow edge $(u \to v)$ is classified as a back-edge if and only if the header node $v$ dominates the source node $u$. Loops that share the same header block are merged into natural loops, and hierarchical loop nesting depths are calculated deterministically (Decision D7).

5. **What does register pressure mean in this project?**
   - *Answer*: Register pressure is defined as the maximum number of simultaneously live virtual registers at any instruction point within a basic block, including at block entry and block exit (Decision D1). Dead definitions interfere at their definition point but are excluded from register pressure counts at that point.

6. **What does Phase 1 NOT do, and which phase will do it?**
   - *Answer*: Phase 1 is purely a static analysis baseline. It intentionally contains no profiling, branch weights, execution counts, or loop heat (deferred to Phase 2). It contains no spill costs, graph coloring, Chaitin-Briggs simplification, coalescing, or adaptive register allocation selection (deferred to Phase 3).

---

## 5. Known Limitations

- **Supported IR Opcodes**: The handwritten parser supports only the opcodes cataloged in `docs/OPCODE_INVENTORY.txt` (the opcodes emitted by Clang `-O0` and `mem2reg` on the benchmark suite). Unsupported opcodes trigger a clear `ParseError`.
- **Define-Line Argument Parsing**: Function argument parsing on `define` lines handles standard scalar and pointer parameters used by the benchmark suite; complex function signatures (e.g. varargs, complex struct byval) are not handled.
- **Single Function Scope**: Liveness and interference analyses operate strictly per function; inter-procedural optimization (IPO) and whole-program live ranges are out of scope.
- **Irreducible CFGs**: Handled by detection (`is_irreducible` flag set in report), but all Clang-generated benchmark loops are reducible.
