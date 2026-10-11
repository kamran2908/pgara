import glob
from pathlib import Path
import pytest
from src.ir.models import Function, BasicBlock, Instruction
from src.ir.parser import parse_module
from src.ir.cfg import CFGBuilder
from src.analysis.loop import LoopAnalyzer

def build_bb(label, targets):
    inst = Instruction(opcode="br", target_labels=[f"%{t}" for t in targets])
    bb = BasicBlock(label=label, instructions=[inst])
    return bb

def link_blocks(func: Function):
    CFGBuilder.build(func)

def test_straight_line():
    b1 = build_bb("1", ["2"])
    b2 = build_bb("2", ["3"])
    b3 = build_bb("3", [])
    func = Function(name="test", blocks=[b1, b2, b3], entry_block=b1)
    link_blocks(func)
    
    res = LoopAnalyzer.analyze(func)
    assert not res.is_irreducible
    assert not res.back_edges
    assert all(b.loop_depth == 0 for b in func.blocks)

def test_single_loop():
    b1 = build_bb("1", ["2"])
    b2 = build_bb("2", ["3", "2"])
    b3 = build_bb("3", [])
    func = Function(name="test", blocks=[b1, b2, b3], entry_block=b1)
    link_blocks(func)
    
    res = LoopAnalyzer.analyze(func)
    assert not res.is_irreducible
    assert res.back_edges == [(b2, b2)]
    assert b2.loop_depth == 1
    assert b1.loop_depth == 0
    assert b3.loop_depth == 0
    assert res.merged_loops[b2] == {b2}

def test_doubly_nested_loop():
    b1 = build_bb("1", ["2"])
    b2 = build_bb("2", ["3", "5"])
    b3 = build_bb("3", ["3", "4"])
    b4 = build_bb("4", ["2"])
    b5 = build_bb("5", [])
    func = Function(name="test", blocks=[b1, b2, b3, b4, b5], entry_block=b1)
    link_blocks(func)
    
    res = LoopAnalyzer.analyze(func)
    assert not res.is_irreducible
    assert set(res.back_edges) == {(b3, b3), (b4, b2)}
    assert res.merged_loops[b2] == {b2, b3, b4}
    assert res.merged_loops[b3] == {b3}
    assert b1.loop_depth == 0
    assert b2.loop_depth == 1
    assert b3.loop_depth == 2
    assert b4.loop_depth == 1
    assert b5.loop_depth == 0

def test_loop_with_early_exit():
    b1 = build_bb("1", ["2"])
    b2 = build_bb("2", ["3"])
    b3 = build_bb("3", ["4", "2"]) # 4 is exit, 2 is header
    b4 = build_bb("4", [])
    func = Function(name="test", blocks=[b1, b2, b3, b4], entry_block=b1)
    link_blocks(func)
    
    res = LoopAnalyzer.analyze(func)
    assert set(res.back_edges) == {(b3, b2)}
    assert res.merged_loops[b2] == {b2, b3}
    assert b1.loop_depth == 0
    assert b2.loop_depth == 1
    assert b3.loop_depth == 1
    assert b4.loop_depth == 0

def test_sibling_loops():
    b1 = build_bb("1", ["2"])
    b2 = build_bb("2", ["2", "3"])
    b3 = build_bb("3", ["3", "4"])
    b4 = build_bb("4", [])
    func = Function(name="test", blocks=[b1, b2, b3, b4], entry_block=b1)
    link_blocks(func)
    
    res = LoopAnalyzer.analyze(func)
    assert set(res.back_edges) == {(b2, b2), (b3, b3)}
    assert res.merged_loops[b2] == {b2}
    assert res.merged_loops[b3] == {b3}
    assert b2.loop_depth == 1
    assert b3.loop_depth == 1
    assert b1.loop_depth == 0
    assert b4.loop_depth == 0

def test_irreducible_cfg():
    b1 = build_bb("1", ["2", "3"])
    b2 = build_bb("2", ["3", "4"])
    b3 = build_bb("3", ["2", "4"])
    b4 = build_bb("4", [])
    func = Function(name="test", blocks=[b1, b2, b3, b4], entry_block=b1)
    link_blocks(func)
    
    res = LoopAnalyzer.analyze(func)
    assert res.is_irreducible

def test_integration_every_parsed_benchmark():
    repo_root = Path(__file__).resolve().parent.parent
    ir_dir = repo_root / "results" / "raw" / "ir"
    files = sorted(ir_dir.glob("*.mem2reg.ll"))
    assert len(files) > 0, f"No mem2reg IR files found in {ir_dir}"
        
    checked_count = 0
    for f in files:
        mod = parse_module(str(f))
        for func in mod.functions:
            CFGBuilder.build(func)
            res = LoopAnalyzer.analyze(func)
            if not res.is_irreducible:
                assert set(res.back_edges) == set(res.retreating_edges)
            checked_count += 1
    print(f"\nIntegration test checked {checked_count} functions for reducibility.")
