import os, sys, subprocess, random, ast, time, json

PROD_ROOT = "production_repos"
REPOS = [d for d in os.listdir(PROD_ROOT) if os.path.isdir(os.path.join(PROD_ROOT, d))]

def get_py_files(root):
    py_files = []
    for r, d, files in os.walk(root):
        if any(ex in r for ex in ["/.", "/tests", "/docs"]): continue
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(r, f))
    return py_files

def extract_symbol(fpath):
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    if not node.name.startswith("_"):
                        return node.name
    except: pass
    return None

def run_debug_tree(log, root):
    cmd = ["python3", "debug_tree.py", log, root]
    result = subprocess.run(cmd, capture_output=True, text=True)
    verdict = "Unknown"
    conf = 0.0
    for line in result.stdout.split("\n"):
        if "VERDICT:" in line: verdict = line.replace("VERDICT:", "").strip()
        if "CONFIDENCE:" in line: 
            try: conf = float(line.replace("CONFIDENCE:", "").replace("%", "").strip())
            except: pass
    return verdict, conf

def stress_test():
    print(f"--- PRODUCTION STRESS TEST: 14 REPOS ---")
    results = []
    
    for repo_name in REPOS:
        repo_path = os.path.join(PROD_ROOT, repo_name)
        print(f"\nAnalyzing {repo_name}...")
        
        py_files = get_py_files(repo_path)
        if not py_files: continue
        
        samples = random.sample(py_files, min(3, len(py_files)))
        repo_results = {"repo": repo_name, "cases": []}
        
        for fpath in samples:
            symbol = extract_symbol(fpath)
            if not symbol: continue
            
            rel_path = os.path.relpath(fpath, repo_path).replace("\\", "/")
            log = f"AttributeError: '{symbol}' object has no attribute 'x'"
            
            # 1. Standard Test
            verdict, conf = run_debug_tree(log, repo_path)
            repo_results["cases"].append({
                "file": rel_path,
                "symbol": symbol,
                "mode": "standard",
                "success": verdict == rel_path,
                "conf": conf
            })
            
            # 2. Adversarial Rename
            new_fpath = fpath.replace(".py", "_renamed.py")
            new_rel = os.path.relpath(new_fpath, repo_path).replace("\\", "/")
            
            try:
                # Rename and commit using relative paths
                rel_fpath = os.path.relpath(fpath, repo_path)
                rel_new_fpath = os.path.relpath(new_fpath, repo_path)
                
                mv_res = subprocess.run(["git", "-C", repo_path, "mv", rel_fpath, rel_new_fpath], capture_output=True)
                if mv_res.returncode != 0:
                    print(f"  [!] git mv failed: {mv_res.stderr.strip()}")
                    continue
                    
                commit_res = subprocess.run(["git", "-C", repo_path, "commit", "-m", f"Adversarial rename of {symbol}"], capture_output=True)
                if commit_res.returncode != 0:
                    print(f"  [!] git commit failed: {commit_res.stderr.strip()}")
                    continue
                
                # Test recovery
                verdict, conf = run_debug_tree(log, repo_path)
                repo_results["cases"].append({
                    "file": new_rel,
                    "old_file": rel_path,
                    "symbol": symbol,
                    "mode": "rename",
                    "success": verdict == new_rel,
                    "conf": conf
                })
                
                # Revert
                subprocess.run(["git", "-C", repo_path, "reset", "--hard", "HEAD~1"], capture_output=True)
            except Exception as e:
                print(f"  [!] Rename failed for {rel_path}: {e}")

        results.append(repo_results)
        
        # Summary for this repo
        successes = [c["success"] for c in repo_results["cases"]]
        acc = (sum(successes) / len(successes)) * 100 if successes else 0
        print(f"  >> Accuracy: {acc:.1f}% | Avg Conf: {sum([c['conf'] for c in repo_results['cases']]) / len(repo_results['cases']):.1f}%")

    with open("production_stress_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFINAL REPORT SAVED TO production_stress_results.json")

if __name__ == "__main__":
    stress_test()
