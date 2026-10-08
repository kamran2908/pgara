A PROJECT PROPOSAL
PGARA: Profile-Guided Adaptive Register Allocation
A Hybrid Graph-Coloring Register Allocator Driven by Runtime Execution Profiles
Submitted for: Compiler Design (Course Code: [Insert])
Team Members: [Insert Names and Registration Numbers]
Guide / Faculty: [Insert Name]
Department: [Insert Department] | Institution: [Insert Institution]
Date: [Insert Date]
Table of Contents
Right-click the table above and choose “Update Field” in Microsoft Word to populate page numbers after editing.
1. Final Project Title and Abstract
Final Title
PGARA: Profile-Guided Adaptive Register Allocation — A Hybrid Graph-Coloring Register Allocator Driven by Runtime Execution Profiles.
Abstract
Register allocation is one of the most performance-critical phases of a compiler's back end: it decides which of a program's unbounded set of virtual values are kept in the small, fixed set of physical registers, and which must be “spilled” to memory. Classical allocators — Chaitin's and Briggs' graph-coloring algorithms, and LLVM's own greedy and linear-scan allocators — pick which values to spill using static cost heuristics, most commonly a count of static uses/definitions optionally weighted by loop-nesting depth. These static estimates are only a proxy for how “hot” a value's live range really is at run time, and they are known to misjudge programs with data-dependent branches, rare error paths, or irregular loops. This project designs, implements, and evaluates PGARA, a two-pass, profile-guided register allocator: an offline profiling pass instruments and executes a program to obtain real per-basic-block execution frequencies, and an allocation pass rebuilds the interference graph over LLVM IR and performs Chaitin–Briggs-style graph coloring, but replaces the static spill-cost heuristic with a dynamic, profile-weighted cost function, so that values live across frequently executed code are strongly preferred for register residency. We implement the full pipeline — IR parsing, control-flow-graph construction, liveness analysis, interference-graph construction, optimistic coloring with conservative coalescing, and profile-weighted spill-cost calculation — in Python on top of real LLVM IR emitted by Clang, and we validate the design on a benchmark suite of C programs including several with irregular, data-dependent control flow. We compare PGARA against a self-implemented static Chaitin–Briggs baseline and against LLVM's native ‑O2 allocator on spill count, a profile-weighted simulated dynamic spill cost, register utilization, and code-size overhead, with a stretch-goal hardware validation that pins register choices via compiler intrinsics to obtain real wall-clock confirmation on two to three benchmark kernels. The project is scoped to be fully buildable within a single college semester by a team of three to five students.
2. Problem Statement and Motivation
Problem Statement
When the number of live values at a program point exceeds the number of available physical registers, a register allocator must choose some values to spill to memory. This choice is made by a spill-cost heuristic. Classical Chaitin-style allocators estimate a value's importance using purely static information — how many times it is textually defined or used, sometimes multiplied by a constant raised to the loop-nesting depth of each occurrence (the Chow & Hennessy priority-based heuristic). This static model implicitly assumes that (a) more deeply nested code always executes more often than less deeply nested code, and (b) every static occurrence of a variable contributes equally to run-time cost. Both assumptions break down for: data-dependent conditional branches (e.g., an error-handling path inside a hot loop that is rarely taken); irregular or early-exit loops whose iteration counts are not visible statically; switch statements with heavily skewed case frequencies; and indirect calls or virtual dispatch. In all of these cases the compiler can pick the wrong value to spill — keeping a rarely used value in a register while repeatedly spilling and reloading a value that dominates the program's actual execution time.
Motivation
Profile-guided optimization (PGO) already delivers well-documented, production-grade gains for inlining, code layout, and branch prediction in GCC (-fprofile-use) and LLVM (-fprofile-instr-use); yet worked, reproducible, teaching-oriented demonstrations of profile-guided register allocation specifically are rare, even though the underlying idea (weight spill cost by real execution frequency rather than a static proxy) has been explored in the research literature since the early 1990s (see Section 16). Most compiler-design courses stop at a static Chaitin–Briggs allocator as the capstone exercise. This project extends that natural stopping point in a direction that is (a) conceptually well-motivated by a genuine gap between static heuristics and real program behaviour, (b) grounded in an active, well-documented line of academic work so it is neither trivial nor speculative, and (c) fully implementable end-to-end within LLVM's existing, freely available tooling (Clang, llvm-profdata) without requiring modification of LLVM's C++ back end. It therefore gives a project team hands-on experience with the full compiler-construction pipeline — CFG construction, dataflow analysis, graph algorithms, and empirical performance evaluation — while producing a genuinely measurable, arguable result rather than a purely descriptive report.
3. Project Objectives
Implement, from LLVM IR upward, a complete register-allocation front end: an IR parser, control-flow-graph (CFG) builder, backward liveness analysis, and interference-graph construction.
Implement a baseline Chaitin–Briggs-style graph-coloring register allocator (optimistic coloring, conservative coalescing, static spill-cost heuristic) as the control condition for the experiment.
Build a lightweight, real profiling pipeline using Clang/LLVM's native instrumentation (-fprofile-instr-generate and llvm-profdata) to obtain genuine per-basic-block execution counts from representative program runs.
Design and implement an adaptive, profile-weighted spill-cost function (PGARA) that is a drop-in replacement for the baseline's cost function, so the experiment isolates the effect of profiling from every other allocator design choice.
Assemble a benchmark suite of at least eight C programs, including at least three with irregular or data-dependent control flow, purpose-built to expose the static-vs-profiled gap.
Quantitatively evaluate spill count, simulated profile-weighted dynamic spill cost, register utilization, and code-size overhead for the baseline, PGARA, and LLVM's native ‑O2 allocator as an external reference point.
Demonstrate at least one concrete, worked case where profiling changes which value is spilled and produces a measurable improvement over the static baseline.
Package the project as a reproducible, tested, documented open-source repository suitable for a public GitHub submission.
4. Detailed Explanation of the Proposed Idea
PGARA is organised as two independent passes that share a common interference-graph representation, so that only one variable — the source of the spill-cost signal — changes between the control and experimental conditions. This design deliberately keeps every other allocator decision (coloring order, coalescing policy, target register count) identical, which is what makes the eventual comparison scientifically meaningful rather than a comparison of two unrelated allocators.
Phase A — Profiling Pass
1. 
Instrumented build. 
Compile the target C program with Clang's built-in instrumentation (clang -fprofile-instr-generate -O0) so every basic block increments a counter.
2. 
Training run(s). 
Execute the instrumented binary over one or more representative training inputs chosen to exercise both common and rare paths.
3. 
Merge. 
Use llvm-profdata merge to combine the raw .profraw counters into a single default.profdata file.
4. 
Extraction. 
A small Python script (extract_profile.py) parses llvm-profdata show ‑‑all-functions ‑‑counts output and produces profile.json, a per-function map from basic-block label to a normalised execution count.
Phase B — Allocation Pass
Phase B runs on the same program's unoptimized, single-static-assignment LLVM IR (clang -O0 -S -emit-llvm), processed one function at a time:
1. 
Parse. 
A hand-written parser reads the restricted LLVM-IR text subset that -O0 output actually uses (arithmetic, memory, branch, phi, and call instructions) into internal BasicBlock / Instruction / Value objects.
2. 
CFG construction. 
Successor/predecessor edges are derived from each block's terminator (br, switch, ret).
3. 
Liveness analysis. 
A backward dataflow fixpoint computes live-in/live-out sets per block (Section 8.2).
4. 
Interference graph. 
An edge is added between two values that are simultaneously live at any program point (Section 8.3).
5. 
Cost assignment. 
Each node in the interference graph is assigned a spill cost using either the static (baseline) or profile-weighted (PGARA) cost function (Section 6).
6. 
Simplify / spill / select. 
Optimistic Chaitin–Briggs coloring for k physical registers (k is a configurable parameter, e.g., 8 or 16) removes low-degree nodes, pushes them on a stack, and, when no low-degree node exists, picks the lowest-cost high-degree node as a potential spill; nodes are then popped and coloured, with an actual spill only confirmed if no colour remains available.
7. 
Reporting. 
The allocator emits an annotated IR listing (each value tagged with its assigned colour or SPILL) plus a machine-readable JSON allocation report consumed by the metrics module.
Because the two cost functions are interchangeable behind a single interface (CostModel.cost(value) → float), the same allocator core (simplify/spill/select + coalescing) is reused unmodified for both the baseline and PGARA runs — this is the central methodological control of the project.
5. Complete System Architecture / Workflow
The pipeline below is the single recommended architecture for the project; both the baseline and PGARA allocation runs pass through the identical stages, diverging only at the cost-model box.
Source Program (program.c)
     |
     +--[A] Instrumented Build  clang -fprofile-instr-generate -O0
     |         |
     |         v   run over training input(s)
     |     raw.profraw  --(llvm-profdata merge)-->  default.profdata
     |         |
     |         v   extract_profile.py
     |     profile.json   { function: { block_label: exec_count } }
     |
     +--[B] Reference IR   clang -O0 -S -emit-llvm  -->  program.ll
               |
               v   parser.py
           Internal IR objects (BasicBlock, Instruction, Value)
               |
               v   cfg.py
           Control-Flow Graph
               |
               v   liveness.py  (backward fixpoint)
           live-in / live-out sets per block
               |
               v   interference.py
           Interference Graph  G = (Values, InterferenceEdges)
               |
               +----------------------+----------------------+
               v                                              v
     cost_static.py  [Baseline]                 cost_adaptive.py  [PGARA]
     (uses/defs, optional 10^loopDepth)          (profile.json execution counts)
               \                                              /
                +--------------------+------------------------+
                                     v
                     allocator.py  (Chaitin-Briggs: simplify / spill / select,
                                    k physical registers, conservative coalescing)
                                     |
                                     v
                     Annotated IR  +  allocation_report.json
                                     |
                                     v
                     metrics.py  -> spills, simulated dynamic spill cost,
                                    register utilization, code-size delta
                                     |
                                     v
                     report_generator.py  -> comparison charts & tables
                                     |
                                     v (stretch goal)
                     hardware_validation/  -ffixed-<reg> pinning on 2-3
                     flagship kernels  ->  real wall-clock via perf / time
