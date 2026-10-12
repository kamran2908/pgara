# PGARA Phase 1 Final Report

## 1. Project Objective
PGARA (Profile-Guided Adaptive Register Allocation) explores a hybrid graph-coloring register allocator driven by runtime execution profiles rather than purely static heuristics. Phase 1 provides the structural baseline for this allocator.

## 2. Phase 1 Scope
Phase 1 focuses entirely on the static analysis foundation. It encompasses IR generation, custom line-based parsing, CFG construction, loop analysis, liveness analysis, and interference graph mapping.

## 3. Architecture/Pipeline
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

## 4. Benchmark Suite
Phase 1 integrates eight core benchmark programs:
1. `b1_straight_line.c`
2. `b2_array_sum.c`
3. `b3_nested_loop.c`
4. `b4_recursive.c`
5. `b5_rare_error.c`
6. `b6_early_exit.c`
7. `b7_switch_heavy.c`
8. `b8_scanner.c`

## 5. LLVM IR Generation
Benchmarks are compiled via `clang -O0 -S -emit-llvm -Xclang -disable-O0-optnone`. The `-Xclang -disable-O0-optnone` flag is required because Clang attaches the `optnone` attribute to functions by default under `-O0`, which causes `opt` to skip the function without optimizing. Standard `opt -passes=mem2reg -S` is then executed to promote stack allocas into SSA registers.

## 6. Custom Parser
IR parsing handles the `.ll` text natively without `llvmlite` or Python LLVM bindings. It implements a strict class hierarchy: `Value`, `Instruction`, `BasicBlock`, `Function`, preserving textual identifiers.

## 7. CFG Construction
The CFG links basic blocks accurately by inspecting terminator instructions (`br`, `switch`, `ret`) and constructing bi-directional predecessor and successor relationships.

## 8. Loop Analysis
Employs standard strict dominator trees to identify back-edges reliably, merges natural loops sharing a header block, and assigns exact structural nesting depths per block.

## 9. Liveness Analysis
A backwards post-order dataflow fixpoint analyzer computes `live_in` and `live_out` sets per block, respecting exact semantics for `phi` nodes across edges (values are live-out to specific incoming edges, not unconditionally live-in).

## 10. Interference Graph
Generates conflict graphs mapping concurrently active live values (instruction definitions mapped backward across live intervals). Accommodates simultaneous `phi` resolution groups at block entries. All function arguments interfere with each other at function entry.

## 11. Register Pressure
Block-level metrics measure peak concurrency across intervals to determine register pressure dynamically. Dead definitions interfere at their definition point but are not counted in register pressure.

## 12. Testing and Verification
The test suite consists of 50 Pytest test executions passing with 0 skips across Python 3.13 and Python 3.14. Liveness and interference analyses were compared against programmatic path-based oracles across 9 functions and 60 basic blocks spanning all 8 benchmarks. Note that these oracles reuse `LivenessAnalyzer.get_llvm_label()` and `Instruction.uses()` from the core infrastructure, so they are not completely independent implementations.

## 13. Determinism and Reproducibility
Reports are byte-identical across runs when executed with the same LLVM compiler version. Phi register names in the generated IR depend on the LLVM version (for example, LLVM 18 produces different phi variable names than LLVM 23 in `b8_scanner`, though graph structure remains identical). Output files strictly conform to `results/raw/phase1/`.

## 14. Phase 1 Benchmark Summary
All eight benchmarks pass execution end-to-end, producing strictly typed JSON telemetry accurately capturing CFG layout, loops, nodes, edges, and register pressure caps.

## 15. Known Limitations
- **Supported Opcodes**: The handwritten parser supports only the opcodes cataloged in `docs/OPCODE_INVENTORY.txt` (the set emitted by `-O0 -mem2reg` on the benchmark suite). Unsupported opcodes raise a `ParseError`.
- **Define-Line Argument Parsing**: Function argument parsing on `define` lines is simplistic, handling scalar and pointer parameters used in the benchmarks, but not varargs or complex struct parameters.
- **Single Function Scope**: Liveness and interference analyses operate strictly per function; inter-procedural analysis (IPO) is out of scope.
- **Irreducible CFGs**: Detected via the `is_irreducible` report field, but all Clang-generated benchmark loops are reducible.

## 16. Explicit Phase 2/3 Boundary
Phase 1 does NOT implement:
- profiling
- llvm-profdata
- profile.json
- execution frequency
- block frequency
- block weights
- heat
- spill cost
- spill simulation
- Chaitin-Briggs
- graph coloring
- simplify/spill/select
- coalescing
- adaptive allocator selection
- LLVM allocator comparison

## 17. Final Phase 1 Status
**FROZEN AND COMPLETE.**
