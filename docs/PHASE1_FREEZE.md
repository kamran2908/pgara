# PGARA Phase 1 Freeze Specification

Frozen code commit: f101dd2bcf72835d5ffb86ecb6a0e32753c582be. This document and the checksums are committed on top of it in a separate docs-only commit; the tag phase1-freeze points at that docs commit.

## 1. Frozen Code Commit
- **Commit SHA**: f101dd2bcf72835d5ffb86ecb6a0e32753c582be
- **Repository State**: Clean working tree, fully verified across Python 3.13 and 3.14.

## 2. Test Verification
- **Test Count**: 51 passed (0 skipped, 0 failed)
- **Pytest Output**:
`
...................................................                      [100%]
51 passed in 2.10s
`

## 3. Toolchain Environment
- **Python**: Python 3.14.2 (also verified on Python 3.13.0)
- **Clang**: clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)
- **Opt**: LLVM version 23.1.3

## 4. Phase 1 Boundary Rules
- Phase 1 contains **NO profiling** (no llvm-profdata, execution counts, branch weights).
- Phase 1 contains **NO cost model** (no spill costs, block weights, loop heat).
- Phase 1 contains **NO adaptive allocation** (no allocator selection, no heuristic tuning).
- Phase 1 contains **NO spilling** (no spill code generation, no spill simulation).
- The report JSON has schema_version 1.

## 5. Per-Benchmark Summary
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

## 6. Tracked Files Covered by Checksums (docs/PHASE1_CHECKSUMS.txt)
Total tracked files: 80

- benchmarks/b1_straight_line.c
- benchmarks/b1_straight_line.ll
- benchmarks/b2_array_sum.c
- benchmarks/b2_array_sum.ll
- benchmarks/b3_nested_loop.c
- benchmarks/b3_nested_loop.ll
- benchmarks/b4_recursive.c
- benchmarks/b4_recursive.ll
- benchmarks/b5_rare_error.c
- benchmarks/b5_rare_error.ll
- benchmarks/b6_early_exit.c
- benchmarks/b6_early_exit.ll
- benchmarks/b7_switch_heavy.c
- benchmarks/b7_switch_heavy.ll
- benchmarks/b8_scanner.c
- benchmarks/b8_scanner.ll
- generate_ir.py
- results/raw/ir/b1_straight_line.mem2reg.ll
- results/raw/ir/b1_straight_line.raw.ll
- results/raw/ir/b2_array_sum.mem2reg.ll
- results/raw/ir/b2_array_sum.raw.ll
- results/raw/ir/b3_nested_loop.mem2reg.ll
- results/raw/ir/b3_nested_loop.raw.ll
- results/raw/ir/b4_recursive.mem2reg.ll
- results/raw/ir/b4_recursive.raw.ll
- results/raw/ir/b5_rare_error.mem2reg.ll
- results/raw/ir/b5_rare_error.raw.ll
- results/raw/ir/b6_early_exit.mem2reg.ll
- results/raw/ir/b6_early_exit.raw.ll
- results/raw/ir/b7_switch_heavy.mem2reg.ll
- results/raw/ir/b7_switch_heavy.raw.ll
- results/raw/ir/b8_scanner.mem2reg.ll
- results/raw/ir/b8_scanner.raw.ll
- results/raw/phase1/b1_straight_line.mem2reg.ll
- results/raw/phase1/b1_straight_line.raw.ll
- results/raw/phase1/b1_straight_line.report.json
- results/raw/phase1/b2_array_sum.mem2reg.ll
- results/raw/phase1/b2_array_sum.raw.ll
- results/raw/phase1/b2_array_sum.report.json
- results/raw/phase1/b3_nested_loop.mem2reg.ll
- results/raw/phase1/b3_nested_loop.raw.ll
- results/raw/phase1/b3_nested_loop.report.json
- results/raw/phase1/b4_recursive.mem2reg.ll
- results/raw/phase1/b4_recursive.raw.ll
- results/raw/phase1/b4_recursive.report.json
- results/raw/phase1/b5_rare_error.mem2reg.ll
- results/raw/phase1/b5_rare_error.raw.ll
- results/raw/phase1/b5_rare_error.report.json
- results/raw/phase1/b6_early_exit.mem2reg.ll
- results/raw/phase1/b6_early_exit.raw.ll
- results/raw/phase1/b6_early_exit.report.json
- results/raw/phase1/b7_switch_heavy.mem2reg.ll
- results/raw/phase1/b7_switch_heavy.raw.ll
- results/raw/phase1/b7_switch_heavy.report.json
- results/raw/phase1/b8_scanner.mem2reg.ll
- results/raw/phase1/b8_scanner.raw.ll
- results/raw/phase1/b8_scanner.report.json
- run_phase1.py
- src/__init__.py
- src/analysis/__init__.py
- src/analysis/interference.py
- src/analysis/liveness.py
- src/analysis/loop.py
- src/ir/__init__.py
- src/ir/cfg.py
- src/ir/models.py
- src/ir/parser.py
- src/toolchain.py
- tests/__init__.py
- tests/test_cfg.py
- tests/test_cli.py
- tests/test_imports.py
- tests/test_interference.py
- tests/test_interference_oracle.py
- tests/test_liveness.py
- tests/test_liveness_oracle.py
- tests/test_loop.py
- tests/test_models.py
- tests/test_parser.py
- tests/test_toolchain.py