Two independent runs of the Phase-B allocation stage — one with cost_static.py, one with cost_adaptive.py — are executed over the same interference graph for every benchmark, and their outputs are diffed by metrics.py to attribute any difference in spill decisions purely to the profiling signal.
6. How Profile-Guided Adaptive Register Allocation Will Work
The mechanism is a single change of formula inside an otherwise standard Chaitin–Briggs allocator: the cost assigned to each interference-graph node is recomputed to reflect how often the code containing that value actually runs, rather than how often it textually appears.
Cost Formulas
Static baseline (Chaitin):
   cost_static(v) = ( sum over occurrences o in uses(v) U defs(v) of 1 ) / degree(v)
 
Static baseline with loop-depth weighting (Chow & Hennessy style):
   cost_depth(v)  = ( sum over o of 10 ^ loopDepth(block(o)) ) / degree(v)
 
PGARA adaptive cost (proposed):
   cost_adaptive(v) = ( sum over o of freq(block(o)) ) / degree(v)
 
   where freq(block) = normalised dynamic execution count of block, read from
   profile.json; if block has no profile coverage (never reached in the
   training run), freq(block) falls back to 10 ^ loopDepth(block) so the
   allocator degrades gracefully instead of always spilling untouched code.
 
Spill selection rule (both allocators, unchanged):
   spill_candidate = argmin over v in G with degree(v) >= k of cost(v)
