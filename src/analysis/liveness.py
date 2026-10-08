from typing import Set, Dict, List
from src.ir.models import Function, BasicBlock, Value
from src.ir.cfg import CFGBuilder
from src.analysis.loop import LoopAnalyzer

class LivenessAnalyzer:
    @staticmethod
    def get_llvm_label(bb: BasicBlock, func: Function) -> str:
        if bb.label == "<implicit_entry>":
            return f"%{len(func.arguments)}"
        return f"%{bb.label}"

    @staticmethod
    def compute_local_liveness(func: Function) -> Tuple[Dict[BasicBlock, Set[Value]], Dict[BasicBlock, Set[Value]]]:
        def_B = {}
        use_B = {}
        for bb in func.blocks:
            d = set()
            u = set()
            
            if bb == func.entry_block:
                for arg in func.arguments:
                    d.add(arg)
                    
            for inst in bb.instructions:
                if inst.opcode == "phi":
                    if inst.result:
                        d.add(inst.result)
                    continue
                    
                for val in inst.uses():
                    if isinstance(val, Value) and val not in d:
                        u.add(val)
                        
                if inst.result:
                    d.add(inst.result)
                    
            def_B[bb] = d
            use_B[bb] = u
        return def_B, use_B

    @staticmethod
    def get_phi_out(B: BasicBlock, S: BasicBlock, func: Function) -> Set[Value]:
        phi_out = set()
        label_B = LivenessAnalyzer.get_llvm_label(B, func)
        for inst in S.instructions:
            if inst.opcode == "phi":
                for val, pred_label in inst.incoming_values:
                    if pred_label == label_B:
                        if isinstance(val, Value):
                            phi_out.add(val)
            else:
                break
        return phi_out

    @staticmethod
    def analyze(func: Function) -> List[str]:
        warnings = []
        def_B, use_B = LivenessAnalyzer.compute_local_liveness(func)
        
        postorder_blocks = CFGBuilder.postorder(func)
        reachable = set(postorder_blocks)
        
        for bb in func.blocks:
            bb.live_in = set()
            bb.live_out = set()
            
        changed = True
        iterations = 0
        while changed:
            changed = False
            iterations += 1
            for bb in postorder_blocks:
                old_in = bb.live_in.copy()
                
                new_out = set()
                for succ in bb.successors:
                    if succ in reachable:
                        new_out.update(succ.live_in)
                        new_out.update(LivenessAnalyzer.get_phi_out(bb, succ, func))
                        
                bb.live_out = new_out
                new_in = use_B[bb].union(bb.live_out - def_B[bb])
                
                if new_in != old_in:
                    bb.live_in = new_in
                    changed = True
                    
        # Sanity Checks
        if func.entry_block:
            args_set = set(func.arguments)
            invalid_in = func.entry_block.live_in - args_set
            if invalid_in:
                names = [v.name for v in invalid_in]
                warnings.append(f"Entry block live-in contains non-arguments: {', '.join(names)}")
                
        doms = LoopAnalyzer.compute_dominators(func, reachable)
        def_block = {}
        for bb in func.blocks:
            for v in def_B[bb]:
                def_block[v] = bb
                
        for bb in postorder_blocks:
            for v in bb.live_in:
                d_bb = def_block.get(v)
                if d_bb and d_bb not in doms.get(bb, set()):
                    warnings.append(f"Value {v.name} is live-in at {bb.label} but not dominated by its definition at {d_bb.label}")
                    
        warnings.append(f"Fixpoint reached in {iterations} iterations (postorder).")
        return warnings

def dump_liveness(func: Function) -> str:
    def_B, use_B = LivenessAnalyzer.compute_local_liveness(func)
    lines = [f"Function: {func.name}"]
    for bb in CFGBuilder.postorder(func)[::-1]: # Reverse postorder for readable dump
        u_str = ", ".join(sorted(v.name for v in use_B[bb]))
        d_str = ", ".join(sorted(v.name for v in def_B[bb]))
        li_str = ", ".join(sorted(v.name for v in bb.live_in))
        lo_str = ", ".join(sorted(v.name for v in bb.live_out))
        
        lines.append(f"  Block: {bb.label}")
        lines.append(f"    use:      [{u_str}]")
        lines.append(f"    def:      [{d_str}]")
        lines.append(f"    live_in:  [{li_str}]")
        lines.append(f"    live_out: [{lo_str}]")
    return "\n".join(lines)
