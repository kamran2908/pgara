import glob
import pytest
from src.ir.models import Function, BasicBlock, Instruction
from src.ir.cfg import CFGBuilder, CFGValidationException
from src.ir.parser import parse_module

def build_bb(label, targets):
    inst = Instruction(opcode="br", target_labels=[f"%{t}" for t in targets])
    bb = BasicBlock(label=label, instructions=[inst])
    return bb

def test_hand_built_straight_line():
    b1 = build_bb("1", ["2"])
    b2 = build_bb("2", ["3"])
    b3 = build_bb("3", [])
    b3.instructions[0].opcode = "ret"
    b3.instructions[0].target_labels = []
    
    func = Function(name="test", blocks=[b1, b2, b3], entry_block=b1)
    warnings = CFGBuilder.build(func)
    assert not warnings
    
    assert b1.successors == {b2}
    assert b2.successors == {b3}
    assert b3.successors == set()
    
    assert b1.predecessors == set()
    assert b2.predecessors == {b1}
    assert b3.predecessors == {b2}

def test_hand_built_diamond():
    b1 = build_bb("1", ["2", "3"])
    b2 = build_bb("2", ["4"])
    b3 = build_bb("3", ["4"])
    b4 = build_bb("4", [])
    b4.instructions[0].opcode = "ret"
    b4.instructions[0].target_labels = []
    
    func = Function(name="test", blocks=[b1, b2, b3, b4], entry_block=b1)
    CFGBuilder.build(func)
    
    assert b1.successors == {b2, b3}
    assert b4.predecessors == {b2, b3}

def test_hand_built_simple_loop():
    b1 = build_bb("1", ["2"])
    b2 = build_bb("2", ["3", "4"])
    b3 = build_bb("3", ["2"])
    b4 = build_bb("4", [])
    b4.instructions[0].opcode = "ret"
    b4.instructions[0].target_labels = []
    
    func = Function(name="test", blocks=[b1, b2, b3, b4], entry_block=b1)
    CFGBuilder.build(func)
    
    assert b2.predecessors == {b1, b3}
    assert b2.successors == {b3, b4}

def test_switch_duplicate_targets():
    b1 = build_bb("1", ["2", "2", "3"])
    b1.instructions[0].opcode = "switch"
    b2 = build_bb("2", ["4"])
    b3 = build_bb("3", ["4"])
    b4 = build_bb("4", [])
    b4.instructions[0].opcode = "ret"
    b4.instructions[0].target_labels = []
    
    func = Function(name="test", blocks=[b1, b2, b3, b4], entry_block=b1)
    CFGBuilder.build(func)
    
    # Due to Sets, the duplicate "2" targets will be merged into a single edge
    assert b1.successors == {b2, b3}
    assert b2.predecessors == {b1}

def test_unreachable_block():
    b1 = build_bb("1", ["2"])
    b2 = build_bb("2", [])
    b2.instructions[0].opcode = "ret"
    b2.instructions[0].target_labels = []
    b3 = build_bb("3", ["2"]) # Unreachable
    
    func = Function(name="test", blocks=[b1, b2, b3], entry_block=b1)
    warnings = CFGBuilder.build(func)
    assert any("Unreachable" in w for w in warnings)
    
def test_integration_every_parsed_benchmark():
    files = glob.glob("results/raw/ir/*.mem2reg.ll")
    if not files:
        pytest.skip("No IR files found")
        
    for f in files:
        mod = parse_module(f)
        for func in mod.functions:
            warnings = CFGBuilder.build(func)
            # The validation logic inside build() ensures symmetry and valid targets
            # We also ensure entry block has no predecessors
            assert not any("Entry block" in w and "has predecessors" in w for w in warnings)