Replacing textual occurrence counts with real execution counts means a value whose few static uses all sit on a hot loop path is scored far more expensive — and therefore far less likely to be spilled — than a value with the same or even a higher static use count that sits entirely on a rarely taken branch. Section 11 works through a concrete example of exactly this situation.
Why the Fallback Matters
A purely profile-driven allocator is fragile: any block the training input never exercises would receive a cost of zero and would always be chosen as the cheapest spill candidate, even if that block turns out to be hot in production. PGARA's fallback to the static loop-depth estimate for zero-coverage blocks is therefore not a minor detail but a core part of the design, and its effect is measured directly in the evaluation (Section 13–14).
7. Baseline Algorithm vs Proposed Algorithm
Aspect
Baseline (Static Chaitin–Briggs)
PGARA (Proposed)
Spill-cost signal
Static use/def counts, optionally × 10^loopDepth
Real measured basic-block execution frequency
Adapts to data-dependent branches
No — depends on lexical loop nesting only
Yes — reflects the actual taken path
Requires a program run before allocation
No
Yes, one offline training run
Coloring strategy
Optimistic coloring (Briggs)
Identical — unchanged, so only the cost signal is varied
Coalescing policy
Conservative coalescing (George & Appel)
Identical — unchanged
Extra runtime complexity
—
O(1) profile-table lookup per occurrence during cost computation
Principal risk
Misjudges irregular / rare hot paths
Sensitive to how representative the training input is
8. Algorithms and Pseudocode
8.1 CFG Construction
function BUILD_CFG(instructions):
    blocks = []                       # ordered list of BasicBlock
    current = new BasicBlock()
    for instr in instructions:
        if instr.is_label():
            if current.non_empty(): blocks.append(current)
            current = new BasicBlock(label = instr.label)
        current.append(instr)
        if instr.is_terminator():      # br, switch, ret
            blocks.append(current)
            current = new BasicBlock()
 
    label_to_block = { b.label: b for b in blocks }
    for b in blocks:
        term = b.terminator()
        for target_label in term.target_labels():   # 1 for br, N for switch
            succ = label_to_block[target_label]
            b.successors.add(succ)
            succ.predecessors.add(b)
    return CFG(blocks, entry = blocks[0])
8.2 Liveness Analysis
function LIVENESS(cfg):
    for b in cfg.blocks:
        b.use = { v : v is read in b before any def of v in b }
        b.def = { v : v is defined (assigned) in b }
        b.live_in  = {}
        b.live_out = {}
 
    changed = true
    while changed:
        changed = false
        for b in reverse_postorder(cfg.blocks):     # visiting order only affects speed
            new_out = union( succ.live_in for succ in b.successors )
            new_in  = b.use  union  (new_out - b.def)
            if new_in != b.live_in or new_out != b.live_out:
                b.live_in, b.live_out = new_in, new_out
                changed = true
    return cfg   # each block now carries live_in / live_out
8.3 Interference Graph Construction
function BUILD_INTERFERENCE_GRAPH(cfg):
    G = Graph()
    for v in all_values(cfg): G.add_node(v)
 
    for b in cfg.blocks:
        live = copy(b.live_out)
        for instr in reversed(b.instructions):
            if instr.has_def():
                d = instr.def_value
                for w in live:
                    if w != d: G.add_edge(d, w)     # d interferes with everything live after it
                live.discard(d)
            live |= instr.use_values
    return G
8.4 Register Allocation (Chaitin–Briggs Simplify / Spill / Select)
function ALLOCATE(G, k, cost_fn):
    stack = []
    Gw = copy(G)
    while Gw.has_nodes():
        low_degree = [ n for n in Gw.nodes() if Gw.degree(n) < k ]
        if low_degree:
            n = pick_any(low_degree)                    # SIMPLIFY (always safely colourable later)
        else:
            n = argmin( Gw.nodes(), key = cost_fn )      # POTENTIAL SPILL: cheapest node
        stack.push(n); Gw.remove_node(n)
 
    colour = {}
    actual_spills = set()
    while stack:
        n = stack.pop()
        used = { colour[m] for m in G.neighbors(n) if m in colour }
        available = REGISTER_COLOURS(k) - used
        if available:
            colour[n] = pick_any(available)              # OPTIMISTIC colouring succeeds
        else:
            actual_spills.add(n)                         # colouring genuinely fails -> real spill
    return colour, actual_spills
8.5 Profiling
# Shell: instrument, run, merge
clang -fprofile-instr-generate -O0 program.c -o program_instrumented
./program_instrumented < training_input.txt
llvm-profdata merge -sparse default.profraw -o default.profdata
 
# Python: extract per-block counts
function EXTRACT_PROFILE(profdata_path, module_name):
    raw = shell("llvm-profdata show --all-functions --counts " + profdata_path)
    profile = {}                                    # function -> { block_label: count }
    for func_record in parse_profdata_text(raw):
        profile[func_record.name] = map_counts_to_blocks(func_record.counts)
    write_json(profile, "profile.json")
    return profile
8.6 Adaptive Spill-Cost Calculation
function ADAPTIVE_COST(v, G, profile, loop_depths):
    total = 0
    for o in occurrences(v):                 # every static use or def of v
        b = block_of(o)
        if profile.has_coverage(b):
            weight = profile.freq(b)          # real dynamic execution count
        else:
            weight = 10 ** loop_depths[b]     # graceful fallback to static estimate
        total += weight
    return total / max(1, G.degree(v))
