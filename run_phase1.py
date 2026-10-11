import os
import glob
import subprocess
import sys
import json
import argparse
from src.ir.parser import parse_module
from src.ir.cfg import CFGBuilder, dump_cfg
from src.analysis.loop import LoopAnalyzer, dump_loops
from src.analysis.liveness import LivenessAnalyzer, dump_liveness
from src.analysis.interference import InterferenceAnalyzer, dump_interference, export_dot
from src.toolchain import resolve_toolchain

def run_cmd(cmd, stage="Command execution"):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error during {stage}: {' '.join(cmd)}", file=sys.stderr)
        stderr_str = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else str(e.stderr)
        print(f"Stderr: {stderr_str}", file=sys.stderr)
        sys.exit(1)

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="PGARA Phase 1 Analysis Pipeline Driver")
    parser.add_argument(
        "benchmarks",
        nargs="*",
        help="Optional benchmark name(s) to run (e.g. b3_nested_loop or b3_nested_loop.c). If omitted, all benchmarks are run."
    )
    parser.add_argument(
        "--bench-dir",
        default="benchmarks",
        help="Directory containing benchmark .c files (default: benchmarks)"
    )
    parser.add_argument(
        "--out-dir",
        default="results/raw/phase1",
        help="Output directory for generated IR, reports, and DOT graphs (default: results/raw/phase1)"
    )
    parser.add_argument(
        "--clang",
        default=None,
        help="Explicit path to clang executable"
    )
    parser.add_argument(
        "--opt",
        default=None,
        help="Explicit path to opt executable"
    )
    parser.add_argument(
        "--dump",
        nargs="+",
        choices=["cfg", "loops", "liveness", "interference"],
        help="Dump internal analysis representations to stdout"
    )
    parser.add_argument(
        "--function",
        default=None,
        help="Filter analysis/dumps/dot to a specific function name"
    )
    parser.add_argument(
        "--dot",
        action="store_true",
        help="Export interference graph to <out-dir>/<benchmark>.<function>.dot"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress startup toolchain info and summary table"
    )

    raw_args = list(sys.argv[1:] if argv is None else argv)
    valid_dumps = {"cfg", "loops", "liveness", "interference"}
    norm_args = []
    i = 0
    while i < len(raw_args):
        if raw_args[i] == "--dump":
            norm_args.append("--dump")
            i += 1
            if i < len(raw_args) and not raw_args[i].startswith("-"):
                norm_args.append(raw_args[i])
                first_is_choice = raw_args[i] in valid_dumps
                i += 1
                if first_is_choice:
                    while i < len(raw_args):
                        if raw_args[i].startswith("-"):
                            break
                        if raw_args[i] in valid_dumps:
                            norm_args.append(raw_args[i])
                            i += 1
                        else:
                            pos_arg = raw_args[i]
                            dump_idx = len(norm_args) - 1
                            while dump_idx >= 0 and norm_args[dump_idx] != "--dump":
                                dump_idx -= 1
                            norm_args.insert(dump_idx, pos_arg)
                            i += 1
        else:
            norm_args.append(raw_args[i])
            i += 1

    return parser.parse_args(norm_args)

