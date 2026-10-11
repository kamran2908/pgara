import os
import glob
import subprocess
import sys
import json
from src.ir.parser import parse_module
from src.ir.cfg import CFGBuilder
from src.analysis.loop import LoopAnalyzer
from src.analysis.liveness import LivenessAnalyzer
from src.analysis.interference import InterferenceAnalyzer
from src.toolchain import resolve_toolchain

def run_cmd(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error running: {' '.join(cmd)}")
        stderr_str = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else str(e.stderr)
        print(f"Stderr: {stderr_str}")
        sys.exit(1)

def main():
    os.makedirs("results/raw/phase1", exist_ok=True)
    benchmarks = glob.glob("benchmarks/*.c")
    if not benchmarks:
        print("No benchmarks found!")
        sys.exit(1)

    clang, opt = resolve_toolchain()

    print(f"{'Benchmark':<20} | {'Funcs':<5} | {'Blocks':<6} | {'Back-Edges':<10} | {'Max Depth':<9} | {'IG Nodes':<8} | {'IG Edges':<8} | {'Max Pressure':<12}")
    print("-" * 95)
    
    for b in sorted(benchmarks):
        b_name = os.path.basename(b).replace('.c', '')
        
        # 1. IR Generation (like Prompt 2)
        raw_ll = f"results/raw/phase1/{b_name}.raw.ll"
        mem2reg_ll = f"results/raw/phase1/{b_name}.mem2reg.ll"
        
        run_cmd([clang, "-O0", "-S", "-emit-llvm", "-Xclang", "-disable-O0-optnone", b, "-o", raw_ll])
        run_cmd([opt, "-passes=mem2reg", "-S", raw_ll, "-o", mem2reg_ll])
        
        # 2. Parse & Analyze
        try:
            mod = parse_module(mem2reg_ll)
        except Exception as e:
            print(f"Failed to parse {b_name}: {e}")
            sys.exit(1)
            
        report = {"benchmark": b_name, "functions": []}
        
        funcs = 0
        total_blocks = 0
        total_back_edges = 0
        max_loop_depth = 0
        total_ig_nodes = 0
        total_ig_edges = 0
        max_pressure = 0
        
        for func in sorted(mod.functions, key=lambda f: f.name):
            try:
                CFGBuilder.build(func)
                loop_res = LoopAnalyzer.analyze(func)
                LivenessAnalyzer.analyze(func)
                ig_res = InterferenceAnalyzer.analyze(func)
            except Exception as e:
                print(f"Failed to analyze function {func.name} in {b_name}: {e}")
                sys.exit(1)
                
            funcs += 1
            total_blocks += len(func.blocks)
            total_back_edges += len(loop_res.back_edges)
            
            func_max_depth = max([b.loop_depth for b in func.blocks]) if func.blocks else 0
            max_loop_depth = max(max_loop_depth, func_max_depth)
            
            res_ig_nodes = len(ig_res.graph.nodes())
            res_ig_edges = len(ig_res.graph.edges())
            
            total_ig_nodes += res_ig_nodes
            total_ig_edges += res_ig_edges
            max_pressure = max(max_pressure, ig_res.max_pressure)
            
            func_data = {
                "name": func.name,
                "blocks": [],
                "edges": [],
                "back_edges": [],
                "interference": {
                    "node_count": res_ig_nodes,
                    "edge_count": res_ig_edges,
                    "max_pressure": ig_res.max_pressure
                }
            }
            
            for bb in sorted(func.blocks, key=lambda b: b.label):
                for succ in sorted(list(bb.successors), key=lambda b: b.label):
                    func_data["edges"].append(f"{bb.label}->{succ.label}")
                    
            for u, v in sorted(loop_res.back_edges, key=lambda e: (e[0].label, e[1].label)):
                func_data["back_edges"].append(f"{u.label}->{v.label}")
                
            for bb in sorted(func.blocks, key=lambda b: b.label):
                func_data["blocks"].append({
                    "label": bb.label,
                    "loop_depth": bb.loop_depth,
                    "live_in": sorted([v.name for v in bb.live_in]),
                    "live_out": sorted([v.name for v in bb.live_out]),
                    "pressure": ig_res.block_pressure[bb]
                })
                
            report["functions"].append(func_data)
            
        print(f"{b_name:<20} | {funcs:<5} | {total_blocks:<6} | {total_back_edges:<10} | {max_loop_depth:<9} | {total_ig_nodes:<8} | {total_ig_edges:<8} | {max_pressure:<12}")
        
        with open(f"results/raw/phase1/{b_name}.report.json", "w") as f:
            json.dump(report, f, indent=2, sort_keys=True)
            
if __name__ == "__main__":
    main()