9. Recommended Tech Stack and Rationale
One stack is recommended below rather than a menu of alternatives, per the project's implementability goal.
Component
Choice
Why
Front end / IR source
Clang / LLVM (system install or apt/brew package)
Produces real, correct, SSA-form LLVM IR (.ll) and real execution profiles from ordinary C source — no toy front end needs to be written.
Profiling
clang -fprofile-instr-generate + llvm-profdata
LLVM's own, battle-tested instrumentation and merge tooling; avoids writing and debugging a custom counter-injection IR pass.
Allocator implementation
Python 3.10+
Fast to write and debug graph algorithms in; performance is not the bottleneck since the deliverable is a research/teaching prototype, not a production allocator.
Graph data structure
NetworkX
Ready-made graph object with degree queries, neighbours, and DOT export, used only as a container — the coloring logic itself is written by the team.
Visualization
Graphviz (dot)
Renders CFGs and interference graphs as images directly from NetworkX for the report and slides.
Metrics & charts
Pandas + Matplotlib
Standard, well-documented libraries for tabulating and plotting spill counts / simulated costs across benchmarks.
Testing
Pytest
Unit-tests liveness/interference correctness against small, hand-verified CFGs before trusting the pipeline on real programs.
Version control
Git + GitHub
Team collaboration, issue tracking, and the final public repository deliverable.
Hardware validation (stretch)
-ffixed-<reg> / register-pinning intrinsics, perf stat, time
Gets a real, measured wall-clock number on commodity hardware without writing a full LLVM back-end register-allocator pass.
A note on IR parsing: an alternative is to use llvmlite (the Python LLVM binding used by Numba) to parse .ll files instead of hand-writing a parser. We recommend hand-writing a small, restricted parser instead, because -O0 IR uses a narrow, very regular textual subset (arithmetic, memory, branch, phi, call), and hand-writing it is directly where the course's learning objectives — understanding IR structure, not just consuming it through a library — are met.
10. Exact Implementation Plan and GitHub Folder Structure
pgara/
|-- README.md
|-- requirements.txt
|-- docs/
|   |-- proposal.md
|   |-- design.md
|   `-- final_report/
|-- src/
|   |-- ir/
|   |   |-- parser.py          # LLVM .ll text -> internal IR objects
|   |   |-- cfg.py             # CFG construction
|   |   `-- models.py          # BasicBlock, Instruction, Value dataclasses
|   |-- analysis/
|   |   |-- liveness.py
|   |   `-- interference.py
|   |-- allocator/
|   |   |-- chaitin_briggs.py  # simplify / spill / select core (shared)
|   |   |-- cost_static.py     # baseline cost function
|   |   |-- cost_adaptive.py   # PGARA cost function
|   |   `-- coalesce.py        # conservative coalescing
|   |-- profiling/
|   |   |-- instrument.sh      # clang -fprofile-instr-generate wrapper
|   |   `-- extract_profile.py # llvm-profdata -> profile.json
|   |-- metrics/
|   |   |-- simulate_cost.py
|   |   `-- report.py
|   `-- cli.py                  # pgara run <bench>.c --mode=static|adaptive
|-- benchmarks/
|   |-- loops/  |-- recursion/  |-- irregular_branch/
|   `-- matrix/ |-- switch_heavy/
|-- tests/
|   |-- test_liveness.py
|   |-- test_interference.py
|   `-- test_allocator.py
|-- hardware_validation/        # stretch goal
|   `-- pin_registers/
`-- results/
    |-- raw/
    `-- charts/
Each src/ module has a single, narrow responsibility and a corresponding test file, so team members can work in parallel with minimal merge conflicts (see Section 18 for the exact role-to-folder mapping).
11. Example: How Profiling Changes Register Allocation
Consider the following representative C function, deliberately constructed so that a hot accumulator and a cold error counter have identical static cost:
int compute(int n, int *data) {
    int sum = 0;          // v1: touched every loop iteration
    int errCount = 0;     // v2: touched only on a rare, data-dependent branch
    for (int i = 0; i < n; i++) {
        if (data[i] < 0) {        // taken in well under 1% of iterations
            errCount++;
            log_error(i);
        }
        sum += data[i] * 2;
    }
    return sum + errCount;
}
Assume register pressure forces exactly one of {sum, errCount} to spill. Both values have one static definition and two static uses (a define, an update, and a final read), so cost_static(sum) = cost_static(errCount): the static allocator has no basis to prefer one over the other and may spill sum — the value that is actually live and updated on every one of the loop's iterations.
Running the program over a representative training input (say n = 100,000, with a small number of negative entries) yields real profile counts of roughly 100,000 executions of the loop body and roughly 50 executions of the error branch. Substituting these into the adaptive formula:
cost_adaptive(sum)      ~ freq(loop_body) x 2 uses   ~ 100,000 x 2 = 200,000
cost_adaptive(errCount) ~ freq(error_block) x 2 uses ~     50 x 2 =     100
 
