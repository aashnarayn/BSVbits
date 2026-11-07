"""Spiral Revision & Multi-Topic Combination Labs across Tracks 1-10 (+24 problems, bringing Mode 1 to 339 problems)."""

from typing import Any, Callable, Dict, List, Tuple
from .curriculum_bank_helpers import (
    make_comb1_problem,
    make_comb2_problem,
    make_seq_step_problem,
)


def build_spiral_reinforcement_problems(make_fn: Callable[..., Dict[str, Any]]) -> List[Dict[str, Any]]:
    p: List[Dict[str, Any]] = []

    def _c1(pid: str, track_id: str, title: str, diff: str, _pts: int, tags: List[str], _prereq: List[str],
            desc: str, spec_txt: str, in_t: str, out_t: str, ref_body: str, stim: List[str], hints: List[str]) -> Dict[str, Any]:
        return make_comb1_problem(
            make_fn, pid, title, track_id, diff, tags,
            in_t, "x", out_t, "compute", "mkDut", "DutIfc",
            "        " + ref_body, stim,
            f"{desc}\n\n### Specification\n{spec_txt}",
            "Reinforces BSV combinational synthesis and bit-level manipulation.",
            "x ---> [mkDut.compute] ---> out",
            hints,
        )

    def _c2(pid: str, track_id: str, title: str, diff: str, _pts: int, tags: List[str], _prereq: List[str],
            desc: str, spec_txt: str, in1_t: str, in2_t: str, out_t: str, ref_body: str, stim: List[Tuple[str, str]], hints: List[str]) -> Dict[str, Any]:
        return make_comb2_problem(
            make_fn, pid, title, track_id, diff, tags,
            in1_t, "a", in2_t, "b", out_t, "compute", "mkDut", "DutIfc",
            "        " + ref_body, stim,
            f"{desc}\n\n### Specification\n{spec_txt}",
            "Reinforces multi-operand BSV datapath composition and strong typing.",
            "(a, b) ---> [mkDut.compute] ---> out",
            hints,
        )

    def _seq(pid: str, track_id: str, title: str, diff: str, _pts: int, tags: List[str], _prereq: List[str],
             desc: str, spec_txt: str, in_t: str, out_t: str, st_decl: str, step_body: str, read_body: str, stim: List[str], hints: List[str]) -> Dict[str, Any]:
        return make_seq_step_problem(
            make_fn, pid, title, track_id, diff, tags,
            in_t, "cmd", out_t, "step", "read", "mkDut", "DutIfc",
            st_decl, step_body, read_body, stim,
            f"{desc}\n\n### Specification\n{spec_txt}",
            "Reinforces atomic state updates and cross-topic sequential RTL design.",
            "cmd ---> [mkDut.step / read] ---> out",
            hints,
        )

    # Track 1 spiral reinforcement (+3)
    p.append(_c1(
        "07y_comb_bcd_valid_checker", "track1_combinational",
        "[Reinforce] 2-Digit Packed BCD Validity Checker", "Easy", 15,
        ["Combinational", "BCD", "Reinforcement"], [],
        "Check if an 8-bit packed BCD byte has both upper (`x[7:4] <= 9`) and lower (`x[3:0] <= 9`) nibbles valid.",
        "Return `1'b1` iff `x[7:4] <= 4'd9 && x[3:0] <= 4'd9`.",
        "Bit#(8)", "Bit#(1)",
        "return (x[7:4] <= 4'd9 && x[3:0] <= 4'd9) ? 1'b1 : 1'b0;",
        ["8'h00", "8'h49", "8'h99", "8'h9A", "8'hA0", "8'hFF"],
        ["Check both nibbles against `4'd9`."]
    ))
    p.append(_c2(
        "07z_comb_conditional_negate_sat8", "track1_combinational",
        "[Combo Lab] Conditional Safe Negate 8-Bit Signed", "Easy", 15,
        ["Combinational", "Signed", "Combo Lab"], [],
        "If `b[0] == 1` (negate enable), negate signed 8-bit `a`, saturating `-128 (8'h80)` to `+127 (8'h7F)`. Otherwise return `a`.",
        "If `b[0] == 1`: return `(a == 8'h80) ? 8'h7F : (~a + 8'd1)`; else return `a`.",
        "Bit#(8)", "Bit#(8)", "Bit#(8)",
        "return (b[0] == 1'b1) ? ((a == 8'h80) ? 8'h7F : (~a + 8'd1)) : a;",
        [("8'h05", "8'd1"), ("8'h80", "8'd1"), ("8'h80", "8'd0"), ("8'hFB", "8'd1")],
        ["Handle the `-128` corner case (`8'h80`) before negating."]
    ))
    p.append(_c1(
        "07za_comb_nibble_majority_mask", "track1_combinational",
        "[Reinforce] 4-Nibble Majority Bitmask (Count >= 2 per Nibble)", "Easy", 15,
        ["Combinational", "Bitwise", "Reinforcement"], [],
        "For each 4-bit nibble `i` in `16-bit x`, set output bit `i` to 1 if that nibble has at least two `1` bits.",
        "For `i` in `0..3`, count 1s in `x[4*i+3 : 4*i]` and set `out[i] = (cnt >= 2)`.",
        "Bit#(16)", "Bit#(4)",
        "Bit#(4) res = 0;\n        for (Integer i = 0; i < 4; i = i + 1) begin\n            Bit#(4) n = x[4*i+3 : 4*i];\n            Bit#(3) c = zeroExtend(n[0]) + zeroExtend(n[1]) + zeroExtend(n[2]) + zeroExtend(n[3]);\n            res[i] = (c >= 3'd2) ? 1'b1 : 1'b0;\n        end\n        return res;",
        ["16'h0000", "16'h137F", "16'h8421", "16'h3333", "16'hF061"],
        ["Sum the 4 bits of each nibble into a `Bit#(3)`."]
    ))

    # Track 2 spiral reinforcement (+3)
    p.append(_c1(
        "11z_types_vector_prefix_xor4", "track2_types",
        "[Reinforce] 4-Nibble Inclusive Prefix XOR Scan", "Easy", 15,
        ["Vectors", "Prefix Scan", "Reinforcement"], [],
        "Compute the inclusive prefix XOR of 4 nibbles in `x`: `p0=n0, p1=n0^n1, p2=n0^n1^n2, p3=n0^n1^n2^n3`.",
        "Return `{p3, p2, p1, p0}`.",
        "Bit#(16)", "Bit#(16)",
        "Bit#(4) p0 = x[3:0];\n        Bit#(4) p1 = p0 ^ x[7:4];\n        Bit#(4) p2 = p1 ^ x[11:8];\n        Bit#(4) p3 = p2 ^ x[15:12];\n        return {p3, p2, p1, p0};",
        ["16'h1111", "16'hF0F0", "16'h1234", "16'hABCD"],
        ["Chain XORs from nibble 0 up to nibble 3."]
    ))
    p.append(_c2(
        "11za_types_struct_vlan_tag_rewriter", "track2_types",
        "[Combo Lab] Ethernet VLAN Priority & VID Rewriter", "Medium", 20,
        ["Structs", "Networking", "Combo Lab"], [],
        "Given 16-bit TCI `{pcp[15:13], dei[12], vid[11:0]}` in `a` and command `b` (`b[15]=override_pcp, b[14:12]=new_pcp, b[11:0]=new_vid_if_nonzero`), rewrite the VLAN tag.",
        "Set `pcp = b[15] ? b[14:12] : a[15:13]`, preserve `dei = a[12]`, and set `vid = (b[11:0] != 0) ? b[11:0] : a[11:0]`.",
        "Bit#(16)", "Bit#(16)", "Bit#(16)",
        "Bit#(3) pcp = (b[15] == 1'b1) ? b[14:12] : a[15:13];\n        Bit#(1) dei = a[12];\n        Bit#(12) vid = (b[11:0] != 0) ? b[11:0] : a[11:0];\n        return {pcp, dei, vid};",
        [("16'h2064", "16'h8000"), ("16'h2064", "16'hD100"), ("16'h2064", "16'h000A")],
        ["Check `b[15]` for PCP override and `b[11:0] != 0` for VID override."]
    ))
    p.append(_c2(
        "11zb_types_vector_dot_bool_and_or", "track2_types",
        "[Revision] 8-Bit Boolean Matrix-Vector Inner Product (AND-OR)", "Easy", 15,
        ["Vectors", "Boolean Algebra", "Revision"], [],
        "Compute the boolean inner product of 8-bit vectors `a` and `b`: OR-reduction of `(a & b)`, plus popcount of `(a & b)` in `[4:1]`.",
        "Return `{popcount(a & b)[3:0], |(a & b)}` (5-bit result).",
        "Bit#(8)", "Bit#(8)", "Bit#(5)",
        "Bit#(8) m = a & b;\n        Bit#(4) c = 0;\n        for (Integer i = 0; i < 8; i = i + 1) c = c + zeroExtend(m[i]);\n        return {c, |m};",
        [("8'h00", "8'hFF"), ("8'hAA", "8'h55"), ("8'hF0", "8'h3C"), ("8'hFF", "8'hFF")],
        ["Compute `m = a & b`, count set bits, and pack `{count, |m}`."]
    ))

    # Track 3 spiral reinforcement (+2)
    p.append(_seq(
        "17w_seq_ping_pong_counter4", "track3_sequential",
        "[Reinforce] Triangle-Wave Ping-Pong Counter (0..7..0)", "Medium", 20,
        ["Sequential", "Counters", "Reinforcement"], [],
        "Design a counter that bounces between `0` and `7`: increments up to 7, reverses direction to decrement down to 0, then reverses again when `cmd[0]==1` (`cmd[1]==1` resets to `val=0, dir=0`).",
        "Maintain `val` (`Bit#(3)`, init 0) and `dir` (`Bit#(1)`, init 0=up). Read returns `{dir, val}`.",
        "Bit#(2)", "Bit#(4)",
        "    Reg#(Bit#(3)) val <- mkReg(0);\n    Reg#(Bit#(1)) dir <- mkReg(0);",
        "        if (cmd[1] == 1'b1) begin val <= 0; dir <= 0; end\n        else if (cmd[0] == 1'b1) begin\n            if (dir == 0) begin\n                if (val == 3'd7) begin val <= 3'd6; dir <= 1; end\n                else val <= val + 1;\n            end else begin\n                if (val == 3'd0) begin val <= 3'd1; dir <= 0; end\n                else val <= val - 1;\n            end\n        end",
        "        return {dir, val};",
        ["2'b01"] * 10 + ["2'b10", "2'b01"],
        ["Flip `dir` at the extreme endpoints `7` and `0`."]
    ))
    p.append(_seq(
        "17x_seq_exponential_backoff_timer", "track3_sequential",
        "[Combo Lab] Collision Exponential Backoff Window Generator", "Medium", 25,
        ["Sequential", "Networking", "Combo Lab"], [],
        "Track collision retry count `attempt` (0..7, init 0). On `cmd == 2'd1` (collision): saturate `attempt <= (attempt == 7) ? 7 : attempt + 1`. On `cmd == 2'd2` (success): `attempt <= 0`. Output `{attempt, (8'd1 << attempt) - 8'd1}` (11-bit `{attempt[2:0], mask[7:0]}`).",
        "Maintain `Reg#(Bit#(3)) attempt <- mkReg(0)`. Read returns `{attempt, (8'd1 << attempt) - 8'd1}`.",
        "Bit#(2)", "Bit#(11)",
        "    Reg#(Bit#(3)) attempt <- mkReg(0);",
        "        if (cmd == 2'd1) attempt <= (attempt == 3'd7) ? 3'd7 : (attempt + 1);\n        else if (cmd == 2'd2) attempt <= 0;",
        "        return {attempt, (8'd1 << attempt) - 8'd1};",
        ["2'd1", "2'd1", "2'd1", "2'd1", "2'd2", "2'd1"],
        ["Window mask is `(8'd1 << attempt) - 8'd1`."]
    ))

    # Track 4 spiral reinforcement (+2)
    p.append(_seq(
        "21t_conc_dual_channel_weighted_arbiter", "track4_concurrency",
        "[Combo Lab] 2-Channel Weighted Fair Queuing (3:1 Weight) Scheduler", "Medium", 25,
        ["Concurrency", "QoS", "Combo Lab"], [],
        "Schedule between high-weight channel 0 (weight 3) and channel 1 (weight 1). `cmd = {req1, req0}`. When both request, grant ch0 up to 3 consecutive times before granting ch1 once.",
        "Maintain `Reg#(Bit#(2)) quota <- mkReg(3)` and `Reg#(Bit#(2)) last_gnt <- mkReg(0)`. Read returns `{quota, last_gnt}`.",
        "Bit#(2)", "Bit#(4)",
        "    Reg#(Bit#(2)) quota <- mkReg(3);\n    Reg#(Bit#(2)) last_gnt <- mkReg(0);",
        "        if (cmd == 2'b11) begin\n            if (quota > 0) begin last_gnt <= 2'b01; quota <= quota - 1; end\n            else begin last_gnt <= 2'b10; quota <= 3; end\n        end else if (cmd[0] == 1'b1) last_gnt <= 2'b01;\n        else if (cmd[1] == 1'b1) last_gnt <= 2'b10;\n        else last_gnt <= 2'b00;",
        "        return {quota, last_gnt};",
        ["2'b11", "2'b11", "2'b11", "2'b11", "2'b11", "2'b10", "2'b01", "2'b00"],
        ["When `cmd == 2'b11` and `quota == 0`, grant channel 1 (`2'b10`) and reload `quota <= 3`."]
    ))
    p.append(_seq(
        "21u_conc_skid_fifo_backpressure_counter", "track4_concurrency",
        "[Reinforce] Elastic Skid Buffer with Stall Event Counter", "Medium", 25,
        ["Concurrency", "Skid Buffer", "Reinforcement"], [],
        "Model a 1-entry buffer with a 4-bit stall counter (`stalls`) that increments whenever `push` (`cmd[4]`) is attempted while full (`valid==1`) and `pop` (`cmd[5]`) is 0.",
        "`cmd = {pop, push, din[3:0]}`. Read returns `{stalls, valid, buf_r}`.",
        "Bit#(6)", "Bit#(9)",
        "    Reg#(Bit#(1)) valid <- mkReg(0);\n    Reg#(Bit#(4)) buf_r <- mkReg(0);\n    Reg#(Bit#(4)) stalls <- mkReg(0);",
        "        Bool pop = unpack(cmd[5]);\n        Bool push = unpack(cmd[4]);\n        Bit#(4) din = cmd[3:0];\n        if (push && valid == 1'b1 && !pop) stalls <= stalls + 1;\n        else if (push && (!(valid == 1'b1) || pop)) begin valid <= 1'b1; buf_r <= din; end\n        else if (pop && !push) valid <= 1'b0;",
        "        return {stalls, valid, buf_r};",
        ["6'b01_1010", "6'b01_1100", "6'b11_0011", "6'b10_0000"],
        ["Count a stall when `push && valid == 1 && !pop`."]
    ))

    # Track 5 spiral reinforcement (+2)
    p.append(_seq(
        "25za_fsm_watchdog_windowed_fsm", "track5_fsms",
        "[Combo Lab] Windowed Watchdog Timer FSM (Early / Valid / Late Kick)", "Hard", 25,
        ["FSM", "Safety-Critical", "Combo Lab"], [],
        "A safety windowed watchdog counts `tick` (`0..7`). Kicking (`cmd[0]==1`) when `tick < 2` (too early) or `tick == 5` (timeout) triggers `fault <= 1`. Kicking when `2 <= tick <= 5` resets `tick <= 0` safely (`cmd[1]==1` clears fault & tick).",
        "Maintain `Reg#(Bit#(3)) tick <- mkReg(0)` and `Reg#(Bit#(1)) fault <- mkReg(0)`. Read returns `{fault, tick}`.",
        "Bit#(2)", "Bit#(4)",
        "    Reg#(Bit#(3)) tick <- mkReg(0);\n    Reg#(Bit#(1)) fault <- mkReg(0);",
        "        if (cmd[1] == 1'b1) begin tick <= 0; fault <= 0; end\n        else if (fault == 0) begin\n            if (cmd[0] == 1'b1) begin\n                if (tick < 3'd2) fault <= 1;\n                else tick <= 0;\n            end else begin\n                if (tick == 3'd5) fault <= 1;\n                else tick <= tick + 1;\n            end\n        end",
        "        return {fault, tick};",
        ["2'b00", "2'b00", "2'b01", "2'b01", "2'b10", "2'b00", "2'b00", "2'b00", "2'b00", "2'b00", "2'b00"],
        ["Early kick (`tick < 2`) or late expiry (`tick == 5` with no kick) latches `fault <= 1`."]
    ))
    p.append(_seq(
        "25zb_fsm_axi_burst_chopper_fsm", "track5_fsms",
        "[Combo Lab] AXI 4KB Boundary Burst Chopper FSM", "Hard", 25,
        ["FSM", "AXI4", "Combo Lab"], [],
        "Given `cmd = {start, len[3:0]}`: chop a transfer into sub-bursts of max length 4 beats. Each cycle while `rem > 0`, emit `sub_len = (rem > 4) ? 4 : rem` and decrement `rem <= rem - sub_len`.",
        "Maintain `Reg#(Bit#(4)) rem <- mkReg(0)` and `Reg#(Bit#(3)) sub_len <- mkReg(0)`. Read returns `{rem, sub_len}`.",
        "Bit#(5)", "Bit#(7)",
        "    Reg#(Bit#(4)) rem <- mkReg(0);\n    Reg#(Bit#(3)) sub_len <- mkReg(0);",
        "        if (cmd[4] == 1'b1) begin rem <= cmd[3:0]; sub_len <= 0; end\n        else if (rem > 0) begin\n            Bit#(4) b = (rem > 4'd4) ? 4'd4 : rem;\n            sub_len <= truncate(b);\n            rem <= rem - b;\n        end else sub_len <= 0;",
        "        return {rem, sub_len};",
        ["5'b1_1011", "5'b0_0000", "5'b0_0000", "5'b0_0000", "5'b0_0000"],
        ["Take `min(rem, 4)` each cycle until `rem == 0`."]
    ))

    # Track 6 DSP & Arithmetic spiral reinforcement (+3)
    p.append(_c2(
        "45zd_dsp_q4_4_linear_interp", "track6_dsp_arithmetic",
        "[Combo Lab] 1D Linear Interpolation (LERP) in 4-Bit Fraction", "Medium", 25,
        ["DSP", "Interpolation", "Combo Lab"], [],
        "Compute linear interpolation between 8-bit unsigned endpoints `a` and `b` at fixed weight `t = 1/4`: `out = a + ((b - a) >> 2)` using signed difference.",
        "Zero-extend `a` and `b` to `Int#(10)`, compute `Int#(10) res = sa + ((sb - sa) >> 2)`, and pack the lower 8 bits.",
        "Bit#(8)", "Bit#(8)", "Bit#(8)",
        "Int#(10) sa = unpack(zeroExtend(a));\n        Int#(10) sb = unpack(zeroExtend(b));\n        Int#(10) r = sa + ((sb - sa) >> 2);\n        return truncate(pack(r));",
        [("8'd0", "8'd100"), ("8'd100", "8'd200"), ("8'd200", "8'd100"), ("8'd40", "8'd40")],
        ["Use signed 10-bit arithmetic so `b < a` interpolates downward properly."]
    ))
    p.append(_c1(
        "45ze_dsp_2d_box_filter_2x2", "track6_dsp_arithmetic",
        "[Reinforce] 2x2 Image Pixel Box Filter Average (4x4-bit Nibbles)", "Easy", 15,
        ["DSP", "Image Processing", "Reinforcement"], [],
        "Given four 4-bit pixel intensities packed in `x` (`p0..p3`), compute their rounded average `(p0 + p1 + p2 + p3 + 2) >> 2`.",
        "Sum all 4 nibbles in `Bit#(6)`, add `6'd2` for rounding, and return `sum[5:2]`.",
        "Bit#(16)", "Bit#(4)",
        "Bit#(6) s = zeroExtend(x[3:0]) + zeroExtend(x[7:4]) + zeroExtend(x[11:8]) + zeroExtend(x[15:12]) + 6'd2;\n        return s[5:2];",
        ["16'h0000", "16'h2468", "16'hFFFF", "16'h1212"],
        ["Adding `2` before `>> 2` rounds to the nearest integer."]
    ))
    p.append(_seq(
        "45zf_dsp_leaky_integrator_iir", "track6_dsp_arithmetic",
        "[Combo Lab] 1st-Order Leaky Integrator IIR Filter (y <= y - (y>>2) + x)", "Medium", 25,
        ["DSP", "IIR Filter", "Combo Lab"], [],
        "Implement a leaky integrator `y <= y - (y >> 2) + zeroExtend(x)` where `x = cmd[5:0]` and `cmd[6] == 1` clears `y <= 0`.",
        "Maintain `Reg#(Bit#(8)) y <- mkReg(0)`. On `cmd[6]==1`: `y <= 0`; else `y <= y - (y >> 2) + zeroExtend(cmd[5:0])`.",
        "Bit#(7)", "Bit#(8)",
        "    Reg#(Bit#(8)) y <- mkReg(0);",
        "        if (cmd[6] == 1'b1) y <= 0;\n        else y <= y - (y >> 2) + zeroExtend(cmd[5:0]);",
        "        return y;",
        ["7'b0_010000", "7'b0_010000", "7'b0_010000", "7'b0_000000", "7'b0_000000", "7'b1_000000"],
        ["Subtract `y >> 2` and add `zeroExtend(cmd[5:0])`."]
    ))

    # Track 7 Memory Subsystems spiral reinforcement (+3)
    p.append(_seq(
        "46za_mem_double_buffer_ping_pong_bank", "track7_memory",
        "[Combo Lab] Ping-Pong Double Buffer Bank Swapper", "Medium", 25,
        ["Memory", "Double Buffer", "Combo Lab"], [],
        "Maintain two 8-bit banks (`bank0`, `bank1`) and active write selector `sel` (init 0). `cmd = {swap, we, wdata[7:0]}`. Writers write to `bank[sel]`, readers always read from `bank[~sel]`. `swap=1` toggles `sel`.",
        "On `step`: if `we`, write `wdata` to active bank (`sel==0 ? bank0 : bank1`); if `swap`, toggle `sel <= ~sel`. Read returns `{sel, (sel == 0) ? bank1 : bank0}`.",
        "Bit#(10)", "Bit#(9)",
        "    Reg#(Bit#(8)) bank0 <- mkReg(0);\n    Reg#(Bit#(8)) bank1 <- mkReg(0);\n    Reg#(Bit#(1)) sel <- mkReg(0);",
        "        if (cmd[8] == 1'b1) begin\n            if (sel == 0) bank0 <= cmd[7:0];\n            else bank1 <= cmd[7:0];\n        end\n        if (cmd[9] == 1'b1) sel <= ~sel;",
        "        return {sel, (sel == 0) ? bank1 : bank0};",
        ["10'b01_10100101", "10'b10_00000000", "10'b01_11110000", "10'b10_00000000"],
        ["Write to `sel`, read from `~sel`, and toggle `sel` when `cmd[9] == 1`."]
    ))
    p.append(_seq(
        "46zb_mem_bloom_filter_8bit_2hash", "track7_memory",
        "[Combo Lab] 8-Bit Hardware Bloom Filter (2 Hash Functions)", "Hard", 25,
        ["Memory", "Bloom Filter", "Combo Lab"], [],
        "Implement an 8-bit Bloom filter bitmap `bmap`. For a 6-bit key `k = cmd[5:0]`, hash1 = `k[2:0]` and hash2 = `k[5:3] ^ k[2:0]`. `cmd[6] == 1` inserts `k` (sets both bits in `bmap`). `cmd[7] == 1` clears `bmap <= 0`. Read returns `{last_hit, bmap}`.",
        "Maintain `Reg#(Bit#(8)) bmap <- mkReg(0)` and `Reg#(Bit#(1)) last_hit <- mkReg(0)`.",
        "Bit#(8)", "Bit#(9)",
        "    Reg#(Bit#(8)) bmap <- mkReg(0);\n    Reg#(Bit#(1)) last_hit <- mkReg(0);",
        "        Bit#(3) h1 = cmd[2:0];\n        Bit#(3) h2 = cmd[5:3] ^ cmd[2:0];\n        if (cmd[7] == 1'b1) begin bmap <= 0; last_hit <= 0; end\n        else if (cmd[6] == 1'b1) begin\n            bmap <= bmap | (8'd1 << h1) | (8'd1 << h2);\n            last_hit <= 1;\n        end else begin\n            last_hit <= bmap[h1] & bmap[h2];\n        end",
        "        return {last_hit, bmap};",
        ["8'b01_001_010", "8'b00_001_010", "8'b00_111_000", "8'b01_111_000", "8'b00_111_000", "8'b10_000_000"],
        ["Set `(8'd1 << h1) | (8'd1 << h2)` on insert and check `bmap[h1] & bmap[h2]` on query."]
    ))
    p.append(_c2(
        "46zc_mem_ecc_synd_error_classifier", "track7_memory",
        "[Reinforce] SEC-DED Parity & Syndrome Error Classifier", "Medium", 20,
        ["Memory", "ECC", "Reinforcement"], [],
        "Given `a = {overall_parity_err[0]}` and `b = syndrome[3:0]`, classify error type: `2'd0` = no error (`p==0 && s==0`), `2'd1` = single-bit correctable (`p==1 && s!=0`), `2'd2` = parity-bit error (`p==1 && s==0`), `2'd3` = double-bit uncorrectable (`p==0 && s!=0`).",
        "Return the 2-bit classification code.",
        "Bit#(1)", "Bit#(4)", "Bit#(2)",
        "if (a == 1'b0 && b == 4'd0) return 2'd0;\n        else if (a == 1'b1 && b != 4'd0) return 2'd1;\n        else if (a == 1'b1 && b == 4'd0) return 2'd2;\n        else return 2'd3;",
        [("1'b0", "4'd0"), ("1'b1", "4'd5"), ("1'b1", "4'd0"), ("1'b0", "4'd3")],
        ["Combine overall parity error `a` and non-zero syndrome `b != 0`."]
    ))

    # Track 8 CDC spiral reinforcement (+3)
    p.append(_seq(
        "38q_cdc_async_fifo_watermark_flags", "track7_cdc",
        "[Combo Lab] Async FIFO Depth & Almost-Full / Almost-Empty Watermarks", "Medium", 25,
        ["CDC", "Async FIFO", "Combo Lab"], [],
        "Given synchronized Gray pointers `cmd = {wgray[3:0], rgray[3:0]}` (depth 8), convert both to binary, compute `occ = wbin - rbin`, and latch `{occ==8, occ>=6, occ<=2, occ==0, occ[3:0]}`.",
        "Maintain `Reg#(Bit#(8)) status <- mkReg(8'b0011_0000)`.",
        "Bit#(8)", "Bit#(8)",
        "    Reg#(Bit#(8)) status <- mkReg(8'b0011_0000);\n    function Bit#(4) g2b(Bit#(4) g);\n        Bit#(4) b = 0;\n        b[3] = g[3]; b[2] = b[3] ^ g[2]; b[1] = b[2] ^ g[1]; b[0] = b[1] ^ g[0];\n        return b;\n    endfunction",
        "        Bit#(4) wb = g2b(cmd[7:4]);\n        Bit#(4) rb = g2b(cmd[3:0]);\n        Bit#(4) occ = wb - rb;\n        status <= {pack(occ == 4'd8), pack(occ >= 4'd6), pack(occ <= 4'd2), pack(occ == 4'd0), occ};",
        "        return status;",
        ["8'h00", "8'h10", "8'h50", "8'h40", "8'hC0", "8'h44"],
        ["Decode both Gray pointers to binary first, then subtract `wb - rb`."]
    ))
    p.append(_seq(
        "38r_cdc_credit_return_toggle_sync", "track7_cdc",
        "[Combo Lab] Cross-Domain Credit Counter with Toggle Return Synchronizer", "Hard", 25,
        ["CDC", "Credit Flow", "Combo Lab"], [],
        "Maintain local transmit credits `cred` (init 4). `cmd = {rx_credit_toggle, tx_send}`. A toggle change on `rx_credit_toggle` (`cmd[1] != prev_tog`) returns +1 credit; `tx_send` (`cmd[0]==1`) consumes -1 credit if available.",
        "Track `Reg#(Bit#(3)) cred <- mkReg(4)` and `Reg#(Bit#(1)) prev_tog <- mkReg(0)`. Read returns `{prev_tog, cred}`.",
        "Bit#(2)", "Bit#(4)",
        "    Reg#(Bit#(3)) cred <- mkReg(4);\n    Reg#(Bit#(1)) prev_tog <- mkReg(0);",
        "        Bool ret = (cmd[1] != prev_tog);\n        prev_tog <= cmd[1];\n        Bool send = (cmd[0] == 1'b1) && (cred > 0 || ret);\n        cred <= cred + (ret ? 3'd1 : 3'd0) - (send ? 3'd1 : 3'd0);",
        "        return {prev_tog, cred};",
        ["2'b01", "2'b01", "2'b11", "2'b10", "2'b00", "2'b10"],
        ["XOR/inequality on `cmd[1]` vs `prev_tog` detects a credit return pulse."]
    ))
    p.append(_c2(
        "38s_cdc_gray_pointer_step_checker", "track7_cdc",
        "[Reinforce] Gray Code Pointer Single-Bit Transition Validator", "Easy", 15,
        ["CDC", "Gray Code", "Reinforcement"], [],
        "Verify that transitioning from 8-bit Gray pointer `a` to `b` changes at most 1 bit (`((a ^ b) & ((a ^ b) - 1)) == 0`).",
        "Let `d = a ^ b`; return `1'b1` iff `(d & (d - 8'd1)) == 0`.",
        "Bit#(8)", "Bit#(8)", "Bit#(1)",
        "Bit#(8) d = a ^ b;\n        return ((d & (d - 8'd1)) == 0) ? 1'b1 : 1'b0;",
        [("8'b0000", "8'b0001"), ("8'b0001", "8'b0011"), ("8'b0001", "8'b0010"), ("8'b0100", "8'b0100")],
        ["A valid Gray pointer step changes 0 or 1 bit, so `d = a ^ b` has `(d & (d - 1)) == 0`."]
    ))

    # Track 9 Verification spiral reinforcement (+3)
    p.append(_seq(
        "44u_verif_req_grant_bounded_liveness", "track9_verification",
        "[Combo Lab] Bounded Liveness Checker (Req Must Be Granted Within 3 Cycles)", "Medium", 25,
        ["Verification", "SVA", "Combo Lab"], [],
        "Monitor `cmd = {gnt, req}`. While `req==1 && gnt==0`, increment wait counter `wait_cnt`. If `wait_cnt == 3` and still `req==1 && gnt==0`, latch `starved <= 1`. When `gnt==1 || req==0`, reset `wait_cnt <= 0`.",
        "Maintain `Reg#(Bit#(2)) wait_cnt <- mkReg(0)` and `Reg#(Bit#(1)) starved <- mkReg(0)`. Read returns `{starved, wait_cnt}`.",
        "Bit#(2)", "Bit#(3)",
        "    Reg#(Bit#(2)) wait_cnt <- mkReg(0);\n    Reg#(Bit#(1)) starved <- mkReg(0);",
        "        if (cmd == 2'b01) begin\n            if (wait_cnt == 2'd3) starved <= 1;\n            else wait_cnt <= wait_cnt + 1;\n        end else wait_cnt <= 0;",
        "        return {starved, wait_cnt};",
        ["2'b01", "2'b01", "2'b11", "2'b01", "2'b01", "2'b01", "2'b01", "2'b00"],
        ["Count consecutive cycles of `cmd == 2'b01` (`req=1, gnt=0`)."]
    ))
    p.append(_c2(
        "44v_verif_bug_hunt_alu_sub_borrow", "track9_verification",
        "[Bug Hunt] Fix the Broken Unsigned Borrow Flag (`a < b`)", "Easy", 20,
        ["Verification", "Bug Hunt", "ALU"], [],
        "A buggy ALU computes `{borrow, diff} = {1'b0, a} + {1'b0, ~b} + 9'd1` and outputs `sum[8]` directly as `borrow`, which is inverted! Fix it so `out[8] == 1` iff `a < b` (`out[7:0] = a - b`).",
        "Return `{pack(a < b), a - b}`.",
        "Bit#(8)", "Bit#(8)", "Bit#(9)",
        "return {pack(a < b), a - b};",
        [("8'd10", "8'd5"), ("8'd5", "8'd10"), ("8'd0", "8'd0"), ("8'd0", "8'd1")],
        ["In 2's complement subtraction `a + ~b + 1`, carry-out is `!borrow`, so `borrow = pack(a < b)`."]
    ))
    p.append(_seq(
        "44w_verif_credit_conservation_checker", "track9_verification",
        "[Combo Lab] End-to-End Credit + In-Flight Conservation Checker", "Hard", 25,
        ["Verification", "Assertions", "Combo Lab"], [],
        "Verify the invariant `credits + inflight == 4` across `cmd = {credit_ret, pkt_send}`. On `pkt_send`: `credits - 1, inflight + 1`. On `credit_ret`: `credits + 1, inflight - 1`. Latch `err <= 1` if underflow/overflow occurs.",
        "Maintain `Reg#(Bit#(3)) cred <- mkReg(4)`, `Reg#(Bit#(3)) inflight <- mkReg(0)`, `Reg#(Bit#(1)) err <- mkReg(0)`. Read returns `{err, cred, inflight}`.",
        "Bit#(2)", "Bit#(7)",
        "    Reg#(Bit#(3)) cred <- mkReg(4);\n    Reg#(Bit#(3)) inflight <- mkReg(0);\n    Reg#(Bit#(1)) err <- mkReg(0);",
        "        Bool ret = unpack(cmd[1]);\n        Bool send = unpack(cmd[0]);\n        if ((send && !ret && cred == 0) || (ret && !send && inflight == 0)) err <= 1;\n        else begin\n            cred <= cred + (ret ? 3'd1 : 3'd0) - (send ? 3'd1 : 3'd0);\n            inflight <= inflight + (send ? 3'd1 : 3'd0) - (ret ? 3'd1 : 3'd0);\n        end",
        "        return {err, cred, inflight};",
        ["2'b01", "2'b01", "2'b11", "2'b10", "2'b10", "2'b10"],
        ["Sending without credits or returning when `inflight == 0` violates conservation."]
    ))

    # Track 10 Architecture spiral reinforcement (+3)
    p.append(_seq(
        "32v_arch_tage_like_bimodal_alt_pred", "track6_architecture",
        "[Combo Lab] Tagged Hybrid Predictor (Base Bimodal + Tagged Override)", "Hard", 30,
        ["Architecture", "Branch Prediction", "Combo Lab"], [],
        "Combine a 2-bit base counter `base_ctr` (init 1) with a 3-bit tagged entry `{tag[1:0], pred_bit}` (`tag_reg`, init 0). `cmd = {we, upd_taken, tag_in[1:0]}`.",
        "Maintain `Reg#(Bit#(2)) base_ctr <- mkReg(1)` and `Reg#(Bit#(3)) tag_reg <- mkReg(0)`. Read returns `{tag_reg, base_ctr}`.",
        "Bit#(4)", "Bit#(5)",
        "    Reg#(Bit#(2)) base_ctr <- mkReg(1);\n    Reg#(Bit#(3)) tag_reg <- mkReg(0);",
        "        if (cmd[3] == 1'b1) begin\n            if (cmd[2] == 1'b1) base_ctr <= (base_ctr == 2'd3) ? 2'd3 : (base_ctr + 1);\n            else base_ctr <= (base_ctr == 2'd0) ? 2'd0 : (base_ctr - 1);\n            tag_reg <= {cmd[1:0], cmd[2]};\n        end",
        "        return {tag_reg, base_ctr};",
        ["4'b11_10", "4'b11_10", "4'b10_01", "4'b00_10"],
        ["Update both saturating `base_ctr` and `{tag, outcome}` on `cmd[3] == 1`."]
    ))
    p.append(_c2(
        "32w_arch_noc_dor_3d_xyz_router", "track6_architecture",
        "[Combo Lab] 3D Torus/Mesh Dimension-Order XYZ Routing Port Selector", "Medium", 25,
        ["Architecture", "NoC", "Combo Lab"], [],
        "Route from current 3D node `a = {cur_z[1:0], cur_y[1:0], cur_x[1:0]}` to destination `b = {dst_z[1:0], dst_y[1:0], dst_x[1:0]}` using strict X-then-Y-then-Z order: `0=Local, 1=+X, 2=-X, 3=+Y, 4=-Y, 5=+Z, 6=-Z`.",
        "Compare X first (`dst_x > cur_x -> 1`, `< -> 2`), then Y (`> -> 3`, `< -> 4`), then Z (`> -> 5`, `< -> 6`), else `0` (Local).",
        "Bit#(6)", "Bit#(6)", "Bit#(3)",
        "Bit#(2) cx = a[1:0]; Bit#(2) cy = a[3:2]; Bit#(2) cz = a[5:4];\n        Bit#(2) dx = b[1:0]; Bit#(2) dy = b[3:2]; Bit#(2) dz = b[5:4];\n        if (dx > cx) return 3'd1;\n        else if (dx < cx) return 3'd2;\n        else if (dy > cy) return 3'd3;\n        else if (dy < cy) return 3'd4;\n        else if (dz > cz) return 3'd5;\n        else if (dz < cz) return 3'd6;\n        else return 3'd0;",
        [("6'b01_01_01", "6'b10_10_10"), ("6'b01_01_10", "6'b10_10_10"), ("6'b01_10_10", "6'b10_10_10"), ("6'b10_10_10", "6'b10_10_10")],
        ["Route along X until `dx == cx`, then Y until `dy == cy`, then Z until `dz == cz`."]
    ))
    p.append(_seq(
        "32x_arch_superscalar_dual_issue_checker", "track6_architecture",
        "[Capstone Combo] 2-Way Superscalar Dual-Issue Hazard & Pairing Unit", "Hard", 30,
        ["Architecture", "Superscalar", "Capstone"], [],
        "Given two adjacent instructions `cmd = {is_mem1, rd1[1:0], rs1[1:0], is_mem0, rd0[1:0], rs0[1:0]}` (10 bits): determine whether both can dual-issue in the same cycle (`can_dual = 1` iff `!(rd0 != 0 && rd0 == rs1)` and `!(is_mem0 == 1 && is_mem1 == 1)`). Accumulate total instructions issued `issued` (+2 if dual-issued, +1 if serialized).",
        "Maintain `Reg#(Bit#(5)) issued <- mkReg(0)` and `Reg#(Bit#(1)) last_dual <- mkReg(0)`. Read returns `{last_dual, issued}`.",
        "Bit#(10)", "Bit#(6)",
        "    Reg#(Bit#(5)) issued <- mkReg(0);\n    Reg#(Bit#(1)) last_dual <- mkReg(0);",
        "        Bit#(1) mem1 = cmd[9]; Bit#(2) rd1 = cmd[8:7]; Bit#(2) rs1 = cmd[6:5];\n        Bit#(1) mem0 = cmd[4]; Bit#(2) rd0 = cmd[3:2]; Bit#(2) rs0 = cmd[1:0];\n        Bool raw = (rd0 != 2'd0) && (rd0 == rs1);\n        Bool mem_clash = (mem0 == 1'b1) && (mem1 == 1'b1);\n        Bool dual = !raw && !mem_clash;\n        issued <= issued + (dual ? 5'd2 : 5'd1);\n        last_dual <= pack(dual);",
        "        return {last_dual, issued};",
        ["10'b0_10_01_0_01_00", "10'b0_10_11_0_01_00", "10'b1_10_11_1_01_00", "10'b1_00_00_0_00_00"],
        ["Dual-issue is blocked if `rd0 != 0 && rd0 == rs1` (inter-instruction RAW) or `mem0 && mem1` (single load/store pipe)."]
    ))

    return p
