# Cluster I: The Analysis Suite (Structural DNA)

This directory consolidates the engines responsible for extracting the fundamental "Identity" of binaries and source files.

## 🧱 Components
- **FBC7 Engine**: Multi-arch disassembly and codon fingerprinting.
- **DebugTree**: AST context tree generation and noise pruning.
- **DebugTree Layer Test**: Parity verification between raw code and analytical representation.

## 🚀 Execution Context
To maintain import compatibility with the rest of the Sovereign stack (specifically the `cae` validator), engines should be executed from the workspace root or with the root in `PYTHONPATH`.

### Example Command
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 cluster_1_analysis/fbc7_engine.py <target_binary>
```

## 🧠 Role in the Fractal Stack
1. Extracts **Structural Fingerprints** (FBC7).
2. Generates **AST Context Trees** (DebugTree).
3. Prunes "Noise" modules prior to LLM context injection to achieve up to 98.5% efficiency on large monoliths.