spill_candidate = argmin(cost) = errCount   (correctly, since it is far cheaper)
PGARA therefore spills errCount and keeps sum resident in a register for the entire hot loop, eliminating on the order of 200,000 store/reload pairs from the loop body at the cost of roughly 50 extra memory accesses on the rare error path — exactly the outcome the static baseline cannot distinguish. This worked example is also the basis for one of the benchmark-suite programs (Section 12) and for the mechanism slide in the presentation (Section 22).
12. Test Cases and Benchmark Programs
Correctness Unit Tests
Liveness fixpoint converges to hand-verified live-in/live-out sets on small (4–6 block) toy CFGs.
Interference-graph edges are present if and only if two values are simultaneously live at some program point, checked against a manually derived reference graph.
Allocator output is a valid k-colouring: no two interfering values share a colour.
Spilled values are correctly identified as those without an available colour after the select phase.
Benchmark Suite (≥ 8 programs)
#
Program
Purpose
1
Straight-line arithmetic
Sanity check — no branches, both allocators should agree exactly.
2
Array-sum loop
Simple, regular hot loop — expected near-parity between baseline and PGARA.
3
Nested loop (small matrix multiply)
Tests loop-depth heuristic vs. real frequency on genuinely nested hot code.
4
Recursive function (factorial / Fibonacci)
Tests interference across call boundaries.
5
Loop with rare error branch (Section 11 example)
Primary case designed to expose the static-vs-profiled gap.
6
Loop with early exit / break
Irregular control flow not captured by lexical loop depth.
7
Switch-heavy function
Many basic blocks with heavily skewed case frequencies.
8
Data-dependent string/token scanner
Realistic irregular branching pattern.
9 (stretch)
1–2 functions adapted from MiBench
Free, open, small-footprint benchmarks for external credibility beyond hand-built tests.
13. Performance Metrics
Static spill count — 
the raw number of values the allocator spills, reported for the baseline, PGARA, and LLVM -O2 (via llc diagnostics) as an external reference point.
Simulated dynamic spill cost (primary metric) — 
for every spilled value, (store_cost + reload_cost × static_use_count) multiplied by the real profiled execution frequency of each spill/reload site, summed across the program; computable for every benchmark without generating or executing real machine code.
Register utilization — 
the frequency-weighted average fraction of live values that are resident in a physical register rather than spilled, across the run.
Code-size delta — 
estimated extra store/load instructions inserted for spill code, reported as a percentage over a spill-free ideal.
Wall-clock execution time (stretch, hardware-validation subset only) — 
measured on 2–3 flagship kernels by pinning the allocator's chosen register set via -ffixed-<reg> / inline-asm register hints and timing repeated runs with perf stat / time.
Cache/memory-access proxy (stretch) — 
perf stat -e cache-misses,L1-dcache-load-misses on the same hardware-validation subset.
14. Expected Results and Limitations
Expected Results
PGARA is expected to reduce simulated dynamic spill cost substantially — a target of roughly 20–40% versus the plain static baseline, broadly consistent with the magnitude of gains reported for profile-informed spill/region decisions in the literature reviewed in Section 16 — concentrated specifically on benchmarks 5–8 (irregular, data-dependent control flow). Benchmarks 1–4 (regular, uniform control flow) are expected to show near parity between the two allocators, since static and profiled weighting largely agree when control flow is predictable; this is itself a useful and honestly reportable finding, since it shows profiling helps precisely where the static heuristic's assumptions break down, and not uniformly everywhere.
Limitations
Training-input dependence: allocation quality is bounded by how representative the training run is of production inputs — mitigated, but not eliminated, by the fallback heuristic.
The allocator operates on one function at a time; there is no interprocedural or whole-program allocation.
The primary simulated-cost metric abstracts away real microarchitectural effects (cache behaviour, out-of-order execution) except within the small hardware-validation subset.
k is a simplified stand-in for a real target's register file; register classes, aliasing, and calling-convention-reserved registers are not modelled.
Instrumentation overhead incurred during the offline training run itself is not counted against production-run numbers, consistent with standard profile-guided-optimization practice.
15. Project Novelty and Research Gap
Using profile information to weight register-allocation spill cost is not, by itself, a new idea: Chow & Hennessy's priority-based allocator (1990) already weighted spill priority by an estimated (static) execution frequency; Wagner et al. (1994) systematically studied how well static estimates approximate real profiles; and Kreahling & Norris (2000) together with Garigipati (2002) explicitly measured the effect of real profiling on register-allocation spill decisions. The contribution of this project, framed honestly at college-project scope, is not a new algorithm but a well-controlled, modern, reproducible engineering demonstration:
Modern, open toolchain. 
The technique is demonstrated end-to-end on current LLVM IR using LLVM's own standard instrumentation-based profiling (llvm-profdata), rather than inside an internal research compiler, making it fully reproducible from a laptop-installed toolchain.
A controlled, single-variable comparison. 
The baseline and PGARA allocators share an identical coloring engine and coalescing policy; only the spill-cost function differs, isolating the profiling signal's effect far more cleanly than most historical studies, which typically change the allocator family and the profiling source at the same time.
An explicit, tested fallback design. 
Blocks with no profile coverage fall back to the static loop-depth estimate, and the project measures this fallback's effect directly — a robustness question the older papers do not foreground.
A cheap, real hardware-validation path. 
Register-pinning via compiler intrinsics gives a genuine wall-clock confirmation on commodity hardware for a subset of kernels, without requiring the team to build a full custom LLVM machine-function pass.
This is deliberately framed as an engineering reproduction and well-scoped extension of established ideas, not as a novel research algorithm — an honest and appropriate framing for an undergraduate compiler-design project.
16. Literature Review
Each paper below is summarised in the same format: what it contributes, and how it connects to PGARA. Every reference was verified against its publisher record; no citation is invented.
Paper 1: Register Allocation via Coloring
Chaitin, G. J., Auslander, M. A., Chandra, A. K., Cocke, J., Hopkins, M. E., & Markstein, P. W. (1981). Computer Languages, 6(1), 47–57.
What it contributes: 
The original paper establishing that register allocation can be modelled as graph colouring: nodes are values, edges connect values simultaneously live, and a k-colouring of the interference graph is a valid k-register allocation.
How it connects to our project: 
Our interference-graph construction (Section 8.3) follows this formulation directly, and it is the theoretical basis of the entire allocator core.
Paper 2: Register Allocation & Spilling via Graph Coloring
Chaitin, G. J. (1982). ACM SIGPLAN Notices, 17(6), 98–105. https://doi.org/10.1145/800230.806984
What it contributes: 
Extends the 1981 formulation to handle spilling naturally within the same graph-colouring framework, using cost estimates of the value of keeping a computation's result in a register rather than in storage.
How it connects to our project: 
This is the direct basis of our simplify/spill/select allocator core (Section 8.4); our project varies exactly the “cost estimate” Chaitin identifies as the key design choice, replacing it with a profile-derived signal.
Paper 3: The Priority-Based Coloring Approach to Register Allocation
Chow, F. C., & Hennessy, J. L. (1990). ACM Transactions on Programming Languages and Systems (TOPLAS), 12(4), 501–536.
What it contributes: 
Introduces spill priorities weighted by an estimated execution frequency — in practice, a static function of loop-nesting depth — rather than a raw static use count.
How it connects to our project: 
Our static-baseline-with-loop-depth variant and the structure of our adaptive cost formula (Section 6) are directly modelled on this priority function; PGARA's contribution is to replace Chow & Hennessy's static frequency estimate with a real, measured one.
Paper 4: Improvements to Graph Coloring Register Allocation
Briggs, P., Cooper, K. D., & Torczon, L. (1994). ACM TOPLAS, 16(3), 428–455. https://doi.org/10.1145/177492.177575
What it contributes: 
Introduces optimistic coloring (attempt a colour even for high-degree nodes rather than assuming they must spill) and conservative coalescing, both of which reduce unnecessary spilling versus Chaitin's original algorithm.
How it connects to our project: 
Our allocator core adopts optimistic coloring and conservative coalescing unchanged from this paper, so that the baseline-vs-PGARA experiment isolates only the spill-cost signal and not a difference in colouring strategy.
Paper 5: Iterated Register Coalescing
George, L., & Appel, A. W. (1996). ACM TOPLAS, 18(3), 300–324. https://doi.org/10.1145/229542.229546
What it contributes: 
Refines Briggs' conservative coalescing into an iterated simplify/coalesce loop that removes more redundant move instructions while still provably preserving colourability.
How it connects to our project: 
Our coalesce.py module (Section 10) follows this iterated formulation.
Paper 6: Linear Scan Register Allocation
Poletto, M., & Sarkar, V. (1999). ACM TOPLAS, 21(5), 895–913. https://doi.org/10.1145/330249.330250
What it contributes: 
Proposes an allocation algorithm that is not based on graph colouring at all: it sweeps live intervals once in program order, trading some allocation quality for much lower compile time — originally motivated by just-in-time compilation.
How it connects to our project: 
Represents the alternative allocator family discussed in our comparison table (Section 17) and explains why LLVM's fast-compilation modes and JIT-style compilers default to linear scan rather than graph colouring.
Paper 7: Optimized Interval Splitting in a Linear Scan Register Allocator
Wimmer, C., & Mössenböck, H. (2005). Proceedings of VEE '05, 132–141. https://doi.org/10.1145/1064979.1064998
What it contributes: 
Extends linear scan with lifetime holes and interval splitting to close much of the quality gap with graph colouring, as implemented in the Java HotSpot client compiler.
How it connects to our project: 
Used as the reference point for why we chose graph colouring (higher achievable quality, well-understood spill-cost hooks) over linear scan for a teaching prototype whose entire point is to study spill-cost decisions in detail.
Paper 8: Accurate Static Estimators for Program Optimization
Wagner, T. A., Maverick, V., Graham, S. L., & Harrison, M. A. (1994). Proceedings of ACM SIGPLAN PLDI '94, 85–96. https://doi.org/10.1145/178243.178251
What it contributes: 
Rigorously compares static compile-time frequency estimation techniques (branch and loop-count heuristics) against real, profiled execution frequencies across several optimizations including register allocation, finding static estimates are often good but not uniformly reliable.
How it connects to our project: 
Directly motivates PGARA's core hypothesis — that real profiles outperform static heuristics specifically where control flow is irregular — and supplies the theoretical justification for our static loop-depth baseline variant.
Paper 9: Efficient Path Profiling
Ball, T., & Larus, J. R. (1996). Proceedings of the 29th Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-29), 46–57. https://doi.org/10.1109/MICRO.1996.566449
What it contributes: 
Establishes efficient instrumentation techniques for basic-block and edge profiling with low run-time overhead — the methodology later built into LLVM's -fprofile-instr-generate infrastructure.
How it connects to our project: 
Our profiling pass (Section 8.5) relies on exactly this style of low-overhead block/edge instrumentation to obtain per-basic-block execution counts.
Paper 10: Improving Register Allocation Using Profiling
Kreahling, W. C., & Norris, C. (2000). Proceedings of the ACM Symposium on Applied Computing (SAC 2000).
What it contributes: 
Directly evaluates profile-guided spill decisions against a static baseline within a research allocator, an experimental design very close in spirit to this project's.
How it connects to our project: 
Our controlled baseline-vs-PGARA methodology (Section 7) mirrors this study's structure, updated to the modern, freely available LLVM ecosystem so it is reproducible without a research-lab-internal compiler.
Paper 11: Evaluating the Use of Profiling by a Region-Based Register Allocator
Garigipati, K. V. (2002). Proceedings of the 2002 ACM Symposium on Applied Computing (SAC '02). https://doi.org/10.1145/508791.508976
What it contributes: 
Shows that allocating registers to the most frequently executed regions first, using real profile data, reduces spill-induced memory traffic in a region-based compilation framework.
How it connects to our project: 
Supports the design of our primary metric — simulated dynamic spill cost weighted by real block frequency (Section 13) — and our expectation that gains concentrate on benchmarks with irregular control flow (Section 14).
17. Comparison with Traditional Approaches
Approach
Allocation quality
Compile-time cost
Uses profile data by default?
Chaitin–Briggs graph coloring (our baseline)
High
O(n²)-ish, graph-heavy, slower to compile
No — static heuristic only
PGARA (proposed)
High, and closer to true dynamic optimum on irregular code
Same as baseline plus one offline profiling run
Yes — core contribution
Linear scan (Poletto & Sarkar / Wimmer & Mössenböck)
Slightly lower than graph coloring on average
Much faster — O(n log n), single pass over intervals
No, by default
LLVM greedy / basic allocator (-O2)
High, production-tuned
Fast, engineered for real compiler use
Only under explicit -fprofile-instr-use PGO builds
GCC IRA (graph-coloring-based)
High, production-tuned
Comparable to LLVM's default
Only under explicit -fprofile-use PGO builds
The comparison highlights that mainstream production compilers already support profile-guided register allocation, but only as an opt-in flag layered on an otherwise static allocator; this project instead makes profiling the explicit object of study, holding every other allocator decision fixed so its isolated effect can be measured directly.
18. Team Division for 3–5 Students
Role (5-member team)
Owns
Deliverables
A — IR Front-End & CFG Lead
src/ir/
parser.py, cfg.py, models.py, IR fixture tests
B — Dataflow & Interference Lead
src/analysis/
liveness.py, interference.py, correctness tests
C — Allocator Lead
src/allocator/
chaitin_briggs.py, coalesce.py, cost_static.py
D — Profiling & Adaptive Cost Lead
src/profiling/, cost_adaptive.py
instrumentation pipeline, extract_profile.py, cost_adaptive.py
E — Benchmarks, Metrics & Report Lead
benchmarks/, src/metrics/
benchmark suite, metrics/report.py, charts, hardware validation, report/slide assembly
For a 4-member team, merge roles D and E. For a 3-member team, merge A with B, and D with E, leaving three roles: IR & Dataflow, Allocator, and Profiling/Benchmarks/Reporting.
19. 10–12 Week Development Roadmap
Week
Milestone
1
Toolchain setup (Clang/LLVM, Python env), study of the .ll text format, repository scaffold, benchmark set selection.
2
IR parser + CFG construction (models.py, parser.py, cfg.py) with unit tests.
3
Backward liveness analysis, validated on hand-verified toy CFGs.
4
Interference-graph construction plus Graphviz visualization.
5
Baseline Chaitin–Briggs allocator core: simplify/spill/select with static cost and conservative coalescing.
6
Baseline validated end-to-end on benchmarks 1–4 (regular control flow). Mid-semester milestone review / demo.
7
Instrumentation and llvm-profdata pipeline; profile.json extraction; profile data wired into the IR objects.
8
Adaptive cost function (PGARA) implemented and integrated; unit tests reproducing the Section 11 worked example.
9
Full benchmark run — baseline vs. PGARA vs. LLVM -O2 reference — across all benchmarks; metrics/report.py and charts.
10
Hardware-validation stretch goal (register pinning on 2–3 flagship kernels) and wall-clock measurement; CLI/tooling polish.
11
Report writing, slide deck, viva preparation, code cleanup, README, reproducibility pass.
12
Buffer week: bug fixes, final rehearsal, submission.
20. MVP, Good Version, and Advanced Version
MVP (guarantees a working, demonstrable project)
IR parser, CFG, liveness, and interference graph for a restricted LLVM-IR subset (no exceptions or vector types).
Baseline Chaitin–Briggs allocator with static cost.
PGARA adaptive allocator with real llvm-profdata-based profile weighting.
At least four benchmarks, simulated dynamic-cost metric only.
Basic CLI and README.
Good Version (target deliverable)
Full 8–9-benchmark suite including irregular-branch programs.
All five metrics from Section 13, with comparison charts.
Graceful profile-missing fallback implemented and specifically tested.
Spill counts compared against real LLVM -O2 output as an external reference point.
Automated pytest suite, plus a complete written report and slide deck.
Advanced / Stretch Version
Hardware-validated wall-clock confirmation via register pinning on 2–3 flagship kernels.
A small interprocedural extension aggregating profile data across a couple of call sites.
A tunable blended cost policy, cost = λ·profile + (1−λ)·staticDepth, with a short ablation study over λ.
(Very ambitious, optional) A real LLVM -regalloc=pgara C++ MachineFunctionPass wired into llc, for teams strong in C++/LLVM internals.
21. Likely Viva Questions and Answers
Q1. 
What problem does register allocation solve?
A: 
It maps an unbounded number of program values (virtual registers) onto a small, fixed set of physical registers, inserting spill code (stores/loads) when demand exceeds supply.
Q2. 
Why is register allocation NP-complete?
A: 
Because optimal allocation for a fixed number of colours reduces to graph k-colouring, which is NP-complete in general graphs; Chaitin et al. (1981) proved this reduction explicitly.
Q3. 
What is an interference graph?
A: 
A graph whose nodes are program values and whose edges connect any two values that are simultaneously live at some program point, i.e., cannot share a register.
Q4. 
What does it mean for a graph to be k-colourable?
A: 
That its nodes can be assigned one of k colours such that no two adjacent nodes share a colour; here, colours correspond to physical registers.
Q5. 
What is spilling?
A: 
Storing a value in memory instead of a register when no register is available for it, requiring extra store/reload instructions at each definition/use.
Q6. 
What is the difference between Chaitin's and Briggs' algorithms?
A: 
Chaitin conservatively assumes any node with degree ≥ k must eventually spill; Briggs' optimistic coloring instead defers that decision until the select phase, since a high-degree node can still end up colourable if its neighbours use fewer than k distinct colours.
Q7. 
Why does liveness analysis run backward?
A: 
Because whether a value is live at a point depends on whether it is used later in execution, i.e., on successor blocks' liveness — information only available by propagating from exits back to entries.
Q8. 
Why is liveness analysis computed as a fixpoint?
A: 
Because live-in/live-out sets are mutually recursive across CFG edges (including back-edges in loops); repeated propagation is iterated until no set changes, guaranteeing the minimal solution to the dataflow equations.
Q9. 
What is register coalescing, and why 'conservative'?
A: 
Coalescing merges the source and destination of a move instruction into one node to eliminate the move; it is done conservatively (Briggs' rule) because merging can increase a node's degree enough to make the graph uncolourable if done carelessly.
Q10. 
Why is your baseline's cost function sometimes weighted by loop depth?
A: 
To emulate Chow & Hennessy's (1990) classical static estimate of execution frequency, giving a fair, well-established static baseline rather than an artificially weak one.
Q11. 
What exactly does PGARA change relative to the baseline?
A: 
Only the spill-cost function: static use/def (or loop-depth) counts are replaced by real, measured basic-block execution counts from an offline profiling run; the coloring and coalescing logic are unchanged.
Q12. 
Why might a static loop-depth heuristic mislead the allocator?
A: 
Because deeper lexical nesting does not guarantee more frequent execution — e.g., a rarely taken error branch nested inside a loop, or an early-exit loop that usually runs only a few iterations.
Q13. 
How do you obtain real execution profiles?
A: 
By compiling with clang -fprofile-instr-generate, running the instrumented binary over representative inputs, and merging the resulting counters with llvm-profdata.
Q14. 
What happens if a basic block has no profile coverage?
A: 
PGARA falls back to the static loop-depth estimate for that block's occurrences, so the allocator degrades gracefully rather than always preferring to spill unreached code.
Q15. 
What is the risk of profile-guided allocation?
A: 
Overfitting to the training input: if production inputs exercise different hot paths than the training run, the allocator's choices may be suboptimal or even worse than the static baseline.
Q16. 
Why do you keep k as a parameter rather than a real ISA's exact register count?
A: 
To let the allocator be evaluated under varying register pressure without hard-coding a specific target ISA's calling convention, aliasing rules, and reserved registers, which are out of scope for this prototype.
Q17. 
What is the difference between graph-coloring and linear-scan allocation?
A: 
Graph coloring builds and colours a full interference graph for higher allocation quality at higher compile-time cost; linear scan sweeps live intervals once in program order for much lower compile time at a modest quality cost.
Q18. 
Why did you choose graph coloring over linear scan for this project?
A: 
Because the project's object of study is the spill-cost decision itself, and graph coloring's simplify/spill/select structure gives an explicit, well-defined hook for that decision that linear scan's interval-sweep does not expose as directly.
Q19. 
Is the IR you operate on in SSA form?
A: 
Yes — Clang's -O0 -emit-llvm output is already LLVM IR, which is SSA by construction; each virtual register has exactly one static definition.
Q20. 
What is rematerialization, and did you implement it?
A: 
Recomputing a cheap value instead of spilling/reloading it (e.g., reloading a constant by re-materializing it rather than fetching from memory); it is not implemented in this project and is listed as future work.
Q21. 
What does llvm-profdata do?
A: 
It merges raw per-run instrumentation counters (.profraw) from one or more training runs into a single, queryable profile database (.profdata) used to drive profile-guided optimizations.
Q22. 
Why use instrumentation-based profiling rather than sampling-based profiling (e.g., perf)?
A: 
Instrumentation gives exact per-block execution counts tied directly to IR block labels, which our allocator needs for precise cost lookup; sampling profilers give statistically approximate, PC-based samples that are harder to map back cleanly onto IR blocks.
Q23. 
How do you validate your liveness analysis is correct?
A: 
By unit-testing it against small, hand-computed CFGs where the correct live-in/live-out sets are derived manually before the code is trusted on real benchmark programs.
Q24. 
Why is the primary evaluation metric a simulated cost rather than measured wall-clock time?
A: 
Because it can be computed uniformly for every benchmark without building a full working code generator, while still capturing exactly the quantity (frequency-weighted spill traffic) the allocator is designed to minimize; wall-clock time is added separately for a small validated subset.
Q25. 
How do you get a real wall-clock number without writing a full LLVM back-end pass?
A: 
By using -ffixed-<reg> / register-pinning compiler intrinsics to force the compiler to keep the allocator's chosen 'keep-in-register' set resident for a couple of flagship kernels, then timing the resulting binaries directly.
Q26. 
What does 'register utilization' mean in your evaluation?
A: 
The frequency-weighted average fraction of live values that are resident in a physical register (rather than spilled) across a program's execution, as estimated from the allocation report and the profile data.
Q27. 
Why does your project not modify LLVM's actual C++ register allocator?
A: 
To keep the project's scope implementable within a single semester by a small team; operating on the textual .ll IR in Python gives the same conceptual pipeline without requiring LLVM C++ build expertise, which is reserved as an optional stretch goal.
Q28. 
What would you do differently with more time?
A: 
Add interprocedural profile aggregation, implement rematerialization, model real ISA register classes and calling-convention constraints, and replace the stretch-goal register-pinning validation with a genuine custom -regalloc LLVM pass.
22. 12–15 Slide Presentation Structure
1. 
Title — project name, team, course.
2. 
Problem & Motivation — why static spill-cost heuristics can be wrong.
3. 
Research Gap / Related Work snapshot — 3–4 key prior papers in one slide.
4. 
Objectives.
5. 
System Architecture — the pipeline diagram (Section 5).
6. 
Baseline Algorithm — Chaitin–Briggs simplify/spill/select.
7. 
Our Adaptive Spill-Cost Formula — the cost_adaptive equation and fallback rule.
8. 
Worked Example — the hot sum / cold errCount case from Section 11.
9. 
Tech Stack.
10. 
Benchmark Suite overview.
11. 
Results — spill count & simulated dynamic cost charts.
12. 
Results — register utilization / code-size charts.
13. 
Hardware Validation (stretch) — real wall-clock confirmation.
14. 
Limitations & Future Work.
15. 
Conclusion + Demo / Q&A.
23. Final Report / Chapter Structure
1. 
Introduction — motivation, objectives, scope.
2. 
Literature Review — the eleven references from Section 16, organized by theme.
3. 
Background — register-allocation theory: graph colouring, liveness, interference.
4. 
System Design & Architecture.
5. 
Implementation — per-module walkthrough matching the folder structure in Section 10.
6. 
Profiling Methodology.
7. 
Experimental Setup — benchmarks, hardware, metrics.
8. 
Results & Analysis.
9. 
Limitations.
10. 
Conclusion & Future Work.
References (formatted per Section 16) and an Appendix (full pseudocode, folder structure, sample IR listings, and pointers into the source-code repository) follow the numbered chapters.
Final Summary
FINAL TITLE: 
PGARA: Profile-Guided Adaptive Register Allocation — A Hybrid Graph-Coloring Register Allocator Driven by Runtime Execution Profiles.
PROBLEM: 
Classical register allocators choose which values to spill using static heuristics (use/def counts, loop-nesting depth) that misjudge data-dependent, irregular, or rarely taken code paths.
SOLUTION: 
A two-pass allocator that reuses one Chaitin–Briggs coloring/coalescing core but replaces the static spill-cost function with one weighted by real, measured basic-block execution frequencies, with a static fallback for unprofiled code.
TECH STACK: 
Clang/LLVM (IR + instrumentation via -fprofile-instr-generate + llvm-profdata), Python 3.10+ with NetworkX, Graphviz, Pandas/Matplotlib, Pytest, Git/GitHub.
BASELINE: 
Self-implemented static Chaitin–Briggs graph-coloring allocator (optimistic coloring, conservative coalescing, static/loop-depth cost).
PROPOSED ALGORITHM: 
PGARA — identical coloring/coalescing core, adaptive profile-weighted spill-cost function: cost_adaptive(v) = Σ freq(block(o)) / degree(v), with a static loop-depth fallback for zero-coverage blocks.
PROFILE DATA: 
Real per-basic-block execution counts obtained via clang -fprofile-instr-generate and llvm-profdata over representative training inputs.
BENCHMARKS: 
≥ 8 C programs spanning straight-line code, regular loops, nested loops, recursion, rare-branch loops, early-exit loops, switch-heavy code, and data-dependent scanning, plus an optional MiBench-derived stretch set.
EVALUATION METRICS: 
Static spill count, simulated profile-weighted dynamic spill cost (primary), register utilization, code-size delta, and (stretch) real wall-clock time and cache misses on a hardware-validated subset.
NOVELTY: 
Not a new algorithm, but a modern, reproducible, single-variable-controlled demonstration of profile-guided spill-cost weighting on real LLVM IR, with an explicit, tested static fallback and a cheap real-hardware validation path.
DIFFICULTY: 
Moderate-to-high for a college semester; fully implementable by 3–5 students without modifying LLVM's own C++ back end (an optional stretch goal only).
TIMELINE: 
10–12 weeks: weeks 1–6 build and validate the static baseline; weeks 7–9 add profiling and the adaptive allocator and run the full benchmark comparison; weeks 10–12 cover hardware validation, reporting, and viva preparation.