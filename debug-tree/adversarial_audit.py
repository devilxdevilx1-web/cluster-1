import os, subprocess, shutil, json, time
import numpy as np

# --- TEST SUITE CONFIG ---
TEST_ROOT = "adversarial_test_env"
os.makedirs(TEST_ROOT, exist_ok=True)

def setup_git_repo():
    os.chdir(TEST_ROOT)
    subprocess.run(["git", "init"], capture_output=True)
    with open("original.py", "w") as f:
        f.write("def core_logic(): return 1/0")
    subprocess.run(["git", "add", "original.py"], capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], capture_output=True)
    subprocess.run(["git", "mv", "original.py", "renamed_v2.py"], capture_output=True)
    subprocess.run(["git", "commit", "-m", "rename"], capture_output=True)
    os.chdir("..")

def run_test(log_text, project_root):
    cmd = ["python3", "debug_tree.py", log_text, project_root]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def audit():
    if os.path.exists(TEST_ROOT):
        shutil.rmtree(TEST_ROOT)
    os.makedirs(TEST_ROOT, exist_ok=True)
    setup_git_repo()
    results = []

    # 1. Capability: Standard Static Bug
    with open(f"{TEST_ROOT}/static_bug.py", "w") as f: f.write("def fail(): return 1/0")
    log = "ZeroDivisionError: division by zero\n  File \"static_bug.py\", line 1, in fail"
    out = run_test(log, TEST_ROOT)
    results.append({"case": "Static Bug", "success": "static_bug.py" in out, "conf": out})

    # 2. Capability: Renamed File Recovery
    log = "ZeroDivisionError: division by zero\n  File \"original.py\", line 1, in core_logic"
    out = run_test(log, TEST_ROOT)
    results.append({"case": "Renamed Recovery", "success": "renamed_v2.py" in out, "conf": out})

    # 3. Adversarial: Monkey Patching
    with open(f"{TEST_ROOT}/base.py", "w") as f: f.write("class Base: pass")
    with open(f"{TEST_ROOT}/patcher.py", "w") as f: f.write("from base import Base\nBase.run = lambda: 1/0")
    log = "ZeroDivisionError\n  File \"patcher.py\", line 2, in <lambda>"
    out = run_test(log, TEST_ROOT)
    results.append({"case": "Monkey Patch", "success": "patcher.py" in out, "target": "base.py", "conf": out})

    # 4. Adversarial: Distributed Config Drift
    with open(f"{TEST_ROOT}/db.py", "w") as f: f.write("def connect(): raise ConnectionError('Failed')")
    log = "ConnectionError: Failed" # No traceback, just error
    out = run_test(log, TEST_ROOT)
    results.append({"case": "Config Drift", "success": "db.py" in out, "conf": out})

    # 5. Emergent: Multi-hop Chain
    with open(f"{TEST_ROOT}/a.py", "w") as f: f.write("from b import func_b")
    with open(f"{TEST_ROOT}/b.py", "w") as f: f.write("def func_b(): pass")
    log = "NameError: func_b is not defined"
    out = run_test(log, TEST_ROOT)
    results.append({"case": "Multi-hop Chain", "success": "b.py" in out, "conf": out})

    # 6. Non-Python Files (Negative Test)
    with open(f"{TEST_ROOT}/config.yaml", "w") as f: f.write("api_key: null")
    log = "KeyError: 'api_key'"
    out = run_test(log, TEST_ROOT)
    results.append({"case": "Non-Python Support", "success": "config.yaml" in out, "conf": out})

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    audit()
