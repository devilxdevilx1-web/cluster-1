import os, subprocess, shutil, json

TEST_ROOT = "crucible_env"

def run_test(log_text, project_root):
    cmd = ["python3", "debug_tree.py", log_text, project_root]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def setup_crucible():
    if os.path.exists(TEST_ROOT):
        shutil.rmtree(TEST_ROOT)
    os.makedirs(TEST_ROOT, exist_ok=True)
    
    # 1. Setup Git Repo for Rename Test
    os.chdir(TEST_ROOT)
    subprocess.run(["git", "init"], capture_output=True)
    
    # Create database.py
    with open("database.py", "w") as f:
        f.write("def connect(): return 'Connected'")
    subprocess.run(["git", "add", "database.py"], capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial DB"], capture_output=True)
    
    # Rename to database_v2.py
    subprocess.run(["git", "mv", "database.py", "database_v2.py"], capture_output=True)
    subprocess.run(["git", "commit", "-m", "Rename DB"], capture_output=True)
    
    # 2. Setup Config
    with open(".env", "w") as f:
        f.write("DB_PORT=9999\nTIMEOUT=500ms")
        
    # 3. Setup Stealth Patcher (Mutation Risk)
    with open("stealth_patcher.py", "w") as f:
        f.write("import database_v2\nsetattr(database_v2, 'connect', lambda: 1/0)")
        
    # 4. Setup Victim
    with open("main.py", "w") as f:
        f.write("from database_v2 import connect\nconnect()")
        
    os.chdir("..")

def conduct_audit():
    setup_crucible()
    
    # THE PROBLEM: A ZeroDivisionError occurs in a renamed file, 
    # but the log mentions a config value and the crash is actually caused by a patcher.
    log = """
    ZeroDivisionError: division by zero
      File "database.py", line 1, in connect
    ErrorMessage: Failed to bind to port 9999.
    """
    
    print("--- CONDUCTING THE CRUCIBLE TEST ---")
    output = run_test(log, TEST_ROOT)
    print(output)
    
    # SUCCESS CRITERIA:
    # 1. Verdict should be database_v2.py (Rename Recovery)
    # 2. .env should be a TOP CANDIDATE (Config Value Matching)
    # 3. stealth_patcher.py should be in SYSTEMIC RISKS (Mutation Detection)
    
    success = ("database_v2.py" in output and 
               ".env" in output and 
               "stealth_patcher.py" in output)
    
    print(f"CRUCIBLE TEST RESULT: {'PASSED' if success else 'FAILED'}")

if __name__ == "__main__":
    conduct_audit()
