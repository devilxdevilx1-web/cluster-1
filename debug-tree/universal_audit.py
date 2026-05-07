import os, subprocess, shutil, json

TEST_ROOT = "universal_test_env"

def run_test(log_text, project_root):
    cmd = ["python3", "debug_tree.py", log_text, project_root]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def audit():
    if os.path.exists(TEST_ROOT):
        shutil.rmtree(TEST_ROOT)
    os.makedirs(TEST_ROOT, exist_ok=True)
    
    results = []

    # 1. Universal Capability: Deep Config Value Matching
    with open(f"{TEST_ROOT}/.env", "w") as f: 
        f.write("DB_HOST=192.168.1.50\nPORT=5432")
    log = "ConnectionError: Failed to connect to 192.168.1.50:5432"
    out = run_test(log, TEST_ROOT)
    # Should find .env because of the IP and Port
    results.append({"case": "Deep Config Value", "success": ".env" in out, "conf": out})

    # 2. Universal Capability: Runtime Mutation Risk (Monkey Patch)
    with open(f"{TEST_ROOT}/patcher.py", "w") as f:
        f.write("import target\nsetattr(target, 'func', lambda: 1/0)")
    with open(f"{TEST_ROOT}/target.py", "w") as f:
        f.write("def func(): pass")
    log = "ZeroDivisionError: division by zero\n  File \"target.py\", line 1, in func"
    out = run_test(log, TEST_ROOT)
    # Should flag patcher.py as a potential cause because it has mutation_risk
    results.append({"case": "Mutation Risk", "success": "SYSTEMIC RISKS" in out and "patcher.py" in out, "conf": out})

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    audit()
