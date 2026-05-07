"""
debug_tree.py — The Sovereign Debug Engine.
Usage: python3 debug_tree.py <log_file> <project_root>
"""
import sys, os, json
from graph_builder import build_graph
from candidate_generator import generate_candidates, calibrate_confidence
from git_history import resolve_history

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 debug_tree.py <log_file_or_text> <project_root>")
        return

    log_input = sys.argv[1]
    root = os.path.abspath(sys.argv[2])

    # Handle log as file or text
    if os.path.exists(log_input):
        with open(log_input, 'r') as f: log = f.read()
    else:
        log = log_input

    print(f"--- DEBUG TREE v9.0: SOVEREIGN DIAGNOSTIC ENGINE ---")
    
    # 1. Build Graph (Python, JS, TS, Go)
    graph = build_graph(root, log)
    
    # NEW: Detect Topological Cycles
    cycles = graph.find_cycles()
    if cycles:
        print("\n⚠️ STRUCTURAL ANOMALIES DETECTED (CIRCULAR DEPENDENCIES):")
        for cycle in cycles:
            print(f"  🔄 Loop: {' -> '.join(cycle)}")
    
    # 2. Resolve History (Live Git Renames)
    history = resolve_history(root)
    
    # 3. Generate Candidates (Multi-Language Tracebacks)
    raw_candidates = generate_candidates(log, root, graph, history=history)
    
    # 4. Calibrate Confidence (Exponential Ranking + Existence Boost)
    ranked, confidence = calibrate_confidence(raw_candidates, log)
    
    if not ranked:
        print("Verdict: Root Cause Unknown.")
        return

    # Output Result
    print(f"VERDICT: {ranked[0]['file']}")
    print(f"CONFIDENCE: {confidence}%")
    
    # NEW: Sovereign Fix Path
    print("\n🏛 SOVEREIGN FIX PATH (CAUSAL SEQUENCE):")
    roots = sorted(ranked[:3], key=lambda x: x['comps'].get('root_influence', 0), reverse=True)
    for i, r in enumerate(roots):
        suffix = " (ROOT CAUSE)" if i == 0 else " (CONSEQUENCE)"
        print(f"  STEP {i+1}: Fix {r['file']}{suffix}")

    print("\nTOP CANDIDATES:")
    for c in ranked[:5]:
        print(f"- {c['file']} (Prob: {round(c['prob']*100, 1)}%) [Comps: {c['comps']}]")

    # Show Systemic Risks (Universal v10)
    risks = [c for c in ranked if c['comps'].get('d', 0) > 0 and any(n.get('type') == 'mutation_risk' for nid, n in graph.nodes.items() if n['file'] == c['file'])]
    if risks:
        print("\nSYSTEMIC RISKS (POTENTIAL MUTATORS):")
        for r in risks[:2]:
            print(f"- {r['file']} (Heuristic match for runtime mutation)")

if __name__ == "__main__":
    main()