def main(argv=None):
    args = parse_args(argv)
    
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    
    bench_dir = args.bench_dir
    all_benchmarks = sorted(glob.glob(os.path.join(bench_dir, "*.c")))
    if not all_benchmarks:
        print(f"Error: No benchmarks found in '{bench_dir}'!", file=sys.stderr)
        sys.exit(1)

    available_map = {
        os.path.basename(f).replace(".c", ""): f for f in all_benchmarks
    }

    if args.benchmarks:
        selected_files = []
        unknown = []
        for b in args.benchmarks:
            clean_name = os.path.basename(b).replace(".c", "")
            if clean_name in available_map:
                selected_files.append(available_map[clean_name])
            else:
                unknown.append(b)
        if unknown:
            avail_list = ", ".join(sorted(available_map.keys()))
            print(f"Error: Unknown benchmark(s): {', '.join(unknown)}. Available benchmarks: {avail_list}", file=sys.stderr)
            sys.exit(2)
    else:
        selected_files = all_benchmarks

    show_table = (not args.quiet) and (not args.dump)

    clang, opt = resolve_toolchain(
        clang_path=args.clang,
        opt_path=args.opt,
        print_info=show_table
    )

    if show_table:
        print(f"{'Benchmark':<20} | {'Funcs':<5} | {'Blocks':<6} | {'Back-Edges':<10} | {'Max Depth':<9} | {'IG Nodes':<8} | {'IG Edges':<8} | {'Max Pressure':<12}")
        print("-" * 95)
    
    for b_path in selected_files:
        b_name = os.path.basename(b_path).replace('.c', '')
        
        # 1. IR Generation
        raw_ll = os.path.join(out_dir, f"{b_name}.raw.ll")
        mem2reg_ll = os.path.join(out_dir, f"{b_name}.mem2reg.ll")
        
        run_cmd(
            [clang, "-O0", "-S", "-emit-llvm", "-Xclang", "-disable-O0-optnone", b_path, "-o", raw_ll],
            stage=f"IR generation (clang) for benchmark '{b_name}'"
        )
        run_cmd(
            [opt, "-passes=mem2reg", "-S", raw_ll, "-o", mem2reg_ll],
            stage=f"IR optimization (opt) for benchmark '{b_name}'"
        )
        
        # 2. Parse & Analyze
        try:
            mod = parse_module(mem2reg_ll)
        except Exception as e:
            print(f"Error during parsing for benchmark '{b_name}': {e}", file=sys.stderr)
            sys.exit(1)
            
        report = {
            "benchmark": b_name,
            "schema_version": 1,
            "functions": []
        }
        
        funcs = 0
        total_blocks = 0
        total_back_edges = 0
        max_loop_depth = 0
        total_ig_nodes = 0
        total_ig_edges = 0
        max_pressure = 0
        
        funcs_to_process = mod.functions
        if args.function:
            funcs_to_process = [f for f in mod.functions if f.name == args.function]
            if not funcs_to_process:
                print(f"Error during function selection for benchmark '{b_name}': Function '{args.function}' not found", file=sys.stderr)
                sys.exit(1)

        for func in sorted(funcs_to_process, key=lambda f: f.name):
            try:
                cfg_warnings = CFGBuilder.build(func)
            except Exception as e:
                print(f"Error during CFG construction for function '{func.name}' in benchmark '{b_name}': {e}", file=sys.stderr)
                sys.exit(1)

            try:
                loop_res = LoopAnalyzer.analyze(func)
            except Exception as e:
                print(f"Error during loop analysis for function '{func.name}' in benchmark '{b_name}': {e}", file=sys.stderr)
                sys.exit(1)

            try:
                liveness_warnings = LivenessAnalyzer.analyze(func)
            except Exception as e:
                print(f"Error during liveness analysis for function '{func.name}' in benchmark '{b_name}': {e}", file=sys.stderr)
                sys.exit(1)

            try:
                ig_res = InterferenceAnalyzer.analyze(func)
            except Exception as e:
                print(f"Error during interference analysis for function '{func.name}' in benchmark '{b_name}': {e}", file=sys.stderr)
                sys.exit(1)

            # Dump representations to stdout if requested
            if args.dump:
                for dump_type in args.dump:
                    if dump_type == "cfg":
                        print(dump_cfg(func))
                    elif dump_type == "loops":
                        print(dump_loops(func, loop_res))
                    elif dump_type == "liveness":
                        print(dump_liveness(func))
                    elif dump_type == "interference":
                        print(dump_interference(func, ig_res))

            # Export DOT file if requested
            if args.dot:
                dot_path = os.path.join(out_dir, f"{b_name}.{func.name}.dot")
                with open(dot_path, "w", encoding="utf-8") as f_dot:
                    f_dot.write(export_dot(func, ig_res))
                
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

            # Compute reachability for additive unreachable_blocks field
            reachable = set()
            if func.entry_block:
                worklist = [func.entry_block]
                while worklist:
                    curr = worklist.pop()
                    if curr not in reachable:
                        reachable.add(curr)
                        worklist.extend(curr.successors)
            unreachable_blocks = sorted([bb.label for bb in func.blocks if bb not in reachable])
            
            func_data = {
                "name": func.name,
                "blocks": [],
                "edges": [],
                "back_edges": [],
                "is_irreducible": loop_res.is_irreducible,
                "unreachable_blocks": unreachable_blocks,
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
            
        if show_table:
            print(f"{b_name:<20} | {funcs:<5} | {total_blocks:<6} | {total_back_edges:<10} | {max_loop_depth:<9} | {total_ig_nodes:<8} | {total_ig_edges:<8} | {max_pressure:<12}")
        
        report_file = os.path.join(out_dir, f"{b_name}.report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)
            
if __name__ == "__main__":
    main()
