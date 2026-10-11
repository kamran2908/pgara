import glob
from pathlib import Path
import pytest
from src.ir.models import Function, BasicBlock, Instruction, Value
from src.ir.parser import parse_module
from src.ir.cfg import CFGBuilder
from src.analysis.liveness import LivenessAnalyzer
from src.analysis.interference import InterferenceAnalyzer, export_dot, InterferenceResult
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
    repo_root = Path(__file__).resolve().parent.parent
    ir_dir = repo_root / "results" / "raw" / "ir"
    files = sorted(ir_dir.glob("*.mem2reg.ll"))
    assert len(files) > 0, f"No mem2reg IR files found in {ir_dir}"
        
    funcs_checked = 0
    mismatches = 0
    
    for f in files:
        mod = parse_module(str(f))
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

def test_export_dot_hand_built_exact():
    """Verify export_dot produces the exact expected DOT string derived by hand."""
    va = Value("%a")
    vb = Value("%b")
    vc = Value("%c")
    func = Function(name="tiny_func")
    res = InterferenceResult()
    res.graph.add_node(va)
    res.graph.add_node(vb)
    res.graph.add_node(vc)
    res.graph.add_edge(va, vb)
    res.graph.add_edge(vb, vc)
    
    expected_dot = (
        'graph IG_tiny_func {\n'
        '  "%a";\n'
        '  "%b";\n'
        '  "%c";\n'
        '  "%a" -- "%b";\n'
        '  "%b" -- "%c";\n'
        '}'
    )
    assert export_dot(func, res) == expected_dot

def test_export_dot_real_function_edge_count_and_determinism():
    """Verify export_dot edge line count matches graph edge count and is deterministic."""
    repo_root = Path(__file__).resolve().parent.parent
    b2_file = repo_root / "results" / "raw" / "ir" / "b2_array_sum.mem2reg.ll"
    assert b2_file.is_file(), f"{b2_file} must exist"
    mod = parse_module(str(b2_file))
    func = mod.functions[0]
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)

    dot1 = export_dot(func, res)
    dot2 = export_dot(func, res)
    assert dot1 == dot2

    edge_lines = [line for line in dot1.splitlines() if " -- " in line]
    assert len(edge_lines) == res.graph.number_of_edges()

def test_unused_argument_interferes_with_all_arguments_documented_decision():
    """
    Documented design decision (Phase 1, interference.py lines 61-66):
    The entry block creates an all-to-all interference clique among all function arguments
    and live values at function entry, even if an argument is completely unused in the function body.
    """
    arg1 = Value("%arg1")
    arg2 = Value("%arg2")  # Unused argument
    res_val = Value("%res")
    
    inst1 = Instruction(opcode="add", result=res_val, operands=[arg1, "1"], raw_text="%res = add i32 %arg1, 1")
    inst2 = Instruction(opcode="ret", operands=[res_val], raw_text="ret i32 %res")
    bb = BasicBlock(label="entry", instructions=[inst1, inst2])
    func = Function(name="fn_unused_arg", arguments=[arg1, arg2], blocks=[bb], entry_block=bb)
    
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)
    
    assert res.graph.has_edge(arg1, arg2)

def test_dead_definition_interferes_with_live_values_but_excluded_from_pressure():
    """
    A dead definition interferes with values live at its definition point,
    but is not itself counted toward that point's register pressure (derived by hand).
    """
    live_val = Value("%live_val")
    dead_val = Value("%dead_val")
    
    # %live_val is defined and live until ret
    inst1 = Instruction(opcode="add", result=live_val, operands=["1", "2"], raw_text="%live_val = add i32 1, 2")
    # %dead_val is defined here while %live_val is live, but %dead_val is never used
    inst2 = Instruction(opcode="add", result=dead_val, operands=["3", "4"], raw_text="%dead_val = add i32 3, 4")
    # %live_val is used here
    inst3 = Instruction(opcode="ret", operands=[live_val], raw_text="ret i32 %live_val")
    
    bb = BasicBlock(label="entry", instructions=[inst1, inst2, inst3])
    func = Function(name="fn_dead_def", arguments=[], blocks=[bb], entry_block=bb)
    
    CFGBuilder.build(func)
    LivenessAnalyzer.analyze(func)
    res = InterferenceAnalyzer.analyze(func)
    
    # %dead_val must interfere with %live_val because %live_val was live across inst2
    assert res.graph.has_edge(dead_val, live_val)
    # Expected pressure derived by hand:
    # At inst3 uses: live={%live_val}, len=1
    # At inst2 def: %live_val is live (1). dead_val discarded, uses 3,4 (no values), len=1
    # At inst1 def: %live_val discarded, uses 1,2, len=0
    # Entry max pressure is therefore 1 (dead_val is not counted)
    assert res.block_pressure[bb] == 1
    assert res.max_pressure == 1
