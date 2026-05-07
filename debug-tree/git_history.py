import subprocess, os

class GitHistory:
    def __init__(self, renames=None):
        self.renames = renames or []

def resolve_history(root):
    """
    Uses 'git log' to detect file renames in the repository history.
    Returns a GitHistory object with a list of (old_path, new_path, similarity_score).
    """
    renames = []
    try:
        # Get renames from git history across all commits
        # --diff-filter=R finds only renames
        cmd = ["git", "-C", root, "log", "--name-status", "--diff-filter=R", "--pretty=format:"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if not line.strip(): continue
                if line.startswith("R"):
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        # Format: R<score>  old_path  new_path
                        try:
                            score = int(parts[0][1:])
                        except:
                            score = 100
                        old_p, new_p = parts[1], parts[2]
                        renames.append((old_p, new_p, score))
    except Exception as e:
        # Fallback to empty if not a git repo or other error
        pass
        
    return GitHistory(renames)
