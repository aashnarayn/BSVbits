"""
Massive Procedural Bank of 48 Additional Parameterized Hardware, DSP, Memory, CDC,
Verification, and Computer Architecture Families for BSVbits Mode 2 (CP Arena).

Brings Mode 2 from 32 families to **80 Procedural Hardware Families** across all 10 tracks,
plus Track-Targeted Reinforcement mappings (`TRACK_TO_CP_FAMILIES`) and Spiral Revision support.
"""

from __future__ import annotations
import random
from typing import Any, Callable, Dict, List
from .curriculum import _make_problem
from .curriculum_bank_helpers import (
    make_comb1_problem,
    make_comb2_problem,
    make_seq_step_problem,
)


def _finalize_cp(prob: Dict[str, Any], seed: int, difficulty: str, track_tag: str) -> Dict[str, Any]:
    prob["number"] = seed % 1000
    prob["track_id"] = "cp_arena"
    prob["track_title"] = f"Competitive Hardware Arena ({track_tag})"
    prob["difficulty"] = difficulty
    return prob


# =============================================================================
# TRACK 1 FAMILIES (Combinational & Bitwise) - #33 to #37
# =============================================================================

def _gen_bit_reversal_permute(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    swap_nibbles = rng.choice([True, False])
    xor_mask = rng.choice([0x00, 0x5A, 0xA5, 0xFF]) if difficulty != "Easy" else 0x00
    mode_desc = "Reverse all 8 bits `x[0..7]` and swap nibbles" if swap_nibbles else "Reverse all 8 bits `out[i] = x[7-i]`"
    body = "        Bit#(8) rev = {x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]};\n"
    if swap_nibbles:
        body += "        rev = {rev[3:0], rev[7:4]};\n"
    body += f"        return rev ^ 8'h{xor_mask:02X};"
    p = make_comb1_problem(
        _make_problem, f"cp_bitrev_{seed}",
        f"CP #{seed % 1000}: Parameterized Bit-Reversal & Permutation Network (Mask=0x{xor_mask:02X})",
        "cp_arena", difficulty, ["CP-Combinational", "Bit Permutation", "Track 1"],
        "Bit#(8)", "x", "Bit#(8)", "permute", "mkCpBitPermute", "CpBitPermuteIfc",
        body, ["8'h01", "8'h80", "8'hA5", "8'h3C", "8'hF0", "8'h12"],
        f"### Competitive Specification\n{mode_desc}, then XOR the result with `8'h{xor_mask:02X}`.",
        "Wire permutations in BSV compile to zero-gate routing.",
        f"x[7:0] ---> [ {mode_desc} ] ---> [ ^ 8'h{xor_mask:02X} ] ---> out[7:0]",
        ["Construct `Bit#(8) rev = {x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]};`.",
         f"{'Swap nibbles `rev = {rev[3:0], rev[7:4]};`.' if swap_nibbles else 'Keep `rev` order.'}",
         f"Return `rev ^ 8'h{xor_mask:02X};`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 1: Combinational")


def _gen_bcd_excess3_codec(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    bias = rng.choice([3, 4, 6])
    p = make_comb1_problem(
        _make_problem, f"cp_bcd_{seed}",
        f"CP #{seed % 1000}: BCD Validity Checker & Excess-{bias} Encoder",
        "cp_arena", difficulty, ["CP-Combinational", "BCD Codec", "Track 1"],
        "Bit#(4)", "bcd", "Bit#(5)", "encodeBcd", "mkCpBcdCodec", "CpBcdCodecIfc",
        f"        Bool valid = (bcd <= 4'd9);\n        Bit#(4) code = valid ? (bcd + 4'd{bias}) : 4'd0;\n        return {{pack(valid), code}};",
        ["4'd0", "4'd5", "4'd9", "4'd10", "4'd12", "4'd15"],
        f"### Competitive Specification\nGiven 4-bit `bcd`: check if it is a valid decimal digit (`bcd <= 4'd9`). If valid, compute `code = bcd + 4'd{bias}` (Excess-{bias}); otherwise `code = 4'd0`. Return 5-bit `{{pack(valid), code}}`.",
        "BCD and Excess-K arithmetic units are widely used in financial and instrumentation hardware.",
        f"bcd[3:0] ---> [ valid = (bcd<=9); code = valid ? bcd+{bias} : 0 ] ---> {{valid, code}}",
        ["Check `Bool valid = (bcd <= 4'd9);`.", f"Compute `code = valid ? (bcd + 4'd{bias}) : 4'd0;`.", "Return `{pack(valid), code}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 1: Combinational")


def _gen_carry_save_compressor(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    w = rng.choice([1, 2])
    p = make_comb2_problem(
        _make_problem, f"cp_csa_{seed}",
        f"CP #{seed % 1000}: 3-Operand Carry-Save Adder (CSA) + Final Adder (Weight={w})",
        "cp_arena", difficulty, ["CP-Combinational", "CSA / Wallace", "Track 1"],
        "Bit#(8)", "a", "Bit#(8)", "b", "Bit#(10)", "csaSum", "mkCpCsa", "CpCsaIfc",
        f"        Bit#(8) c = (a ^ b);\n        Bit#(8) ps = a ^ b ^ c;\n        Bit#(8) pc = (a & b) | (b & c) | (a & c);\n        return zeroExtend(ps) + (zeroExtend(pc) << 1) * 10'd{w};",
        [("8'd10", "8'd20"), ("8'd100", "8'd55"), ("8'hFF", "8'h01"), ("8'hAA", "8'h55")],
        f"### Competitive Specification\nGiven 8-bit `a` and `b`, let third operand `c = a ^ b`. Compute bitwise Carry-Save sum `ps = a ^ b ^ c` and carry vector `pc = (a & b) | (b & c) | (a & c)`, and return `zeroExtend(ps) + (zeroExtend(pc) << 1) * 10'd{w}` (`Bit#(10)`).",
        "3:2 Carry-Save Compressors eliminate carry propagation chains inside high-speed multipliers.",
        "(a, b, c=a^b) ---> [ ps = a^b^c, pc = maj(a,b,c) ] ---> ps + (pc<<1)*w",
        ["Compute `Bit#(8) c = a ^ b;`.", "Compute `ps = a ^ b ^ c;` and `pc = (a & b) | (b & c) | (a & c);`.", f"Return `zeroExtend(ps) + (zeroExtend(pc) << 1) * 10'd{w};`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 1: Combinational")


def _gen_majority_voter_tmr(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb2_problem(
        _make_problem, f"cp_tmr_{seed}",
        f"CP #{seed % 1000}: Triple-Modular Redundancy (TMR) Voter & Fault Locator",
        "cp_arena", difficulty, ["CP-Combinational", "TMR Fault Tolerance", "Track 1"],
        "Bit#(8)", "a", "Bit#(8)", "b", "Bit#(9)", "voteTmr", "mkCpTmrVoter", "CpTmrVoterIfc",
        "        Bit#(8) c = a ^ 8'h01;\n        Bit#(8) maj = (a & b) | (b & c) | (a & c);\n        Bit#(1) disagree = |(a ^ b);\n        return {disagree, maj};",
        [("8'hA5", "8'hA5"), ("8'hA5", "8'hA4"), ("8'hFF", "8'h00"), ("8'h12", "8'h12")],
        "### Competitive Specification\nGiven redundant module outputs `a` and `b`, and synthesized 3rd channel `c = a ^ 8'h01`, compute the bitwise majority vote `maj = (a & b) | (b & c) | (a & c)` and disagreement flag `disagree = |(a ^ b)`. Return `{disagree, maj}` (`Bit#(9)`).",
        "Spacecraft and automotive lockstep processors use bitwise TMR majority voters to mask single-event upsets (SEUs).",
        "(a, b, c=a^1) ---> [ maj = (a&b)|(b&c)|(a&c) ] ---> {|(a^b), maj}",
        ["Set `Bit#(8) c = a ^ 8'h01;`.", "Compute `maj = (a & b) | (b & c) | (a & c);`.", "Return `{|(a ^ b), maj}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 1: Combinational")


def _gen_popcount_threshold(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    thresh = rng.choice([3, 4, 5])
    p = make_comb1_problem(
        _make_problem, f"cp_popth_{seed}",
        f"CP #{seed % 1000}: 8-Bit Hamming Weight & Threshold>={thresh} Detector",
        "cp_arena", difficulty, ["CP-Combinational", "Popcount", "Track 1"],
        "Bit#(8)", "x", "Bit#(5)", "popThresh", "mkCpPopThresh", "CpPopThreshIfc",
        f"        Bit#(4) c = 0;\n        for (Integer i = 0; i < 8; i = i + 1) c = c + zeroExtend(x[i]);\n        return {{pack(c >= 4'd{thresh}), c}};",
        ["8'h00", "8'h07", "8'h0F", "8'h55", "8'h7F", "8'hFF"],
        f"### Competitive Specification\nCount the number of `1` bits (`c`, `Bit#(4)`) in `Bit#(8) x`, and return `{{pack(c >= 4'd{thresh}), c}}` (`Bit#(5)`).",
        "Static `for (Integer i = 0; i < 8; i = i + 1)` loops unroll into parallel adder trees in BSV.",
        f"x[7:0] ---> [ popcount(x) ] ---> {{c >= {thresh}, c[3:0]}}",
        ["Loop `i` from `0` to `7` and accumulate `c = c + zeroExtend(x[i]);`.", f"Return `{{pack(c >= 4'd{thresh}), c}};`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 1: Combinational")


# =============================================================================
# TRACK 2 FAMILIES (Strong Types, Vectors, ECC & Crossbars) - #38 to #42
# =============================================================================

def _gen_simd_vector_alu(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    op_mode = rng.choice(["add_wrap", "xor_inv", "max_nibble"])
    if op_mode == "add_wrap":
        desc = "Unpack `a` and `b` into `Vector#(4, Bit#(4))` and add each of the four 4-bit nibble lanes independently modulo 16 (`va[i] + vb[i]`)."
        expr = "va[i] + vb[i]"
    elif op_mode == "xor_inv":
        desc = "Unpack `a` and `b` into `Vector#(4, Bit#(4))` and compute bitwise XNOR `~(va[i] ^ vb[i])` on each of the four 4-bit nibble lanes."
        expr = "~(va[i] ^ vb[i])"
    else:
        desc = "Unpack `a` and `b` into `Vector#(4, Bit#(4))` and select the lane-wise maximum `(va[i] > vb[i]) ? va[i] : vb[i]` for each of the four 4-bit nibble lanes."
        expr = "(va[i] > vb[i]) ? va[i] : vb[i]"
    p = make_comb2_problem(
        _make_problem, f"cp_simd_{seed}",
        f"CP #{seed % 1000}: 4-Lane 4-Bit SIMD Vector Unit ({op_mode})",
        "cp_arena", difficulty, ["CP-Types", "Vector SIMD", "Track 2"],
        "Bit#(16)", "a", "Bit#(16)", "b", "Bit#(16)", "simdOp", "mkCpSimd", "CpSimdIfc",
        f"        Vector#(4, Bit#(4)) va = unpack(a);\n        Vector#(4, Bit#(4)) vb = unpack(b);\n        Vector#(4, Bit#(4)) vr;\n        for (Integer i = 0; i < 4; i = i + 1) begin\n            vr[i] = {expr};\n        end\n        return pack(vr);",
        [("16'h1234", "16'h4321"), ("16'hFFFF", "16'h0123"), ("16'hA5A5", "16'h5A5A"), ("16'h8042", "16'h1928")],
        f"### Competitive Specification\n{desc}",
        "BSV `Vector#(4, Bit#(4))` and static loops express sub-word SIMD parallelism without carry bleed between lanes.",
        f"(a[15:0], b[15:0]) ---> [ 4x Nibble Lane {op_mode} ] ---> out[15:0]",
        ["Unpack `Vector#(4, Bit#(4)) va = unpack(a);` and `vb = unpack(b);`.", f"Loop `i = 0..3`: `vr[i] = {expr};` and `return pack(vr);`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 2: Strong Types & Vectors")


def _gen_hamming_secded_codec(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb1_problem(
        _make_problem, f"cp_hamm_{seed}",
        f"CP #{seed % 1000}: Hamming (7,4) SEC Codeword & Overall Parity Encoder",
        "cp_arena", difficulty, ["CP-Types", "ECC / Hamming", "Track 2"],
        "Bit#(4)", "d", "Bit#(8)", "encodeEcc", "mkCpHamming", "CpHammingIfc",
        "        Bit#(1) p1 = d[0] ^ d[1] ^ d[3];\n        Bit#(1) p2 = d[0] ^ d[2] ^ d[3];\n        Bit#(1) p4 = d[1] ^ d[2] ^ d[3];\n        Bit#(7) cw = {d[3], d[2], d[1], p4, d[0], p2, p1};\n        return {^cw, cw};",
        ["4'h0", "4'h1", "4'h5", "4'hA", "4'hC", "4'hF"],
        "### Competitive Specification\nEncode 4-bit data `d` into an 8-bit SEC-DED codeword `{p_all, d[3], d[2], d[1], p4, d[0], p2, p1}` where `p1 = d[0]^d[1]^d[3]`, `p2 = d[0]^d[2]^d[3]`, `p4 = d[1]^d[2]^d[3]`, and `p_all = ^cw` (overall parity of the 7-bit Hamming word).",
        "ECC encoders protect SRAM caches and HBM/DDR channels against single-bit upsets and detect double-bit errors.",
        "d[3:0] ---> [ p1, p2, p4, cw, ^cw ] ---> {^cw, cw[6:0]}",
        ["Compute `p1 = d[0]^d[1]^d[3]`, `p2 = d[0]^d[2]^d[3]`, `p4 = d[1]^d[2]^d[3]`.", "Pack `Bit#(7) cw = {d[3], d[2], d[1], p4, d[0], p2, p1};` and return `{^cw, cw}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 2: Strong Types & Vectors")


def _gen_crossbar_switch_4x4(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb2_problem(
        _make_problem, f"cp_xbar_{seed}",
        f"CP #{seed % 1000}: 4x4 Non-Blocking Nibble Crossbar Switch",
        "cp_arena", difficulty, ["CP-Types", "Crossbar Switch", "Track 2"],
        "Bit#(16)", "in_lanes", "Bit#(8)", "sel", "Bit#(16)", "routeXbar", "mkCpXbar4", "CpXbar4Ifc",
        "        Vector#(4, Bit#(4)) v = unpack(in_lanes);\n        Vector#(4, Bit#(4)) out_v;\n        for (Integer i = 0; i < 4; i = i + 1) begin\n            Bit#(2) s = sel[2*i+1 : 2*i];\n            out_v[i] = v[s];\n        end\n        return pack(out_v);",
        [("16'hDCBA", "8'b11_10_01_00"), ("16'hDCBA", "8'b00_01_10_11"), ("16'h1234", "8'b00_00_00_00"), ("16'hF0E1", "8'b01_00_11_10")],
        "### Competitive Specification\nUnpack `in_lanes` (`Bit#(16)`) into `Vector#(4, Bit#(4)) v`. For each output port `i` (`0..3`), select input lane `s = sel[2*i+1 : 2*i]` so `out_v[i] = v[s]`, and return `pack(out_v)`.",
        "`Vector#(4, Bit#(4)) v = unpack(in_lanes)` lets you index 4-bit lanes dynamically with `v[s]`!",
        "in_lanes[15:0], sel[7:0] ---> [ out_v[i] = v[sel[2*i+1:2*i]] ] ---> pack(out_v)",
        ["Unpack `Vector#(4, Bit#(4)) v = unpack(in_lanes);`.", "For `i = 0..3`, index `v[sel[2*i+1 : 2*i]]` and `return pack(out_v);`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 2: Strong Types & Vectors")


def _gen_prefix_scan_network(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    use_xor = rng.choice([True, False])
    op_sym = "^" if use_xor else "+"
    op_name = "XOR" if use_xor else "Modulo-16 Sum"
    p = make_comb1_problem(
        _make_problem, f"cp_scan_{seed}",
        f"CP #{seed % 1000}: 4-Lane Inclusive Prefix {op_name} Scan Network",
        "cp_arena", difficulty, ["CP-Types", "Prefix Scan", "Track 2"],
        "Bit#(16)", "x", "Bit#(16)", "prefixScan", "mkCpPrefixScan", "CpPrefixScanIfc",
        f"        Bit#(4) n0 = x[3:0];\n        Bit#(4) n1 = n0 {op_sym} x[7:4];\n        Bit#(4) n2 = n1 {op_sym} x[11:8];\n        Bit#(4) n3 = n2 {op_sym} x[15:12];\n        return {{n3, n2, n1, n0}};",
        ["16'h1111", "16'h1234", "16'hF0F0", "16'h2468"],
        f"### Competitive Specification\nGiven four 4-bit nibbles in `x`, compute the inclusive prefix {op_name} scan: `n0 = x[3:0]`, `n1 = n0 {op_sym} x[7:4]`, `n2 = n1 {op_sym} x[11:8]`, `n3 = n2 {op_sym} x[15:12]`, and return `{{n3, n2, n1, n0}}`.",
        "Parallel prefix scans (Kogge-Stone, Brent-Kung) are the foundation of fast adders and GPU warp primitives.",
        f"x[15:0] ---> [ n_k = n_(k-1) {op_sym} x_k ] ---> {{n3, n2, n1, n0}}",
        [f"Compute `n0 = x[3:0]`, `n1 = n0 {op_sym} x[7:4]`, `n2 = n1 {op_sym} x[11:8]`, `n3 = n2 {op_sym} x[15:12]`.", "Return `{n3, n2, n1, n0}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 2: Strong Types & Vectors")


def _gen_ipv4_header_validator(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    min_ihl = rng.choice([5, 6])
    p = make_comb1_problem(
        _make_problem, f"cp_ipv4_{seed}",
        f"CP #{seed % 1000}: IPv4 Packet Header Validator (Ver==4, IHL>={min_ihl}, TTL>1)",
        "cp_arena", difficulty, ["CP-Types", "Packet Parser", "Track 2"],
        "Bit#(16)", "hdr", "Bit#(9)", "validateHdr", "mkCpIpv4Val", "CpIpv4ValIfc",
        f"        Bit#(4) ver = hdr[15:12];\n        Bit#(4) ihl = hdr[11:8];\n        Bit#(8) ttl = hdr[7:0];\n        Bool ok = (ver == 4'd4) && (ihl >= 4'd{min_ihl}) && (ttl > 8'd1);\n        Bit#(8) next_ttl = ok ? (ttl - 8'd1) : 8'd0;\n        return {{pack(ok), next_ttl}};",
        ["16'h4540", "16'h4602", "16'h4501", "16'h6540", "16'h4440"],
        f"### Competitive Specification\nUnpack 16-bit header `hdr` into `ver = hdr[15:12]`, `ihl = hdr[11:8]`, `ttl = hdr[7:0]`. Packet is valid (`ok`) iff `ver == 4'd4 && ihl >= 4'd{min_ihl} && ttl > 8'd1`. Return `{{pack(ok), ok ? (ttl - 1) : 8'd0}}` (`Bit#(9)`).",
        "Line-rate L3 switches validate version, header length, and decrement TTL in a single combinational stage.",
        f"hdr={{ver,ihl,ttl}} ---> [ ver==4 && ihl>={min_ihl} && ttl>1 ] ---> {{ok, ttl-1}}",
        ["Extract `ver = hdr[15:12]`, `ihl = hdr[11:8]`, `ttl = hdr[7:0]`.", f"Check `ok = (ver == 4'd4) && (ihl >= 4'd{min_ihl}) && (ttl > 8'd1);`.", "Return `{pack(ok), ok ? (ttl - 1) : 8'd0}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 2: Strong Types & Vectors")


# =============================================================================
# TRACK 3 FAMILIES (Sequential, Timers, CRC, Dividers) - #43 to #47
# =============================================================================

def _gen_crc8_serial_parallel(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    poly = rng.choice([0x07, 0x1D, 0x31])
    p = make_seq_step_problem(
        _make_problem, f"cp_crc8_{seed}",
        f"CP #{seed % 1000}: Serial CRC-8 Engine (Poly=0x{poly:02X})",
        "cp_arena", difficulty, ["CP-Sequential", "CRC-8", "Track 3"],
        "Bit#(2)", "cmd", "Bit#(8)", "step", "read", "mkCpCrc8", "CpCrc8Ifc",
        "    Reg#(Bit#(8)) crc <- mkReg(8'h00);",
        f"        if (cmd[1] == 1'b1) crc <= 8'h00;\n        else begin\n            Bit#(1) fb = crc[7] ^ cmd[0];\n            crc <= (crc << 1) ^ (fb == 1'b1 ? 8'h{poly:02X} : 8'h00);\n        end",
        "        return crc;",
        ["2'b01", "2'b01", "2'b00", "2'b01", "2'b00", "2'b10", "2'b01"],
        f"### Competitive Specification\nImplement a serial CRC-8 generator with polynomial `8'h{poly:02X}`. Input `cmd = {{clr, din}}`. On `clr == 1`, reset `crc <= 8'h00`. Otherwise compute `fb = crc[7] ^ din` and update `crc <= (crc << 1) ^ (fb == 1 ? 8'h{poly:02X} : 8'h00)`.",
        "LFSR-based CRC engines protect Ethernet, PCIe, and USB frames in hardware.",
        f"cmd={{clr,din}} ---> [ fb=crc[7]^din; crc<=(crc<<1)^(fb?0x{poly:02X}:0) ] ---> crc[7:0]",
        ["Check `if (cmd[1] == 1'b1) crc <= 8'h00;`.", f"Compute `Bit#(1) fb = crc[7] ^ cmd[0];` and update `crc <= (crc << 1) ^ (fb == 1'b1 ? 8'h{poly:02X} : 8'h00);`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 3: Sequential & Rules")


def _gen_clk_divider_fractional(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    inc = rng.choice([3, 5, 7])
    p = make_seq_step_problem(
        _make_problem, f"cp_fdiv_{seed}",
        f"CP #{seed % 1000}: Bresenham Fractional Clock-Enable Generator (Step={inc}/16)",
        "cp_arena", difficulty, ["CP-Sequential", "Fractional Divider", "Track 3"],
        "Bit#(1)", "en", "Bit#(5)", "step", "read", "mkCpFracDiv", "CpFracDivIfc",
        "    Reg#(Bit#(4)) acc <- mkReg(0);\n    Reg#(Bit#(1)) tick_r <- mkReg(0);",
        f"        if (en == 1'b1) begin\n            Bit#(5) s = zeroExtend(acc) + 5'd{inc};\n            acc <= s[3:0];\n            tick_r <= s[4];\n        end else tick_r <= 0;",
        "        return {tick_r, acc};",
        ["1'b1", "1'b1", "1'b1", "1'b1", "1'b1", "1'b1", "1'b0", "1'b1"],
        f"### Competitive Specification\nMaintain 4-bit phase accumulator `acc` and 1-bit overflow pulse `tick_r`. When `en == 1`, compute 5-bit `s = zeroExtend(acc) + 5'd{inc}`, latch `acc <= s[3:0]` and `tick_r <= s[4]`. When `en == 0`, set `tick_r <= 0`. Return `{{tick_r, acc}}`.",
        "Phase-accumulator (DDS/Bresenham) dividers synthesize arbitrary fractional baud rates from a system clock.",
        f"en ---> [ s = acc + {inc}; acc <= s[3:0]; tick_r <= s[4] ] ---> {{tick_r, acc}}",
        [f"Compute `Bit#(5) s = zeroExtend(acc) + 5'd{inc};` when `en == 1'b1`.", "Set `acc <= s[3:0]; tick_r <= s[4];`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 3: Sequential & Rules")


def _gen_ping_pong_wave_gen(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    peak = rng.choice([5, 6, 7])
    p = make_seq_step_problem(
        _make_problem, f"cp_ppong_{seed}",
        f"CP #{seed % 1000}: Triangle-Wave Ping-Pong Counter (0..{peak}..0)",
        "cp_arena", difficulty, ["CP-Sequential", "Ping-Pong Counter", "Track 3"],
        "Bit#(1)", "en", "Bit#(4)", "step", "read", "mkCpPingPong", "CpPingPongIfc",
        "    Reg#(Bit#(3)) val <- mkReg(0);\n    Reg#(Bit#(1)) dir <- mkReg(0);",
        f"        if (en == 1'b1) begin\n            if (dir == 0) begin\n                if (val == 3'd{peak}) begin val <= 3'd{peak - 1}; dir <= 1; end\n                else val <= val + 1;\n            end else begin\n                if (val == 3'd0) begin val <= 3'd1; dir <= 0; end\n                else val <= val - 1;\n            end\n        end",
        "        return {dir, val};",
        ["1'b1"] * 12,
        f"### Competitive Specification\nMaintain `val` (`Bit#(3)`, init 0) and `dir` (`Bit#(1)`, init 0=up). When `en == 1`: if `dir == 0`, count up until `val == 3'd{peak}`, then bounce to `val <= 3'd{peak - 1}; dir <= 1;`. If `dir == 1`, count down until `val == 0`, then bounce to `val <= 3'd1; dir <= 0;`. Return `{{dir, val}}`.",
        "Triangle-wave up/down counters drive center-aligned motor PWM generators.",
        f"en ---> [ 0 -> 1 -> ... -> {peak} -> {peak-1} -> ... -> 0 ] ---> {{dir, val}}",
        [f"When `dir == 0` and `val == 3'd{peak}`, set `val <= 3'd{peak - 1}; dir <= 1;`.", "When `dir == 1` and `val == 3'd0`, set `val <= 3'd1; dir <= 0;`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 3: Sequential & Rules")


def _gen_exp_backoff_controller(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    max_exp = rng.choice([5, 6, 7])
    p = make_seq_step_problem(
        _make_problem, f"cp_bkoff_{seed}",
        f"CP #{seed % 1000}: Collision Exponential Backoff Window Generator (MaxExp={max_exp})",
        "cp_arena", difficulty, ["CP-Sequential", "Networking", "Track 3"],
        "Bit#(2)", "cmd", "Bit#(11)", "step", "read", "mkCpBackoff", "CpBackoffIfc",
        "    Reg#(Bit#(3)) exp_r <- mkReg(0);",
        f"        if (cmd == 2'd1) exp_r <= (exp_r == 3'd{max_exp}) ? 3'd{max_exp} : (exp_r + 1);\n        else if (cmd == 2'd2) exp_r <= 0;",
        "        return {exp_r, (8'd1 << exp_r) - 8'd1};",
        ["2'd1", "2'd1", "2'd1", "2'd1", "2'd2", "2'd1"],
        f"### Competitive Specification\nTrack retry exponent `exp_r` (`Bit#(3)`, init 0). On `cmd == 2'd1` (collision), increment `exp_r` saturating at `3'd{max_exp}`. On `cmd == 2'd2` (success), reset `exp_r <= 0`. Return 11-bit `{{exp_r, (8'd1 << exp_r) - 8'd1}}`.",
        "Ethernet CSMA/CD and NoC contention controllers double the backoff window `(2^k - 1)` on each collision.",
        f"cmd ---> [ exp_r sat {max_exp} ] ---> {{exp_r, (1<<exp_r)-1}}",
        [f"On `cmd == 2'd1`, saturate `exp_r` at `3'd{max_exp}`.", "Return `{exp_r, (8'd1 << exp_r) - 8'd1}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 3: Sequential & Rules")


def _gen_piso_sipo_transceiver(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    msb_first = rng.choice([True, False])
    shift_expr = "(sh << 1)" if msb_first else "(sh >> 1)"
    out_bit = "sh[3]" if msb_first else "sh[0]"
    dir_lbl = "MSB-First" if msb_first else "LSB-First"
    p = make_seq_step_problem(
        _make_problem, f"cp_piso_{seed}",
        f"CP #{seed % 1000}: 4-Bit {dir_lbl} PISO Serializer Shift Register",
        "cp_arena", difficulty, ["CP-Sequential", "PISO Shift Register", "Track 3"],
        "Bit#(5)", "cmd", "Bit#(5)", "step", "read", "mkCpPiso", "CpPisoIfc",
        "    Reg#(Bit#(4)) sh <- mkReg(0);",
        f"        if (cmd[4] == 1'b1) sh <= cmd[3:0];\n        else sh <= {shift_expr};",
        f"        return {{{out_bit}, sh}};",
        ["5'b1_1011", "5'b0_0000", "5'b0_0000", "5'b0_0000", "5'b0_0000"],
        f"### Competitive Specification\nImplement a 4-bit {dir_lbl} Parallel-In Serial-Out (PISO) register `sh`. Given `cmd = {{load, pdata[3:0]}}`: when `load == 1`, load `sh <= cmd[3:0]`; otherwise shift `sh <= {shift_expr}`. Return `{{{out_bit}, sh}}` (`Bit#(5)`).",
        "PISO shift registers serialize parallel bus words onto SPI/UART/JTAG wires.",
        f"cmd={{load,pdata}} ---> [ load ? pdata : {shift_expr} ] ---> {{{out_bit}, sh}}",
        ["When `cmd[4] == 1`, load `sh <= cmd[3:0]`.", f"Otherwise shift `sh <= {shift_expr}` and return `{{{out_bit}, sh}}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 3: Sequential & Rules")


# =============================================================================
# TRACK 4 FAMILIES (Concurrency, Ehr/CReg, FIFOs & QoS) - #48 to #52
# =============================================================================

def _gen_ehr_bypass_pipeline(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    inc = rng.choice([2, 3, 5])
    p = make_seq_step_problem(
        _make_problem, f"cp_ehr_{seed}",
        f"CP #{seed % 1000}: Ehr#(2, Bit#(8)) Intra-Cycle Write-to-Read Bypass Stage (+{inc})",
        "cp_arena", difficulty, ["CP-Concurrency", "Ehr Bypass", "Track 4"],
        "Bit#(9)", "cmd", "Bit#(8)", "step", "read", "mkCpEhrBypass", "CpEhrBypassIfc",
        "    Reg#(Bit#(8)) r <- mkReg(0);",
        f"        Bit#(8) bypassed = (cmd[8] == 1'b1) ? cmd[7:0] : r;\n        r <= bypassed + 8'd{inc};",
        "        return r;",
        ["9'b1_00001010", "9'b0_00000000", "9'b0_00000000", "9'b1_00100000", "9'b0_00000000"],
        f"### Competitive Specification\nModel an `Ehr#(2, Bit#(8))` intra-cycle bypass where port 0 optionally writes `cmd[7:0]` (when `cmd[8] == 1`) and port 1 reads the updated value in the **same cycle** and adds `8'd{inc}`: `bypassed = (cmd[8] == 1) ? cmd[7:0] : r; r <= bypassed + 8'd{inc};`.",
        "Ephemeral History Registers (`Ehr`) forward writes from earlier ports to later ports within the same clock cycle.",
        f"cmd={{we,wdata}} ---> [ bypassed = we ? wdata : r; r <= bypassed + {inc} ] ---> r",
        ["Compute `Bit#(8) bypassed = (cmd[8] == 1'b1) ? cmd[7:0] : r;`.", f"Update `r <= bypassed + 8'd{inc};`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 4: Concurrency & FIFOs")


def _gen_token_bucket_shaper(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    burst_cap = rng.choice([5, 6, 7])
    p = make_seq_step_problem(
        _make_problem, f"cp_tbkt_{seed}",
        f"CP #{seed % 1000}: Token-Bucket QoS Traffic Policer (MaxTokens={burst_cap})",
        "cp_arena", difficulty, ["CP-Concurrency", "QoS Token Bucket", "Track 4"],
        "Bit#(2)", "cmd", "Bit#(4)", "step", "read", "mkCpTokenBucket", "CpTokenBucketIfc",
        f"    Reg#(Bit#(3)) tok <- mkReg(3'd{burst_cap});\n    Reg#(Bit#(1)) pass_r <- mkReg(0);",
        f"        Bool refill = unpack(cmd[1]);\n        Bool req = unpack(cmd[0]);\n        Bit#(3) t1 = (refill && tok < 3'd{burst_cap}) ? (tok + 1) : tok;\n        if (req && t1 > 0) begin tok <= t1 - 1; pass_r <= 1; end\n        else begin tok <= t1; pass_r <= 0; end",
        "        return {pass_r, tok};",
        ["2'b01", "2'b01", "2'b11", "2'b10", "2'b01", "2'b00"],
        f"### Competitive Specification\nMaintain token count `tok` (`Bit#(3)`, init `3'd{burst_cap}`) and `pass_r` (`Bit#(1)`, init 0). Given `cmd = {{refill, req}}`: first apply `refill` (`t1 = (refill && tok < 3'd{burst_cap}) ? tok + 1 : tok`), then if `req && t1 > 0`, consume 1 token (`tok <= t1 - 1; pass_r <= 1;`) else `tok <= t1; pass_r <= 0;`. Return `{{pass_r, tok}}`.",
        "NIC hardware traffic shapers replenish tokens and admit packets in the same clock cycle without losing credits.",
        f"cmd={{refill,req}} ---> [ t1 = refill ? sat({burst_cap}, tok+1) : tok; req -> t1-1 ] ---> {{pass_r, tok}}",
        [f"Compute `t1 = (refill && tok < 3'd{burst_cap}) ? (tok + 1) : tok;`.", "If `req && t1 > 0`, set `tok <= t1 - 1; pass_r <= 1;` else `tok <= t1; pass_r <= 0;`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 4: Concurrency & FIFOs")


def _gen_wfq_weighted_scheduler(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    w0 = rng.choice([2, 3])
    p = make_seq_step_problem(
        _make_problem, f"cp_wfq_{seed}",
        f"CP #{seed % 1000}: 2-Queue Weighted Fair Scheduler ({w0}:1 Quota)",
        "cp_arena", difficulty, ["CP-Concurrency", "WFQ Arbiter", "Track 4"],
        "Bit#(2)", "cmd", "Bit#(4)", "step", "read", "mkCpWfq", "CpWfqIfc",
        f"    Reg#(Bit#(2)) quota <- mkReg(2'd{w0});\n    Reg#(Bit#(2)) gnt <- mkReg(0);",
        f"        if (cmd == 2'b11) begin\n            if (quota > 0) begin gnt <= 2'b01; quota <= quota - 1; end\n            else begin gnt <= 2'b10; quota <= 2'd{w0}; end\n        end else if (cmd[0] == 1'b1) gnt <= 2'b01;\n        else if (cmd[1] == 1'b1) gnt <= 2'b10;\n        else gnt <= 2'b00;",
        "        return {quota, gnt};",
        ["2'b11", "2'b11", "2'b11", "2'b11", "2'b10", "2'b01", "2'b00"],
        f"### Competitive Specification\nSchedule between Queue 0 (weight `{w0}`) and Queue 1 (weight `1`) given `cmd = {{req1, req0}}`. When both request (`cmd == 2'b11`), if `quota > 0` grant Queue 0 (`gnt <= 2'b01; quota <= quota - 1;`), else grant Queue 1 (`gnt <= 2'b10; quota <= 2'd{w0};`). If only one requests, grant it without changing `quota`. Return `{{quota, gnt}}`.",
        "Weighted Fair Queuing (WFQ) prevents high-priority traffic from starving lower-priority flows.",
        f"cmd={{req1,req0}} ---> [ {w0}:1 Weighted Scheduler ] ---> {{quota, gnt}}",
        [f"When `cmd == 2'b11`, check `quota > 0` to grant `2'b01` or reload `quota <= 2'd{w0}` and grant `2'b10`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 4: Concurrency & FIFOs")


def _gen_gearbox_16to8_unpacker(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_gbox16to8_{seed}",
        f"CP #{seed % 1000}: 16-to-8 Unpacking Serializer Gearbox",
        "cp_arena", difficulty, ["CP-Concurrency", "Gearbox 16:8", "Track 4"],
        "Bit#(17)", "cmd", "Bit#(9)", "step", "read", "mkCpGearbox16to8", "CpGearbox16to8Ifc",
        "    Reg#(Bit#(8)) hi_buf <- mkReg(0);\n    Reg#(Bit#(1)) has_hi <- mkReg(0);\n    Reg#(Bit#(8)) out_b <- mkReg(0);",
        "        if (has_hi == 1'b1) begin\n            out_b <= hi_buf;\n            has_hi <= 0;\n        end else if (cmd[16] == 1'b1) begin\n            out_b <= cmd[7:0];\n            hi_buf <= cmd[15:8];\n            has_hi <= 1;\n        end",
        "        return {has_hi, out_b};",
        ["17'h1_CAFE", "17'h0_0000", "17'h1_BEEF", "17'h0_0000"],
        "### Competitive Specification\nUnpack a 16-bit word (`cmd[15:0]` when `cmd[16] == 1`) into two sequential 8-bit outputs: on the load cycle (when `has_hi == 0 && cmd[16] == 1`), output `out_b <= cmd[7:0]`, save `hi_buf <= cmd[15:8]`, and set `has_hi <= 1`. On the next cycle (`has_hi == 1`), emit `out_b <= hi_buf` and clear `has_hi <= 0`. Return `{has_hi, out_b}`.",
        "SERDES and PCIe PCS layers use gearboxes to bridge wide internal datapaths to narrow serial lanes.",
        "cmd={valid,word[15:0]} ---> [ Cycle 0: word[7:0], Cycle 1: word[15:8] ] ---> {has_hi, out_b}",
        ["If `has_hi == 1`, set `out_b <= hi_buf; has_hi <= 0;`.", "Else if `cmd[16] == 1`, set `out_b <= cmd[7:0]; hi_buf <= cmd[15:8]; has_hi <= 1;`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 4: Concurrency & FIFOs")


def _gen_coalescing_irq_ctrl(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    thresh = rng.choice([3, 4])
    p = make_seq_step_problem(
        _make_problem, f"cp_irq_{seed}",
        f"CP #{seed % 1000}: Interrupt Coalescing & Pending Mask Controller (Batch={thresh})",
        "cp_arena", difficulty, ["CP-Concurrency", "Interrupt Controller", "Track 4"],
        "Bit#(5)", "cmd", "Bit#(8)", "step", "read", "mkCpIrqCoal", "CpIrqCoalIfc",
        "    Reg#(Bit#(4)) pend <- mkReg(0);\n    Reg#(Bit#(3)) cnt <- mkReg(0);",
        f"        if (cmd[4] == 1'b1) begin pend <= 0; cnt <= 0; end\n        else begin\n            pend <= pend | cmd[3:0];\n            if (cmd[3:0] != 0) cnt <= (cnt == 3'd{thresh}) ? 3'd{thresh} : (cnt + 1);\n        end",
        f"        return {{pack(cnt >= 3'd{thresh}), cnt, pend}};",
        ["5'b0_0001", "5'b0_0010", "5'b0_0100", "5'b0_1000", "5'b1_0000", "5'b0_0011"],
        f"### Competitive Specification\nGiven `cmd = {{ack_clr, irq_in[3:0]}}`: when `ack_clr == 1`, clear `pend <= 0; cnt <= 0;`. Otherwise OR-accumulate `pend <= pend | cmd[3:0]` and whenever `cmd[3:0] != 0`, increment event counter `cnt` (saturating at `3'd{thresh}`). Assert interrupt line `fire = (cnt >= 3'd{thresh})`. Return `{{pack(fire), cnt, pend}}` (`Bit#(8)`).",
        "High-speed NVMe and Ethernet controllers coalesce interrupts until N events accumulate to avoid CPU interrupt storms.",
        f"cmd={{clr,irq[3:0]}} ---> [ pend |= irq; cnt++ ] ---> {{cnt>={thresh}, cnt, pend}}",
        [f"Accumulate `pend <= pend | cmd[3:0];` and increment `cnt` saturating at `3'd{thresh}` when `cmd[3:0] != 0`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 4: Concurrency & FIFOs")


# =============================================================================
# TRACK 5 FAMILIES (FSMs, Serial Protocols, Bus Bridges) - #53 to #57
# =============================================================================

def _gen_uart_rx_oversampler(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    half_baud = rng.choice([2, 3])
    p = make_seq_step_problem(
        _make_problem, f"cp_uartrx_{seed}",
        f"CP #{seed % 1000}: UART Start-Bit Mid-Eye Detector FSM (MidTick={half_baud})",
        "cp_arena", difficulty, ["CP-FSM", "UART Receiver", "Track 5"],
        "Bit#(1)", "rx_in", "Bit#(4)", "step", "read", "mkCpUartStart", "CpUartStartIfc",
        "    Reg#(Bit#(3)) ticks <- mkReg(0);\n    Reg#(Bit#(1)) locked <- mkReg(0);",
        f"        if (rx_in == 1'b0) begin\n            if (ticks == 3'd{half_baud}) locked <= 1;\n            else ticks <= ticks + 1;\n        end else begin\n            ticks <= 0;\n            locked <= 0;\n        end",
        "        return {locked, ticks};",
        ["1'b1", "1'b0", "1'b1", "1'b0", "1'b0", "1'b0", "1'b0", "1'b1"],
        f"### Competitive Specification\nDetect a valid UART start bit by verifying `rx_in == 0` stays low for `{half_baud}` consecutive oversample ticks: while `rx_in == 0`, if `ticks == 3'd{half_baud}` set `locked <= 1`, else increment `ticks <= ticks + 1`. Whenever `rx_in == 1`, reset `ticks <= 0; locked <= 0;`. Return `{{locked, ticks}}`.",
        "Oversampling the UART start bit until the center of the bit eye filters out false start glitches on noisy serial lines.",
        f"rx_in ---> [ Count 0s up to {half_baud} -> locked=1 ] ---> {{locked, ticks}}",
        [f"When `rx_in == 0`, check `ticks == 3'd{half_baud}` to set `locked <= 1` else `ticks <= ticks + 1`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 5: FSMs & Serial Protocols")


def _gen_spi_cpol_cpha_master(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_spi_{seed}",
        f"CP #{seed % 1000}: SPI Full-Duplex Master Shift-Exchange FSM",
        "cp_arena", difficulty, ["CP-FSM", "SPI Master", "Track 5"],
        "Bit#(6)", "cmd", "Bit#(5)", "step", "read", "mkCpSpiMaster", "CpSpiMasterIfc",
        "    Reg#(Bit#(4)) sh <- mkReg(0);\n    Reg#(Bit#(1)) busy <- mkReg(0);\n    Reg#(Bit#(2)) cnt <- mkReg(0);",
        "        if (cmd[5] == 1'b1) begin\n            sh <= cmd[3:0]; busy <= 1; cnt <= 3;\n        end else if (busy == 1'b1) begin\n            sh <= {sh[2:0], cmd[4]};\n            if (cnt == 0) busy <= 0;\n            else cnt <= cnt - 1;\n        end",
        "        return {busy, sh};",
        ["6'b1_0_1010", "6'b0_1_0000", "6'b0_0_0000", "6'b0_1_0000", "6'b0_1_0000"],
        "### Competitive Specification\nGiven `cmd = {start, miso, tx_init[3:0]}`: when `start == 1`, load `sh <= cmd[3:0]; busy <= 1; cnt <= 3;`. While `busy == 1` (and `start == 0`), shift `sh <= {sh[2:0], cmd[4]}` (capturing `miso`) and if `cnt == 0` set `busy <= 0` else `cnt <= cnt - 1`. Return `{busy, sh}`.",
        "SPI simultaneously shifts out MOSI (`sh[3]`) and shifts in MISO (`cmd[4]`) into the same shift register.",
        "cmd={start,miso,tx[3:0]} ---> [ sh <= {sh[2:0], miso} ] ---> {busy, sh}",
        ["On `cmd[5] == 1`, load `sh <= cmd[3:0]; busy <= 1; cnt <= 3;`.", "While `busy == 1`, shift `sh <= {sh[2:0], cmd[4]}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 5: FSMs & Serial Protocols")


def _gen_i2c_addr_matcher_fsm(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    my_addr = rng.choice([0x2A, 0x50, 0x68])
    p = make_comb1_problem(
        _make_problem, f"cp_i2c_{seed}",
        f"CP #{seed % 1000}: I2C 7-Bit Target Address & Broadcast Matcher (Addr=0x{my_addr:02X})",
        "cp_arena", difficulty, ["CP-FSM", "I2C Protocol", "Track 5"],
        "Bit#(8)", "addr_byte", "Bit#(3)", "matchI2c", "mkCpI2cMatch", "CpI2cMatchIfc",
        f"        Bit#(7) a = addr_byte[7:1];\n        Bit#(1) rw = addr_byte[0];\n        Bool hit = (a == 7'h{my_addr:02X}) || (a == 7'h00);\n        return {{pack(hit), pack(a == 7'h00), rw}};",
        [f"8'h{(my_addr << 1):02X}", f"8'h{(my_addr << 1) | 1:02X}", "8'h00", "8'hFF", "8'hA0"],
        f"### Competitive Specification\nGiven an I2C address byte `addr_byte = {{addr[6:0], rw}}`: check if `addr == 7'h{my_addr:02X}` (unicast match) or `addr == 7'h00` (general call broadcast). Return 3-bit `{{pack(hit), pack(addr == 7'h00), rw}}`.",
        "I2C target peripherals match both their assigned 7-bit slave address and the `7'h00` General Call address.",
        f"addr_byte[7:0] ---> [ addr==0x{my_addr:02X} || addr==0x00 ] ---> {{hit, is_gcall, rw}}",
        [f"Slice `a = addr_byte[7:1]` and `rw = addr_byte[0]`.", f"Set `hit = (a == 7'h{my_addr:02X}) || (a == 7'h00);` and return `{{pack(hit), pack(a == 7'h00), rw}}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 5: FSMs & Serial Protocols")


def _gen_hdlc_zero_stuffer_fsm(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    max_ones = rng.choice([4, 5])
    p = make_seq_step_problem(
        _make_problem, f"cp_hdlc_{seed}",
        f"CP #{seed % 1000}: HDLC / USB Bit-Stuffer FSM (Stuff Zero After {max_ones} Ones)",
        "cp_arena", difficulty, ["CP-FSM", "HDLC / USB", "Track 5"],
        "Bit#(1)", "din", "Bit#(4)", "step", "read", "mkCpHdlcStuff", "CpHdlcStuffIfc",
        "    Reg#(Bit#(3)) ones <- mkReg(0);\n    Reg#(Bit#(1)) stuff <- mkReg(0);",
        f"        if (din == 1'b1) begin\n            if (ones == 3'd{max_ones - 1}) begin ones <= 0; stuff <= 1; end\n            else begin ones <= ones + 1; stuff <= 0; end\n        end else begin\n            ones <= 0; stuff <= 0;\n        end",
        "        return {stuff, ones};",
        ["1'b1", "1'b1", "1'b1", "1'b1", "1'b1", "1'b1", "1'b0", "1'b1"],
        f"### Competitive Specification\nTrack consecutive `1` bits on `din`. When `{max_ones}` consecutive `1`s arrive (`din == 1 && ones == 3'd{max_ones - 1}`), assert `stuff <= 1` and reset `ones <= 0`. Otherwise increment `ones` on `din == 1` (or reset `ones <= 0` on `din == 0`) with `stuff <= 0`. Return `{{stuff, ones}}`.",
        "USB 2.0, CAN, and HDLC transmitters insert a stuff bit after N consecutive 1s to guarantee clock recovery transitions.",
        f"din ---> [ Count consecutive 1s up to {max_ones} -> stuff=1 ] ---> {{stuff, ones}}",
        [f"When `din == 1` and `ones == 3'd{max_ones - 1}`, set `ones <= 0; stuff <= 1;`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 5: FSMs & Serial Protocols")


def _gen_axi_burst_chopper_fsm(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    max_burst = rng.choice([3, 4])
    p = make_seq_step_problem(
        _make_problem, f"cp_axichop_{seed}",
        f"CP #{seed % 1000}: AXI Burst Chopper FSM (MaxSubBurst={max_burst} Beats)",
        "cp_arena", difficulty, ["CP-FSM", "AXI4 DMA", "Track 5"],
        "Bit#(5)", "cmd", "Bit#(7)", "step", "read", "mkCpAxiChopper", "CpAxiChopperIfc",
        "    Reg#(Bit#(4)) rem <- mkReg(0);\n    Reg#(Bit#(3)) sub_b <- mkReg(0);",
        f"        if (cmd[4] == 1'b1) begin rem <= cmd[3:0]; sub_b <= 0; end\n        else if (rem > 0) begin\n            Bit#(4) b = (rem > 4'd{max_burst}) ? 4'd{max_burst} : rem;\n            sub_b <= truncate(b);\n            rem <= rem - b;\n        end else sub_b <= 0;",
        "        return {rem, sub_b};",
        ["5'b1_1010", "5'b0_0000", "5'b0_0000", "5'b0_0000", "5'b0_0000"],
        f"### Competitive Specification\nGiven `cmd = {{start, total_beats[3:0]}}`: on `start == 1`, load `rem <= cmd[3:0]; sub_b <= 0;`. Each subsequent cycle while `rem > 0`, issue a sub-burst of size `b = min(rem, 4'd{max_burst})` (`sub_b <= truncate(b); rem <= rem - b;`). Return `{{rem, sub_b}}`.",
        "DMA engines chop large transfers into smaller bursts to respect AXI 4KB boundary and QoS latency limits.",
        f"cmd={{start,len}} ---> [ b = min(rem, {max_burst}); rem -= b ] ---> {{rem, sub_b}}",
        [f"While `rem > 0`, compute `Bit#(4) b = (rem > 4'd{max_burst}) ? 4'd{max_burst} : rem;`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 5: FSMs & Serial Protocols")


# =============================================================================
# TRACK 6 FAMILIES (Digital Arithmetic, VLSI Datapaths & DSP) - #58 to #62
# =============================================================================

def _gen_q4_4_fixed_point_mac(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb2_problem(
        _make_problem, f"cp_q44_{seed}",
        f"CP #{seed % 1000}: Q4.4 Fixed-Point Multiplier with Half-LSB Rounding",
        "cp_arena", difficulty, ["CP-DSP", "Fixed-Point Q4.4", "Track 6"],
        "Bit#(8)", "a", "Bit#(8)", "b", "Bit#(8)", "mulQ44", "mkCpQ44Mul", "CpQ44MulIfc",
        "        Bit#(16) prod = zeroExtend(a) * zeroExtend(b) + 16'd8;\n        return prod[11:4];",
        [("8'h10", "8'h10"), ("8'h18", "8'h18"), ("8'h24", "8'h08"), ("8'h0C", "8'h0C")],
        "### Competitive Specification\nMultiply two unsigned Q4.4 fixed-point numbers `a` and `b` (4 integer bits, 4 fractional bits), add `16'd8` (`0.5` LSB of the Q4.4 output) for rounding, and return the middle 8 bits `prod[11:4]`.",
        "Fixed-point DSP hardware adds `1 << (frac_bits - 1)` before slicing to achieve round-to-nearest.",
        "(a, b) [Q4.4] ---> [ prod = a*b + 8 ] ---> prod[11:4] [Q4.4]",
        ["Compute `Bit#(16) prod = zeroExtend(a) * zeroExtend(b) + 16'd8;`.", "Return `prod[11:4];`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 6: Arithmetic & DSP")


def _gen_cordic_stage_rotator(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    shift_k = rng.choice([1, 2])
    p = make_comb2_problem(
        _make_problem, f"cp_cordic_{seed}",
        f"CP #{seed % 1000}: CORDIC Stage-{shift_k} Micro-Rotation Datapath",
        "cp_arena", difficulty, ["CP-DSP", "CORDIC", "Track 6"],
        "Bit#(8)", "x", "Bit#(8)", "y", "Bit#(16)", "cordicStep", "mkCpCordic", "CpCordicIfc",
        f"        Bit#(8) xn = x - (y >> {shift_k});\n        Bit#(8) yn = y + (x >> {shift_k});\n        return {{xn, yn}};",
        [("8'd64", "8'd0"), ("8'd64", "8'd32"), ("8'd100", "8'd20"), ("8'd40", "8'd40")],
        f"### Competitive Specification\nCompute one counter-clockwise CORDIC micro-rotation stage with shift index `k = {shift_k}`: `xn = x - (y >> {shift_k})` and `yn = y + (x >> {shift_k})`. Return 16-bit `{{xn, yn}}`.",
        "CORDIC computes trigonometric rotations using only bit-shifts and additions.",
        f"(x, y) ---> [ xn = x - (y>>{shift_k}), yn = y + (x>>{shift_k}) ] ---> {{xn, yn}}",
        [f"Compute `xn = x - (y >> {shift_k})` and `yn = y + (x >> {shift_k})`.", "Return `{xn, yn}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 6: Arithmetic & DSP")


def _gen_fir_3tap_symmetric(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    c0 = rng.choice([1, 2])
    c1 = rng.choice([2, 4])
    p = make_seq_step_problem(
        _make_problem, f"cp_fir3_{seed}",
        f"CP #{seed % 1000}: 3-Tap Symmetric FIR Filter (Taps=[{c0}, {c1}, {c0}])",
        "cp_arena", difficulty, ["CP-DSP", "FIR Filter", "Track 6"],
        "Bit#(4)", "x_in", "Bit#(8)", "step", "read", "mkCpFir3", "CpFir3Ifc",
        "    Reg#(Bit#(4)) x0 <- mkReg(0);\n    Reg#(Bit#(4)) x1 <- mkReg(0);\n    Reg#(Bit#(4)) x2 <- mkReg(0);",
        "        x0 <= x_in; x1 <= x0; x2 <= x1;",
        f"        return (zeroExtend(x0) + zeroExtend(x2)) * 8'd{c0} + zeroExtend(x1) * 8'd{c1};",
        ["4'd4", "4'd8", "4'd12", "4'd0", "4'd0", "4'd5"],
        f"### Competitive Specification\nMaintain a 3-sample delay line `x0, x1, x2` (`Reg#(Bit#(4))`, init 0). On `step(x_in)`, shift `x0 <= x_in; x1 <= x0; x2 <= x1;`. In `read()`, exploit tap symmetry `[{c0}, {c1}, {c0}]` by pre-adding `(zeroExtend(x0) + zeroExtend(x2)) * 8'd{c0} + zeroExtend(x1) * 8'd{c1}`.",
        "Linear-phase symmetric FIR filters pre-add symmetric delay taps to cut multiplier count in half!",
        f"x_in ---> [ x0 -> x1 -> x2 ] ---> (x0+x2)*{c0} + x1*{c1}",
        ["Shift `x0 <= x_in; x1 <= x0; x2 <= x1;`.", f"Return `(zeroExtend(x0) + zeroExtend(x2)) * 8'd{c0} + zeroExtend(x1) * 8'd{c1};`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 6: Arithmetic & DSP")


def _gen_ewma_iir_filter(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    sh = rng.choice([1, 2])
    p = make_seq_step_problem(
        _make_problem, f"cp_ewma_{seed}",
        f"CP #{seed % 1000}: Exponentially Weighted Moving Average (EWMA) IIR Filter (Shift={sh})",
        "cp_arena", difficulty, ["CP-DSP", "IIR Filter", "Track 6"],
        "Bit#(8)", "sample", "Bit#(8)", "step", "read", "mkCpEwma", "CpEwmaIfc",
        "    Reg#(Bit#(8)) avg <- mkReg(0);",
        f"        avg <= avg - (avg >> {sh}) + (sample >> {sh});",
        "        return avg;",
        ["8'd64", "8'd64", "8'd128", "8'd128", "8'd0", "8'd32"],
        f"### Competitive Specification\nUpdate state register `avg` (`Reg#(Bit#(8))`, init 0) on each `sample` using multiplierless IIR smoothing: `avg <= avg - (avg >> {sh}) + (sample >> {sh});`. Return `avg`.",
        "Shift-and-subtract EWMA filters smooth sensor telemetry and TCP RTT estimates using zero DSP multipliers.",
        f"sample ---> [ avg <= avg - (avg>>{sh}) + (sample>>{sh}) ] ---> avg",
        [f"Update `avg <= avg - (avg >> {sh}) + (sample >> {sh});`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 6: Arithmetic & DSP")


def _gen_sorting_network_4elem(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb1_problem(
        _make_problem, f"cp_sort4_{seed}",
        f"CP #{seed % 1000}: 4-Nibble Parallel Bitonic Sorting Network (Ascending)",
        "cp_arena", difficulty, ["CP-DSP", "Sorting Network", "Track 6"],
        "Bit#(16)", "x", "Bit#(16)", "sort4", "mkCpSort4", "CpSort4Ifc",
        "        Bit#(4) a = x[3:0]; Bit#(4) b = x[7:4]; Bit#(4) c = x[11:8]; Bit#(4) d = x[15:12];\n"
        "        if (a > b) begin Bit#(4) t = a; a = b; b = t; end\n"
        "        if (c > d) begin Bit#(4) t = c; c = d; d = t; end\n"
        "        if (a > c) begin Bit#(4) t = a; a = c; c = t; end\n"
        "        if (b > d) begin Bit#(4) t = b; b = d; d = t; end\n"
        "        if (b > c) begin Bit#(4) t = b; b = c; c = t; end\n"
        "        return {d, c, b, a};",
        ["16'h1423", "16'hFEDC", "16'h0918", "16'h5555", "16'h3719"],
        "### Competitive Specification\nSort the four 4-bit nibbles `a=x[3:0], b=x[7:4], c=x[11:8], d=x[15:12]` in ascending order (`a <= b <= c <= d`) using a 5-comparator sorting network, and return `{d, c, b, a}`.",
        "5-comparator sorting networks sort 4 elements in a single clock cycle for median filters and switch schedulers.",
        "x={d,c,b,a} ---> [ 5 Compare-and-Swap Stages ] ---> {max, mid2, mid1, min}",
        ["Compare-swap pairs `(a,b)` and `(c,d)`, then `(a,c)` and `(b,d)`, then `(b,c)`.", "Return `{d, c, b, a}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 6: Arithmetic & DSP")


# =============================================================================
# TRACK 7 FAMILIES (Memory Subsystems, BRAMs, CAMs, LIFO, Free-List) - #63 to #68
# =============================================================================

def _gen_bram_write_first_bypass(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    write_first = rng.choice([True, False])
    mode_name = "Write-First (Bypass New Data on Collision)" if write_first else "Read-First (Return Old Data on Collision)"
    dout_expr = "(we && (waddr == raddr)) ? wdata : mem[raddr]" if write_first else "mem[raddr]"
    p = make_seq_step_problem(
        _make_problem, f"cp_bram_{seed}",
        f"CP #{seed % 1000}: Dual-Port 4x8 Synchronous BRAM ({'Write-First' if write_first else 'Read-First'})",
        "cp_arena", difficulty, ["CP-Memory", "BRAM Collision", "Track 7"],
        "Bit#(13)", "cmd", "Bit#(8)", "step", "read", "mkCpBram", "CpBramIfc",
        "    Vector#(4, Reg#(Bit#(8))) mem <- replicateM(mkReg(0));\n    Reg#(Bit#(8)) rdata <- mkReg(0);",
        f"        Bool we = unpack(cmd[12]);\n        Bit#(2) waddr = cmd[11:10];\n        Bit#(2) raddr = cmd[9:8];\n        Bit#(8) wdata = cmd[7:0];\n        if (we) mem[waddr] <= wdata;\n        rdata <= {dout_expr};",
        "        return rdata;",
        ["13'b1_01_00_10100101", "13'b1_01_01_11110000", "13'b0_00_01_00000000", "13'b1_10_10_00001111"],
        f"### Competitive Specification\nImplement a 4x8 synchronous BRAM with **{mode_name}** semantics. Given `cmd = {{we, waddr[1:0], raddr[1:0], wdata[7:0]}}`: if `we == 1`, write `mem[waddr] <= wdata`, and latch `rdata <= {dout_expr}`. Return `rdata`.",
        "Understanding Read-First vs Write-First address collision behavior is essential when inferring FPGA Block RAMs.",
        f"cmd={{we,waddr,raddr,wdata}} ---> [ rdata <= {dout_expr} ] ---> rdata",
        [f"Latch `rdata <= {dout_expr};` and update `if (we) mem[waddr] <= wdata;`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 7: Memory Subsystems")


def _gen_cam_4entry_lookup(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb2_problem(
        _make_problem, f"cp_cam_{seed}",
        f"CP #{seed % 1000}: 4-Entry Content-Addressable Memory (CAM) Parallel Match Mask",
        "cp_arena", difficulty, ["CP-Memory", "CAM Lookup", "Track 7"],
        "Bit#(16)", "cam_keys", "Bit#(4)", "search_key", "Bit#(5)", "camLookup", "mkCpCam4", "CpCam4Ifc",
        "        Bit#(4) m = 0;\n        for (Integer i = 0; i < 4; i = i + 1) begin\n            m[i] = (cam_keys[4*i+3 : 4*i] == search_key) ? 1'b1 : 1'b0;\n        end\n        return {|m, m};",
        [("16'hCBA9", "4'hA"), ("16'h5A5A", "4'h5"), ("16'h1234", "4'hF"), ("16'hFFFF", "4'hF")],
        "### Competitive Specification\nCompare `search_key` (`Bit#(4)`) in parallel against all four 4-bit entries packed in `cam_keys` (`cam_keys[4*i+3:4*i]`). Set `m[i] = 1` on match, and return 5-bit `{|m, m}` (`{hit_any, match_bitmap}`).",
        "Fully associative TLBs and cache tag arrays use parallel CAM comparators to locate entries in 1 cycle.",
        "(cam_keys[15:0], search_key[3:0]) ---> [ m[i] = (key_i == search_key) ] ---> {|m, m}",
        ["Loop `i` from 0 to 3 and set `m[i] = pack(cam_keys[4*i+3 : 4*i] == search_key);`.", "Return `{|m, m}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 7: Memory Subsystems")


def _gen_tcam_wildcard_matcher(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb2_problem(
        _make_problem, f"cp_tcam_{seed}",
        f"CP #{seed % 1000}: Ternary CAM (TCAM) Wildcard Mask Rule Matcher",
        "cp_arena", difficulty, ["CP-Memory", "TCAM / ACL", "Track 7"],
        "Bit#(8)", "pkt_key", "Bit#(16)", "rule_spec", "Bit#(1)", "tcamMatch", "mkCpTcam", "CpTcamIfc",
        "        Bit#(8) r_val  = rule_spec[15:8];\n        Bit#(8) r_mask = rule_spec[7:0];\n        return (((pkt_key ^ r_val) & ~r_mask) == 0) ? 1'b1 : 1'b0;",
        [("8'hA5", "16'hA0_0F"), ("8'hB5", "16'hA0_0F"), ("8'hFF", "16'h00_FF"), ("8'h42", "16'h42_00")],
        "### Competitive Specification\nGiven `pkt_key` (`Bit#(8)`) and `rule_spec = {r_val[7:0], r_mask[7:0]}` where `r_mask[i] == 1` marks a wildcard ('don't care') bit: return `1'b1` iff `((pkt_key ^ r_val) & ~r_mask) == 0`.",
        "Network routers use Ternary CAMs (0, 1, X) for longest-prefix routing and ACL firewall tables.",
        "(pkt_key, {r_val, r_mask}) ---> [ ((pkt_key ^ r_val) & ~r_mask) == 0 ] ---> match",
        ["Extract `r_val = rule_spec[15:8]` and `r_mask = rule_spec[7:0]`.", "Return `(((pkt_key ^ r_val) & ~r_mask) == 0) ? 1'b1 : 1'b0;`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 7: Memory Subsystems")


def _gen_lifo_hardware_stack(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_lifo_{seed}",
        f"CP #{seed % 1000}: 4-Deep Hardware LIFO Call/Return Stack",
        "cp_arena", difficulty, ["CP-Memory", "LIFO Stack", "Track 7"],
        "Bit#(6)", "cmd", "Bit#(7)", "step", "read", "mkCpLifo", "CpLifoIfc",
        "    Vector#(4, Reg#(Bit#(4))) stk <- replicateM(mkReg(0));\n    Reg#(Bit#(3)) sp <- mkReg(0);",
        "        Bool push = unpack(cmd[5]);\n        Bool pop  = unpack(cmd[4]);\n        if (push && sp < 4) begin stk[sp[1:0]] <= cmd[3:0]; sp <= sp + 1; end\n        else if (pop && sp > 0) begin sp <= sp - 1; end",
        "        Bit#(2) top_idx = (sp > 0) ? truncate(sp - 1) : 0;\n        return {sp, (sp > 0) ? stk[top_idx] : 4'd0};",
        ["6'b10_1010", "6'b10_1100", "6'b01_0000", "6'b10_0101", "6'b01_0000", "6'b01_0000"],
        "### Competitive Specification\nImplement a 4-entry 4-bit LIFO stack `stk` with stack pointer `sp` (`Bit#(3)`, `0..4`). Given `cmd = {push, pop, din[3:0]}`: on `push && sp < 4`, write `stk[sp[1:0]] <= cmd[3:0]; sp <= sp + 1;`. On `!push && pop && sp > 0`, decrement `sp <= sp - 1;`. Return `{sp, (sp > 0) ? stk[truncate(sp - 1)] : 4'd0}` (`Bit#(7)`).",
        "Hardware return-address stacks (RAS) and expression evaluators use low-latency register-based LIFOs.",
        "cmd={push,pop,din} ---> [ 4-Entry LIFO Stack (sp=0..4) ] ---> {sp, top}",
        ["Push to `stk[sp[1:0]]` when `push && sp < 4`, and read top from `stk[truncate(sp - 1)]` when `sp > 0`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 7: Memory Subsystems")


def _gen_bitmap_freelist_alloc(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb1_problem(
        _make_problem, f"cp_flist_{seed}",
        f"CP #{seed % 1000}: 8-Slot Physical Register Free-List Priority Allocator",
        "cp_arena", difficulty, ["CP-Memory", "Free-List Allocator", "Track 7"],
        "Bit#(8)", "free_mask", "Bit#(12)", "allocSlot", "mkCpFreeList", "CpFreeListIfc",
        "        Bit#(3) idx = 0;\n        Bool found = False;\n        for (Integer i = 0; i < 8; i = i + 1) begin\n            if (!found && free_mask[i] == 1'b1) begin idx = fromInteger(i); found = True; end\n        end\n        Bit#(8) next_mask = found ? (free_mask & ~(8'd1 << idx)) : free_mask;\n        return {pack(found), idx, next_mask};",
        ["8'b1111_1111", "8'b1111_1110", "8'b1010_0000", "8'b0000_0000", "8'b0001_0000"],
        "### Competitive Specification\nGiven an 8-bit `free_mask` (`1` = free slot), find the lowest-indexed free slot `idx` (`0..7`), clear that bit in `next_mask = free_mask & ~(8'd1 << idx)`, and return 12-bit `{pack(found), idx, next_mask}`.",
        "Out-of-order CPU register alias tables (RAT) allocate free physical registers from a bitmask every cycle.",
        "free_mask[7:0] ---> [ Find lowest 1-bit idx & clear ] ---> {found, idx[2:0], next_mask[7:0]}",
        ["Find the first `i` where `free_mask[i] == 1`.", "Clear `free_mask & ~(8'd1 << idx)` when `found`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 7: Memory Subsystems")


def _gen_bloom_filter_2hash(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_bloom_{seed}",
        f"CP #{seed % 1000}: 8-Bit Dual-Hash Hardware Bloom Filter",
        "cp_arena", difficulty, ["CP-Memory", "Bloom Filter", "Track 7"],
        "Bit#(7)", "cmd", "Bit#(9)", "step", "read", "mkCpBloom", "CpBloomIfc",
        "    Reg#(Bit#(8)) bmap <- mkReg(0);\n    Reg#(Bit#(1)) hit_r <- mkReg(0);",
        "        Bit#(3) h1 = cmd[2:0];\n        Bit#(3) h2 = cmd[5:3] ^ cmd[2:0];\n        if (cmd[6] == 1'b1) begin\n            bmap <= bmap | (8'd1 << h1) | (8'd1 << h2);\n            hit_r <= 1;\n        end else begin\n            hit_r <= bmap[h1] & bmap[h2];\n        end",
        "        return {hit_r, bmap};",
        ["7'b1_001_010", "7'b0_001_010", "7'b0_111_000", "7'b1_111_000", "7'b0_111_000"],
        "### Competitive Specification\nMaintain an 8-bit Bloom filter `bmap` (`Reg#(Bit#(8))`, init 0). For `cmd = {insert, key[5:0]}`, compute `h1 = cmd[2:0]` and `h2 = cmd[5:3] ^ cmd[2:0]`. If `insert == 1`, set both bits `bmap <= bmap | (8'd1 << h1) | (8'd1 << h2); hit_r <= 1;`. Otherwise query `hit_r <= bmap[h1] & bmap[h2];`. Return `{hit_r, bmap}`.",
        "Hardware Bloom filters avoid unnecessary cache snoop and off-chip DRAM lookups.",
        "cmd={ins,key[5:0]} ---> [ h1=k[2:0], h2=k[5:3]^k[2:0] ] ---> {hit_r, bmap}",
        ["Compute `h1 = cmd[2:0]` and `h2 = cmd[5:3] ^ cmd[2:0]`.", "OR-in `(8'd1 << h1) | (8'd1 << h2)` on insert, or check `bmap[h1] & bmap[h2]` on query."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 7: Memory Subsystems")


# =============================================================================
# TRACK 8 FAMILIES (CDC, Gray Pointers, Resets & Handshakes) - #69 to #73
# =============================================================================

def _gen_cdc_syncbit_chain(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_cdcsync_{seed}",
        f"CP #{seed % 1000}: 3-Stage CDC Synchronizer + Rising/Falling Edge Detector",
        "cp_arena", difficulty, ["CP-CDC", "SyncBit Chain", "Track 8"],
        "Bit#(1)", "async_in", "Bit#(5)", "step", "read", "mkCpCdcSync", "CpCdcSyncIfc",
        "    Reg#(Bit#(1)) s1 <- mkReg(0);\n    Reg#(Bit#(1)) s2 <- mkReg(0);\n    Reg#(Bit#(1)) s3 <- mkReg(0);",
        "        s1 <= async_in; s2 <= s1; s3 <= s2;",
        "        return {s2 & ~s3, ~s2 & s3, s3, s2, s1};",
        ["1'b0", "1'b1", "1'b1", "1'b1", "1'b0", "1'b0", "1'b1"],
        "### Competitive Specification\nShift `async_in` through a 3-FF synchronizer chain `s1 <= async_in; s2 <= s1; s3 <= s2;`. In `read()`, return `{rise, fall, s3, s2, s1}` where `rise = s2 & ~s3` and `fall = ~s2 & s3`.",
        "2-FF synchronization (`s1, s2`) resolves metastability while the 3rd FF (`s3`) enables synchronous edge detection in the destination clock domain.",
        "async_in ---> [ s1 -> s2 -> s3 ] ---> {s2 & ~s3, ~s2 & s3, s3, s2, s1}",
        ["Shift `s1 <= async_in; s2 <= s1; s3 <= s2;`.", "Return `{s2 & ~s3, ~s2 & s3, s3, s2, s1}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 8: Clock Domain Crossing")


def _gen_cdc_toggle_pulse_sync(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_cdcpulse_{seed}",
        f"CP #{seed % 1000}: Toggle-Based Cross-Domain Pulse Synchronizer (`mkSyncPulse`)",
        "cp_arena", difficulty, ["CP-CDC", "SyncPulse", "Track 8"],
        "Bit#(1)", "src_pulse", "Bit#(4)", "step", "read", "mkCpSyncPulse", "CpSyncPulseIfc",
        "    Reg#(Bit#(1)) tog <- mkReg(0);\n    Reg#(Bit#(1)) d1 <- mkReg(0);\n    Reg#(Bit#(1)) d2 <- mkReg(0);",
        "        Bit#(1) next_tog = tog ^ src_pulse;\n        tog <= next_tog;\n        d1 <= next_tog;\n        d2 <= d1;",
        "        return {d1 ^ d2, d2, d1, tog};",
        ["1'b0", "1'b1", "1'b0", "1'b0", "1'b1", "1'b1", "1'b0"],
        "### Competitive Specification\nConvert `src_pulse` into a toggle level `next_tog = tog ^ src_pulse`, register `tog <= next_tog`, and pass it through destination stages `d1 <= next_tog; d2 <= d1;`. Output `{dst_pulse, d2, d1, tog}` where `dst_pulse = d1 ^ d2`.",
        "A single-cycle pulse in a fast domain is converted to a level toggle (`tog ^ pulse`) so a slower destination clock never misses it.",
        "src_pulse ---> [ tog ^= pulse ] ---> [ d1 -> d2 ] ---> dst_pulse = d1 ^ d2",
        ["Compute `Bit#(1) next_tog = tog ^ src_pulse;`.", "Update `tog <= next_tog; d1 <= next_tog; d2 <= d1;` and return `{d1 ^ d2, d2, d1, tog}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 8: Clock Domain Crossing")


def _gen_cdc_reset_stretcher(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    hold = rng.choice([3, 4])
    p = make_seq_step_problem(
        _make_problem, f"cp_rststr_{seed}",
        f"CP #{seed % 1000}: {hold}-Cycle Reset Stretcher Bridge (`SyncReset`)",
        "cp_arena", difficulty, ["CP-CDC", "Reset Stretcher", "Track 8"],
        "Bit#(1)", "rst_req", "Bit#(4)", "step", "read", "mkCpRstStretch", "CpRstStretchIfc",
        f"    Reg#(Bit#(3)) cnt <- mkReg(3'd{hold});",
        f"        if (rst_req == 1'b1) cnt <= 3'd{hold};\n        else if (cnt > 0) cnt <= cnt - 1;",
        "        return {pack(cnt > 0), cnt};",
        ["1'b0", "1'b0", "1'b1", "1'b0", "1'b0", "1'b0", "1'b0"],
        f"### Competitive Specification\nHold reset active (`rst_out = (cnt > 0)`) for `{hold}` clock cycles after `rst_req == 1`: when `rst_req == 1`, reload `cnt <= 3'd{hold}`; otherwise if `cnt > 0`, decrement `cnt <= cnt - 1`. Return `{{pack(cnt > 0), cnt}}`.",
        "BSV's `mkAsyncReset` stretches reset assertion across N destination clock edges so all flip-flops exit reset cleanly.",
        f"rst_req ---> [ cnt = {hold} down to 0 ] ---> {{cnt > 0, cnt}}",
        [f"Reload `cnt <= 3'd{hold}` on `rst_req == 1`, else decrement while `cnt > 0`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 8: Clock Domain Crossing")


def _gen_cdc_async_fifo_gray_occ(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    af_th = rng.choice([5, 6])
    p = make_comb2_problem(
        _make_problem, f"cp_cdcocc_{seed}",
        f"CP #{seed % 1000}: Gray-Pointer Async FIFO Occupancy & Almost-Full>={af_th} Calculator",
        "cp_arena", difficulty, ["CP-CDC", "Async FIFO Gray", "Track 8"],
        "Bit#(4)", "wgray", "Bit#(4)", "rgray", "Bit#(7)", "calcFifoOcc", "mkCpAsyncOcc", "CpAsyncOccIfc",
        f"        Bit#(4) wb = 0; wb[3]=wgray[3]; wb[2]=wb[3]^wgray[2]; wb[1]=wb[2]^wgray[1]; wb[0]=wb[1]^wgray[0];\n"
        f"        Bit#(4) rb = 0; rb[3]=rgray[3]; rb[2]=rb[3]^rgray[2]; rb[1]=rb[2]^rgray[1]; rb[0]=rb[1]^rgray[0];\n"
        f"        Bit#(4) occ = wb - rb;\n"
        f"        return {{pack(occ == 4'd8), pack(occ >= 4'd{af_th}), pack(occ == 4'd0), occ}};",
        [("4'b0000", "4'b0000"), ("4'b0011", "4'b0000"), ("4'b0101", "4'b0000"), ("4'b1100", "4'b0000")],
        f"### Competitive Specification\nGiven 4-bit Gray-coded write pointer `wgray` and read pointer `rgray` for an 8-deep Async FIFO: convert both from Gray to binary (`wb`, `rb`), compute `occ = wb - rb`, and return 7-bit `{{full(occ==8), almost_full(occ>={af_th}), empty(occ==0), occ[3:0]}}`.",
        "Async FIFOs synchronize Gray pointers across clock domains and decode them to binary to compute exact occupancy and watermarks.",
        f"(wgray, rgray) ---> [ Gray->Bin: occ = wb - rb ] ---> {{full, occ>={af_th}, empty, occ}}",
        ["Convert `wgray` to `wb` and `rgray` to `rb` via prefix XOR.", f"Compute `occ = wb - rb` and return `{{pack(occ == 4'd8), pack(occ >= 4'd{af_th}), pack(occ == 4'd0), occ}};`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 8: Clock Domain Crossing")


def _gen_cdc_mcp_req_ack_fsm(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_cdcmcp_{seed}",
        f"CP #{seed % 1000}: 4-Phase Multi-Cycle Path (MCP) Req/Ack Source FSM",
        "cp_arena", difficulty, ["CP-CDC", "4-Phase Handshake", "Track 8"],
        "Bit#(2)", "cmd", "Bit#(2)", "step", "read", "mkCpMcpFsm", "CpMcpFsmIfc",
        "    Reg#(Bit#(1)) req_r <- mkReg(0);\n    Reg#(Bit#(1)) busy <- mkReg(0);",
        "        Bool send = unpack(cmd[1]);\n        Bool ack  = unpack(cmd[0]);\n        if (busy == 0) begin\n            if (send && !ack) begin req_r <= 1; busy <= 1; end\n        end else begin\n            if (req_r == 1 && ack) req_r <= 0;\n            else if (req_r == 0 && !ack) busy <= 0;\n        end",
        "        return {busy, req_r};",
        ["2'b10", "2'b00", "2'b01", "2'b01", "2'b00", "2'b10"],
        "### Competitive Specification\nImplement a 4-phase Req/Ack source controller given `cmd = {send, ack}`:\n- When `busy == 0 && send && !ack`: assert `req_r <= 1; busy <= 1;`.\n- When `busy == 1 && req_r == 1 && ack`: deassert `req_r <= 0;`.\n- When `busy == 1 && req_r == 0 && !ack`: complete handshake `busy <= 0;`.\nReturn `{busy, req_r}`.",
        "4-phase req/ack handshakes safely transfer multi-bit buses across asynchronous clock domains.",
        "cmd={send,ack} ---> [ Idle -> Req=1 -> Wait Ack=1 -> Req=0 -> Wait Ack=0 ] ---> {busy, req_r}",
        ["Follow the 3 transitions: start (`!busy && send && !ack`), drop req (`busy && req_r && ack`), clear busy (`busy && !req_r && !ack`)."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 8: Clock Domain Crossing")


# =============================================================================
# TRACK 9 FAMILIES (Verification, SVA Monitors & Coverage) - #74 to #77
# =============================================================================

def _gen_verif_bounded_liveness(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    max_wait = rng.choice([2, 3])
    p = make_seq_step_problem(
        _make_problem, f"cp_vlive_{seed}",
        f"CP #{seed % 1000}: [Verification] Bounded Liveness Monitor (MaxWait={max_wait} Cycles)",
        "cp_arena", difficulty, ["CP-Verification", "Bounded Liveness SVA", "Track 9"],
        "Bit#(2)", "sig", "Bit#(4)", "step", "read", "mkCpVerifLiveness", "CpVerifLivenessIfc",
        "    Reg#(Bit#(2)) wcnt <- mkReg(0);\n    Reg#(Bit#(1)) err <- mkReg(0);",
        f"        if (sig == 2'b01) begin\n            if (wcnt == 2'd{max_wait}) err <= 1;\n            else wcnt <= wcnt + 1;\n        end else wcnt <= 0;",
        "        return {err, 1'b0, wcnt};",
        ["2'b01", "2'b01", "2'b11", "2'b01", "2'b01", "2'b01", "2'b01"],
        f"### Competitive Verification Specification\nMonitor `sig = {{gnt, req}}`. Whenever `req == 1 && gnt == 0` (`sig == 2'b01`), if `wcnt == 2'd{max_wait}`, latch sticky violation `err <= 1`, else increment `wcnt <= wcnt + 1`. When `gnt == 1 || req == 0`, reset `wcnt <= 0`. Return `{{err, 1'b0, wcnt}}`.",
        "Synthesizable SVA bounded-liveness monitors (`req |-> ##[0:N] gnt`) catch arbiter deadlocks in emulation.",
        f"sig={{gnt,req}} ---> [ req && !gnt > {max_wait} cyc -> err=1 ] ---> {{err, 0, wcnt}}",
        [f"When `sig == 2'b01`, check `wcnt == 2'd{max_wait}` to set `err <= 1`, else increment `wcnt`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 9: Verification & Monitors")


def _gen_verif_credit_conservation(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    init_c = rng.choice([3, 4])
    p = make_seq_step_problem(
        _make_problem, f"cp_vcred_{seed}",
        f"CP #{seed % 1000}: [Verification] Credit + In-Flight Conservation Monitor (Total={init_c})",
        "cp_arena", difficulty, ["CP-Verification", "Credit Conservation", "Track 9"],
        "Bit#(2)", "ev", "Bit#(7)", "step", "read", "mkCpVerifCredit", "CpVerifCreditIfc",
        f"    Reg#(Bit#(3)) cred <- mkReg(3'd{init_c});\n    Reg#(Bit#(3)) flt <- mkReg(0);\n    Reg#(Bit#(1)) err <- mkReg(0);",
        "        Bool ret = unpack(ev[1]);\n        Bool snd = unpack(ev[0]);\n        if ((snd && !ret && cred == 0) || (ret && !snd && flt == 0)) err <= 1;\n        else begin\n            cred <= cred + (ret ? 3'd1 : 3'd0) - (snd ? 3'd1 : 3'd0);\n            flt  <= flt  + (snd ? 3'd1 : 3'd0) - (ret ? 3'd1 : 3'd0);\n        end",
        "        return {err, cred, flt};",
        ["2'b01", "2'b01", "2'b11", "2'b10", "2'b10", "2'b10"],
        f"### Competitive Verification Specification\nVerify credit conservation (`cred + flt == {init_c}`) given `ev = {{credit_ret, pkt_send}}`. If `pkt_send` occurs when `cred == 0 && !credit_ret` or `credit_ret` occurs when `flt == 0 && !pkt_send`, latch `err <= 1`. Otherwise update `cred` and `flt`. Return `{{err, cred, flt}}`.",
        "Conservation monitors verify that no credits or packets are leaked across link resets and flow-control stalls.",
        f"ev={{ret,snd}} ---> [ cred + flt == {init_c} invariant ] ---> {{err, cred, flt}}",
        ["Flag `err <= 1` on underflow (`snd && !ret && cred == 0` or `ret && !snd && flt == 0`)."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 9: Verification & Monitors")


def _gen_verif_gray_transition(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_vgray_{seed}",
        f"CP #{seed % 1000}: [Verification] Gray Pointer Single-Bit Step Assertion Monitor",
        "cp_arena", difficulty, ["CP-Verification", "CDC Gray Monitor", "Track 9"],
        "Bit#(4)", "g_in", "Bit#(5)", "step", "read", "mkCpVerifGray", "CpVerifGrayIfc",
        "    Reg#(Bit#(4)) prev_g <- mkReg(0);\n    Reg#(Bit#(1)) err <- mkReg(0);",
        "        Bit#(4) d = g_in ^ prev_g;\n        if ((d & (d - 4'd1)) != 0) err <= 1;\n        prev_g <= g_in;",
        "        return {err, prev_g};",
        ["4'b0001", "4'b0011", "4'b0010", "4'b0110", "4'b0000"],
        "### Competitive Verification Specification\nVerify that 4-bit Gray pointer `g_in` changes by at most 1 bit from `prev_g` each cycle: let `d = g_in ^ prev_g`; if `(d & (d - 4'd1)) != 0`, latch sticky `err <= 1`. Update `prev_g <= g_in` and return `{err, prev_g}`.",
        "CDC assertion monitors ensure Gray-coded pointers never glitch multiple bits across a clock boundary.",
        "g_in ---> [ d = g_in ^ prev_g; (d & (d-1)) != 0 -> err=1 ] ---> {err, prev_g}",
        ["Compute `Bit#(4) d = g_in ^ prev_g;`.", "If `(d & (d - 4'd1)) != 0`, set `err <= 1;`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 9: Verification & Monitors")


def _gen_verif_coverage_bin_tracker(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_vcov_{seed}",
        f"CP #{seed % 1000}: [Verification] 8-Bin Functional Coverage Bitmap & 100% Goal Monitor",
        "cp_arena", difficulty, ["CP-Verification", "Functional Coverage", "Track 9"],
        "Bit#(3)", "sample_bin", "Bit#(9)", "step", "read", "mkCpVerifCov", "CpVerifCovIfc",
        "    Reg#(Bit#(8)) cov <- mkReg(0);",
        "        cov <= cov | (8'd1 << sample_bin);",
        "        return {&cov, cov};",
        ["3'd0", "3'd1", "3'd2", "3'd3", "3'd4", "3'd5", "3'd6", "3'd7"],
        "### Competitive Verification Specification\nAccumulate visited coverage bins in `cov` (`Reg#(Bit#(8))`, init 0) via `cov <= cov | (8'd1 << sample_bin)`. Return 9-bit `{&cov, cov}` where MSB `&cov` asserts `1` when all 8 bins have been hit!",
        "Hardware coverage trackers measure corner-case stimulus completeness during FPGA-accelerated verification.",
        "sample_bin[2:0] ---> [ cov |= (1 << sample_bin) ] ---> {&cov, cov[7:0]}",
        ["Update `cov <= cov | (8'd1 << sample_bin);`.", "Return `{&cov, cov}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 9: Verification & Monitors")


# =============================================================================
# TRACK 10 FAMILIES (Protocols, NoC, Predictors & Superscalar) - #78 to #80
# =============================================================================

def _gen_noc_3d_xyz_router(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb2_problem(
        _make_problem, f"cp_noc3d_{seed}",
        f"CP #{seed % 1000}: 3D Mesh NoC Dimension-Order XYZ Routing Engine",
        "cp_arena", difficulty, ["CP-Architecture", "3D NoC Router", "Track 10"],
        "Bit#(6)", "cur", "Bit#(6)", "dst", "Bit#(3)", "route3D", "mkCpNoc3D", "CpNoc3DIfc",
        "        Bit#(2) cx = cur[1:0]; Bit#(2) cy = cur[3:2]; Bit#(2) cz = cur[5:4];\n"
        "        Bit#(2) dx = dst[1:0]; Bit#(2) dy = dst[3:2]; Bit#(2) dz = dst[5:4];\n"
        "        if (dx > cx) return 3'd1;\n"
        "        else if (dx < cx) return 3'd2;\n"
        "        else if (dy > cy) return 3'd3;\n"
        "        else if (dy < cy) return 3'd4;\n"
        "        else if (dz > cz) return 3'd5;\n"
        "        else if (dz < cz) return 3'd6;\n"
        "        else return 3'd0;",
        [("6'b01_01_01", "6'b10_10_10"), ("6'b01_01_10", "6'b10_10_10"), ("6'b01_10_10", "6'b10_10_10"), ("6'b10_10_10", "6'b10_10_10")],
        "### Competitive Specification\nRoute a flit from `cur = {cz[1:0], cy[1:0], cx[1:0]}` to `dst = {dz[1:0], dy[1:0], dx[1:0]}` using deadlock-free X-then-Y-then-Z routing: `1`=+X, `2`=-X, `3`=+Y, `4`=-Y, `5`=+Z, `6`=-Z, `0`=Local.",
        "Dimension-Ordered Routing (DOR) guarantees deadlock freedom in 2D/3D multi-chiplet torus and mesh fabrics.",
        "(cur, dst) ---> [ X != -> 1/2 | Y != -> 3/4 | Z != -> 5/6 | Local -> 0 ] ---> dir[2:0]",
        ["Compare `dx` vs `cx` first (`1`/`2`), then `dy` vs `cy` (`3`/`4`), then `dz` vs `cz` (`5`/`6`), else `0`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 10: Architecture & Protocols")


def _gen_gshare_branch_predictor(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_seq_step_problem(
        _make_problem, f"cp_gshare_{seed}",
        f"CP #{seed % 1000}: Gshare Global-History XOR Branch Predictor",
        "cp_arena", difficulty, ["CP-Architecture", "Gshare Predictor", "Track 10"],
        "Bit#(4)", "cmd", "Bit#(4)", "step", "read", "mkCpGshare", "CpGshareIfc",
        "    Vector#(4, Reg#(Bit#(2))) pht <- replicateM(mkReg(2'b01));\n    Reg#(Bit#(2)) ghr <- mkReg(0);",
        "        Bit#(2) pc_low = cmd[1:0];\n        Bit#(2) idx = pc_low ^ ghr;\n        if (cmd[3] == 1'b1) begin\n            Bit#(2) c = pht[idx];\n            if (cmd[2] == 1'b1) pht[idx] <= (c == 2'd3) ? 2'd3 : (c + 1);\n            else pht[idx] <= (c == 2'd0) ? 2'd0 : (c - 1);\n            ghr <= {ghr[0], cmd[2]};\n        end",
        "        return {ghr, pht[ghr]};",
        ["4'b11_01", "4'b11_01", "4'b10_10", "4'b11_11", "4'b00_00"],
        "### Competitive Specification\nMaintain a 4-entry 2-bit Pattern History Table `pht` (init `2'b01`) and 2-bit Global History Register `ghr` (init 0). Given `cmd = {upd_en, taken, pc_low[1:0]}`: compute XOR index `idx = pc_low ^ ghr`. When `upd_en == 1`, update `pht[idx]` with 2-bit saturation (`+1` if `taken==1` else `-1`) and shift `ghr <= {ghr[0], taken}`. Return `{ghr, pht[ghr]}`.",
        "Gshare XORs the branch PC with global branch history to distinguish correlated branch paths.",
        "cmd={we,taken,pc[1:0]} ---> [ idx = pc ^ ghr; update pht[idx]; ghr <= {ghr[0],taken} ] ---> {ghr, pht[ghr]}",
        ["Compute `Bit#(2) idx = cmd[1:0] ^ ghr;`.", "When `cmd[3] == 1`, update `pht[idx]` saturating in `0..3` and shift `ghr <= {ghr[0], cmd[2]}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 10: Architecture & Protocols")


def _gen_superscalar_dual_issue(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    p = make_comb2_problem(
        _make_problem, f"cp_dualiss_{seed}",
        f"CP #{seed % 1000}: 2-Way Superscalar Dual-Issue Hazard & Port Pairing Unit",
        "cp_arena", difficulty, ["CP-Architecture", "Superscalar Issue", "Track 10"],
        "Bit#(5)", "inst0", "Bit#(5)", "inst1", "Bit#(3)", "checkDualIssue", "mkCpDualIssue", "CpDualIssueIfc",
        "        Bit#(1) m0 = inst0[4]; Bit#(2) rd0 = inst0[3:2];\n"
        "        Bit#(1) m1 = inst1[4]; Bit#(2) rs1 = inst1[1:0];\n"
        "        Bool raw = (rd0 != 2'd0) && (rd0 == rs1);\n"
        "        Bool port_clash = (m0 == 1'b1) && (m1 == 1'b1);\n"
        "        Bool ok = !raw && !port_clash;\n"
        "        return {pack(ok), pack(raw), pack(port_clash)};",
        [("5'b0_01_00", "5'b0_10_01"), ("5'b0_01_00", "5'b0_10_11"), ("5'b1_01_00", "5'b1_10_11"), ("5'b1_00_00", "5'b0_10_00")],
        "### Competitive Specification\nGiven two instructions `inst0 = {is_mem0, rd0[1:0], rs0[1:0]}` and `inst1 = {is_mem1, rd1[1:0], rs1[1:0]}`: check inter-instruction RAW hazard `raw = (rd0 != 0 && rd0 == rs1)` and single-memory-port structural hazard `port_clash = (is_mem0 == 1 && is_mem1 == 1)`. Both dual-issue (`ok = !raw && !port_clash`). Return `{pack(ok), pack(raw), pack(port_clash)}`.",
        "Superscalar dispatch stages check data dependencies and structural port limits before pairing instructions.",
        "(inst0, inst1) ---> [ raw=(rd0!=0 && rd0==rs1), clash=(m0&&m1) ] ---> {ok, raw, clash}",
        ["Check `raw = (rd0 != 2'd0) && (rd0 == rs1);` and `port_clash = (m0 == 1'b1) && (m1 == 1'b1);`.", "Return `{pack(!raw && !port_clash), pack(raw), pack(port_clash)}`."],
    )
    return _finalize_cp(p, seed, difficulty, "Track 10: Architecture & Protocols")


# =============================================================================
# EXPORT BANK DICTIONARY, CATEGORIES & TRACK-TO-CP REINFORCEMENT MAP
# =============================================================================

BANK_CP_GENERATORS: Dict[str, Callable[..., Dict[str, Any]]] = {
    # Track 1 (+5)
    "bit_reversal_permute": _gen_bit_reversal_permute,
    "bcd_excess3_codec": _gen_bcd_excess3_codec,
    "carry_save_compressor": _gen_carry_save_compressor,
    "majority_voter_tmr": _gen_majority_voter_tmr,
    "popcount_threshold": _gen_popcount_threshold,
    # Track 2 (+5)
    "simd_vector_alu": _gen_simd_vector_alu,
    "hamming_secded_codec": _gen_hamming_secded_codec,
    "crossbar_switch_4x4": _gen_crossbar_switch_4x4,
    "prefix_scan_network": _gen_prefix_scan_network,
    "ipv4_header_validator": _gen_ipv4_header_validator,
    # Track 3 (+5)
    "crc8_serial_parallel": _gen_crc8_serial_parallel,
    "clk_divider_fractional": _gen_clk_divider_fractional,
    "ping_pong_wave_gen": _gen_ping_pong_wave_gen,
    "exp_backoff_controller": _gen_exp_backoff_controller,
    "piso_sipo_transceiver": _gen_piso_sipo_transceiver,
    # Track 4 (+5)
    "ehr_bypass_pipeline": _gen_ehr_bypass_pipeline,
    "token_bucket_shaper": _gen_token_bucket_shaper,
    "wfq_weighted_scheduler": _gen_wfq_weighted_scheduler,
    "gearbox_16to8_unpacker": _gen_gearbox_16to8_unpacker,
    "coalescing_irq_ctrl": _gen_coalescing_irq_ctrl,
    # Track 5 (+5)
    "uart_rx_oversampler": _gen_uart_rx_oversampler,
    "spi_cpol_cpha_master": _gen_spi_cpol_cpha_master,
    "i2c_addr_matcher_fsm": _gen_i2c_addr_matcher_fsm,
    "hdlc_zero_stuffer_fsm": _gen_hdlc_zero_stuffer_fsm,
    "axi_burst_chopper_fsm": _gen_axi_burst_chopper_fsm,
    # Track 6 (+5)
    "q4_4_fixed_point_mac": _gen_q4_4_fixed_point_mac,
    "cordic_stage_rotator": _gen_cordic_stage_rotator,
    "fir_3tap_symmetric": _gen_fir_3tap_symmetric,
    "ewma_iir_filter": _gen_ewma_iir_filter,
    "sorting_network_4elem": _gen_sorting_network_4elem,
    # Track 7 (+6)
    "bram_write_first_bypass": _gen_bram_write_first_bypass,
    "cam_4entry_lookup": _gen_cam_4entry_lookup,
    "tcam_wildcard_matcher": _gen_tcam_wildcard_matcher,
    "lifo_hardware_stack": _gen_lifo_hardware_stack,
    "bitmap_freelist_alloc": _gen_bitmap_freelist_alloc,
    "bloom_filter_2hash": _gen_bloom_filter_2hash,
    # Track 8 (+5)
    "cdc_syncbit_chain": _gen_cdc_syncbit_chain,
    "cdc_toggle_pulse_sync": _gen_cdc_toggle_pulse_sync,
    "cdc_reset_stretcher": _gen_cdc_reset_stretcher,
    "cdc_async_fifo_gray_occ": _gen_cdc_async_fifo_gray_occ,
    "cdc_mcp_req_ack_fsm": _gen_cdc_mcp_req_ack_fsm,
    # Track 9 (+4)
    "verif_bounded_liveness": _gen_verif_bounded_liveness,
    "verif_credit_conservation": _gen_verif_credit_conservation,
    "verif_gray_transition": _gen_verif_gray_transition,
    "verif_coverage_bin_tracker": _gen_verif_coverage_bin_tracker,
    # Track 10 (+3)
    "noc_3d_xyz_router": _gen_noc_3d_xyz_router,
    "gshare_branch_predictor": _gen_gshare_branch_predictor,
    "superscalar_dual_issue": _gen_superscalar_dual_issue,
}


BANK_CP_CATEGORIES: List[Dict[str, str]] = [
    {"id": "track1_combinational", "name": "🎯 Track 1 Reinforce: Combinational Logic, Codecs & Adders"},
    {"id": "track2_types", "name": "🎯 Track 2 Reinforce: Strong Types, SIMD Vectors, ECC & Crossbars"},
    {"id": "track3_sequential", "name": "🎯 Track 3 Reinforce: Sequential Counters, LFSR, CRC & Timers"},
    {"id": "track4_concurrency", "name": "🎯 Track 4 Reinforce: Concurrency, Ehr, FIFOs, Gearboxes & QoS"},
    {"id": "track5_fsms", "name": "🎯 Track 5 Reinforce: FSMs, UART, SPI, I2C, HDLC & AXI Bursts"},
    {"id": "track6_dsp_arithmetic", "name": "🎯 Track 6 Reinforce: Arithmetic, Fixed-Point, CORDIC, FIR/IIR & Sorting"},
    {"id": "track7_memory", "name": "🎯 Track 7 Reinforce: Memory Subsystems, BRAM, CAM, TCAM, LIFO & Bloom"},
    {"id": "track7_cdc", "name": "🎯 Track 8 Reinforce: Clock Domain Crossing, Gray Pointers & Handshakes"},
    {"id": "track9_verification", "name": "🎯 Track 9 Reinforce: Verification Monitors, SVA, Scoreboards & Bug Hunts"},
    {"id": "track6_architecture", "name": "🎯 Track 10 Reinforce: Protocols, NoC, Caches, Predictors & Superscalar"},
    {"id": "bit_reversal_permute", "name": "33. Bit-Reversal & Nibble Permutation Network"},
    {"id": "bcd_excess3_codec", "name": "34. BCD Validity & Excess-K Decimal Encoder"},
    {"id": "carry_save_compressor", "name": "35. 3:2 Carry-Save Adder (CSA) Compressor"},
    {"id": "majority_voter_tmr", "name": "36. Triple-Modular Redundancy (TMR) Voter"},
    {"id": "popcount_threshold", "name": "37. Hamming Weight & Threshold Detector"},
    {"id": "simd_vector_alu", "name": "38. 4-Lane 4-Bit SIMD Vector Unit"},
    {"id": "hamming_secded_codec", "name": "39. Hamming (7,4) SEC-DED ECC Encoder"},
    {"id": "crossbar_switch_4x4", "name": "40. 4x4 Non-Blocking Nibble Crossbar Switch"},
    {"id": "prefix_scan_network", "name": "41. 4-Lane Inclusive Prefix Scan Network"},
    {"id": "ipv4_header_validator", "name": "42. IPv4 Packet Header Validator & TTL Engine"},
    {"id": "crc8_serial_parallel", "name": "43. Programmable Polynomial CRC-8 Engine"},
    {"id": "clk_divider_fractional", "name": "44. Bresenham Fractional Clock-Enable Divider"},
    {"id": "ping_pong_wave_gen", "name": "45. Triangle-Wave Ping-Pong Counter"},
    {"id": "exp_backoff_controller", "name": "46. Collision Exponential Backoff Window Generator"},
    {"id": "piso_sipo_transceiver", "name": "47. 4-Bit PISO Serializer Shift Register"},
    {"id": "ehr_bypass_pipeline", "name": "48. Ehr#(2, t) Intra-Cycle Bypass Stage"},
    {"id": "token_bucket_shaper", "name": "49. Token-Bucket QoS Traffic Policer"},
    {"id": "wfq_weighted_scheduler", "name": "50. 2-Queue Weighted Fair Scheduler (WFQ)"},
    {"id": "gearbox_16to8_unpacker", "name": "51. 16-to-8 Unpacking Serializer Gearbox"},
    {"id": "coalescing_irq_ctrl", "name": "52. Interrupt Coalescing & Mask Controller"},
    {"id": "uart_rx_oversampler", "name": "53. UART Start-Bit Mid-Eye Oversampler FSM"},
    {"id": "spi_cpol_cpha_master", "name": "54. SPI Full-Duplex Master Shift-Exchange FSM"},
    {"id": "i2c_addr_matcher_fsm", "name": "55. I2C 7-Bit Target & Broadcast Matcher"},
    {"id": "hdlc_zero_stuffer_fsm", "name": "56. HDLC / USB Consecutive-One Bit-Stuffer FSM"},
    {"id": "axi_burst_chopper_fsm", "name": "57. AXI 4KB Boundary Burst Chopper FSM"},
    {"id": "q4_4_fixed_point_mac", "name": "58. Q4.4 Fixed-Point Multiplier with Rounding"},
    {"id": "cordic_stage_rotator", "name": "59. CORDIC Micro-Rotation Shift-Add Stage"},
    {"id": "fir_3tap_symmetric", "name": "60. 3-Tap Symmetric Linear-Phase FIR Filter"},
    {"id": "ewma_iir_filter", "name": "61. Exponentially Weighted Moving Average (EWMA) IIR"},
    {"id": "sorting_network_4elem", "name": "62. 4-Nibble Parallel Bitonic Sorting Network"},
    {"id": "bram_write_first_bypass", "name": "63. Dual-Port 4x8 Synchronous BRAM (Read/Write-First)"},
    {"id": "cam_4entry_lookup", "name": "64. 4-Entry Content-Addressable Memory (CAM)"},
    {"id": "tcam_wildcard_matcher", "name": "65. Ternary CAM (TCAM) Wildcard Rule Matcher"},
    {"id": "lifo_hardware_stack", "name": "66. 4-Deep Hardware LIFO Call/Return Stack"},
    {"id": "bitmap_freelist_alloc", "name": "67. 8-Slot Physical Register Free-List Allocator"},
    {"id": "bloom_filter_2hash", "name": "68. 8-Bit Dual-Hash Hardware Bloom Filter"},
    {"id": "cdc_syncbit_chain", "name": "69. 3-Stage CDC Synchronizer & Edge Extractor"},
    {"id": "cdc_toggle_pulse_sync", "name": "70. Toggle-Based Cross-Domain Pulse Synchronizer"},
    {"id": "cdc_reset_stretcher", "name": "71. N-Cycle Reset Stretcher Bridge"},
    {"id": "cdc_async_fifo_gray_occ", "name": "72. Gray-Pointer Async FIFO Occupancy & Watermarks"},
    {"id": "cdc_mcp_req_ack_fsm", "name": "73. 4-Phase Multi-Cycle Path (MCP) Req/Ack FSM"},
    {"id": "verif_bounded_liveness", "name": "74. Verification: Req-Grant Bounded Liveness Monitor"},
    {"id": "verif_credit_conservation", "name": "75. Verification: Credit + In-Flight Conservation Monitor"},
    {"id": "verif_gray_transition", "name": "76. Verification: Gray Pointer Single-Bit Step Monitor"},
    {"id": "verif_coverage_bin_tracker", "name": "77. Verification: 8-Bin Functional Coverage Tracker"},
    {"id": "noc_3d_xyz_router", "name": "78. 3D Mesh NoC Dimension-Order XYZ Router"},
    {"id": "gshare_branch_predictor", "name": "79. Gshare Global-History XOR Branch Predictor"},
    {"id": "superscalar_dual_issue", "name": "80. 2-Way Superscalar Dual-Issue Hazard Unit"},
]


TRACK_TO_CP_FAMILIES: Dict[str, List[str]] = {
    "track1_combinational": [
        "prio_encoder", "clz_ctz_detector", "onehot_therm_codec", "gray_codec",
        "crc_parity_gen", "barrel_rotator", "window_comparator",
        "bit_reversal_permute", "bcd_excess3_codec", "carry_save_compressor",
        "majority_voter_tmr", "popcount_threshold",
    ],
    "track2_types": [
        "prio_encoder", "onehot_therm_codec", "packet_firewall",
        "simd_vector_alu", "hamming_secded_codec", "crossbar_switch_4x4",
        "prefix_scan_network", "ipv4_header_validator",
    ],
    "track3_sequential": [
        "modulo_counter", "updown_sat_counter", "johnson_ring_counter",
        "lfsr_scrambler", "debounce_glitch_filter", "pwm_timer", "watchdog_timer",
        "crc8_serial_parallel", "clk_divider_fractional", "ping_pong_wave_gen",
        "exp_backoff_controller", "piso_sipo_transceiver",
    ],
    "track4_concurrency": [
        "regslice_transform", "skid_credit_fifo", "gearbox_serializer",
        "ehr_bypass_pipeline", "token_bucket_shaper", "wfq_weighted_scheduler",
        "gearbox_16to8_unpacker", "coalescing_irq_ctrl",
    ],
    "track5_fsms": [
        "pattern_fsm", "vending_mealy_fsm", "uart_rx_oversampler",
        "spi_cpol_cpha_master", "i2c_addr_matcher_fsm", "hdlc_zero_stuffer_fsm",
        "axi_burst_chopper_fsm",
    ],
    "track6_dsp_arithmetic": [
        "saturating_alu", "mac_engine", "carry_save_compressor",
        "q4_4_fixed_point_mac", "cordic_stage_rotator", "fir_3tap_symmetric",
        "ewma_iir_filter", "sorting_network_4elem",
    ],
    "track7_memory": [
        "axi_wstrb_merger", "bram_write_first_bypass", "cam_4entry_lookup",
        "tcam_wildcard_matcher", "lifo_hardware_stack", "bitmap_freelist_alloc",
        "bloom_filter_2hash",
    ],
    "track7_cdc": [
        "gray_codec", "cdc_syncbit_chain", "cdc_toggle_pulse_sync",
        "cdc_reset_stretcher", "cdc_async_fifo_gray_occ", "cdc_mcp_req_ack_fsm",
    ],
    "track9_verification": [
        "verif_arbiter_checker", "verif_axi_handshake", "verif_fifo_conservation",
        "verif_bounded_liveness", "verif_credit_conservation",
        "verif_gray_transition", "verif_coverage_bin_tracker",
    ],
    "track6_architecture": [
        "arbiter_perm", "round_robin_arbiter", "apb_slave_periph",
        "axi_wstrb_merger", "noc_xy_router", "branch_predictor_bht",
        "pipeline_forwarding", "noc_3d_xyz_router", "gshare_branch_predictor",
        "superscalar_dual_issue",
    ],
}
