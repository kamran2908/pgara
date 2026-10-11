import os
import sys
import subprocess
import pytest

from src.ir.parser import parse_module
from src.ir.cfg import CFGBuilder
from src.analysis.loop import LoopAnalyzer
from src.analysis.liveness import LivenessAnalyzer, dump_liveness
from src.analysis.interference import InterferenceAnalyzer, export_dot

OPT_FALLBACK = r"C:\LLVM-23.1.3\clang+llvm-23.1.3-x86_64-pc-windows-msvc\bin\opt.exe"
if "PGARA_OPT" not in os.environ and os.path.isfile(OPT_FALLBACK):
    os.environ["PGARA_OPT"] = OPT_FALLBACK

def _toolchain_available():
    try:
        from src.toolchain import find_tool
        find_tool("clang")
        find_tool("opt")
        return True
    except Exception:
        return False

def test_cli_help():
    proc = subprocess.run(
        [sys.executable, "run_phase1.py", "--help"],
        capture_output=True,
        text=True
    )
    assert proc.returncode == 0
    assert "usage:" in proc.stdout.lower()
    assert "--dump" in proc.stdout
    assert "--dot" in proc.stdout
    assert "--function" in proc.stdout

def test_cli_unknown_benchmark():
    proc = subprocess.run(
        [sys.executable, "run_phase1.py", "nonexistent"],
        capture_output=True,
        text=True
    )
    assert proc.returncode == 2
    assert "Unknown benchmark" in proc.stderr
    assert "Available benchmarks:" in proc.stderr

@pytest.mark.skipif(not _toolchain_available(), reason="LLVM toolchain (clang/opt) not found in PATH or environment")
def test_cli_dump_liveness(tmp_path):
    proc = subprocess.run(
        [sys.executable, "run_phase1.py", "--dump", "liveness", "b2_array_sum", "--out-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=True
    )
    mem2reg_path = tmp_path / "b2_array_sum.mem2reg.ll"
    assert mem2reg_path.exists()

    mod = parse_module(str(mem2reg_path))
    expected_dumps = []
    for func in sorted(mod.functions, key=lambda f: f.name):
        CFGBuilder.build(func)
        LivenessAnalyzer.analyze(func)
        expected_dumps.append(dump_liveness(func))
    expected_str = "\n".join(expected_dumps)

    assert proc.stdout.strip() == expected_str.strip()

@pytest.mark.skipif(not _toolchain_available(), reason="LLVM toolchain (clang/opt) not found in PATH or environment")
def test_cli_dot(tmp_path):
    proc = subprocess.run(
        [sys.executable, "run_phase1.py", "b2_array_sum", "--dot", "--out-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=True
    )
    mem2reg_path = tmp_path / "b2_array_sum.mem2reg.ll"
    assert mem2reg_path.exists()

    mod = parse_module(str(mem2reg_path))
    assert len(mod.functions) > 0
    for func in mod.functions:
        dot_file = tmp_path / f"b2_array_sum.{func.name}.dot"
        assert dot_file.exists()

        CFGBuilder.build(func)
        LoopAnalyzer.analyze(func)
        LivenessAnalyzer.analyze(func)
        ig_res = InterferenceAnalyzer.analyze(func)
        expected_dot = export_dot(func, ig_res)

        assert dot_file.read_text(encoding="utf-8").strip() == expected_dot.strip()
