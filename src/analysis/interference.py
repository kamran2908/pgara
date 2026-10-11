import networkx as nx
from typing import Dict, Set, List
from src.ir.models import Function, BasicBlock, Value

class InterferenceResult:
    def __init__(self):
        self.graph = nx.Graph()
        self.block_pressure: Dict[BasicBlock, int] = {}
        self.max_pressure: int = 0

class InterferenceAnalyzer:
    @staticmethod
    def analyze(func: Function) -> InterferenceResult:
        res = InterferenceResult()
        
        nodes = set(func.arguments)
        for bb in func.blocks:
            for inst in bb.instructions:
                if inst.result:
                    nodes.add(inst.result)
                    
        for n in nodes:
            res.graph.add_node(n)
            
        for bb in func.blocks:
            live = set(bb.live_out)
            max_p = len(live)
            
            non_phis = [inst for inst in bb.instructions if inst.opcode != "phi"]
            phis = [inst for inst in bb.instructions if inst.opcode == "phi"]
            
            for inst in reversed(non_phis):
                d = inst.result
                if d:
                    for l in live:
                        if d != l:
                            res.graph.add_edge(d, l)
                    live.discard(d)
                
                for u in inst.uses():
                    if isinstance(u, Value):
                        live.add(u)
                        
                max_p = max(max_p, len(live))
                
            phi_results = [inst.result for inst in phis if inst.result]
            if phi_results:
                for d in phi_results:
                    for other_d in phi_results:
                        if d != other_d:
                            res.graph.add_edge(d, other_d)
                    for l in live:
                        if d != l:
                            res.graph.add_edge(d, l)
                        
                for d in phi_results:
                    live.discard(d)
                    
                max_p = max(max_p, len(live))
                
            if bb == func.entry_block:
                entry_live = live.union(func.arguments).union(bb.live_in)
                entry_list = list(entry_live)
                for i in range(len(entry_list)):
                    for j in range(i+1, len(entry_list)):
                        res.graph.add_edge(entry_list[i], entry_list[j])
                max_p = max(max_p, len(entry_live))
                
            res.block_pressure[bb] = max_p
            res.max_pressure = max(res.max_pressure, max_p)
            
        return res

def export_dot(func: Function, res: InterferenceResult) -> str:
    lines = [f"graph IG_{func.name.replace('@', '')} {{"]
    for n in sorted(res.graph.nodes(), key=lambda v: v.name):
        lines.append(f'  "{n.name}";')
    edges = set()
    for u, v in res.graph.edges():
        u_name, v_name = (u.name, v.name) if u.name < v.name else (v.name, u.name)
        edges.add((u_name, v_name))
    for u_name, v_name in sorted(edges):
        lines.append(f'  "{u_name}" -- "{v_name}";')
    lines.append("}")
    return "\n".join(lines)

def dump_interference(func: Function, res: InterferenceResult) -> str:
    lines = [f"Function: {func.name}"]
    lines.append(f"  Max Pressure: {res.max_pressure}")
    
    lines.append("  Nodes & Degrees:")
    for n in sorted(res.graph.nodes(), key=lambda v: v.name):
        lines.append(f"    {n.name}: {res.graph.degree[n]}")
        
    lines.append("  Edges:")
    edges = set()
    for u, v in res.graph.edges():
        u_name, v_name = (u.name, v.name) if u.name < v.name else (v.name, u.name)
        edges.add(f"{u_name} -- {v_name}")
    for e in sorted(edges):
        lines.append(f"    {e}")
        
    lines.append("  Block Pressures:")
    for bb in sorted(func.blocks, key=lambda b: b.label):
        lines.append(f"    Block {bb.label}: max={res.block_pressure[bb]}, |live_in|={len(bb.live_in)}, |live_out|={len(bb.live_out)}")
        
    return "\n".join(lines)
