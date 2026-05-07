import os, sys
# Add current dir to path to import local modules
sys.path.append(os.path.abspath("."))
from graph_builder import build_graph

graph = build_graph("crucible_env")
for nid, node in graph.nodes.items():
    if node["file"] == ".env":
        print(f"Node: {node['name']} | Type: {node['type']}")
