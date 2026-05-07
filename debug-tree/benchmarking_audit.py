import time, os, subprocess

REPOS = [
    ("real_repos/requests/src", "ImportError: Session not found"),
    ("real_repos/fastapi/fastapi", "AttributeError: FastAPI has no attribute 'x'"),
    ("real_repos/httpx/httpx", "NameError: Client is not defined"),
    ("real_repos/pydantic/pydantic", "TypeError: BaseModel expected 1 argument")
]

def run_audit():
    print(f"{'Repository':<25} | {'Files':<6} | {'Time (s)':<10} | {'Verdict'} | {'Conf'}")
    print("-" * 85)
    
    for repo, err in REPOS:
        start = time.time()
        cmd = ["python3", "debug_tree.py", err, repo]
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.time()
        
        file_count = sum([len(files) for r, d, files in os.walk(repo) if any(files)])
        
        verdict = "Unknown"
        conf = "0%"
        for line in result.stdout.split("\n"):
            if "VERDICT:" in line:
                verdict = line.replace("VERDICT:", "").strip()
            if "CONFIDENCE:" in line:
                conf = line.replace("CONFIDENCE:", "").strip()
        
        print(f"{repo:<25} | {file_count:<6} | {end-start:<10.3f} | {verdict:<20} | {conf}")

if __name__ == "__main__":
    run_audit()
