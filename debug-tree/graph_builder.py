"""
graph_builder.py — Multi-Language AST, Regex & Config Graph Builder.
Supports Python, JS, TS, Go, and Configuration files (Env, YAML, JSON, TOML).
"""
import os, ast, re, json

class DependencyGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = [] # List of (from_file, to_file)

    def add_node(self, file_path, name, node_type):
        node_id = f"{file_path}:{name}"
        if node_id in self.nodes:
            existing_type = self.nodes[node_id]["type"]
            if existing_type != "usage" and node_type == "usage":
                return 
        self.nodes[node_id] = {"file": file_path, "name": name, "type": node_type}

    def add_edge(self, from_file, to_file):
        if (from_file, to_file) not in self.edges:
            self.edges.append((from_file, to_file))

    def find_cycles(self):
        """Topological Cycle Detection (DFS)."""
        adj = {}
        for f_from, f_to in self.edges:
            if f_from not in adj: adj[f_from] = []
            adj[f_from].append(f_to)
        
        visited = set()
        path = []
        cycles = []

        def visit(u):
            if u in path:
                cycles.append(path[path.index(u):] + [u])
                return
            if u in visited: return
            visited.add(u)
            path.append(u)
            for v in adj.get(u, []):
                visit(v)
            path.pop()

        for node in list(adj.keys()):
            visit(node)
        return cycles

def build_graph(root, log=""):
    graph = DependencyGraph()
    
    JS_PATTERNS = [
        (re.compile(r'function\s+([a-zA-Z0-9_]+)\s*\('), "function"),
        (re.compile(r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:\([^)]*\)|[a-zA-Z0-9_]+)\s*=>'), "arrow_function"),
        (re.compile(r'class\s+([a-zA-Z0-9_]+)'), "class")
    ]
    
    GO_PATTERNS = [
        (re.compile(r'func\s+(?:\([^)]*\)\s+)?([a-zA-Z0-9_]+)\s*\('), "function"),
        (re.compile(r'type\s+([a-zA-Z0-9_]+)\s+struct'), "struct")
    ]

    for r, dirs, files in os.walk(root):
        if any(ex in r for ex in ["/.", "/node_modules", "/venv", "/__pycache__"]): continue
        
        for f in files:
            fpath = os.path.join(r, f)
            rel = os.path.relpath(fpath, root).replace("\\", "/")
            
            if f.endswith(".py"):
                try:
                    with open(fpath, 'r', encoding='utf-8') as src:
                        content = src.read()
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.Import, ast.ImportFrom)):
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        target = alias.name.replace(".", "/") + ".py"
                                        graph.add_edge(rel, target)
                                else:
                                    if node.module:
                                        target = node.module.replace(".", "/") + ".py"
                                        graph.add_edge(rel, target)
                            elif isinstance(node, ast.FunctionDef):
                                graph.add_node(rel, node.name, "function")
                            elif isinstance(node, ast.ClassDef):
                                graph.add_node(rel, node.name, "class")
                except: pass
            
            elif f.endswith(".js") or f.endswith(".ts"):
                try:
                    with open(fpath, 'r', encoding='utf-8') as src:
                        content = src.read()
                        for pattern, ntype in JS_PATTERNS:
                            for match in pattern.finditer(content):
                                graph.add_node(rel, match.group(1), ntype)
                except: pass

            elif f.endswith(".go"):
                try:
                    with open(fpath, 'r', encoding='utf-8') as src:
                        content = src.read()
                        for pattern, ntype in GO_PATTERNS:
                            for match in pattern.finditer(content):
                                graph.add_node(rel, match.group(1), ntype)
                except: pass

            elif f.endswith((".env", ".yaml", ".yml", ".json", ".toml")):
                try:
                    with open(fpath, 'r', encoding='utf-8') as src:
                        content = src.read()
                        keys = re.findall(r'([a-zA-Z0-9_]{3,})\s*[=:]', content)
                        for k in set(keys):
                            graph.add_node(rel, k, "config_key")
                except: pass
                
    return graph
