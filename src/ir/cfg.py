from typing import List, Set
from src.ir.models import Function, BasicBlock

class CFGValidationException(Exception):
    pass

class CFGBuilder:
    @staticmethod
    def build(func: Function) -> List[str]:
        """
        Builds the CFG for a function.
        Populates the predecessors and successors of all BasicBlocks in the function.
        Duplicate edges (e.g. from a switch with multiple cases to the same block)
        are inherently handled by using Sets for predecessors and successors.
        
        Returns a list of warnings (e.g. unreachable blocks, entry block with predecessors).
        """
        warnings = []
        
        # Build label to block map
        label_to_block = {bb.label: bb for bb in func.blocks}
        if func.entry_block and func.entry_block.label == "<implicit_entry>":
            label_to_block[str(len(func.arguments))] = func.entry_block
        
        for bb in func.blocks:
            bb.predecessors.clear()
            bb.successors.clear()
            
        for bb in func.blocks:
            term = bb.terminator
            if not term:
                raise CFGValidationException(f"Block {bb.label} has no terminator")
                
            for target_label in term.target_labels:
                target_name = target_label[1:]
                target_bb = label_to_block.get(target_name)
                if not target_bb:
                    raise CFGValidationException(f"Terminator in {bb.label} targets missing block {target_label}")
                
                bb.successors.add(target_bb)
                target_bb.predecessors.add(bb)
                
        # Validate symmetry
        for bb in func.blocks:
            for succ in bb.successors:
                if bb not in succ.predecessors:
                    raise CFGValidationException(f"Asymmetric edge: {bb.label} -> {succ.label}")
            for pred in bb.predecessors:
                if bb not in pred.successors:
                    raise CFGValidationException(f"Asymmetric edge: {pred.label} -> {bb.label}")
                    
        # Check entry block predecessors
        if func.entry_block and func.entry_block.predecessors:
            warnings.append(f"Entry block {func.entry_block.label} has predecessors")
            
        # Reachability analysis
        reachable = set()
        if func.entry_block:
            worklist = [func.entry_block]
            while worklist:
                curr = worklist.pop()
                if curr not in reachable:
                    reachable.add(curr)
                    worklist.extend(curr.successors)
                    
        unreachable = [bb for bb in func.blocks if bb not in reachable]
        if unreachable:
            labels = [bb.label for bb in unreachable]
            warnings.append(f"Unreachable blocks detected: {', '.join(labels)}")
            
        return warnings

    @staticmethod
    def postorder(func: Function) -> List[BasicBlock]:
        if not func.entry_block:
            return []
            
        visited = set()
        result = []
        
        def dfs_deterministic(bb):
            visited.add(bb)
            for succ in sorted(bb.successors, key=lambda x: x.label):
                if succ not in visited:
                    dfs_deterministic(succ)
            result.append(bb)
            
        dfs_deterministic(func.entry_block)
        return result
        
    @staticmethod
    def reverse_postorder(func: Function) -> List[BasicBlock]:
        return CFGBuilder.postorder(func)[::-1]

def dump_cfg(func: Function) -> str:
    lines = [f"Function: {func.name}"]
    for bb in func.blocks:
        succ_labels = sorted(s.label for s in bb.successors)
        pred_labels = sorted(p.label for p in bb.predecessors)
        succ_str = ", ".join(succ_labels) if succ_labels else "none"
        pred_str = ", ".join(pred_labels) if pred_labels else "none"
        lines.append(f"  Block: {bb.label} -> succ:[{succ_str}] (pred:[{pred_str}])")
    return "\n".join(lines)
