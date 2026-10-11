import glob
from pathlib import Path
import pytest
from src.ir.models import Function, BasicBlock, Instruction, Value
from src.ir.parser import parse_module
from src.ir.cfg import CFGBuilder
from src.analysis.liveness import LivenessAnalyzer
from tests.test_liveness_oracle import check_oracle

def build_bb(label, insts):
    return BasicBlock(label=label, instructions=insts)

def test_hand_straight_line():
    # %1 = add %0, 1
    # ret %1
    v0 = Value("%0")
    v1 = Value("%1")
    i1 = Instruction("add", result=v1, operands=[v0])
    i2 = Instruction("ret", result=None, operands=[v1], target_labels=[])
    
    b1 = build_bb("1", [i1])
    b2 = build_bb("2", [i2])
    
    func = Function(name="test", arguments=[v0], blocks=[b1, b2], entry_block=b1)
    b1.instructions[0].target_labels = ["%2"]
    b1.instructions.append(Instruction("br", target_labels=["%2"]))
    CFGBuilder.build(func)
    
    LivenessAnalyzer.analyze(func)
    
    assert b1.live_in == set()
    assert b1.live_out == {v1}
    assert b2.live_in == {v1}
    assert b2.live_out == set()

def test_hand_diamond_phi():
    # b1: br %c, 2, 3
    # b2: %2 = 1, br 4
    # b3: %3 = 2, br 4
    # b4: %4 = phi [ %2, 2 ], [ %3, 3 ]
    vc = Value("%c")
    v2 = Value("%2")
    v3 = Value("%3")
    v4 = Value("%4")
    
    b1 = build_bb("1", [Instruction("br", operands=[vc], target_labels=["%2", "%3"])])
    b2 = build_bb("2", [Instruction("add", result=v2), Instruction("br", target_labels=["%4"])])
    b3 = build_bb("3", [Instruction("add", result=v3), Instruction("br", target_labels=["%4"])])
    b4 = build_bb("4", [
        Instruction("phi", result=v4, incoming_values=[(v2, "%2"), (v3, "%3")]),
        Instruction("ret", operands=[v4], target_labels=[])
    ])
    
    func = Function(name="test", arguments=[vc], blocks=[b1, b2, b3, b4], entry_block=b1)
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    
    # live_out of b2 should be {v2} (due to phi in b4)
    assert v2 in b2.live_out
    assert v3 not in b2.live_out
    # live_out of b3 should be {v3}
    assert v3 in b3.live_out
    assert v2 not in b3.live_out
    # live_in of b4 should be empty because phi uses are read on the edge!
    assert v2 not in b4.live_in
    assert v3 not in b4.live_in
    assert v4 not in b4.live_in

def test_hand_loop_carried_phi():
    # 1: br 2
    # 2: %2 = phi [ %0, 1 ], [ %3, 2 ]
    #    %3 = add %2, 1
    #    br %c, 2, 4
    # 4: ret %2
    v0, v2, v3, vc = Value("%0"), Value("%2"), Value("%3"), Value("%c")
    b1 = build_bb("1", [Instruction("br", target_labels=["%2"])])
    b2 = build_bb("2", [
        Instruction("phi", result=v2, incoming_values=[(v0, "%1"), (v3, "%2")]),
        Instruction("add", result=v3, operands=[v2]),
        Instruction("br", operands=[vc], target_labels=["%2", "%4"])
    ])
    b4 = build_bb("4", [Instruction("ret", operands=[v2], target_labels=[])])
    func = Function(name="test", arguments=[v0, vc], blocks=[b1, b2, b4], entry_block=b1)
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    
    # live_out of b2 is {v2, v3, vc} because v3 is used in phi on back-edge, v2 is used in b4, vc is used in branch
    assert b2.live_out == {v2, v3, vc}

def test_hand_value_across_loop():
    # %0 is passed to entry, used ONLY in exit block 4
    # 1: br 2
    # 2: br %c, 2, 4
    # 4: ret %0
    v0, vc = Value("%0"), Value("%c")
    b1 = build_bb("1", [Instruction("br", target_labels=["%2"])])
    b2 = build_bb("2", [Instruction("br", operands=[vc], target_labels=["%2", "%4"])])
    b4 = build_bb("4", [Instruction("ret", operands=[v0], target_labels=[])])
    func = Function(name="test", arguments=[v0, vc], blocks=[b1, b2, b4], entry_block=b1)
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    
    # %0 is live in all blocks
    assert v0 in b1.live_out
    assert v0 in b2.live_in
    assert v0 in b2.live_out

def test_hand_dead_value():
    v0 = Value("%0")
    vd = Value("%dead")
    b1 = build_bb("1", [Instruction("add", result=vd), Instruction("ret", operands=[v0], target_labels=[])])
    func = Function(name="test", arguments=[v0], blocks=[b1], entry_block=b1)
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    assert vd not in b1.live_out
    assert vd not in b1.live_in

def test_integration_every_parsed_benchmark():
    repo_root = Path(__file__).resolve().parent.parent
    ir_dir = repo_root / "results" / "raw" / "ir"
    files = sorted(ir_dir.glob("*.mem2reg.ll"))
    assert len(files) > 0, f"No mem2reg IR files found in {ir_dir}"
        
    funcs_checked = 0
    blocks_checked = 0
    for f in files:
        mod = parse_module(str(f))
        for func in mod.functions:
            CFGBuilder.build(func)
            warnings = LivenessAnalyzer.analyze(func)
            
            # Check Oracle
            f_c, b_c = check_oracle(func)
            funcs_checked += f_c
            blocks_checked += b_c
            
            # Ensure no warnings about entry block non-args
            assert not any("Entry block live-in contains non-arguments" in w for w in warnings)
            assert not any("but not dominated by its definition" in w for w in warnings)
            
    print(f"\nIntegration test checked oracle for {funcs_checked} functions and {blocks_checked} blocks.")
