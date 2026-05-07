#!/usr/bin/env python3
"""
FBC7 ENGINE — Hardened Sovereign Edition
- Step 2: Multi-arch disassembly front-end (otool/objdump)
- Step 3: Codon fingerprint — fixed-width feature vector
- Step 4: Cross-binary similarity score
- Step 5: Complete codon dictionary
"""

import re, math, os, subprocess, struct, hashlib, json
from collections import Counter, defaultdict
from cae.validator.engine import ConstraintEngine, ArchitectureContract

# ══════════════════════════════════════════════════════════════════
# STEP 2: MULTI-ARCH DISASSEMBLY FRONT-END
# ══════════════════════════════════════════════════════════════════

ARM64_CATS = {
    "MEM":  {"ldr","str","ldp","stp","ldur","stur","ldrb","strb","ldrh","strh",
             "ldrsb","ldrsh","ldrsw","prfm","ldar","stlr","ldaxr","stxr","ldxr",
             "ldarb","stlrb","ldarh","stlrh","ldnp","stnp","ld1","ld2","ld3","ld4",
             "st1","st2","st3","st4"},
    "CTRL": {"b","bl","blr","br","cbz","cbnz","ret","retab","retaa","tbnz","tbz",
             "b.eq","b.ne","b.lt","b.le","b.gt","b.ge","b.lo","b.hi","b.ls",
             "b.hs","b.mi","b.pl","b.vs","b.vc","b.al","b.nv"},
    "ARITH":{"add","sub","mul","madd","msub","mneg","neg","sdiv","udiv","smull",
             "umull","smulh","umulh","subs","adds","adc","sbc","adcs","sbcs",
             "addp","addv","uaddlv","saddlv"},
    "ADDR": {"adrp","adr"},
    "MOV":  {"mov","movz","movk","movn","fmov","umov","ins","dup","ext","smov"},
    "CMP":  {"cmp","cmn","tst","ccmp","ccmn","cset","csel","csinc","csinv",
             "csneg","fcmp","fcmpe","fccmp"},
    "BIT":  {"and","orr","eor","orn","bic","eon","lsl","lsr","asr","ror","sbfx",
             "ubfx","bfi","sbfiz","ubfiz","extr","cls","clz","rbit","rev","rev16",
             "rev32","ands","bics","orns"},
    "FLOAT":{"fadd","fsub","fmul","fdiv","fmadd","fmsub","fnmadd","fnmsub","fneg",
             "fabs","fsqrt","frecpe","frsqrte","scvtf","ucvtf","fcvtns","fcvtnu",
             "fcvtzs","fcvtzu","frecps","frsqrts"},
    "SIMD": {"zip1","zip2","uzp1","uzp2","trn1","trn2","tbl","tbx","pmull","pmull2",
             "shl","sshr","ushr","sli","sri","sqadd","uqadd","sqsub","uqsub"},
    "SEC":  {"pacibsp","autibsp","paciasp","autiasp","xpaclri","pacia","pacib",
             "autia","autib","paciaz","paciza","pacibz","pacizb"},
    "SYS":  {"nop","brk","hlt","isb","dsb","dmb","dc","ic","at","tlbi","sys","msr","mrs"},
}

X86_CATS = {
    "MEM":  {"mov","movq","movl","movb","movw","movzx","movsx","movzbl","movsbl",
             "movzbq","movsbq","movslq","lea","push","pop","pushq","popq","xchg",
             "movabs","movapd","movaps","movupd","movups","movdqu","movdqa",
             "movsd","movss","movd","movq","lods","stos","cmps","movsx","bswap",
             "xlatb","lfence","sfence","mfence","prefetch","prefetchnta",
             "prefetcht0","prefetcht1","prefetcht2"},
    "CTRL": {"jmp","je","jne","jz","jnz","jl","jle","jg","jge","ja","jb","jae",
             "jbe","jns","js","jp","jnp","jo","jno","jrcxz","jecxz","call","ret",
             "retq","callq","jmpq","loop","loope","loopne","syscall","sysret",
             "int","iret","hlt","ud2","endbr64","endbr32"},
    "ARITH":{"add","sub","imul","mul","idiv","div","neg","inc","dec","adc","sbb",
             "addq","subq","addl","subl","addb","subb","addw","subw","imulq",
             "imull","mulq","mull","divq","divl","idivq","idivl","incq","decq",
             "incl","decl","lea","adcq","sbbq","adcl","sbbl"},
    "CMP":  {"cmp","test","cmovl","cmovge","cmove","cmovne","cmovg","cmovle",
             "cmova","cmovb","cmovae","cmovbe","cmovs","cmovns","cmpq","cmpl",
             "cmpb","cmpw","testq","testl","testb","testw","sete","setne","setl",
             "setg","setle","setge","seta","setb","setae","setbe","sets","setns",
             "seto","setno","setp","setnp","fcomi","fcomip","fucomi","fucomip"},
    "BIT":  {"and","or","xor","not","shl","shr","sar","ror","rol","rcl","rcr",
             "bsf","bsr","bt","btc","btr","bts","andb","andl","andq","andw",
             "orl","orq","orb","orw","xorl","xorq","xorb","xorw","notl","notq",
             "shll","shrl","sarl","roll","rorl","shlq","shrq","sarq","rorq",
             "rolq","popcnt","lzcnt","tzcnt","andn","bextr","blsi","blsr","blsmsk"},
    "FLOAT":{"addsd","subsd","mulsd","divsd","addss","subss","mulss","divss",
             "sqrtsd","sqrtss","cvtsi2sd","cvtsi2ss","cvtsd2si","cvtss2si",
             "cvtsd2ss","cvtss2sd","ucomisd","ucomiss","comisd","comiss",
             "cvttsd2si","cvttss2si","movlpd","movhpd","unpcklpd","unpckhpd",
             "andpd","orpd","xorpd","andnpd","minsd","maxsd","minss","maxss",
             "roundsd","roundss","fld","fst","fstp","fadd","fsub","fmul","fdiv"},
    "SIMD": {"addpd","subpd","mulpd","divpd","addps","subps","mulps","divps",
             "pand","por","pxor","pandn","pcmpeqb","pcmpeqw","pcmpeqd","pcmpeqq",
             "pcmpgtb","pcmpgtw","pcmpgtd","punpcklbw","punpcklwd","punpckldq",
             "punpcklqdq","pshufb","pshufd","pshufhw","pshuflw","pslldq","psrldq",
             "psllw","pslld","psllq","psrlw","psrld","psrlq","psraw","psrad",
             "pmullw","pmulld","pmulhw","pmulhuw","paddb","paddw","paddd","paddq",
             "psubb","psubw","psubd","psubq","pmovmskb","pextrb","pextrd","pextrq",
             "pinsrb","pinsrd","pinsrq","vpand","vpor","vpxor","vmovdqu","vmovdqa",
             "vpcmpeqb","vpcmpeqd","vpshufb","vpshufd","vpslldq","vpsrldq",
             "palignr","vpalignr","vpermq","vperm2i128","vinserti128","vextracti128"},
    "STACK":{"push","pop","pushq","popq","pushfq","popfq","pusha","popa","enter","leave"},
    "SYS":  {"syscall","sysret","int","iret","hlt","ud2","rdtsc","rdtscp","cpuid",
             "xgetbv","xsetbv","rdmsr","wrmsr","in","out","cli","sti","clc","stc",
             "cld","std","pause","nop","fnop","fwait","wait","rep","repe","repne"},
}

