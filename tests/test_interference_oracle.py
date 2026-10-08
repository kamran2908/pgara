from typing import Tuple, Set
from src.ir.models import Function, BasicBlock, Value
from src.analysis.liveness import LivenessAnalyzer

def oracle_is_live_at_point(V: Value, bb: BasicBlock, inst_idx: int, func: Function) -> bool:
    queue = []
    visited = set()
    queue.append((bb, bb, inst_idx + 1))
    
    while queue:
        curr, pred, start_idx = queue.pop(0)
        state = (curr, pred, start_idx)
        if state in visited:
            continue
        visited.add(state)
        
        is_defined = False
        used = False
        pred_label = LivenessAnalyzer.get_llvm_label(pred, func)
        
        for i in range(start_idx, len(curr.instructions)):
            inst = curr.instructions[i]
            if inst.opcode == "phi":
                if pred != curr:
                    for val, incoming_label in inst.incoming_values:
                        if incoming_label == pred_label and val == V:
                            used = True
                if inst.result == V:
                    is_defined = True
            else:
                if V in list(inst.uses()):
                    used = True
                if inst.result == V:
                    is_defined = True
                    
            if used or is_defined:
                break
                
        if used:
            return True
        if is_defined:
            continue
            
        for succ in curr.successors:
            queue.append((succ, curr, 0))
            
    return False

def get_oracle_interferences(func: Function) -> Set[Tuple[Value, Value]]:
    all_values = set(func.arguments)
    for bb in func.blocks:
        for inst in bb.instructions:
            if inst.result:
                all_values.add(inst.result)
                
    live_sets = []
    defs_at_point = []
    
    for bb in func.blocks:
        live_entry = {v for v in all_values if oracle_is_live_at_point(v, bb, -1, func)}
        live_sets.append(live_entry)
        if bb == func.entry_block:
            defs_at_point.append((set(func.arguments), live_entry))
            
        phis = [inst for inst in bb.instructions if inst.opcode == "phi"]
        if phis:
            phi_defs = {inst.result for inst in phis if inst.result}
            idx_after_phis = len(phis) - 1
            live_after_phis = {v for v in all_values if oracle_is_live_at_point(v, bb, idx_after_phis, func)}
            defs_at_point.append((phi_defs, live_after_phis))
            live_sets.append(live_after_phis)
            
        for i, inst in enumerate(bb.instructions):
            if inst.opcode == "phi":
                continue
            live_after = {v for v in all_values if oracle_is_live_at_point(v, bb, i, func)}
            live_sets.append(live_after)
            if inst.result:
                defs_at_point.append(({inst.result}, live_after))
                
    edges = set()
    def add_edge(x, y):
        if x != y:
            edges.add((x, y) if x.name < y.name else (y, x))
            
    for l_set in live_sets:
        l_list = list(l_set)
        for i in range(len(l_list)):
            for j in range(i+1, len(l_list)):
                add_edge(l_list[i], l_list[j])
                
    for defs, l_after in defs_at_point:
        d_list = list(defs)
        for i in range(len(d_list)):
            for j in range(i+1, len(d_list)):
                add_edge(d_list[i], d_list[j])
        for d in defs:
            for l in l_after:
                add_edge(d, l)
                
    return edges
