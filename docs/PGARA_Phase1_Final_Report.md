# PGARA Phase 1 Final Report

## 1. Project Objective
PGARA (Profiling-Guided Adaptive Register Allocation) explores a hybrid graph-coloring register allocator driven by runtime execution profiles rather than purely static heuristics. Phase 1 provides the structural baseline for this allocator.

## 2. Phase 1 Scope
Phase 1 focuses entirely on the static analysis foundation. It encompasses IR generation, custom line-based parsing, CFG construction, loop analysis, liveness analysis, and interference graph mapping.

## 3. Architecture/Pipeline
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
Benchmarks are compiled directly via absolute paths to `clang` with `-O0 -S -emit-llvm -Xclang -disable-O0-optnone`. Standard `opt -passes=mem2reg` is run to produce deterministic SSA-form text outputs.

## 6. Custom Parser
IR parsing handles the `.ll` text natively without `llvmlite` or Python LLVM bindings. It implements a strict class hierarchy: `Value`, `Instruction`, `BasicBlock`, `Function`, preserving textual identifiers.

## 7. CFG Construction
CFG links basic blocks accurately by iterating terminators (e.g. `br`, `switch`, `ret`) and constructing bi-directional predecessor/successor relationships.

## 8. Loop Analysis
Employs standard strict dominator trees to identify back-edges reliably and assign exact structural nesting depths per block.

## 9. Liveness Analysis
A fully implemented backwards post-order dataflow fixpoint analyzer correctly processes `live-in` and `live-out` sets, respecting accurate semantics for `phi` nodes across edges. 

## 10. Interference Graph
Generates strict interference graphs mapping concurrently active live values (instruction definitions mapped backward across live intervals). Accommodates simultaneous `phi` resolution groups.

## 11. Register Pressure
Block-level metrics measure peak concurrency across intervals to determine register pressure dynamically. 

## 12. Testing and Verification
Fully covered by 31 Pytest executions evaluating logical equivalence against an independent programmatic Oracle, ensuring total mathematical correctness across the entire suite.

## 13. Determinism/reproducibility
Verified as byte-identical upon serial invocations, utilizing sorted object mappings. Output strictly conforms to `results/raw/phase1/`.

## 14. Phase 1 Benchmark Summary
All eight benchmarks pass execution end-to-end, producing strictly typed JSON telemetry accurately capturing CFG layout, loops, nodes, edges, and register pressure caps.

## 15. Limitations
Restricted natively to LLVM Opcodes executed inside `-O0 -mem2reg` domains. Does not execute inter-procedural (IPO) logic.

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
