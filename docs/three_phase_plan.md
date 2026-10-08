# Profile-Guided Adaptive Register Allocation (PGARA)
## 3-Phase Project Plan

### Phase 1: Analysis (Implemented)
The goal of Phase 1 is to build a robust structural and dataflow analysis foundation capable of interpreting Clang-generated LLVM IR without relying on LLVM's internal C++ APIs.

*   **IR Generation**: Automated pipeline extracting IR from C benchmarks using `clang` and `opt` (`mem2reg`).
*   **Parser**: Custom line-based parser strictly modeling LLVM IR in memory (`BasicBlock`, `Instruction`, `Value`).
*   **CFG Builder**: Discovers predecessors/successors, detects loop back-edges, and calculates loop nesting depths.
*   **Liveness Analysis**: Backward dataflow fixpoint calculation that accurately handles complex phi-node edge semantics (values are `live-out` to predecessors).
*   **Interference Graph**: Backward pass over blocks using `live` sets to build a strict conflict graph, measuring register pressure per block.

### Phase 2: Profiling & Metrics (Planned)
The goal of Phase 2 is to inject real runtime data into the static analysis environment to distinguish between hot execution paths (tight loops) and cold execution paths (error handling).

*   **Instrumentation**: Compile benchmarks using Clang source-based instrumentation (`-fprofile-instr-generate`).
*   **Profile Extraction**: Run the compiled binaries to gather raw execution counts, then use `llvm-profdata` to export the data.
*   **Metric Synthesis**: Map the exported execution profiles back to our in-memory CFG blocks.
*   **ComputeMetrics Pass**: Calculate a block "density" or "heat" metric, typically represented as `weight / pressure`.
*   **Fallback Mechanism**: Add a static fallback heuristic (e.g., nesting loop depth) for blocks lacking profile coverage.

### Phase 3: Adaptive Allocation (Planned)
The goal of Phase 3 is to implement the actual allocation algorithms and conditionally switch between them on a per-block basis depending on the metrics gathered in Phase 2.

*   **Static Chaitin-Briggs Baseline**: Implement a complete Chaitin-Briggs graph coloring allocator (simplify, potential-spill, select) as the baseline for hot paths.
*   **Adaptive Selection**: Introduce a conditional threshold to evaluate static metrics against profile-guided adaptive metrics.
*   **Boundary Stitching**: Develop a mechanism to gracefully "stitch" variable allocations across the boundaries of blocks that use different allocation strategies, managing necessary spills or reloads.
*   **Evaluation (Stretch)**: Compare generated allocation efficiency against LLVM's native register allocator across the benchmark suite.
