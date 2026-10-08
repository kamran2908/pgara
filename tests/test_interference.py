import glob
import pytest
from src.ir.models import Function, BasicBlock, Instruction, Value
from src.ir.parser import parse_module
from src.ir.cfg import CFGBuilder
from src.analysis.liveness import LivenessAnalyzer
from src.analysis.interference import InterferenceAnalyzer
from tests.test_interference_oracle import get_oracle_interferences

def build_bb(label, insts):
    return BasicBlock(label=label, instructions=insts)

def has_edge(res, u, v):
    return res.graph.has_edge(u, v)

def test_hand_overlap():
    v1, v2 = Value("%1"), Value("%2")
    i1 = Instruction("add", result=v1, operands=[])
    i2 = Instruction("add", result=v2, operands=[])
    i3 = Instruction("add", result=None, operands=[v1, v2])
    i4 = Instruction("ret", target_labels=[])
    b1 = build_bb("1", [i1, i2, i3, i4])
    func = Function(name="test", arguments=[], blocks=[b1], entry_block=b1)
    
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)
    
    assert has_edge(res, v1, v2)
    assert res.block_pressure[b1] == 2

def test_hand_no_overlap():
    v1, v2 = Value("%1"), Value("%2")
    i1 = Instruction("add", result=v1, operands=[])
    i2 = Instruction("add", result=None, operands=[v1])
    i3 = Instruction("add", result=v2, operands=[])
    i4 = Instruction("add", result=None, operands=[v2])
    i5 = Instruction("ret", target_labels=[])
    b1 = build_bb("1", [i1, i2, i3, i4, i5])
    func = Function(name="test", arguments=[], blocks=[b1], entry_block=b1)
    
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)
    
    assert not has_edge(res, v1, v2)
    assert res.block_pressure[b1] == 1

def test_hand_dead_def():
    v1, v2 = Value("%1"), Value("%2")
    i1 = Instruction("add", result=v1, operands=[])
    i2 = Instruction("add", result=v2, operands=[]) # dead
    i3 = Instruction("add", result=None, operands=[v1])
    i4 = Instruction("ret", target_labels=[])
    b1 = build_bb("1", [i1, i2, i3, i4])
    func = Function(name="test", arguments=[], blocks=[b1], entry_block=b1)
    
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)
    
    assert has_edge(res, v1, v2)

def test_hand_phi_interfere():
    v1, v2 = Value("%1"), Value("%2")
    i1 = Instruction("phi", result=v1, incoming_values=[])
    i2 = Instruction("phi", result=v2, incoming_values=[])
    i3 = Instruction("add", result=None, operands=[v1])
    i4 = Instruction("add", result=None, operands=[v2])
    i5 = Instruction("ret", target_labels=[])
    b1 = build_bb("1", [i1, i2, i3, i4, i5])
    func = Function(name="test", arguments=[], blocks=[b1], entry_block=b1)
    
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)
    
    assert has_edge(res, v1, v2)

def test_hand_args_interfere():
    v1, v2 = Value("%1"), Value("%2")
    i1 = Instruction("add", result=None, operands=[v1])
    i2 = Instruction("add", result=None, operands=[v2])
    i3 = Instruction("ret", target_labels=[])
    b1 = build_bb("1", [i1, i2, i3])
    func = Function(name="test", arguments=[v1, v2], blocks=[b1], entry_block=b1)
    
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)
    
    assert has_edge(res, v1, v2)

def test_hand_loop_carried():
    v1, vc = Value("%1"), Value("%c")
    b1 = build_bb("1", [Instruction("br", target_labels=["%2"])])
    b2 = build_bb("2", [
        Instruction("br", operands=[vc], target_labels=["%2", "%4"])
    ])
    b4 = build_bb("4", [Instruction("ret", operands=[v1], target_labels=[])])
    func = Function(name="test", arguments=[v1, vc], blocks=[b1, b2, b4], entry_block=b1)
    
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)
    
    assert has_edge(res, v1, vc)
    assert res.block_pressure[b2] == 2

def test_integration_every_parsed_benchmark():
    files = glob.glob("results/raw/ir/*.mem2reg.ll")
    if not files:
        pytest.skip("No IR files found")
        
    funcs_checked = 0
    mismatches = 0
    
    for f in files:
        mod = parse_module(f)
        for func in mod.functions:
            CFGBuilder.build(func)
            LivenessAnalyzer.analyze(func)
            res = InterferenceAnalyzer.analyze(func)
            
            # 1. Oracle Check
            oracle_edges = get_oracle_interferences(func)
            
            res_edges = set()
            for u, v in res.graph.edges():
                res_edges.add((u, v) if u.name < v.name else (v, u))
                
            if oracle_edges != res_edges:
                print(f"Mismatch in {func.name}:")
                print(f"  Oracle - Res = {oracle_edges - res_edges}")
                print(f"  Res - Oracle = {res_edges - oracle_edges}")
                mismatches += 1
                
            # 2. Pressure sanity check
            for bb in func.blocks:
                assert res.block_pressure[bb] >= len(bb.live_in)
                assert res.block_pressure[bb] >= len(bb.live_out)
                
            funcs_checked += 1
            
    assert mismatches == 0, f"Found {mismatches} mismatching functions."
    print(f"\nIntegration test checked oracle for {funcs_checked} functions.")
