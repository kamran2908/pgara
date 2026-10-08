import os
import glob
import tempfile
import pytest
from src.ir.parser import parse_module, parse_instruction, ParseError
from src.ir.models import Value, Instruction

def test_snippets():
    # Write a snippet file covering: phi, switch, br (cond/uncond), calls (void/non-void), %struct, numeric labels, unnamed entry
    snippet = """
define void @test(i32 %0, ptr %1) {
  %3 = add i32 %0, 1
  br label %4

4:
  %5 = phi i32 [ 0, %2 ], [ %3, %4 ]
  switch i32 %5, label %6 [
    i32 0, label %7
  ]

6:
  br i1 1, label %7, label %4

7:
  %8 = call i32 @some_func(ptr %1, %struct.Foo* null)
  call void @void_func()
  ret void
}
"""
    with tempfile.NamedTemporaryFile("w", delete=False, encoding='utf-8') as f:
        f.write(snippet)
        temp_name = f.name
        
    try:
        mod = parse_module(temp_name)
        assert len(mod.functions) == 1
        func = mod.functions[0]
        
        assert func.name == "test"
        assert len(func.arguments) == 2
        assert func.arguments[0].name == "%0"
        assert func.arguments[1].name == "%1"
        
        assert len(func.blocks) == 4
        # Implicit entry
        assert func.blocks[0].label == "<implicit_entry>"
        assert len(func.blocks[0].instructions) == 2
        assert func.blocks[0].instructions[1].opcode == "br"
        assert func.blocks[0].instructions[1].target_labels == ["%4"]
        
        # Block 4
        assert func.blocks[1].label == "4"
        assert func.blocks[1].instructions[0].opcode == "phi"
        assert func.blocks[1].instructions[0].incoming_values == [("0", "%2"), (Value("%3"), "%4")]
        
        assert func.blocks[1].instructions[1].opcode == "switch"
        assert func.blocks[1].instructions[1].target_labels == ["%6", "%7"]
        assert list(func.blocks[1].instructions[1].uses()) == [Value("%5")]
        
        # Block 6
        assert func.blocks[2].label == "6"
        assert func.blocks[2].instructions[0].opcode == "br"
        assert func.blocks[2].instructions[0].target_labels == ["%7", "%4"]
        
        # Block 7
        assert func.blocks[3].label == "7"
        assert func.blocks[3].instructions[0].opcode == "call"
        assert func.blocks[3].instructions[0].result == Value("%8")
        uses_call1 = list(func.blocks[3].instructions[0].uses())
        assert len(uses_call1) == 1
        assert uses_call1[0] == Value("%1") # %struct.Foo* must NOT be captured as a value!
        
        assert func.blocks[3].instructions[1].opcode == "call"
        assert func.blocks[3].instructions[1].result is None
        
        assert func.blocks[3].instructions[2].opcode == "ret"
    finally:
        os.remove(temp_name)

def test_integration_mem2reg_files():
    files = glob.glob("results/raw/ir/*.mem2reg.ll")
    if not files:
        pytest.skip("No mem2reg IR files found")
        
    for f in files:
        mod = parse_module(f)
        for func in mod.functions:
            # Gather defined locals
            defined_locals = {arg.name for arg in func.arguments}
            for bb in func.blocks:
                for inst in bb.instructions:
                    if inst.result:
                        defined_locals.add(inst.result.name)
            
            # Map implicit entry label
            block_labels = {bb.label for bb in func.blocks}
            implicit_id = f"%{len(func.arguments)}"
            
            for bb in func.blocks:
                if bb.label == "<implicit_entry>":
                    block_labels.add(implicit_id[1:])
                
                # Check terminator
                assert len(bb.instructions) > 0, f"Empty block {bb.label} in {func.name}"
                term = bb.instructions[-1]
                assert term.is_terminator, f"Block {bb.label} in {func.name} does not end with a terminator. Ends with {term.opcode}"
                
                # Check that only the last instruction is a terminator
                for i in range(len(bb.instructions) - 1):
                    assert not bb.instructions[i].is_terminator, f"Early terminator in block {bb.label} of {func.name}"

                for inst in bb.instructions:
                    # Check targets
                    for t in inst.target_labels:
                        assert t[1:] in block_labels, f"Target label {t} not found in {f} ({func.name})"
                    
                    if inst.opcode == "phi":
                        for val, pred in inst.incoming_values:
                            assert pred[1:] in block_labels, f"Phi pred label {pred} not found in {f} ({func.name})"
                    
                    # Check uses
                    for use in inst.uses():
                        assert use.name in defined_locals, f"Value {use.name} used but not defined in {f} ({func.name})"