def classify_instr(mnemonic, cats):
    m = mnemonic.lower().rstrip('.')
    for cat, ops in cats.items():
        if m in ops:
            return cat
    return "OTH"

@ConstraintEngine.enforce_boundary
def disassemble_mac(binary_path):
    """Extract instruction mnemonics from Mach-O binary using otool."""
    if not os.path.exists(binary_path):
        return []
    try:
        r = subprocess.run(['otool', '-tV', binary_path], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return []
        mnemonics = []
        for line in r.stdout.split('\n'):
            m = re.search(r'\s+([a-z\.]+)(\s+|$)', line)
            if m:
                mn = m.group(1).lower()
                if mn not in ('nop', 'data16'):
                    mnemonics.append(mn)
        return mnemonics
    except Exception:
        return []

@ConstraintEngine.enforce_boundary
def disassemble_auto(binary_path):
    import platform
    if platform.system() == 'Darwin':
        return disassemble_mac(binary_path)
    else:
        return disassemble_linux(binary_path)

@ConstraintEngine.enforce_boundary
def disassemble_linux(binary_path, arch='auto'):
    """Extract instruction mnemonics from ELF binary using objdump."""
    try:
        r = subprocess.run(['objdump', '-d', '--no-show-raw-insn', '-M', 'intel', binary_path], capture_output=True, text=True, timeout=60)
        mnemonics = []
        for line in r.stdout.split('\n'):
            m = re.match(r'^\s+[0-9a-f]+:\s+([\w.]+)', line)
            if m:
                mn = m.group(1).lower()
                if mn not in ('nop', 'data16'):
                    mnemonics.append(mn)
        return mnemonics
    except Exception:
        return []

@ConstraintEngine.enforce_boundary
def compute_fingerprint(instructions, cats, arch='arm64'):
    """Compute the FBC7 fixed-width fingerprint vector for a binary."""
    assert isinstance(instructions, list), "INVARIANT_VIOLATION: instructions must be list"
    assert isinstance(cats, dict), "INVARIANT_VIOLATION: cats must be dict"
    if not instructions: return None

    total = len(instructions)
    cat_counts = Counter(classify_instr(i, cats) for i in instructions)
    cat_pcts = {c: (cat_counts.get(c, 0) / total) * 100 for c in cats}

    trigrams = Counter(tuple(instructions[i:i+3]) for i in range(total-2))
    top_tri_total = sum(v for _, v in trigrams.most_common(500))
    top_tri_cover = (top_tri_total / (total - 2) * 100) if total > 2 else 0

    instr_entropy = -sum((c/total)*math.log2(c/total) for c in Counter(instructions).values() if c > 0)
    
    vec = {c + '%': round(cat_pcts.get(c, 0), 3) for c in cats}
    vec['instr_entropy'] = round(instr_entropy, 4)
    vec['top500_tri_cover'] = round(top_tri_cover, 3)
    vec['total_instrs'] = total
    
    top100_str = '|'.join(' '.join(g) for g, _ in trigrams.most_common(100))
    vec['struct_hash'] = hashlib.md5(top100_str.encode()).hexdigest()[:16]
    return vec

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
        import platform
        cats = ARM64_CATS if platform.processor() == 'arm' else X86_CATS
        instrs = disassemble_auto(target)
        fp = compute_fingerprint(instrs, cats)
        if fp:
            for k, v in fp.items():
                print(f"{k}: {v}")
