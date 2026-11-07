"""
Extended Procedural Hardware, Protocol, Verification & Computer Architecture Families
and Multi-Format Question Transformers for the BSVbits Competitive Arena (Mode 2).

Adds 23 additional parameterized generators (bringing total CP Arena corpus to 33 families!)
plus 5 question formats:
  1. `design_from_spec`        - Design module from specification
  2. `bug_fix_rtl`             - Debug & fix an injected RTL/BSV bug in an existing module
  3. `fill_in_blanks`          - Rapid LeetCode-style fill-in-the-blanks completion
  4. `verification_monitor`    - Write a property checker / verification monitor for A, B, C invariants
  5. `reverse_engineer_mystery`- Identify & implement a circuit from its I/O trace & characteristics
"""

from __future__ import annotations

import datetime
import hashlib
import random
import re
from typing import Any, Dict, List, Optional

from .curriculum import _make_problem


def _gen_clz_ctz_detector(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    count_leading = rng.choice([True, False])
    count_ones = rng.choice([False, True]) if difficulty != "Easy" else False
    target_bit = 1 if count_ones else 0
    stop_bit = 0 if count_ones else 1
    op_name = (
        ("Count Leading Ones (CLO)" if count_ones else "Count Leading Zeros (CLZ)")
        if count_leading
        else ("Count Trailing Ones (CTO)" if count_ones else "Count Trailing Zeros (CTZ)")
    )
    scan_dir = "MSB `x[7]` down to LSB `x[0]`" if count_leading else "LSB `x[0]` up to MSB `x[7]`"
    loop_hdr = (
        "for (Integer i = 7; i >= 0; i = i - 1)"
        if count_leading
        else "for (Integer i = 0; i < 8; i = i + 1)"
    )

    ref_snip = f"""    method Bit#(4) countBits(Bit#(8) x);
        Bit#(4) cnt = 0;
        Bool stop = False;
        {loop_hdr} begin
            if (!stop) begin
                if (x[i] == 1'b{stop_bit}) stop = True;
                else cnt = cnt + 1;
            end
        end
        return cnt;
    endmethod"""

    return _make_problem(
        pid=f"cp_clz_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 8-Bit {op_name} Unit",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "Bit Manipulation", op_name.split()[2].strip("()")],
        description=f"""
### Competitive Specification
Design an 8-bit **{op_name}** unit (`mkCpBitCounter`):
- Scan input `Bit#(8) x` starting from **{scan_dir}**.
- Count how many consecutive `{target_bit}` bits appear before the first `{stop_bit}` bit.
- Return the 4-bit count (`Bit#(4)`, ranging from `0` to `8`).
""",
        bsv_vs_verilog="Bit-manipulation instructions (`CLZ`, `CTZ`, `CLO`, `CTO` in RISC-V `Zbb` and ARM) use static priority loops in BSV.",
        diagram=f"x[7:0] ---> [ Scan {scan_dir} counting '{target_bit}'s until '{stop_bit}' ] ---> Bit#(4) (0..8)",
        interface_name="CpBitCounterIfc",
        module_name="mkCpBitCounter",
        interface_def="""
interface CpBitCounterIfc;
    method Bit#(4) countBits(Bit#(8) x);
endinterface
""",
        snippet_template="""    method Bit#(4) countBits(Bit#(8) x);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) tv[8] = {8'h00, 8'hFF, 8'h80, 8'h01, 8'hF0, 8'h0F, 8'h3C, 8'h7E};
        Bit#(8) x = tv[cycle];
        Bit#(4) r = ref_dut.countBits(x);
        Bit#(4) u = user_dut.countBits(x);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=x:0x%02h|ref=cnt:%0d|user=cnt:%0d|match=%0d|note=BitCount", cycle, x, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Use `{loop_hdr}` with `Bool stop = False;` and `Bit#(4) cnt = 0;`.",
            f"While `!stop`, if `x[i] == 1'b{stop_bit}` set `stop = True;`, else increment `cnt = cnt + 1;`.",
            "Return `cnt`.",
        ],
    )


def _gen_onehot_therm_codec(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    is_therm = rng.choice([True, False])
    invert_out = rng.choice([False, True]) if difficulty == "Hard" else False
    mode_name = "Thermometer Mask (`(1 << idx) - 1`)" if is_therm else "One-Hot Mask (`1 << idx`)"
    inv_str = " (Bitwise Inverted `~mask`)" if invert_out else ""
    expr = "((8'd1 << idx) - 8'd1)" if is_therm else "(8'd1 << idx)"
    if invert_out:
        expr = f"(~{expr})"

    ref_snip = f"""    method Bit#(8) encodeIdx(Bit#(3) idx);
        return {expr};
    endmethod

    method Bool isOneHot8(Bit#(8) v);
        return (v != 0) && ((v & (v - 1)) == 0);
    endmethod"""

    return _make_problem(
        pid=f"cp_ohtherm_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: {mode_name}{inv_str} & One-Hot Validator",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "One-Hot", "Thermometer Code"],
        description=f"""
### Competitive Specification
Implement two combinational methods in `mkCpOhTherm`:
1. `encodeIdx(Bit#(3) idx)`: Return the 8-bit **{mode_name}{inv_str}**:
   `return {expr};`
2. `isOneHot8(Bit#(8) v)`: Return `True` if and only if `v` has **exactly one `1` bit** (`(v != 0) && ((v & (v - 1)) == 0)`).
""",
        bsv_vs_verilog="Thermometer and one-hot masks are used in high-speed DACs, barrel shifters, and byte-lane mask generators.",
        diagram=f"idx[2:0] ---> {expr}   |   v[7:0] ---> (v != 0) && ((v & (v-1)) == 0)",
        interface_name="CpOhThermIfc",
        module_name="mkCpOhTherm",
        interface_def="""
interface CpOhThermIfc;
    method Bit#(8) encodeIdx(Bit#(3) idx);
    method Bool    isOneHot8(Bit#(8) v);
endinterface
""",
        snippet_template="""    method Bit#(8) encodeIdx(Bit#(3) idx);
        // === YOUR CODE HERE ===
        return 0;
    endmethod

    method Bool isOneHot8(Bit#(8) v);
        // === YOUR CODE HERE ===
        return False;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(3) idx = cycle[2:0];
        Bit#(8) tv[8] = {8'h00, 8'h01, 8'h03, 8'h04, 8'h18, 8'h20, 8'h80, 8'hFF};
        Bit#(8) r1 = ref_dut.encodeIdx(idx);
        Bit#(8) u1 = user_dut.encodeIdx(idx);
        Bool r2 = ref_dut.isOneHot8(tv[cycle]);
        Bool u2 = user_dut.isOneHot8(tv[cycle]);
        Bool ok = (r1 == u1) && (r2 == u2);
        $display("@WAVE cycle=%0d|in=idx:%0d,v:0x%02h|ref=enc:0x%02h,oh:%0d|user=enc:0x%02h,oh:%0d|match=%0d|note=OhTherm",
            cycle, idx, tv[cycle], r1, r2?1:0, u1, u2?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"In `encodeIdx(idx)`, `return {expr};`.",
            "In `isOneHot8(v)`, `return (v != 0) && ((v & (v - 1)) == 0);`.",
        ],
    )


def _gen_window_comparator(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    lo = rng.choice([16, 24, 32, 40])
    hi = rng.choice([160, 180, 200, 220])
    ref_snip = f"""    method Bit#(2) classify(Bit#(8) x);
        if (x < 8'd{lo}) return 2'b01;
        else if (x > 8'd{hi}) return 2'b10;
        else return 2'b00;
    endmethod

    method Bit#(8) clampWindow(Bit#(8) x);
        if (x < 8'd{lo}) return 8'd{lo};
        else if (x > 8'd{hi}) return 8'd{hi};
        else return x;
    endmethod"""

    return _make_problem(
        pid=f"cp_wincomp_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Sensor Window Comparator & Clamper ([{lo}, {hi}])",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "Window Comparator", "Sensor Clamping"],
        description=f"""
### Competitive Specification
Design a digital **Window Comparator & Clamper** (`mkCpWinComp`) with window bounds `LO = 8'd{lo}` and `HI = 8'd{hi}`:
1. `classify(Bit#(8) x)`:
   - Return `2'b01` if `x < 8'd{lo}` (Under-Window Alarm)
   - Return `2'b10` if `x > 8'd{hi}` (Over-Window Alarm)
   - Return `2'b00` if `8'd{lo} <= x <= 8'd{hi}` (Inside Window)
2. `clampWindow(Bit#(8) x)`:
   - Clamp `x` into `[8'd{lo}, 8'd{hi}]`.
""",
        bsv_vs_verilog="Digital ADC threshold monitors in automotive and industrial ASICs combine window classification with value clamping.",
        diagram=f"x[7:0] ---> [ Window [{lo}..{hi}] ] ---> classify (00/01/10) & clampWindow(x)",
        interface_name="CpWinCompIfc",
        module_name="mkCpWinComp",
        interface_def="""
interface CpWinCompIfc;
    method Bit#(2) classify(Bit#(8) x);
    method Bit#(8) clampWindow(Bit#(8) x);
endinterface
""",
        snippet_template="""    method Bit#(2) classify(Bit#(8) x);
        // === YOUR CODE HERE ===
        return 0;
    endmethod

    method Bit#(8) clampWindow(Bit#(8) x);
        // === YOUR CODE HERE ===
        return x;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body=f"""    rule test;
        Bit#(8) tv[6] = {{8'd5, 8'd{lo}, 8'd100, 8'd{hi}, 8'd240, 8'd{lo - 1}}};
        Bit#(8) x = tv[cycle];
        Bit#(2) r1 = ref_dut.classify(x);
        Bit#(2) u1 = user_dut.classify(x);
        Bit#(8) r2 = ref_dut.clampWindow(x);
        Bit#(8) u2 = user_dut.clampWindow(x);
        Bool ok = (r1 == u1) && (r2 == u2);
        $display("@WAVE cycle=%0d|in=x:%0d|ref=cls:%02b,clmp:%0d|user=cls:%02b,clmp:%0d|match=%0d|note=WinComp", cycle, x, r1, r2, u1, u2, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"In `classify(x)`, check `if (x < 8'd{lo}) return 2'b01; else if (x > 8'd{hi}) return 2'b10; else return 2'b00;`.",
            f"In `clampWindow(x)`, check `if (x < 8'd{lo}) return 8'd{lo}; else if (x > 8'd{hi}) return 8'd{hi}; else return x;`.",
        ],
    )


def _gen_updown_sat_counter(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    ceil_val = rng.choice([12, 15, 20, 30])
    step_val = rng.choice([1, 2, 3])
    ref_snip = f"""    Reg#(Bit#(8)) cnt <- mkReg(0);

    method Action step(Bool up, Bool clear);
        if (clear) begin
            cnt <= 0;
        end else if (up) begin
            cnt <= (cnt + 8'd{step_val} >= 8'd{ceil_val}) ? 8'd{ceil_val} : (cnt + 8'd{step_val});
        end else begin
            cnt <= (cnt <= 8'd{step_val}) ? 8'd0 : (cnt - 8'd{step_val});
        end
    endmethod

    method Bit#(8) read();
        return cnt;
    endmethod"""

    return _make_problem(
        pid=f"cp_satcnt_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Saturating Up/Down Counter (Step={step_val}, Max={ceil_val})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "Saturating Counter", "Counters"],
        description=f"""
### Competitive Specification
Design an 8-bit **Saturating Up/Down Counter** (`mkCpSatCounter`) with `STEP = 8'd{step_val}` and `MAX_VAL = 8'd{ceil_val}`:
- State: `Reg#(Bit#(8)) cnt <- mkReg(0);`
- `step(Bool up, Bool clear)`:
  - If `clear == True`: reset `cnt <= 0;`.
  - Else if `up == True`: increment `cnt` by `8'd{step_val}`, **saturating (clamping) at `8'd{ceil_val}`** (never wrapping!).
  - Else (`up == False`): decrement `cnt` by `8'd{step_val}`, **saturating at `8'd0`** (never underflowing!).
- `read()`: return `cnt`.
""",
        bsv_vs_verilog="Saturating counters prevent wrap-around bugs in QoS credit trackers, adaptive equalizers, and branch predictors.",
        diagram=f"step(up, clear) ---> [ Saturate in [0 .. {ceil_val}] by +/- {step_val} ] ---> read()",
        interface_name="CpSatCounterIfc",
        module_name="mkCpSatCounter",
        interface_def="""
interface CpSatCounterIfc;
    method Action step(Bool up, Bool clear);
    method Bit#(8) read();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) cnt <- mkReg(0);

    method Action step(Bool up, Bool clear);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) read();
        return cnt;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bool vup[8]  = {True, True, True, True, False, False, True, False};
        Bool vclr[8] = {False, False, False, False, False, False, True, False};
        Bit#(8) r = ref_dut.read();
        Bit#(8) u = user_dut.read();
        ref_dut.step(vup[cycle], vclr[cycle]);
        user_dut.step(vup[cycle], vclr[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=up:%0d,clr:%0d|ref=cnt:%0d|user=cnt:%0d|match=%0d|note=SatCounter",
            cycle, vup[cycle]?1:0, vclr[cycle]?1:0, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Check `if (clear) cnt <= 0;` first.",
            f"When `up` is `True`, `cnt <= (cnt + 8'd{step_val} >= 8'd{ceil_val}) ? 8'd{ceil_val} : (cnt + 8'd{step_val});`.",
            f"When `up` is `False`, `cnt <= (cnt <= 8'd{step_val}) ? 8'd0 : (cnt - 8'd{step_val});`.",
        ],
    )


def _gen_johnson_ring_counter(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    is_johnson = rng.choice([True, False])
    if is_johnson:
        title_str = "4-Bit Johnson (Twisted-Ring) Counter (`{~q[0], q[3:1]}`)"
        init_val = "4'b0000"
        next_expr = "{~q[0], q[3:1]}"
        desc_detail = "On each clock cycle (`rule tick`), shift right and feed the **inverted LSB `~q[0]`** into the MSB: `q <= {~q[0], q[3:1]};` (cycling through 8 states: `0000 -> 1000 -> 1100 -> 1110 -> 1111 -> 0111 -> 0011 -> 0001 -> 0000`)."
    else:
        title_str = "4-Bit One-Hot Ring Counter (`{q[2:0], q[3]}`)"
        init_val = "4'b0001"
        next_expr = "{q[2:0], q[3]}"
        desc_detail = "On each clock cycle (`rule tick`), rotate left by 1 bit: `q <= {q[2:0], q[3]};` (cycling through `0001 -> 0010 -> 0100 -> 1000 -> 0001`)."

    ref_snip = f"""    Reg#(Bit#(4)) q <- mkReg({init_val});

    rule tick;
        q <= {next_expr};
    endrule

    method Bit#(4) out();
        return q;
    endmethod"""

    return _make_problem(
        pid=f"cp_ring_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: {title_str}",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "Ring / Johnson Counter", "Counters"],
        description=f"""
### Competitive Specification
Design a **{title_str}** (`mkCpRingCounter`):
- Initialize `Reg#(Bit#(4)) q <- mkReg({init_val});`.
- {desc_detail}
- `out()` returns `q`.
""",
        bsv_vs_verilog="Johnson counters produce glitch-free adjacent Gray-like state transitions with zero combinational adder delay.",
        diagram=f"q (init {init_val}) ---> [ q <= {next_expr} ] ---> out()[3:0]",
        interface_name="CpRingCounterIfc",
        module_name="mkCpRingCounter",
        interface_def="""
interface CpRingCounterIfc;
    method Bit#(4) out();
endinterface
""",
        snippet_template=f"""    Reg#(Bit#(4)) q <- mkReg({init_val});

    // Write rule tick
    // === YOUR CODE HERE ===

    method Bit#(4) out();
        return q;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(4) r = ref_dut.out();
        Bit#(4) u = user_dut.out();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=clk:1|ref=q:%04b|user=q:%04b|match=%0d|note=RingCounter", cycle, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 8) begin
            $display("@SUMMARY total=9 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Write `rule tick; q <= {next_expr}; endrule`.",
            "Keep `out()` returning `q`.",
        ],
    )


def _gen_lfsr_scrambler(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    init_seed = rng.choice([0xA5, 0x5A, 0x3C, 0x96])
    tap_mask = rng.choice([0xB8, 0xB4, 0x8E])
    ref_snip = f"""    Reg#(Bit#(8)) lfsr <- mkReg(8'h{init_seed:02X});

    method ActionValue#(Bit#(8)) scrambleByte(Bit#(8) din);
        Bit#(8) dout = din ^ lfsr;
        Bit#(8) next_s = lfsr >> 1;
        if (lfsr[0] == 1) next_s = next_s ^ 8'h{tap_mask:02X};
        lfsr <= next_s;
        return dout;
    endmethod"""

    return _make_problem(
        pid=f"cp_scram_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Galois LFSR Data Scrambler (Tap=0x{tap_mask:02X}, Seed=0x{init_seed:02X})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "LFSR Scrambler", "PCIe / Ethernet PHY"],
        description=f"""
### Competitive Specification
High-speed serial links (PCIe, USB3, Ethernet PCS) XOR every transmitted byte with a **Galois LFSR Scrambler** (`mkCpScrambler`) to eliminate DC bias:
- State: `Reg#(Bit#(8)) lfsr <- mkReg(8'h{init_seed:02X});`
- In `scrambleByte(Bit#(8) din)`:
  1. Compute scrambled output `Bit#(8) dout = din ^ lfsr;`.
  2. Advance `lfsr` by 1 Galois step:
     `Bit#(8) next_s = lfsr >> 1;`
     `if (lfsr[0] == 1) next_s = next_s ^ 8'h{tap_mask:02X};`
     `lfsr <= next_s;`
  3. Return `dout`.
""",
        bsv_vs_verilog="Scramblers use `ActionValue#(Bit#(8))` in BSV because encrypting a byte simultaneously returns `din ^ lfsr` and advances the LFSR state.",
        diagram=f"din ^ lfsr ---> dout   |   lfsr <= (lfsr >> 1) ^ (lfsr[0] ? 8'h{tap_mask:02X} : 0)",
        interface_name="CpScramblerIfc",
        module_name="mkCpScrambler",
        interface_def="""
interface CpScramblerIfc;
    method ActionValue#(Bit#(8)) scrambleByte(Bit#(8) din);
endinterface
""",
        snippet_template=f"""    Reg#(Bit#(8)) lfsr <- mkReg(8'h{init_seed:02X});

    method ActionValue#(Bit#(8)) scrambleByte(Bit#(8) din);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) din = 8'h10 + cycle[7:0] * 8'h11;
        Bit#(8) r <- ref_dut.scrambleByte(din);
        Bit#(8) u <- user_dut.scrambleByte(din);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=din:0x%02h|ref=dout:0x%02h|user=dout:0x%02h|match=%0d|note=Scrambler", cycle, din, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bit#(8) dout = din ^ lfsr;` using the current `lfsr` state.",
            f"Compute `Bit#(8) next_s = (lfsr[0] == 1) ? ((lfsr >> 1) ^ 8'h{tap_mask:02X}) : (lfsr >> 1);`.",
            "Update `lfsr <= next_s;` and `return dout;`.",
        ],
    )


def _gen_watchdog_timer(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    timeout_cycles = rng.choice([3, 4, 5])
    ref_snip = f"""    Reg#(Bit#(4)) timer <- mkReg(0);
    Reg#(Bool)    alarm <- mkReg(False);

    method Action stepWatchdog(Bool kick);
        if (kick) begin
            timer <= 0;
        end else if (timer == 4'd{timeout_cycles}) begin
            alarm <= True;
        end else begin
            timer <= timer + 1;
        end
    endmethod

    method Bool isExpired();
        return alarm;
    endmethod"""

    return _make_problem(
        pid=f"cp_wdt_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Hardware Watchdog Timer (Timeout={timeout_cycles} Cycles)",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "Watchdog Timer", "Safety-Critical SoC"],
        description=f"""
### Competitive Specification
Design a safety-critical **Hardware Watchdog Timer** (`mkCpWatchdog`) with `TIMEOUT = 4'd{timeout_cycles}`:
- Registers: `Reg#(Bit#(4)) timer <- mkReg(0);` and sticky fault register `Reg#(Bool) alarm <- mkReg(False);`.
- In `stepWatchdog(Bool kick)`:
  - If `kick == True` (CPU heartbeat received): reset `timer <= 0;`.
  - Else if `timer == 4'd{timeout_cycles}`: assert sticky fault `alarm <= True;`.
  - Else: increment `timer <= timer + 1;`.
- `isExpired()` returns `alarm` (once `alarm` becomes `True`, it remains `True`!).
""",
        bsv_vs_verilog="Automotive ISO-26262 SoCs use sticky watchdog alarms so a hung CPU is guaranteed to trigger a system reset.",
        diagram=f"stepWatchdog(kick) ---> [ kick ? timer<=0 : (timer=={timeout_cycles} ? alarm<=1 : timer++) ] ---> isExpired()",
        interface_name="CpWatchdogIfc",
        module_name="mkCpWatchdog",
        interface_def="""
interface CpWatchdogIfc;
    method Action stepWatchdog(Bool kick);
    method Bool   isExpired();
endinterface
""",
        snippet_template="""    Reg#(Bit#(4)) timer <- mkReg(0);
    Reg#(Bool)    alarm <- mkReg(False);

    method Action stepWatchdog(Bool kick);
        // === YOUR CODE HERE ===
    endmethod

    method Bool isExpired();
        return alarm;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bool vkick[8] = {False, False, True, False, False, False, False, True};
        Bool r = ref_dut.isExpired();
        Bool u = user_dut.isExpired();
        ref_dut.stepWatchdog(vkick[cycle]);
        user_dut.stepWatchdog(vkick[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=kick:%0d|ref=alarm:%0d|user=alarm:%0d|match=%0d|note=Watchdog", cycle, vkick[cycle]?1:0, r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `stepWatchdog(Bool kick)`, check `if (kick) timer <= 0;`.",
            f"Else check `else if (timer == 4'd{timeout_cycles}) alarm <= True; else timer <= timer + 1;`.",
        ],
    )


def _gen_gearbox_serializer(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    big_endian = rng.choice([True, False])
    order_name = "Big-Endian (`{first_byte, second_byte}`)" if big_endian else "Little-Endian (`{second_byte, first_byte}`)"
    pack_expr = "{low_byte, b}" if big_endian else "{b, low_byte}"

    ref_snip = f"""    Reg#(Bit#(8))  low_byte <- mkReg(0);
    Reg#(Bool)     has_half <- mkReg(False);
    Reg#(Bit#(16)) out_word <- mkReg(0);
    Reg#(Bool)     out_val  <- mkReg(False);

    method Action pushByte(Bit#(8) b) if (!out_val);
        if (!has_half) begin
            low_byte <= b;
            has_half <= True;
        end else begin
            out_word <= {pack_expr};
            out_val  <= True;
            has_half <= False;
        end
    endmethod

    method ActionValue#(Bit#(16)) popWord() if (out_val);
        out_val <= False;
        return out_word;
    endmethod"""

    return _make_problem(
        pid=f"cp_gearbox_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 8-to-16 Bit {order_name.split()[0]} Gearbox Upsizer",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "Gearbox / SerDes", "Regslices"],
        description=f"""
### Competitive Specification
Design an **8-to-16 Bit Gearbox Upsizer** (`mkCpGearbox`) using **{order_name}** byte ordering:
- First `pushByte(b)` (`!has_half`): stores `low_byte <= b; has_half <= True;`.
- Second `pushByte(b)` (`has_half`): forms the 16-bit word `out_word <= {pack_expr};`, sets `out_val <= True; has_half <= False;`.
- `popWord() if (out_val)`: clears `out_val <= False;` and returns `out_word`.
""",
        bsv_vs_verilog="Implicit guards `if (!out_val)` on `pushByte` and `if (out_val)` on `popWord` prevent byte overwrite without manual stall logic.",
        diagram=f"Byte 0 (`low_byte`), Byte 1 (`b`) ---> [ out_word <= {pack_expr} ] ---> popWord()",
        interface_name="CpGearboxIfc",
        module_name="mkCpGearbox",
        interface_def="""
interface CpGearboxIfc;
    method Action pushByte(Bit#(8) b);
    method ActionValue#(Bit#(16)) popWord();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8))  low_byte <- mkReg(0);
    Reg#(Bool)     has_half <- mkReg(False);
    Reg#(Bit#(16)) out_word <- mkReg(0);
    Reg#(Bool)     out_val  <- mkReg(False);

    method Action pushByte(Bit#(8) b) if (!out_val);
        // === YOUR CODE HERE ===
    endmethod

    method ActionValue#(Bit#(16)) popWord() if (out_val);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        if (cycle == 0 || cycle == 1 || cycle == 3 || cycle == 4) begin
            Bit#(8) b = 8'hA0 + cycle[7:0];
            ref_dut.pushByte(b);
            user_dut.pushByte(b);
            $display("@WAVE cycle=%0d|in=push:0x%02h|ref=ok:1|user=ok:1|match=1|note=Push", cycle, b);
            passed_cnt <= passed_cnt + 1;
        end else if (cycle == 2 || cycle == 5) begin
            Bit#(16) r <- ref_dut.popWord();
            Bit#(16) u <- user_dut.popWord();
            Bool ok = (r == u);
            $display("@WAVE cycle=%0d|in=pop:1|ref=w:0x%04h|user=w:0x%04h|match=%0d|note=Pop", cycle, r, u, ok ? 1 : 0);
            passed_cnt <= passed_cnt + (ok ? 1 : 0);
        end
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", passed_cnt + 1);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `pushByte(b) if (!out_val)`, when `!has_half`, set `low_byte <= b; has_half <= True;`.",
            f"When `has_half` is `True`, set `out_word <= {pack_expr}; out_val <= True; has_half <= False;`.",
            "In `popWord() if (out_val)`, set `out_val <= False; return out_word;`.",
        ],
    )


def _gen_packet_firewall(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    bad_tag = rng.choice([1, 2, 3])
    xor_key = rng.choice([0x55, 0xAA, 0x0F, 0xF0])
    ref_snip = f"""    Reg#(Bit#(8)) drop_cnt <- mkReg(0);

    method ActionValue#(Maybe#(Bit#(8))) inspectPkt(Bit#(2) tag, Bit#(8) payload);
        if (tag == 2'd{bad_tag}) begin
            drop_cnt <= drop_cnt + 1;
            return tagged Invalid;
        end else begin
            return tagged Valid (payload ^ 8'h{xor_key:02X});
        end
    endmethod

    method Bit#(8) droppedCount();
        return drop_cnt;
    endmethod"""

    return _make_problem(
        pid=f"cp_fw_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Inline Packet Firewall & Payload Masker (Drop Tag={bad_tag})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "Packet Firewall", "Maybe#(t)"],
        description=f"""
### Competitive Specification
Design an inline **Network Packet Firewall** (`mkCpFirewall`):
- Hold a dropped-packet counter `Reg#(Bit#(8)) drop_cnt <- mkReg(0);`.
- In `inspectPkt(Bit#(2) tag, Bit#(8) payload)`:
  - If `tag == 2'd{bad_tag}` (blocked security tag): increment `drop_cnt <= drop_cnt + 1;` and return `tagged Invalid`.
  - Otherwise: return `tagged Valid (payload ^ 8'h{xor_key:02X})`.
- `droppedCount()` returns `drop_cnt`.
""",
        bsv_vs_verilog="Returning `Maybe#(Bit#(8))` combines the packet drop decision (`Valid` vs `Invalid`) with the transformed payload.",
        diagram=f"(tag, payload) ---> [ tag == {bad_tag} ? drop_cnt++, Invalid : Valid (payload ^ 0x{xor_key:02X}) ]",
        interface_name="CpFirewallIfc",
        module_name="mkCpFirewall",
        interface_def="""
interface CpFirewallIfc;
    method ActionValue#(Maybe#(Bit#(8))) inspectPkt(Bit#(2) tag, Bit#(8) payload);
    method Bit#(8) droppedCount();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) drop_cnt <- mkReg(0);

    method ActionValue#(Maybe#(Bit#(8))) inspectPkt(Bit#(2) tag, Bit#(8) payload);
        // === YOUR CODE HERE ===
        return tagged Invalid;
    endmethod

    method Bit#(8) droppedCount();
        return drop_cnt;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(2) t = cycle[1:0];
        Bit#(8) p = 8'hC0 + cycle[7:0];
        let r <- ref_dut.inspectPkt(t, p);
        let u <- user_dut.inspectPkt(t, p);
        Bit#(8) rc = ref_dut.droppedCount();
        Bit#(8) uc = user_dut.droppedCount();
        Bool ok = (r == u) && (rc == uc);
        $display("@WAVE cycle=%0d|in=tag:%0d,p:0x%02h|ref=val:%0d,drp:%0d|user=val:%0d,drp:%0d|match=%0d|note=Firewall",
            cycle, t, p, isValid(r)?1:0, rc, isValid(u)?1:0, uc, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"If `tag == 2'd{bad_tag}`, increment `drop_cnt <= drop_cnt + 1;` and `return tagged Invalid;`.",
            f"Else `return tagged Valid (payload ^ 8'h{xor_key:02X});`.",
        ],
    )


def _gen_vending_mealy_fsm(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    price = rng.choice([15, 20, 25])
    ref_snip = f"""    Reg#(Bit#(8)) bal <- mkReg(0);

    method ActionValue#(Bit#(9)) insertCoin(Bit#(8) coin);
        Bit#(8) tot = bal + coin;
        if (tot >= 8'd{price}) begin
            bal <= 0;
            Bit#(8) chg = tot - 8'd{price};
            return {{1'b1, chg}};
        end else begin
            bal <= tot;
            return {{1'b0, 8'd0}};
        end
    endmethod"""

    return _make_problem(
        pid=f"cp_vend_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Vending Machine FSM (Price={price} Cents, Dispense + Change)",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "Vending FSM", "Control + Datapath"],
        description=f"""
### Competitive Specification
Design a **Vending Machine Controller FSM** (`mkCpVending`) where an item costs **`8'd{price}` cents**:
- State: `Reg#(Bit#(8)) bal <- mkReg(0);`
- `insertCoin(Bit#(8) coin)` returns a 9-bit packed result `{{dispense_bit, change[7:0]}}`:
  - Let `Bit#(8) tot = bal + coin;`.
  - If `tot >= 8'd{price}`: reset `bal <= 0;` and return `{{1'b1, tot - 8'd{price}}}`.
  - Else: update `bal <= tot;` and return `{{1'b0, 8'd0}}`.
""",
        bsv_vs_verilog="Packing `{dispense, change[7:0]}` into `Bit#(9)` gives a single-cycle Mealy output on coin insertion.",
        diagram=f"coin ---> [ tot = bal + coin ] --(tot >= {price})--> {{1'b1, tot - {price}}}, bal <= 0",
        interface_name="CpVendingIfc",
        module_name="mkCpVending",
        interface_def="""
interface CpVendingIfc;
    method ActionValue#(Bit#(9)) insertCoin(Bit#(8) coin);
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) bal <- mkReg(0);

    method ActionValue#(Bit#(9)) insertCoin(Bit#(8) coin);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) coins[6] = {8'd5, 8'd10, 8'd10, 8'd25, 8'd10, 8'd20};
        Bit#(9) r <- ref_dut.insertCoin(coins[cycle]);
        Bit#(9) u <- user_dut.insertCoin(coins[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=coin:%0d|ref=disp:%0d,chg:%0d|user=disp:%0d,chg:%0d|match=%0d|note=Vending",
            cycle, coins[cycle], r[8], r[7:0], u[8], u[7:0], ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bit#(8) tot = bal + coin;`.",
            f"If `tot >= 8'd{price}`, set `bal <= 0;` and `return {{1'b1, tot - 8'd{price}}};`.",
            "Otherwise set `bal <= tot;` and `return {1'b0, 8'd0};`.",
        ],
    )


def _gen_apb_slave_periph(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    ro_addr = rng.choice([0, 3])
    magic_id = rng.choice([0xCAFE, 0xBEEF, 0x1234])
    ref_snip = f"""    Vector#(4, Reg#(Bit#(16))) regs <- replicateM(mkReg(0));

    method ActionValue#(Bit#(16)) apbStep(Bool psel, Bool penable, Bool pwrite, Bit#(2) paddr, Bit#(16) pwdata);
        if (psel && penable && pwrite) begin
            if (paddr != 2'd{ro_addr}) regs[paddr] <= pwdata;
            return 0;
        end else if (psel && !pwrite) begin
            return (paddr == 2'd{ro_addr}) ? 16'h{magic_id:04X} : regs[paddr];
        end else begin
            return 0;
        end
    endmethod"""

    return _make_problem(
        pid=f"cp_apb_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: AMBA APB3 Peripheral Slave (RO Hardware ID at Addr {ro_addr}=0x{magic_id:04X})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Protocol", "AMBA APB3", "SoC Bus"],
        description=f"""
### Competitive Specification
Design a 4-register **AMBA APB3 Peripheral Slave** (`mkCpApbSlave`) where address `2'd{ro_addr}` is a **Read-Only Hardware ID Register** returning `16'h{magic_id:04X}`:
- Hold `Vector#(4, Reg#(Bit#(16))) regs <- replicateM(mkReg(0));`.
- In `apbStep(Bool psel, Bool penable, Bool pwrite, Bit#(2) paddr, Bit#(16) pwdata)`:
  - **APB Write (`psel && penable && pwrite`)**: If `paddr != 2'd{ro_addr}`, write `regs[paddr] <= pwdata;` (writes to `2'd{ro_addr}` are ignored!). Return `0`.
  - **APB Read (`psel && !pwrite`)**: If `paddr == 2'd{ro_addr}`, return `16'h{magic_id:04X}`, else return `regs[paddr]`.
  - **Idle**: Return `0`.
""",
        bsv_vs_verilog="Real SoC peripherals always have a Read-Only ID/Version register at offset 0 or 3 that ignores APB writes.",
        diagram=f"APB (psel, penable, pwrite, paddr) ---> [ addr=={ro_addr} is RO 0x{magic_id:04X} | others RW ]",
        interface_name="CpApbSlaveIfc",
        module_name="mkCpApbSlave",
        interface_def="""
interface CpApbSlaveIfc;
    method ActionValue#(Bit#(16)) apbStep(Bool psel, Bool penable, Bool pwrite, Bit#(2) paddr, Bit#(16) pwdata);
endinterface
""",
        snippet_template="""    Vector#(4, Reg#(Bit#(16))) regs <- replicateM(mkReg(0));

    method ActionValue#(Bit#(16)) apbStep(Bool psel, Bool penable, Bool pwrite, Bit#(2) paddr, Bit#(16) pwdata);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bool vsel[6] = {True, True, True, True, True, True};
        Bool vena[6] = {True, True, True, True, True, True};
        Bool vwr[6]  = {True, False, True, False, True, False};
        Bit#(2) va[6]= {2'd0, 2'd0, 2'd1, 2'd1, 2'd3, 2'd3};
        Bit#(16) r <- ref_dut.apbStep(vsel[cycle], vena[cycle], vwr[cycle], va[cycle], 16'hABCD);
        Bit#(16) u <- user_dut.apbStep(vsel[cycle], vena[cycle], vwr[cycle], va[cycle], 16'hABCD);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=a:%0d,wr:%0d|ref=rd:0x%04h|user=rd:0x%04h|match=%0d|note=APB3 RO/RW", cycle, va[cycle], vwr[cycle]?1:0, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"When `psel && penable && pwrite`, check `if (paddr != 2'd{ro_addr}) regs[paddr] <= pwdata;` and `return 0;`.",
            f"When `psel && !pwrite`, `return (paddr == 2'd{ro_addr}) ? 16'h{magic_id:04X} : regs[paddr];`.",
        ],
    )


def _gen_noc_xy_router(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    my_x = rng.choice([2, 3, 4])
    my_y = rng.choice([2, 3, 4])
    yx_order = rng.choice([False, True]) if difficulty != "Easy" else False
    algo_name = "YX (Vertical-First, then Horizontal)" if yx_order else "XY (Horizontal-First, then Vertical)"

    if not yx_order:
        body_code = f"""        if (dst_x > 4'd{my_x}) return 3'd1;      // EAST
        else if (dst_x < 4'd{my_x}) return 3'd2; // WEST
        else if (dst_y > 4'd{my_y}) return 3'd3; // NORTH
        else if (dst_y < 4'd{my_y}) return 3'd4; // SOUTH
        else return 3'd0;                        // LOCAL"""
    else:
        body_code = f"""        if (dst_y > 4'd{my_y}) return 3'd3;      // NORTH
        else if (dst_y < 4'd{my_y}) return 3'd4; // SOUTH
        else if (dst_x > 4'd{my_x}) return 3'd1; // EAST
        else if (dst_x < 4'd{my_x}) return 3'd2; // WEST
        else return 3'd0;                        // LOCAL"""

    ref_snip = f"""    method Bit#(3) computePort(Bit#(4) dst_x, Bit#(4) dst_y);
{body_code}
    endmethod"""

    return _make_problem(
        pid=f"cp_noc_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 2D Mesh NoC {algo_name.split()[0]} Router at Tile ({my_x}, {my_y})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Architecture", "NoC Router", "Interconnect"],
        description=f"""
### Competitive Specification
Design the routing logic for a 2D Mesh Network-on-Chip Router located at **fixed tile coordinates `(MY_X = 4'd{my_x}, MY_Y = 4'd{my_y})`** using **{algo_name}** dimension-ordered routing:
- Port encodings (`Bit#(3)`):
  - `3'd0` = **LOCAL** (`dst_x == {my_x} && dst_y == {my_y}`)
  - `3'd1` = **EAST** (`dst_x > {my_x}`)
  - `3'd2` = **WEST** (`dst_x < {my_x}`)
  - `3'd3` = **NORTH** (`dst_y > {my_y}`)
  - `3'd4` = **SOUTH** (`dst_y < {my_y}`)
- Routing Priority: **{algo_name}**!
""",
        bsv_vs_verilog="Dimension-ordered routing (`XY` or `YX`) prevents cyclic buffer dependencies across the 2D mesh.",
        diagram=f"(dst_x, dst_y) vs ({my_x}, {my_y}) ---> [ {algo_name} ] ---> Port (0=L, 1=E, 2=W, 3=N, 4=S)",
        interface_name="CpNocRouterIfc",
        module_name="mkCpNocRouter",
        interface_def="""
interface CpNocRouterIfc;
    method Bit#(3) computePort(Bit#(4) dst_x, Bit#(4) dst_y);
endinterface
""",
        snippet_template="""    method Bit#(3) computePort(Bit#(4) dst_x, Bit#(4) dst_y);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body=f"""    rule test;
        Bit#(4) dx[6] = {{4'd{my_x}, 4'd6, 4'd1, 4'd{my_x}, 4'd{my_x}, 4'd0}};
        Bit#(4) dy[6] = {{4'd{my_y}, 4'd6, 4'd1, 4'd7, 4'd0, 4'd{my_y}}};
        Bit#(3) r = ref_dut.computePort(dx[cycle], dy[cycle]);
        Bit#(3) u = user_dut.computePort(dx[cycle], dy[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=dx:%0d,dy:%0d|ref=port:%0d|user=port:%0d|match=%0d|note=NoC Router", cycle, dx[cycle], dy[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Compare `dst_x` against `4'd{my_x}` and `dst_y` against `4'd{my_y}` in **{algo_name}** order.",
            "Return `3'd1` (EAST), `3'd2` (WEST), `3'd3` (NORTH), `3'd4` (SOUTH), or `3'd0` (LOCAL).",
        ],
    )


def _gen_branch_predictor_bht(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    init_state = rng.choice([1, 2])
    init_name = "Weakly Not-Taken (`2'b01`)" if init_state == 1 else "Weakly Taken (`2'b10`)"
    ref_snip = f"""    Vector#(4, Reg#(Bit#(2))) bht <- replicateM(mkReg(2'd{init_state}));

    method Bool predict(Bit#(2) idx);
        return bht[idx][1] == 1;
    endmethod

    method Action update(Bit#(2) idx, Bool taken);
        Bit#(2) s = bht[idx];
        if (taken) bht[idx] <= (s == 2'b11) ? 2'b11 : (s + 1);
        else       bht[idx] <= (s == 2'b00) ? 2'b00 : (s - 1);
    endmethod"""

    return _make_problem(
        pid=f"cp_bht_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 2-Bit Saturating Branch Predictor BHT (Init={init_name})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Architecture", "Branch Predictor", "2-Bit Counter"],
        description=f"""
### Competitive Specification
Design a 4-entry **2-Bit Saturating Counter Branch History Table (`BHT`)** (`mkCpBht`) initialized to **{init_name}**:
- `predict(Bit#(2) idx)`: Return `True` if `bht[idx] >= 2'b10` (i.e. `bht[idx][1] == 1`), else `False`.
- `update(Bit#(2) idx, Bool taken)`:
  - If `taken == True`: saturate-increment `bht[idx]` up to `2'b11`.
  - If `taken == False`: saturate-decrement `bht[idx]` down to `2'b00`.
""",
        bsv_vs_verilog="2-bit saturating counters add hysteresis to branch prediction so a single loop exit does not flip the prediction.",
        diagram=f"bht[0..3] (init 2'd{init_state}) ---> predict = bht[idx][1] == 1, update = +/-1 sat [0..3]",
        interface_name="CpBhtIfc",
        module_name="mkCpBht",
        interface_def="""
interface CpBhtIfc;
    method Bool   predict(Bit#(2) idx);
    method Action update(Bit#(2) idx, Bool taken);
endinterface
""",
        snippet_template=f"""    Vector#(4, Reg#(Bit#(2))) bht <- replicateM(mkReg(2'd{init_state}));

    method Bool predict(Bit#(2) idx);
        // === YOUR CODE HERE ===
        return False;
    endmethod

    method Action update(Bit#(2) idx, Bool taken);
        // === YOUR CODE HERE ===
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bool vt[8] = {True, False, False, False, True, True, True, False};
        Bool r = ref_dut.predict(2'd0);
        Bool u = user_dut.predict(2'd0);
        ref_dut.update(2'd0, vt[cycle]);
        user_dut.update(2'd0, vt[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=taken:%0d|ref=pred:%0d|user=pred:%0d|match=%0d|note=BHT", cycle, vt[cycle]?1:0, r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `predict(idx)`, `return bht[idx][1] == 1;`.",
            "In `update(idx, taken)`, saturate at `2'b11` when `taken` and at `2'b00` when `!taken`.",
        ],
    )


def _gen_pipeline_forwarding(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    ref_snip = """    method Bit#(16) forwardOp(Bit#(3) rs, Bit#(16) rf_val, Bool ex_we, Bit#(3) ex_rd, Bit#(16) ex_val, Bool wb_we, Bit#(3) wb_rd, Bit#(16) wb_val);
        if (ex_we && (ex_rd != 0) && (ex_rd == rs)) return ex_val;
        else if (wb_we && (wb_rd != 0) && (wb_rd == rs)) return wb_val;
        else return rf_val;
    endmethod"""

    return _make_problem(
        pid=f"cp_fwd_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 5-Stage CPU Pipeline Data Forwarding Multiplexer (`EX > WB > RF`)",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Architecture", "Forwarding Unit", "RISC-V Pipeline"],
        description="""
### Competitive Specification
Design a 5-stage CPU **Pipeline Data Forwarding Unit** (`mkCpForwarding`):
- Given source register `Bit#(3) rs` and register-file read value `rf_val`:
  1. **Younger Stage Priority (`EX/MEM`)**: If `ex_we && (ex_rd != 0) && (ex_rd == rs)`, return `ex_val`.
  2. **Older Stage Priority (`MEM/WB`)**: Else if `wb_we && (wb_rd != 0) && (wb_rd == rs)`, return `wb_val`.
  3. **Default (`RF`)**: Otherwise return `rf_val`.
- Remember: Register `3'd0` (`x0`) is hardwired to zero and must **never** be forwarded!
""",
        bsv_vs_verilog="Priority-encoding `ex_rd == rs` ahead of `wb_rd == rs` ensures back-to-back writes to the same register forward the youngest instruction's result.",
        diagram="rs ---> [ Check EX (ex_we & ex_rd!=0 & ex_rd==rs) -> Check WB -> RF ] ---> Bit#(16)",
        interface_name="CpForwardingIfc",
        module_name="mkCpForwarding",
        interface_def="""
interface CpForwardingIfc;
    method Bit#(16) forwardOp(Bit#(3) rs, Bit#(16) rf_val, Bool ex_we, Bit#(3) ex_rd, Bit#(16) ex_val, Bool wb_we, Bit#(3) wb_rd, Bit#(16) wb_val);
endinterface
""",
        snippet_template="""    method Bit#(16) forwardOp(Bit#(3) rs, Bit#(16) rf_val, Bool ex_we, Bit#(3) ex_rd, Bit#(16) ex_val, Bool wb_we, Bit#(3) wb_rd, Bit#(16) wb_val);
        // === YOUR CODE HERE ===
        return rf_val;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(3) vrs[6] = {3'd1, 3'd1, 3'd1, 3'd0, 3'd3, 3'd4};
        Bool exw[6]    = {True, True, False, True, False, False};
        Bit#(3) exr[6] = {3'd1, 3'd1, 3'd1, 3'd0, 3'd2, 3'd4};
        Bool wbw[6]    = {False, True, True, True, True, False};
        Bit#(3) wbr[6] = {3'd1, 3'd1, 3'd1, 3'd0, 3'd3, 3'd4};
        Bit#(16) r = ref_dut.forwardOp(vrs[cycle], 16'h1000, exw[cycle], exr[cycle], 16'h2000, wbw[cycle], wbr[cycle], 16'h3000);
        Bit#(16) u = user_dut.forwardOp(vrs[cycle], 16'h1000, exw[cycle], exr[cycle], 16'h2000, wbw[cycle], wbr[cycle], 16'h3000);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=rs:%0d|ref=val:0x%04h|user=val:0x%04h|match=%0d|note=Forwarding", cycle, vrs[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Check `if (ex_we && (ex_rd != 0) && (ex_rd == rs)) return ex_val;` first.",
            "Next check `else if (wb_we && (wb_rd != 0) && (wb_rd == rs)) return wb_val;`.",
            "Otherwise `return rf_val;`.",
        ],
    )


def _gen_verif_arbiter_checker(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    ref_snip = """    method Bool checkArbProps(Bit#(4) req, Bit#(4) gnt);
        Bool subset_ok = (gnt & ~req) == 0;
        Bool mutex_ok  = (gnt & (gnt - 1)) == 0;
        Bool work_ok   = (req == 0) || (gnt != 0);
        return subset_ok && mutex_ok && work_ok;
    endmethod"""

    return _make_problem(
        pid=f"cp_varb_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: [Verification] 4-Port Arbiter Property Checker (Subset, Mutex & Work-Conserving)",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Verification", "Property Checker", "Formal Invariants"],
        description="""
### Competitive Verification Specification
Write a hardware **Property Checker** (`mkCpArbChecker`) that verifies whether a 4-port arbiter's `(req, gnt)` outputs satisfy all **3 formal arbiter invariants**:
1. **Property A (No Unsolicited Grant)**: `(gnt & ~req) == 0`
2. **Property B (Mutual Exclusion / At-Most-One-Hot)**: `(gnt & (gnt - 1)) == 0`
3. **Property C (Work-Conserving)**: `(req == 0) || (gnt != 0)`
Return `True` if and only if all three properties hold!
""",
        bsv_vs_verilog="Combining `subset_ok && mutex_ok && work_ok` forms a complete specification monitor for any 4-port arbiter.",
        diagram="(req[3:0], gnt[3:0]) ---> [ Check Prop A && Prop B && Prop C ] ---> Bool",
        interface_name="CpArbCheckerIfc",
        module_name="mkCpArbChecker",
        interface_def="""
interface CpArbCheckerIfc;
    method Bool checkArbProps(Bit#(4) req, Bit#(4) gnt);
endinterface
""",
        snippet_template="""    method Bool checkArbProps(Bit#(4) req, Bit#(4) gnt);
        // === YOUR CODE HERE ===
        return False;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(4) vreq[8] = {4'b0000, 4'b0101, 4'b0101, 4'b1111, 4'b1010, 4'b0010, 4'b0000, 4'b0110};
        Bit#(4) vgnt[8] = {4'b0000, 4'b0001, 4'b0101, 4'b0000, 4'b0100, 4'b0010, 4'b0001, 4'b0100};
        Bool r = ref_dut.checkArbProps(vreq[cycle], vgnt[cycle]);
        Bool u = user_dut.checkArbProps(vreq[cycle], vgnt[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=req:0x%01h,gnt:0x%01h|ref=ok:%0d|user=ok:%0d|match=%0d|note=ArbVerify", cycle, vreq[cycle], vgnt[cycle], r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Check `Bool subset_ok = (gnt & ~req) == 0;`.",
            "Check `Bool mutex_ok = (gnt & (gnt - 1)) == 0;`.",
            "Check `Bool work_ok = (req == 0) || (gnt != 0);` and return `subset_ok && mutex_ok && work_ok;`.",
        ],
    )


def _gen_verif_axi_handshake(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    ref_snip = """    Reg#(Bool)    stalled   <- mkReg(False);
    Reg#(Bit#(8)) held_data <- mkReg(0);

    method ActionValue#(Bool) monitorBeat(Bool valid, Bool ready, Bit#(8) data);
        Bool ok = !stalled || (valid && (data == held_data));
        stalled <= (valid && !ready);
        if (valid && !ready) held_data <= data;
        return ok;
    endmethod"""

    return _make_problem(
        pid=f"cp_vaxi_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: [Verification] AXI-Stream Valid/Data Stability Protocol Monitor",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Verification", "AXI Protocol Monitor", "Handshake SVA"],
        description="""
### Competitive Verification Specification
Implement a stateful **AXI Ready/Valid Protocol Monitor** (`mkCpAxiMonitor`):
- In AXI, whenever `valid == True && ready == False` (a backpressured beat), on the **next clock cycle** the master **MUST keep `valid == True` AND keep `data == held_data`**!
- Track `Reg#(Bool) stalled <- mkReg(False);` and `Reg#(Bit#(8)) held_data <- mkReg(0);`.
- In `monitorBeat(Bool valid, Bool ready, Bit#(8) data)`:
  - Check `Bool ok = !stalled || (valid && (data == held_data));`.
  - Update `stalled <= (valid && !ready);` and if `valid && !ready`, latch `held_data <= data;`.
  - Return `ok`.
""",
        bsv_vs_verilog="Protocol monitors written in BSV can be attached directly to AXI busses in Bluesim or FPGA emulation.",
        diagram="(valid, ready, data) ---> [ If prev (valid && !ready), require (valid && data==held_data) ] ---> ok",
        interface_name="CpAxiMonitorIfc",
        module_name="mkCpAxiMonitor",
        interface_def="""
interface CpAxiMonitorIfc;
    method ActionValue#(Bool) monitorBeat(Bool valid, Bool ready, Bit#(8) data);
endinterface
""",
        snippet_template="""    Reg#(Bool)    stalled   <- mkReg(False);
    Reg#(Bit#(8)) held_data <- mkReg(0);

    method ActionValue#(Bool) monitorBeat(Bool valid, Bool ready, Bit#(8) data);
        // === YOUR CODE HERE ===
        return True;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bool vv[8] = {True, True, True, False, True, True, True, False};
        Bool vr[8] = {False, True, False, False, False, False, True, True};
        Bit#(8) vd[8] = {8'h11, 8'h11, 8'h22, 8'h22, 8'h33, 8'h44, 8'h44, 8'h00};
        Bool r <- ref_dut.monitorBeat(vv[cycle], vr[cycle], vd[cycle]);
        Bool u <- user_dut.monitorBeat(vv[cycle], vr[cycle], vd[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=v:%0d,r:%0d,d:0x%02h|ref=ok:%0d|user=ok:%0d|match=%0d|note=AXI Monitor",
            cycle, vv[cycle]?1:0, vr[cycle]?1:0, vd[cycle], r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bool ok = !stalled || (valid && (data == held_data));`.",
            "Update `stalled <= (valid && !ready);` and `if (valid && !ready) held_data <= data;`.",
            "Return `ok`.",
        ],
    )


def _gen_crc_parity_gen(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    odd_mode = rng.choice([True, False])
    p_name = "Odd Parity (`~(^x)`)" if odd_mode else "Even Parity (`^x`)"
    p_expr = "~(^x)" if odd_mode else "(^x)"
    ref_snip = f"""    method Bit#(9) appendParity(Bit#(8) x);
        Bit#(1) p = {p_expr};
        return {{p, x}};
    endmethod"""

    return _make_problem(
        pid=f"cp_par_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 8-Bit {p_name} Frame Generator",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "Parity / ECC", "Datapath"],
        description=f"""
### Competitive Specification
Design an 8-bit **{p_name} Frame Generator** (`mkCpParityGen`):
- Given an 8-bit payload `Bit#(8) x`, compute the 1-bit parity bit `Bit#(1) p = {p_expr};`.
- Return the 9-bit frame `{{p, x}}` (`Bit#(9)`).
""",
        bsv_vs_verilog="Reduction XOR `^x` computes the parity of an N-bit bus in a balanced log2(N)-depth XOR tree.",
        diagram=f"x[7:0] ---> [ p = {p_expr} ] ---> {{p, x[7:0]}}",
        interface_name="CpParityGenIfc",
        module_name="mkCpParityGen",
        interface_def="""
interface CpParityGenIfc;
    method Bit#(9) appendParity(Bit#(8) x);
endinterface
""",
        snippet_template="""    method Bit#(9) appendParity(Bit#(8) x);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) tv[6] = {8'h00, 8'h01, 8'h03, 8'h55, 8'h7F, 8'hFF};
        Bit#(9) r = ref_dut.appendParity(tv[cycle]);
        Bit#(9) u = user_dut.appendParity(tv[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=x:0x%02h|ref=out:0x%03h|user=out:0x%03h|match=%0d|note=Parity", cycle, tv[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Compute `Bit#(1) p = {p_expr};`.",
            "Return `{p, x};`.",
        ],
    )


def _gen_debounce_glitch_filter(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    ref_snip = """    Reg#(Bit#(3)) hist  <- mkReg(0);
    Reg#(Bit#(1)) clean <- mkReg(0);

    method ActionValue#(Bit#(1)) filterSample(Bit#(1) raw_in);
        Bit#(3) next_h = {hist[1:0], raw_in};
        Bit#(1) next_c = (next_h == 3'b111) ? 1'b1 : ((next_h == 3'b000) ? 1'b0 : clean);
        hist  <= next_h;
        clean <= next_c;
        return next_c;
    endmethod"""

    return _make_problem(
        pid=f"cp_deb_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 3-Sample Majority/All-Ones Glitch Debouncer",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "Debouncer", "Glitch Filter"],
        description="""
### Competitive Specification
Design a **3-Sample Glitch Filter** (`mkCpDebouncer`):
- Hold `Reg#(Bit#(3)) hist <- mkReg(0);` and `Reg#(Bit#(1)) clean <- mkReg(0);`.
- In `filterSample(Bit#(1) raw_in)`:
  - Shift `Bit#(3) next_h = {hist[1:0], raw_in};`.
  - If `next_h == 3'b111`, set `next_c = 1'b1`; else if `next_h == 3'b000`, set `next_c = 1'b0`; else keep `next_c = clean`.
  - Update `hist <= next_h; clean <= next_c;` and return `next_c`.
""",
        bsv_vs_verilog="Requiring 3 consecutive identical samples (`3'b111` or `3'b000`) filters out single-cycle and two-cycle noise spikes.",
        diagram="raw_in ---> [ next_h = {hist[1:0], raw_in} ] ---> (111=>1, 000=>0, else clean)",
        interface_name="CpDebouncerIfc",
        module_name="mkCpDebouncer",
        interface_def="""
interface CpDebouncerIfc;
    method ActionValue#(Bit#(1)) filterSample(Bit#(1) raw_in);
endinterface
""",
        snippet_template="""    Reg#(Bit#(3)) hist  <- mkReg(0);
    Reg#(Bit#(1)) clean <- mkReg(0);

    method ActionValue#(Bit#(1)) filterSample(Bit#(1) raw_in);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(1) vraw[8] = {1'b1, 1'b0, 1'b1, 1'b1, 1'b1, 1'b0, 1'b0, 1'b0};
        Bit#(1) r <- ref_dut.filterSample(vraw[cycle]);
        Bit#(1) u <- user_dut.filterSample(vraw[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=raw:%0d|ref=clean:%0d|user=clean:%0d|match=%0d|note=Debouncer", cycle, vraw[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bit#(3) next_h = {hist[1:0], raw_in};`.",
            "Compute `Bit#(1) next_c = (next_h == 3'b111) ? 1'b1 : ((next_h == 3'b000) ? 1'b0 : clean);`.",
            "Update `hist <= next_h; clean <= next_c; return next_c;`.",
        ],
    )


def _gen_skid_credit_fifo(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    init_c = rng.choice([4, 6, 8])
    ref_snip = f"""    Reg#(Bit#(4)) cred <- mkReg(4'd{init_c});

    method Action stepCredits(Bool send_flit, Bool credit_ret);
        if (send_flit && !credit_ret && (cred > 0))
            cred <= cred - 1;
        else if (!send_flit && credit_ret && (cred < 4'd{init_c}))
            cred <= cred + 1;
    endmethod

    method Bit#(4) creditsLeft();
        return cred;
    endmethod"""

    return _make_problem(
        pid=f"cp_cred_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Interconnect Credit Counter (Max Credits={init_c}, Simultaneous Send+Return)",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Protocol", "Credit Flow Control", "NoC / PCIe"],
        description=f"""
### Competitive Specification
Design a link-layer **Credit Flow Control Counter** (`mkCpCreditCtrl`) initialized to **`MAX_CREDITS = 4'd{init_c}`**:
- In `stepCredits(Bool send_flit, Bool credit_ret)`:
  - If `send_flit && !credit_ret && (cred > 0)`: decrement `cred <= cred - 1;`.
  - Else if `!send_flit && credit_ret && (cred < 4'd{init_c})`: increment `cred <= cred + 1;`.
  - If both `send_flit && credit_ret` happen simultaneously, `cred` remains unchanged!
- `creditsLeft()` returns `cred`.
""",
        bsv_vs_verilog="Simultaneous flit transmission and credit return is the steady-state full-throughput condition of any PCIe/NoC link.",
        diagram=f"(send_flit, credit_ret) ---> [ cred (init {init_c}): -1, +1, or hold ] ---> creditsLeft()",
        interface_name="CpCreditCtrlIfc",
        module_name="mkCpCreditCtrl",
        interface_def="""
interface CpCreditCtrlIfc;
    method Action stepCredits(Bool send_flit, Bool credit_ret);
    method Bit#(4) creditsLeft();
endinterface
""",
        snippet_template=f"""    Reg#(Bit#(4)) cred <- mkReg(4'd{init_c});

    method Action stepCredits(Bool send_flit, Bool credit_ret);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(4) creditsLeft();
        return cred;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bool vs[8] = {True, True, True, False, True, False, False, True};
        Bool vr[8] = {False, False, True, True, True, True, False, False};
        Bit#(4) r = ref_dut.creditsLeft();
        Bit#(4) u = user_dut.creditsLeft();
        ref_dut.stepCredits(vs[cycle], vr[cycle]);
        user_dut.stepCredits(vs[cycle], vr[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=s:%0d,r:%0d|ref=c:%0d|user=c:%0d|match=%0d|note=Credits", cycle, vs[cycle]?1:0, vr[cycle]?1:0, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "If `send_flit && !credit_ret && (cred > 0)`, set `cred <= cred - 1;`.",
            f"Else if `!send_flit && credit_ret && (cred < 4'd{init_c})`, set `cred <= cred + 1;`.",
        ],
    )


def _gen_axi_wstrb_merger(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    ref_snip = """    method Bit#(16) mergeWstrb(Bit#(16) old_word, Bit#(16) wdata, Bit#(2) wstrb);
        Bit#(8) b0 = (wstrb[0] == 1) ? wdata[7:0]  : old_word[7:0];
        Bit#(8) b1 = (wstrb[1] == 1) ? wdata[15:8] : old_word[15:8];
        return {b1, b0};
    endmethod"""

    return _make_problem(
        pid=f"cp_wstrb_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: AXI4-Lite 16-Bit Byte-Lane Write Strobe (`WSTRB`) Merger",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Protocol", "AXI4-Lite WSTRB", "Byte Enable"],
        description="""
### Competitive Specification
Design a combinational **AXI4-Lite 16-Bit Write-Strobe Byte Merger** (`mkCpWstrbMerger`):
- Given `Bit#(16) old_word`, `Bit#(16) wdata`, and 2-bit byte-enable `Bit#(2) wstrb`:
  - Byte 0 (`[7:0]`): `(wstrb[0] == 1) ? wdata[7:0] : old_word[7:0]`
  - Byte 1 (`[15:8]`): `(wstrb[1] == 1) ? wdata[15:8] : old_word[15:8]`
- Return `{b1, b0}` (`Bit#(16)`).
""",
        bsv_vs_verilog="Byte-lane strobe multiplexing (`WSTRB`) allows unaligned byte writes to 16/32/64-bit AXI registers.",
        diagram="old_word[15:0], wdata[15:0], wstrb[1:0] ---> [ Byte-Lane Mux ] ---> {b1, b0}",
        interface_name="CpWstrbMergerIfc",
        module_name="mkCpWstrbMerger",
        interface_def="""
interface CpWstrbMergerIfc;
    method Bit#(16) mergeWstrb(Bit#(16) old_word, Bit#(16) wdata, Bit#(2) wstrb);
endinterface
""",
        snippet_template="""    method Bit#(16) mergeWstrb(Bit#(16) old_word, Bit#(16) wdata, Bit#(2) wstrb);
        // === YOUR CODE HERE ===
        return old_word;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(2) vs[4] = {2'b00, 2'b01, 2'b10, 2'b11};
        Bit#(2) st = vs[cycle[1:0]];
        Bit#(16) r = ref_dut.mergeWstrb(16'hCAFE, 16'hBEEF, st);
        Bit#(16) u = user_dut.mergeWstrb(16'hCAFE, 16'hBEEF, st);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=strb:%02b|ref=out:0x%04h|user=out:0x%04h|match=%0d|note=WSTRB", cycle, st, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 3) begin
            $display("@SUMMARY total=4 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Select `Bit#(8) b0 = (wstrb[0] == 1) ? wdata[7:0] : old_word[7:0];`.",
            "Select `Bit#(8) b1 = (wstrb[1] == 1) ? wdata[15:8] : old_word[15:8];` and `return {b1, b0};`.",
        ],
    )


def _gen_round_robin_arbiter(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    init_p = rng.choice([0, 1, 2])
    ref_snip = f"""    Reg#(Bit#(2)) prio <- mkReg(2'd{init_p});

    method ActionValue#(Bit#(4)) nextGrant(Bit#(4) req);
        Bit#(4) gnt = 0;
        Bit#(2) np = prio;
        Bool found = False;
        for (Integer i = 0; i < 4; i = i + 1) begin
            Bit#(2) idx = prio + fromInteger(i);
            if (!found && (req[idx] == 1)) begin
                gnt[idx] = 1;
                np = idx + 1;
                found = True;
            end
        end
        prio <= np;
        return gnt;
    endmethod"""

    return _make_problem(
        pid=f"cp_rr_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 4-Port Round-Robin Arbiter (Initial Pointer={init_p})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Protocol", "Round-Robin Arbiter", "Fair Scheduling"],
        description=f"""
### Competitive Specification
Design a 4-port **Round-Robin Arbiter** (`mkCpRRArb`) with rotating pointer `Reg#(Bit#(2)) prio <- mkReg(2'd{init_p});`:
- In `nextGrant(Bit#(4) req)`:
  - Scan `i = 0 .. 3` checking `Bit#(2) idx = prio + fromInteger(i);`.
  - The first port `idx` with `req[idx] == 1` receives the one-hot grant `gnt[idx] = 1`, and updates `prio <= idx + 1;`.
  - If `req == 0`, return `4'b0000` and keep `prio` unchanged.
""",
        bsv_vs_verilog="Modulo-4 pointer wrap (`Bit#(2) idx = prio + fromInteger(i)`) unrolls into a 4-input barrel priority arbiter.",
        diagram=f"req[3:0] ---> [ Scan idx = prio..prio+3 (init prio={init_p}) ] ---> gnt[3:0], prio <= winner+1",
        interface_name="CpRRArbIfc",
        module_name="mkCpRRArb",
        interface_def="""
interface CpRRArbIfc;
    method ActionValue#(Bit#(4)) nextGrant(Bit#(4) req);
endinterface
""",
        snippet_template=f"""    Reg#(Bit#(2)) prio <- mkReg(2'd{init_p});

    method ActionValue#(Bit#(4)) nextGrant(Bit#(4) req);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(4) vreq[6] = {4'b1111, 4'b1111, 4'b1010, 4'b1010, 4'b0100, 4'b0000};
        Bit#(4) r <- ref_dut.nextGrant(vreq[cycle]);
        Bit#(4) u <- user_dut.nextGrant(vreq[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=req:0x%01h|ref=gnt:0x%01h|user=gnt:0x%01h|match=%0d|note=RRArb", cycle, vreq[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Loop `for (Integer i = 0; i < 4; i = i + 1)` with `Bit#(2) idx = prio + fromInteger(i);`.",
            "On the first `req[idx] == 1`, set `gnt[idx] = 1; np = idx + 1; found = True;`.",
            "Update `prio <= np; return gnt;`.",
        ],
    )


def _gen_verif_fifo_conservation(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    max_d = rng.choice([4, 8])
    ref_snip = f"""    Reg#(Bit#(4)) occ <- mkReg(0);

    method ActionValue#(Bool) checkFifoCycle(Bool enq, Bool deq, Bool emp, Bool full);
        Bool ok = (emp == (occ == 0)) && (full == (occ == 4'd{max_d})) &&
                  !(occ == 4'd{max_d} && enq && !deq) && !(occ == 0 && deq && !enq);
        if (ok) begin
            if (enq && !deq) occ <= occ + 1;
            else if (!enq && deq) occ <= occ - 1;
        end
        return ok;
    endmethod"""

    return _make_problem(
        pid=f"cp_vfifo_{seed}",
        number=seed % 1000,
        title=f"CP #{seed % 1000}: [Verification] FIFO Occupancy & Boundary Invariant Monitor (Depth={max_d})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Verification", "FIFO Invariant Monitor", "Scoreboard"],
        description=f"""
### Competitive Verification Specification
Implement a stateful **FIFO Invariant Monitor** (`mkCpFifoMonitor`) for a FIFO of capacity **`DEPTH = 4'd{max_d}`**:
- Track shadow occupancy `Reg#(Bit#(4)) occ <- mkReg(0);`.
- In `checkFifoCycle(Bool enq, Bool deq, Bool emp, Bool full)`:
  - Verify all 4 invariants:
    1. `emp == (occ == 0)`
    2. `full == (occ == 4'd{max_d})`
    3. No overflow: `!(occ == 4'd{max_d} && enq && !deq)`
    4. No underflow: `!(occ == 0 && deq && !enq)`
  - If all 4 hold (`ok == True`), update `occ` (`+1` if `enq && !deq`, `-1` if `!enq && deq`).
  - Return `ok`.
""",
        bsv_vs_verilog="Shadow occupancy scoreboards catch pointer corruption and flag timing bugs in custom FIFOs.",
        diagram=f"(enq, deq, emp, full) ---> [ Check emp/full/ovf/udf against occ (0..{max_d}) ] ---> Bool",
        interface_name="CpFifoMonitorIfc",
        module_name="mkCpFifoMonitor",
        interface_def="""
interface CpFifoMonitorIfc;
    method ActionValue#(Bool) checkFifoCycle(Bool enq, Bool deq, Bool emp, Bool full);
endinterface
""",
        snippet_template="""    Reg#(Bit#(4)) occ <- mkReg(0);

    method ActionValue#(Bool) checkFifoCycle(Bool enq, Bool deq, Bool emp, Bool full);
        // === YOUR CODE HERE ===
        return True;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bool ve[6] = {True, True, False, False, False, True};
        Bool vd[6] = {False, True, True, True, True, False};
        Bool vemp[6] = {True, False, False, False, True, True};
        Bool vful[6] = {False, False, False, False, False, False};
        Bool r <- ref_dut.checkFifoCycle(ve[cycle], vd[cycle], vemp[cycle], vful[cycle]);
        Bool u <- user_dut.checkFifoCycle(ve[cycle], vd[cycle], vemp[cycle], vful[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=enq:%0d,deq:%0d|ref=ok:%0d|user=ok:%0d|match=%0d|note=FifoVerify", cycle, ve[cycle]?1:0, vd[cycle]?1:0, r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Check `Bool ok = (emp == (occ == 0)) && (full == (occ == 4'd{max_d})) && !(occ == 4'd{max_d} && enq && !deq) && !(occ == 0 && deq && !enq);`.",
            "When `ok` is `True`, update `occ <= occ + 1` on `enq && !deq`, or `occ <= occ - 1` on `!enq && deq`.",
        ],
    )


EXTRA_CP_GENERATORS = {
    "clz_ctz_detector": _gen_clz_ctz_detector,
    "onehot_therm_codec": _gen_onehot_therm_codec,
    "window_comparator": _gen_window_comparator,
    "crc_parity_gen": _gen_crc_parity_gen,
    "updown_sat_counter": _gen_updown_sat_counter,
    "johnson_ring_counter": _gen_johnson_ring_counter,
    "lfsr_scrambler": _gen_lfsr_scrambler,
    "debounce_glitch_filter": _gen_debounce_glitch_filter,
    "watchdog_timer": _gen_watchdog_timer,
    "skid_credit_fifo": _gen_skid_credit_fifo,
    "gearbox_serializer": _gen_gearbox_serializer,
    "packet_firewall": _gen_packet_firewall,
    "vending_mealy_fsm": _gen_vending_mealy_fsm,
    "apb_slave_periph": _gen_apb_slave_periph,
    "axi_wstrb_merger": _gen_axi_wstrb_merger,
    "noc_xy_router": _gen_noc_xy_router,
    "round_robin_arbiter": _gen_round_robin_arbiter,
    "branch_predictor_bht": _gen_branch_predictor_bht,
    "pipeline_forwarding": _gen_pipeline_forwarding,
    "verif_arbiter_checker": _gen_verif_arbiter_checker,
    "verif_axi_handshake": _gen_verif_axi_handshake,
    "verif_fifo_conservation": _gen_verif_fifo_conservation,
}


# =============================================================================
# QUESTION FORMAT TRANSFORMER (5 Modes: Design, Bug-Fix, Fill-Blanks, Verification, Mystery)
# =============================================================================

CP_QUESTION_FORMATS: List[Dict[str, str]] = [
    {"id": "all", "name": "All 7 Formats (Mixed Practice)"},
    {"id": "design_from_spec", "name": "1. Design Module from Spec"},
    {"id": "bug_fix_rtl", "name": "2. Debug & Fix Buggy RTL (Bug Hunt)"},
    {"id": "fill_in_blanks", "name": "3. Fill-in-the-Blanks (Rapid Speedrun)"},
    {"id": "verification_monitor", "name": "4. Verification & Property Checking"},
    {"id": "reverse_engineer_mystery", "name": "5. Reverse-Engineer Mystery Circuit"},
    {"id": "spiral_reinforcement", "name": "6. Spiral Track Reinforcement & Revision"},
    {"id": "speed_coding_sprint", "name": "7. 90-Second Blitz Speed-Coding Sprint"},
]


def apply_question_format(
    prob: Dict[str, Any],
    question_format: str,
    rng: random.Random,
) -> Dict[str, Any]:
    """
    Transform a generated CP problem into one of the 7 interactive question formats:
      - `design_from_spec`
      - `bug_fix_rtl`
      - `fill_in_blanks`
      - `verification_monitor`
      - `reverse_engineer_mystery`
      - `spiral_reinforcement`
      - `speed_coding_sprint`
    """
    if prob["cp_category"].startswith("verif_"):
        fmt = "verification_monitor"
    elif question_format in ("all", "", None):
        fmt = rng.choice([
            "design_from_spec", "design_from_spec", "bug_fix_rtl",
            "fill_in_blanks", "reverse_engineer_mystery", "spiral_reinforcement",
        ])
    else:
        fmt = question_format

    prob["question_format"] = fmt
    ref = prob["reference_snippet"]

    if fmt == "bug_fix_rtl":
        # Deterministically inject a realistic RTL bug into the reference snippet!
        buggy = ref
        bug_desc = "An off-by-one or inverted operator bug was introduced in the datapath/control logic."
        replacements = [
            (" + 1", " + 2", "Off-by-one increment (`+ 2` instead of `+ 1`)"),
            (" - 1", " + 1", "Inverted arithmetic direction (`+ 1` instead of `- 1`)"),
            (" ^ ", " & ", "Wrong bitwise operator (`&` used instead of `^`)"),
            (" == 1", " == 0", "Inverted bit-polarity check (`== 0` instead of `== 1`)"),
            (" >> 1", " << 1", "Reversed shift direction (`<< 1` instead of `>> 1`)"),
            (" < ", " > ", "Reversed relational comparison (`>` instead of `<`)"),
        ]
        for old_s, new_s, desc in replacements:
            if old_s in buggy:
                buggy = buggy.replace(old_s, new_s, 1)
                bug_desc = desc
                break

        prob["snippet_template"] = (
            "    // [BUG HUNT MODE]: Find and fix the RTL bug in the implementation below!\n"
            + buggy
        )
        prob["full_template"] = (
            f"module {prob['module_name']}({prob['interface_name']});\n"
            f"{prob['snippet_template']}\n"
            f"endmodule"
        )
        prob["title"] = re.sub(r"^CP #(\d+):", r"CP #\1 [Bug Hunt]:", prob["title"])
        prob["tags"] = ["Format: Bug Hunt"] + prob.get("tags", [])
        prob["description"] = (
            "> [!WARNING]\n"
            "> **RTL Debugging Challenge (`bug_fix_rtl`)**: The module below already has an implementation in your editor, "
            "but it contains a **hardware bug** causing simulation mismatches against the specification! "
            "Run **Compile & Verify** to inspect the failing waveform cycles, or inspect the code against the spec below and fix the bug.\n\n"
            + prob["description"]
        )
        prob["hints"] = [f"Bug Hunt Clue: Look closely for: {bug_desc}"] + prob.get("hints", [])
        prob["time_limit_sec"] = max(120, int(prob.get("time_limit_sec", 240) * 0.75))

    elif fmt in ("fill_in_blanks", "speed_coding_sprint"):
        # Replace key expressions (`return ...;` or `<= ...;`) with `/* TODO_BLANK */ ?`
        lines = ref.splitlines()
        blanked_lines = []
        blanks_made = 0
        for line in lines:
            if blanks_made < 2 and ("<=" in line and "<-" not in line):
                lhs = line.split("<=")[0]
                blanked_lines.append(f"{lhs}<= /* TODO_BLANK */ ?;")
                blanks_made += 1
            elif blanks_made < 2 and ("return " in line and "?" in line):
                indent = line[: len(line) - len(line.lstrip())]
                blanked_lines.append(f"{indent}return /* TODO_BLANK */ ?;")
                blanks_made += 1
            else:
                blanked_lines.append(line)
        if blanks_made == 0:
            # Fallback: blank the last return statement
            for i in range(len(blanked_lines) - 1, -1, -1):
                if "return " in blanked_lines[i]:
                    indent = blanked_lines[i][: len(blanked_lines[i]) - len(blanked_lines[i].lstrip())]
                    blanked_lines[i] = f"{indent}return /* TODO_BLANK */ ?;"
                    break

        prob["snippet_template"] = (
            "    // [FILL-IN-THE-BLANKS MODE]: Replace each `/* TODO_BLANK */ ?` with the correct BSV expression!\n"
            + "\n".join(blanked_lines)
        )
        prob["full_template"] = (
            f"module {prob['module_name']}({prob['interface_name']});\n"
            f"{prob['snippet_template']}\n"
            f"endmodule"
        )
        badge = "90s Speed Sprint" if fmt == "speed_coding_sprint" else "Fill-in-Blanks"
        prob["title"] = re.sub(r"^CP #(\d+):", f"CP #\\1 [{badge}]:", prob["title"])
        prob["tags"] = [f"Format: {badge}"] + prob.get("tags", [])
        prob["description"] = (
            "> [!TIP]\n"
            f"> **{badge} (`{fmt}`)**: Most of the BSV module is already written for you in the editor! "
            "Simply replace each `/* TODO_BLANK */ ?` placeholder to complete the circuit.\n\n"
            + prob["description"]
        )
        prob["time_limit_sec"] = 90 if fmt == "speed_coding_sprint" else max(90, int(prob.get("time_limit_sec", 240) * 0.6))

    elif fmt == "reverse_engineer_mystery":
        prob["title"] = re.sub(r"^CP #(\d+):", r"CP #\1 [Mystery RTL]:", prob["title"])
        prob["tags"] = ["Format: Reverse-Engineer"] + prob.get("tags", [])
        prob["description"] = (
            "> [!IMPORTANT]\n"
            "> **Reverse-Engineering Challenge (`reverse_engineer_mystery`)**: Use the architectural diagram, interface signature, "
            "and specification below (plus the Bluesim Golden Waveform trace when you run **Compile & Verify**) to deduce and implement the exact hardware behavior!\n\n"
            + prob["description"]
        )
    elif fmt == "spiral_reinforcement":
        prob["title"] = re.sub(r"^CP #(\d+):", r"CP #\1 [Spiral Reinforce]:", prob["title"])
        prob["tags"] = ["Format: Spiral Reinforce"] + prob.get("tags", [])
        prob["description"] = (
            "> [!NOTE]\n"
            "> **Spiral Track Reinforcement (`spiral_reinforcement`)**: This problem reinforces your Mode 1 Guided Curriculum concepts "
            "with fresh randomized parameters to build muscle memory and hardware intuition.\n\n"
            + prob["description"]
        )
    elif fmt == "verification_monitor":
        prob["tags"] = ["Format: Verification Monitor"] + prob.get("tags", [])
    else:
        prob["tags"] = ["Format: Design from Spec"] + prob.get("tags", [])

    return prob
