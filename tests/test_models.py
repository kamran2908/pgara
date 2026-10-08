from src.ir.models import Value, Instruction, BasicBlock, Function, Module

def test_value_equality_hash():
    v1 = Value("%5")
    v2 = Value("%5")
    v3 = Value("%x")
    
    assert v1 == v2
    assert v1 != v3
    
    # Test hash behavior in sets
    s = {v1, v3}
    assert v2 in s
    assert len(s) == 2

def test_instruction_helpers():
    # phi test
    v1 = Value("%1")
    res = Value("%3")
    phi_inst = Instruction(
        opcode="phi",
        result=res,
        incoming_values=[(v1, "bb1"), ("42", "bb2")]
    )
    assert phi_inst.is_phi is True
    assert phi_inst.is_terminator is False
    assert phi_inst.defs() == {res}
    assert phi_inst.uses() == {v1}  # "42" is not a Value object
    
    # terminator test
    term_inst = Instruction(
        opcode="br",
        target_labels=["bb1", "bb2"]
    )
    assert term_inst.is_terminator is True
    assert term_inst.is_phi is False
    assert term_inst.defs() == set()
    assert term_inst.uses() == set()

    # normal instruction test
    op_inst = Instruction(
        opcode="add",
        result=Value("%4"),
        operands=[Value("%1"), Value("%2")]
    )
    assert op_inst.is_phi is False
    assert op_inst.is_terminator is False
    assert op_inst.defs() == {Value("%4")}
    assert op_inst.uses() == {Value("%1"), Value("%2")}

def test_basic_block_helpers():
    phi = Instruction(opcode="phi", result=Value("%2"))
    add = Instruction(opcode="add", result=Value("%3"))
    br = Instruction(opcode="br", target_labels=["bb2"])
    
    bb = BasicBlock(
        label="bb1",
        instructions=[phi, add, br]
    )
    
    assert bb.phis == [phi]
    assert bb.non_phi_instructions == [add, br]
    assert bb.terminator == br
