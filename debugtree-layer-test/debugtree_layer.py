import os
import ast

class DebugTreeLayer:
    def __init__(self, root_path):
        self.root_path = root_path
        self.adj = {}

    def scan_project(self):
        print(f"--- DebugTree Scanning: {self.root_path} ---")
        for filename in os.listdir(self.root_path):
            if filename.endswith(".py"):
                self.adj[filename] = []
                file_path = os.path.join(self.root_path, filename)
                with open(file_path, "r") as f:
                    try:
                        tree = ast.parse(f.read())
                        self._extract_imports(filename, tree)
                    except:
                        continue

    def _extract_imports(self, source_file, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = f"{node.module}.py" if node.module else "unknown"
                self.adj[source_file].append(module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.adj[source_file].append(f"{alias.name}.py")

    def find_cycle(self):
        visited = set()
        stack = []
        path = []

        def dfs(node):
            if node in stack:
                # Cycle found
                cycle_start_idx = stack.index(node)
                return stack[cycle_start_idx:] + [node]
            if node in visited:
                return None
            
            visited.add(node)
            stack.append(node)
            
            if node in self.adj:
                for neighbor in self.adj[node]:
                    res = dfs(neighbor)
                    if res: return res
            
            stack.pop()
            return None

        for node in list(self.adj.keys()):
            res = dfs(node)
            if res:
                print("\n🚨 [SOVEREIGN DISCOVERY]: Circular Dependency Detected!")
                cycle_path = " -> ".join(res)
                print(f"PATH: {cycle_path}")
                
                return f"""
I have analyzed the project structure locally using DebugTree.
The 'ImportError' is caused by a CIRCULAR DEPENDENCY:
{cycle_path}

Root Cause: '{res[0]}' and '{res[-1]}' are locked in a recursive import chain.
Sovereign Fix: Decouple shared logic into a standalone 'shared_utils.py' or use local imports.
"""
        return "No circular dependency found."

if __name__ == "__main__":
    dt = DebugTreeLayer("/Users/kanchetidevieswar/hybrid/debugtree-layer-test")
    dt.scan_project()
    sovereign_prompt = dt.find_cycle()
    print("\n--- SOVEREIGN PROMPT TO CLAUDE ---")
    print(sovereign_prompt)
