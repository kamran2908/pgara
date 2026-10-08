from typing import List, Set, Dict, Tuple
from src.ir.models import Function, BasicBlock

class LoopAnalysisResult:
    def __init__(self):
        self.dominators: Dict[BasicBlock, Set[BasicBlock]] = {}
        self.back_edges: List[Tuple[BasicBlock, BasicBlock]] = [] # (u, v)
        self.retreating_edges: List[Tuple[BasicBlock, BasicBlock]] = []
        self.is_irreducible: bool = False
        self.merged_loops: Dict[BasicBlock, Set[BasicBlock]] = {} # header -> body_blocks

class LoopAnalyzer:
    @staticmethod
    def compute_reachable(func: Function) -> Set[BasicBlock]:
        reachable = set()
        if not func.entry_block:
            return reachable
        stack = [func.entry_block]
        while stack:
            curr = stack.pop()
            if curr not in reachable:
                reachable.add(curr)
                stack.extend(curr.successors)
        return reachable

    @staticmethod
    def compute_dominators(func: Function, reachable: Set[BasicBlock]) -> Dict[BasicBlock, Set[BasicBlock]]:
        dom = {}
        if not func.entry_block:
            return dom
        
        for bb in reachable:
            if bb == func.entry_block:
                dom[bb] = {func.entry_block}
            else:
                dom[bb] = set(reachable)
                
        changed = True
        while changed:
            changed = False
            for bb in reachable:
                if bb == func.entry_block:
                    continue
                # Intersection of dominators of predecessors
                preds = [p for p in bb.predecessors if p in reachable]
                if preds:
                    new_dom = set.intersection(*(dom[p] for p in preds))
                else:
                    new_dom = set()
                new_dom.add(bb)
                if new_dom != dom[bb]:
                    dom[bb] = new_dom
                    changed = True
        return dom

    @staticmethod
    def get_dfs_retreating_edges(func: Function, reachable: Set[BasicBlock]) -> List[Tuple[BasicBlock, BasicBlock]]:
        visited = set()
        in_stack = set()
        retreating = []
        
        def dfs(bb):
            visited.add(bb)
            in_stack.add(bb)
            for succ in sorted(bb.successors, key=lambda x: x.label):
                if succ in reachable:
                    if succ in in_stack:
                        retreating.append((bb, succ))
                    elif succ not in visited:
                        dfs(succ)
            in_stack.remove(bb)
            
        if func.entry_block:
            dfs(func.entry_block)
            
        return retreating

    @staticmethod
    def analyze(func: Function) -> LoopAnalysisResult:
        res = LoopAnalysisResult()
        reachable = LoopAnalyzer.compute_reachable(func)
        if not reachable:
            return res
            
        res.dominators = LoopAnalyzer.compute_dominators(func, reachable)
        
        # Dominator-based back edges: u -> v where v dominates u
        for bb in sorted(reachable, key=lambda b: b.label):
            for succ in sorted(bb.successors, key=lambda b: b.label):
                if succ in reachable and succ in res.dominators.get(bb, set()):
                    res.back_edges.append((bb, succ))
                    
        res.retreating_edges = LoopAnalyzer.get_dfs_retreating_edges(func, reachable)
        
        if set(res.back_edges) != set(res.retreating_edges):
            res.is_irreducible = True
            
        # Natural loops
        loops = {}
        for u, v in res.back_edges:
            header = v
            body = {header, u}
            stack = [u]
            while stack:
                curr = stack.pop()
                if curr != header:
                    for pred in curr.predecessors:
                        if pred in reachable and pred not in body:
                            body.add(pred)
                            stack.append(pred)
            
            if header not in loops:
                loops[header] = set()
            loops[header].update(body)
            
        res.merged_loops = loops
        
        for bb in reachable:
            bb.loop_depth = sum(1 for body in loops.values() if bb in body)
            
        return res

def dump_loops(func: Function, res: LoopAnalysisResult) -> str:
    lines = [f"Function: {func.name}"]
    if res.is_irreducible:
        lines.append("  [WARNING] Irreducible CFG detected!")
        
    back_edges_str = ", ".join([f"{u.label}->{v.label}" for u, v in res.back_edges])
    lines.append(f"  Back-edges: [{back_edges_str}]")
    
    for header in sorted(res.merged_loops.keys(), key=lambda b: b.label):
        body_labels = sorted(b.label for b in res.merged_loops[header])
        lines.append(f"  Loop {header.label}: body=[{', '.join(body_labels)}]")
        
    for bb in sorted(LoopAnalyzer.compute_reachable(func), key=lambda b: b.label):
        lines.append(f"  Block {bb.label}: depth={bb.loop_depth}")
        
    return "\n".join(lines)
