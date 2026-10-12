# PGARA Phase 1 Fix Report

## 1. Fix Status Summary Table

| Fix | Description / Requirements | Evidence File(s) | Status |
|---|---|---|---|
| Fix 1 | Missing `Tuple` import in `src/analysis/liveness.py`, multi-Python verification (3.13 & 3.14), untracking compiled bytecode, `.gitignore` setup | `evidence/01_env.txt`<br>`evidence/02_git_diff_stat.txt`<br>`evidence/02b_git_diff_analysis.txt`<br>`evidence/03_pytest_314.txt`<br>`evidence/03_pytest_313.txt` | PASS |
| Fix 2 | Configurable toolchain (`PGARA_CLANG`, `PGARA_OPT`, system `PATH`, `--clang`, `--opt`), removing hardcoded Windows paths, clean exit codes | `evidence/01_env.txt`<br>`evidence/10_fresh_clone.txt`<br>`evidence/11_toolchain_failures.txt` | PASS |
| Fix 3 | Missing parser and unit tests, `docs/OPCODE_INVENTORY.txt`, `tools/opcode_inventory.py`, zero silent skips | `evidence/04_collect.txt`<br>`evidence/09_opcode_inventory.txt` | PASS |
| Fix 4 | Full CLI (`run_phase1.py`), `--dump` and `--dot` modes, exit codes (0/1/2), additive report fields (`schema_version`, `is_irreducible`, `unreachable_blocks`), additivity proof, CLI test suite | `evidence/05_run_a.txt`<br>`evidence/05_run_b.txt`<br>`evidence/05_hashes_a.txt`<br>`evidence/05_hashes_b.txt`<br>`evidence/05_diff.txt`<br>`evidence/06_hashes_committed.txt`<br>`evidence/07_b2_dumps.txt`<br>`evidence/07_b3_dumps.txt`<br>`evidence/07_b5_compute_dumps.txt`<br>`evidence/07_b5_log_error_dumps.txt`<br>`evidence/07_dot_files.txt`<br>`evidence/11_toolchain_failures.txt` | PASS |
| Fix 4 repair | Make CLI tests independent of working directory (`REPO_ROOT`, `cwd=REPO_ROOT`), verification from root and parent directories | `evidence/03_pytest_otherdir.txt`<br>`evidence/03_pytest_314.txt`<br>`evidence/03_pytest_313.txt` | PASS |
| Fix 5 | Documentation alignment in `README.md` and `docs/PGARA_Phase1_Final_Report.md`: project name, Python 3.13/3.14, decisions D1–D8, toolchain priority, per-block report structure, reproducibility, where files live, removal of overclaims | `evidence/02_git_diff_stat.txt`<br>`evidence/08_leakage_scan.txt`<br>`evidence/10_fresh_clone.txt` | PASS |
| Fix 5b | Extraction of proper LLVM version string for `opt` in startup banner line, unit test, README sample output update | `evidence/01_env.txt`<br>`evidence/02_git_diff_stat.txt`<br>`evidence/05_run_a.txt`<br>`evidence/10_fresh_clone.txt` | PASS |

## 2. Skipped Tests

0 skipped

## 3. Total Test Counts for Both Python Versions

- **Python 3.14**: `evidence/03_pytest_314.txt`, line 60:
  `============================= 51 passed in 1.81s ==============================`
- **Python 3.13**: `evidence/03_pytest_313.txt`, line 59:
  `============================= 51 passed in 1.74s ==============================`

## 4. Items That Could Not Be Done

None. All required steps, analyses, verifications, and evidence generation were successfully performed.

## 5. Known Remaining Defects

1. **Opcode Coverage Scope**: The handwritten LLVM IR parser intentionally supports only the 17 opcodes produced by Clang `-O0` and `opt -passes=mem2reg` on the benchmark suite (documented in `docs/OPCODE_INVENTORY.txt`). Uncataloged LLVM instructions raise `ParseError`.
2. **Parameter Parsing Scope**: The function signature parser on `define` lines assumes standard scalar and pointer arguments; complex argument formats (varargs, complex aggregates passed by value) are out of scope.
3. **Analysis Scope**: Liveness, CFG, loops, and interference analysis operate strictly within single-function boundaries (no inter-procedural optimization or whole-program analysis).
