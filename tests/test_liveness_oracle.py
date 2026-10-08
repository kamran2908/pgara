from typing import Tuple
from src.ir.models import Function, BasicBlock, Value
from src.ir.parser import parse_module
from src.ir.cfg import CFGBuilder
from src.analysis.liveness import LivenessAnalyzer

def oracle_is_live_out(V: Value, start_B: BasicBlock, func: Function) -> bool:
    queue = []
    visited = set()
    for succ in start_B.successors:
        queue.append((succ, start_B))
        
    while queue:
        curr, pred = queue.pop(0)
        state = (curr, pred)
        if state in visited:
            continue
        visited.add(state)
        
        # 1. Check phis
        is_defined = False
        used_in_phi = False
        pred_label = LivenessAnalyzer.get_llvm_label(pred, func)
        for inst in curr.instructions:
            if inst.opcode == "phi":
                for val, incoming_label in inst.incoming_values:
                    if incoming_label == pred_label and val == V:
                        used_in_phi = True
                if inst.result == V:
                    is_defined = True
            else:
                break
                
        if used_in_phi:
            return True
        if is_defined:
            continue # Path killed
            
        # 2. Check non-phis
        used_in_non_phi = False
        defined_in_non_phi = False
        for inst in curr.instructions:
            if inst.opcode == "phi": continue
            if V in list(inst.uses()):
                used_in_non_phi = True
                break
            if inst.result == V:
                defined_in_non_phi = True
                break
                
        if used_in_non_phi:
            return True
        if defined_in_non_phi:
            continue # Path killed
            
        # 3. Propagate to successors
        for succ in curr.successors:
            queue.append((succ, curr))
            
    return False

def check_oracle(func: Function) -> Tuple[int, int]:
    # Gather all local values
    all_values = set(func.arguments)
    for bb in func.blocks:
        for inst in bb.instructions:
            if inst.result:
                all_values.add(inst.result)
                
    checked_blocks = 0
    for bb in func.blocks:
        for V in all_values:
            oracle_live = oracle_is_live_out(V, bb, func)
            computed_live = V in bb.live_out
            assert oracle_live == computed_live, f"Oracle mismatch for {V.name} at {bb.label}: oracle={oracle_live}, computed={computed_live}"
        checked_blocks += 1
    return 1, checked_blocks
