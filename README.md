# PGARA: Phase 1 Implementation

This repository contains the Phase 1 implementation of PGARA (Profiling-Guided Adaptive Register Allocation). Phase 1 establishes the deterministic baseline, providing foundational compiler analysis required for structural optimization, strictly omitting profiling, heat-maps, and allocation decisions (which are deferred to Phases 2 and 3).

## What Phase 1 Does
- **IR Generation**: Compiles C code into LLVM IR (without optimizations using `-O0` and `-disable-O0-optnone`) and runs `mem2reg` to promote stack variables to SSA form.
- **Line-based IR Parsing**: Parses the resulting `.mem2reg.ll` LLVM IR text deterministically using a handwritten parser. No dependency on `llvmlite` or Python LLVM bindings.
- **CFG Construction**: Builds the precise Control Flow Graph containing basic blocks, terminator instructions, and explicit successor/predecessor edges.
- **Loop Analysis**: Computes reachability and strict dominator trees to deduce structural back-edges and construct natural loop bodies, assigning block loop-nesting depths deterministically.
- **Liveness Analysis**: Computes rigorous backwards data-flow fixed-points (using Post-Order traversal for rapid convergence), maintaining exact LLVM phi semantics (values are live-out to specific incoming edges, not unconditionally live-in).
- **Interference Graph Construction**: Calculates a strict conflict graph (no move exemptions). It walks liveness sets instruction-by-instruction backwards and treats phi groupings properly to synthesize precise per-block register pressure data (highest number of simultaneously live virtual registers).
- **Comprehensive Validation**: Every analysis incorporates an independent path-based Oracle solver that validates the dataflow equations programmatically across every function and block, guaranteeing pristine mathematical correctness.

## Phase 1 Pipeline

```text
  C benchmark
      ↓
  Clang LLVM IR
      ↓
  mem2reg
      ↓
  Custom LLVM IR Parser
      ↓
  CFG
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
The project validates on eight specific benchmarks, designed to expose varying control flow complexity:
1. `b1_straight_line.c`: Pure sequential operations without branches.
2. `b2_array_sum.c`: A single flat array accumulation loop.
3. `b3_nested_loop.c`: Matrix operations testing depth/back-edges.
4. `b4_recursive.c`: Factorial/Fibonacci style recursive call logic.
5. `b5_rare_error.c`: Loop containing an extremely rare error condition branch.
6. `b6_early_exit.c`: Loop exhibiting sudden termination/break.
7. `b7_switch_heavy.c`: High degree out-edge blocks modelling skewed path probabilities.
8. `b8_scanner.c`: Emulates string token scanning with data-dependent transitions.

## Installation & Requirements

### Dependencies
- Python 3.8+
- [NetworkX](https://networkx.org/) (`pip install networkx`)
- [pytest](https://docs.pytest.org/) (`pip install pytest`)
- Clang & LLVM `opt` 

You can install Python dependencies securely using:
```bash
pip install -r requirements.txt
```

### LLVM Path Configuration
The system executes absolute paths pointing to `clang` and `opt` binaries (configured at the top of `run_phase1.py` and `generate_ir.py`). Modify the `CLANG` and `OPT` variables inside `run_phase1.py` to point to your LLVM `bin` directory before executing.

## Running the Driver

The end-to-end integration driver automatically extracts all Phase 1 C benchmarks, generates IR, parses them, constructs all structural CFG dependencies, and executes analyses. 

```bash
python run_phase1.py
```

### Outputs
The driver generates execution logs sequentially to the console and outputs deterministic serialized metadata for every function inside the directory:
```
results/raw/phase1/<benchmark_name>.report.json
```
These JSON files strictly track structural metadata: CFG paths, block depths, phi edges, pressure maps, and live sets per instruction boundary.

## Running the Tests

The repository is built strictly around PyTest with extensive integration logic against independent oracles and determinism matrices.

```bash
python -m pytest -v -s
```

## Proposal Decisions (D1-D7) Implemented

Phase 1 strictly respects the proposal boundaries:
- **D1 (Register Pressure)**: Captured intrinsically by evaluating the local maximum intersection of live intervals directly from liveness backward-walking graph.
- **D3 (Nodes)**: Extracts strictly local virtual registers (arguments and instruction outputs), filtering unallocatable constants and global labels.
- **D4 (Export)**: Can cleanly generate native textual `DOT` export scripts natively (no external `GraphViz` dependencies) for human inspection.
- **D6 (Phis)**: Simulated simultaneously as an integrated group execution boundary to perfectly prevent artificial structural anomalies inside the interference graph without polluting live-sets incorrectly.
- **D7 (Loop Nesting Depth)**: Computed formally using standard graph-reachability Dominator derivations.

## Known Limitations & Not in Phase 1
- **Supported IR Opcodes**: The handwritten line parser accurately filters opcodes explicitly used by `-O0 -mem2reg` benchmarks (e.g. `br`, `add`, `switch`, `phi`, etc). Vast architectures of LLVM IR unexposed to these minimal benchmarks might be ignored.
- **Irreducible CFGs**: Validated mathematically, but all LLVM Clang output produces reducible loops.
- **Function Boundary Context**: Liveness and interference do NOT calculate inter-procedural values (IPO). They evaluate strictly inside the context of a single Function. 

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
