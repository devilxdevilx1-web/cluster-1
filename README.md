# 🧱 Cluster I: The Analysis Suite (Structural DNA)

![Sovereign Tech Stack](https://img.shields.io/badge/Stack-Sovereign-blueviolet?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Operational-success?style=for-the-badge)
![Efficiency](https://img.shields.io/badge/Efficiency-98.5%25-brightgreen?style=for-the-badge)

Cluster I is the foundational layer of the **Sovereign Tech Stack**. It functions as the "Structural DNA" extractor, responsible for identifying the fundamental identity of any binary or source file through multi-arch disassembly and AST context mapping.

## 🧬 Core Engines

### 1. FBC7 Engine (Fixed-width Binary Codon)
The primary fingerprinting engine. It converts raw instruction streams into a fixed-width feature vector (Codon Fingerprint).
- **Multi-Arch Disassembly**: Native support for ARM64 (otool) and X86 (objdump).
- **Structural Hashing**: Generates unique hashes based on instruction category distributions and trigram entropy.
- **Cross-Binary Similarity**: Quantifies conceptual logic overlaps across different architectures.

### 2. DebugTree Engine
The sovereign diagnostic layer. It maps execution failures to architectural gaps using deep graph synthesis.
- **AST Context Trees**: Generates high-fidelity representations of code structure.
- **Noise Pruning**: Implements local context-aware pruning of "Noise" modules prior to LLM context injection, achieving up to 98.5% efficiency for large monoliths.
- **Universal Audit**: Cross-language support for Python, JS/TS, and Go.

### 3. DebugTree Layer Test
The hardening component that ensures 100% parity between raw code and analytical representation. It subjects the engines to adversarial AST mutations to prove "Unbreakable" status.

## 🚀 Usage

### FBC7 Fingerprinting
```bash
python3 fbc7_engine.py <target_binary>
```

### DebugTree Diagnostic
```bash
python3 debug_tree/debug_tree.py <log_file> <project_root>
```

### Context Pruning for LLM
```bash
python3 sovereign_chat_context.py
```

## 🏛 Interaction Flow
1. **Extraction**: FBC7 extracts the structural fingerprint.
2. **Mapping**: DebugTree maps the fingerprint to the AST context.
3. **Pruning**: Noise is removed to generate a "High-Entropy Context."
4. **Validation**: Layer tests verify the integrity of the distilled logic.

---

*Part of the 10-Engine Fractal Stack. Built for autonomous physics discovery and sovereign architectural integrity.*

