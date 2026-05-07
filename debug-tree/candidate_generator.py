"""
candidate_generator.py — Probabilistic Scoring & Multi-Language Calibration.
Supports Python, JS, TS, Go, and Config Files.
"""
import os, re, math
import numpy as np
from collections import Counter

PROD_EXCLUDES = {"docs/", "examples/", "tests/", "scripts/", "benchmarks/", "docs_src/", "test/"}
GENERIC_SYMBOLS = {"self", "args", "kwargs", "cls", "origin", "name", "value", "getattr", "setattr"}

def generate_candidates(log, root, graph, history=None):
    root = os.path.abspath(root)
    
    # 1. Extract Deep Signals (Symbols, Locals, Values)
    tb_symbols = set(re.findall(r'(?:in|at)\s+([a-zA-Z0-9_<>$.]+)', log))
    quoted_symbols = set(re.findall(r"[\"']([a-zA-Z0-9_.]+)[\"']", log))
    cap_symbols = set(re.findall(r'\b([A-Z][a-zA-Z0-9_]+)\b', log))
    id_symbols = set(re.findall(r'\b([a-z]+_[a-zA-Z0-9_]+|[a-z]+[A-Z][a-zA-Z0-9]+)\b', log))
    
    # Extract "Locals" or "Values" from logs (e.g. x=None, port: 8080)
    value_signals = set(re.findall(r'\b([a-zA-Z0-9_.-]{4,})\b', log))
    
    all_log_symbols = (tb_symbols | quoted_symbols | cap_symbols | id_symbols | value_signals) - GENERIC_SYMBOLS
    all_log_symbols = {s for s in all_log_symbols if len(s) > 2}
    
    frames = []
    file_func_map = {}
    
    # 2. Multi-Language Frame Extraction
    py_pattern = re.compile(r'File ["\']([^"\']+)["\'], line (\d+)(?:, in ([a-zA-Z0-9_]+))?')
    js_pattern = re.compile(r'at\s+(?:([^()]+)\s+\()?([^:() ]+):(\d+)(?::(\d+))?\)?')
    go_pattern = re.compile(r'([^\s:]+\.go):(\d+)')

    for m in py_pattern.finditer(log):
        fpath, func = m.group(1), m.group(3)
        _add_frame(fpath, func, root, frames, file_func_map)
        
    for m in js_pattern.finditer(log):
        func, fpath = m.group(1), m.group(2)
        if func: func = func.strip()
        _add_frame(fpath, func, root, frames, file_func_map)

    for m in go_pattern.finditer(log):
        fpath = m.group(1)
        _add_frame(fpath, None, root, frames, file_func_map)

    frame_set = set(frames)
    comp_scores = {}
    
    # Initialize scores for traceback files
    if frames:
        for i, f in enumerate(frames):
            p_val = math.pow((i + 1) / len(frames), 2)
            comp_scores[f] = {"p": p_val, "d": 0.0, "r": 0.0, "h": 0.0, "depth": i+1, "ambiguity": 0}

    # 3. Graph Scoring & Ambiguity Detection
    symbol_occurrence = Counter()
    for nid, node in graph.nodes.items():
        symbol_occurrence[node["name"]] += 1

    for nid, node in graph.nodes.items():
        f = node["file"]
        name = node["name"]
        
        if any(f.startswith(ex) for ex in PROD_EXCLUDES) and f not in frame_set: continue
        if f not in comp_scores: 
            comp_scores[f] = {"p": 0.0, "d": 0.0, "r": 0.0, "h": 0.0, "depth": 0, "ambiguity": 0}
        
        if name in all_log_symbols:
            is_in_context = any(ctx in nid for ctx in file_func_map.get(f, []))
            # Penalize ambiguity: if symbol is in 100 files, it's a weak signal
            occ = symbol_occurrence[name]
            
            ntype = node.get("type", "definition")
            type_weight = 1.0
            if ntype == "usage": type_weight = 0.1
            elif ntype == "config_value": type_weight = 1.2 # Strong signal if a value in log matches config
            elif ntype == "mutation_risk": type_weight = 0.5 # Heuristic signal for monkey patching
            
            strength = (1.0 if is_in_context else 0.4) * type_weight / (1.0 + math.log10(occ))
            
            # Special boost for unique identifiers or config keys
            if (node.get("type") == "config_key" or node.get("type") == "usage") and occ == 1:
                strength *= 1.5
                
            comp_scores[f]["d"] = max(comp_scores[f]["d"], strength)
            comp_scores[f]["ambiguity"] = max(comp_scores[f]["ambiguity"], occ)

    # 4. Git History (Renames)
    if history:
        for old_p, new_p, sim in history.renames:
            # If the OLD file is in the log (frames), give score to NEW file
            if old_p in comp_scores:
                if new_p not in comp_scores: 
                    comp_scores[new_p] = {"p": 0.0, "d": 0.0, "r": 0.0, "h": 0.0, "depth": 0, "ambiguity": 0}
                # Successor inherits signals from predecessor
                for k in ["p", "d", "depth", "ambiguity"]: 
                    comp_scores[new_p][k] = max(comp_scores[new_p][k], comp_scores[old_p][k])
                comp_scores[new_p]["h"] = max(comp_scores[new_p]["h"], sim / 100.0)
            
            # If the NEW file is found (via symbols), it's a "known entity" with history
            if new_p in comp_scores:
                comp_scores[new_p]["h"] = max(comp_scores[new_p]["h"], sim / 100.0)

    # 4.5 Global Risk Heuristics (Universal v10)
    # If we have any candidates, give a baseline boost to mutation risks
    if comp_scores:
        for nid, node in graph.nodes.items():
            if node.get("type") == "mutation_risk":
                f = node["file"]
                if f not in comp_scores:
                    comp_scores[f] = {"p": 0.0, "d": 0.1, "r": 0.0, "h": 0.0, "depth": 0, "ambiguity": 0}
                else:
                    comp_scores[f]["d"] = max(comp_scores[f]["d"], 0.2)

    # 5. Topological Causal Inference (New Cluster V Logic)
    # Calculate "Out-Degree" for each file to find the 'Root Mutator'
    out_degree = Counter()
    for f_from, f_to in graph.edges:
        out_degree[f_from] += 1

    # 6. Final Scoring with Causal Re-Ranking
    W = {"p": 0.4, "d": 0.4, "h": 0.2}
    final_candidates = []
    for f, comps in comp_scores.items():
        raw_score = sum(W[k] * comps[k] for k in W)
        
        # Causal Boost: If this is a Root File that many others depend on, it's more likely the Root Cause
        impact = out_degree[f]
        if impact > 0:
            raw_score *= (1.0 + math.log10(impact + 1))
            comps["root_influence"] = impact
        else:
            comps["root_influence"] = 0
            
        # Existence Boost
        exists = os.path.exists(os.path.join(root, f))
        if exists: raw_score *= 1.2
        else: raw_score *= 0.5
            
        if raw_score > 0: 
            final_candidates.append({"file": f, "raw_score": raw_score, "comps": comps, "has_frames": len(frames) > 0})
            
    return final_candidates

def _add_frame(fpath, func, root, frames, file_func_map):
    if not os.path.isabs(fpath): fpath = os.path.join(root, fpath)
    fpath = os.path.normpath(fpath)
    root = os.path.normpath(root)
    if fpath.startswith(root):
        rel = os.path.relpath(fpath, root).replace("\\","/")
        if rel not in frames: frames.append(rel)
        if func: file_func_map.setdefault(rel, set()).add(func)

def calibrate_confidence(candidates, log, temp=0.05):
    if not candidates: return [], 0.0
    
    raw_scores = np.array([c["raw_score"] for c in candidates])
    exp_s = np.exp(raw_scores / temp)
    all_probs = exp_s / np.sum(exp_s)
    for i, c in enumerate(candidates): c["prob"] = all_probs[i]
    ranked = sorted(candidates, key=lambda x: x["prob"], reverse=True)
    winner = ranked[0]
    
    # --- RIGOROUS CALIBRATION (The Overconfidence Fix) ---
    m = 0.4 # Lower base signal
    
    if winner["has_frames"]:
        m += 0.3 # High signal if in traceback
    
    if winner["comps"]["d"] > 0.8:
        m += 0.3 # Strong symbol match
    elif winner["comps"]["d"] > 0.4:
        m += 0.15
        
    # Penalty for ambiguity
    if winner["comps"]["ambiguity"] > 3:
        m -= 0.15 * math.log10(winner["comps"]["ambiguity"])
        
    # Penalty for Lack of Traceback
    c = 0.95 if winner["has_frames"] else 0.6 # Less drastic reduction if we have good symbol matches
    
    if winner["comps"]["h"] > 0.8: m += 0.3 # History is a strong signal
    
    confidence = (winner["prob"] * m * c) * 100
    
    # Final Cap: Never go above 55% if there's no traceback, unless history is involved
    if not winner["has_frames"] and winner["comps"]["h"] < 0.5:
        confidence = min(55.0, confidence)
        
    return ranked, round(min(98, confidence), 2)
