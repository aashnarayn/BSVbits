"""
Dynamic Competitive Hardware Programming (CP Arena) Problem Generator for BSVbits.
Procedurally generates fresh, parameterized RTL & BSV problems on the fly across:
  - Priority Encoders & Leading/Trailing-One Detectors (Combinational)
  - Modulo-N / Saturating / Custom-Step Counters (Sequential)
  - Elastic RegSlices & Pipeline Transform Buffers (Sequential)
  - Dynamic Bit-Sequence Detector FSMs with KMP State Tables (Sequential FSM)
  - Binary <-> Gray Code & Parity Converters (Combinational)
  - Multi-Mode Barrel Rotators & Shifters (Combinational)
  - VLSI DSP Saturating Arithmetic & Clamping Units (Combinational)
  - Programmable PWM & Period Timers (Sequential)
  - Custom-Permutation Hardware Arbiters (Combinational/Sequential)
  - Guarded Multiply-Accumulate (MAC) Engines (Sequential)

Every generated problem comes with:
  1. Complete specification + truth/state diagram
  2. Verified Golden Reference BSV Solution on hand (`reference_bsv` & `reference_snippet`)
  3. Cycle-accurate Bluesim Co-Simulation Testbench (`testbench_bsv`)
  4. Progressive Clues (`hints`) for the Smart AI/Semantic Evaluator
"""

from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional

from .curriculum import _make_problem


CP_CATEGORIES: List[Dict[str, str]] = [
    {"id": "all", "name": "All Primitives (Random Mix)"},
    {"id": "priority_encoder", "name": "Priority Encoders & Bit Finders (Comb)"},
    {"id": "counters", "name": "Counters, Timers & PWM (Seq)"},
    {"id": "regslices", "name": "RegSlices, FIFOs & Elastic Stages (Seq)"},
    {"id": "fsms", "name": "Sequence & Protocol FSMs (Seq)"},
    {"id": "datapath", "name": "Barrel Shifters, Gray Code & DSP MAC (Comb/Seq)"},
    {"id": "arbiters", "name": "Arbiters & Crossbar Schedulers (Comb/Seq)"},
]


def generate_cp_problem(
    difficulty: str = "Medium",
    category: str = "all",
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate a fresh, parameterized competitive programming BSV problem.
    All components (spec, golden BSV reference, testbench, hints) are synthesized dynamically.
    """
    if seed is None:
        seed = int(time.time() * 1000) % 1000000 + random.randint(1, 99999)
    rng = random.Random(seed)

    difficulty_norm = difficulty.capitalize() if difficulty.lower() in ("easy", "medium", "hard") else "Medium"

    cat_map = {
        "priority_encoder": ["prio_encoder", "arbiter_perm"],
        "counters": ["modulo_counter", "pwm_timer"],
        "regslices": ["regslice_transform", "mac_engine"],
        "fsms": ["pattern_fsm"],
        "datapath": ["gray_codec", "barrel_rotator", "saturating_alu"],
        "arbiters": ["arbiter_perm", "prio_encoder"],
    }

    if category in cat_map:
        templates = cat_map[category]
    else:
        if difficulty_norm == "Easy":
            templates = ["prio_encoder", "gray_codec", "saturating_alu", "modulo_counter"]
        elif difficulty_norm == "Hard":
            templates = ["pattern_fsm", "regslice_transform", "arbiter_perm", "mac_engine", "barrel_rotator"]
        else:
            templates = [
                "prio_encoder",
                "modulo_counter",
                "regslice_transform",
                "pattern_fsm",
                "gray_codec",
                "barrel_rotator",
                "saturating_alu",
                "pwm_timer",
                "arbiter_perm",
                "mac_engine",
            ]

    chosen = rng.choice(templates)
    dispatch = {
        "prio_encoder": _gen_prio_encoder,
        "modulo_counter": _gen_modulo_counter,
        "regslice_transform": _gen_regslice_transform,
        "pattern_fsm": _gen_pattern_fsm,
        "gray_codec": _gen_gray_codec,
        "barrel_rotator": _gen_barrel_rotator,
        "saturating_alu": _gen_saturating_alu,
        "pwm_timer": _gen_pwm_timer,
        "arbiter_perm": _gen_arbiter_perm,
        "mac_engine": _gen_mac_engine,
    }
    prob = dispatch[chosen](rng, seed, difficulty_norm)
    prob["mode_type"] = "cp"
    prob["seed"] = seed
    prob["cp_category"] = chosen
    prob["time_limit_sec"] = 180 if difficulty_norm == "Easy" else (300 if difficulty_norm == "Medium" else 480)
    prob["points"] = 100 if difficulty_norm == "Easy" else (250 if difficulty_norm == "Medium" else 500)
    return prob


def _gen_prio_encoder(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    msb_first = rng.choice([True, False])
    active_low = rng.choice([False, True]) if difficulty != "Easy" else False
    dir_name = "MSB-First (Highest Index Priority)" if msb_first else "LSB-First (Lowest Index Priority)"
    pol_name = "Active-Low (`0` = active request)" if active_low else "Active-High (`1` = active request)"
    target_bit = "0" if active_low else "1"
    idle_vec = "8'hFF" if active_low else "8'h00"

    indices = list(range(7, -1, -1)) if msb_first else list(range(8))
    cond_lines = []
    for i, idx in enumerate(indices):
        kw = "if" if i == 0 else "else if"
        cond_lines.append(f"        {kw} (req[{idx}] == 1'b{target_bit}) return tagged Valid 3'd{idx};")
    cond_lines.append("        else return tagged Invalid;")
    ref_snip = "    method Maybe#(Bit#(3)) encode(Bit#(8) req);\n" + "\n".join(cond_lines) + "\n    endmethod"

    pid = f"cp_prio8_{seed}"
    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 8-to-3 {('Active-Low ' if active_low else '')}{('MSB' if msb_first else 'LSB')}-Priority Encoder",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "Priority Encoder", "Maybe#(Bit#(3))"],
        description=f"""
### Competitive Specification
Design an **8-to-3 Priority Encoder** (`mkCpPrio8`) with the following parameterized hardware rules:
- **Input**: `Bit#(8) req`
- **Polarity**: **{pol_name}** — a request at bit position `i` is active when `req[i] == 1'b{target_bit}`.
- **Priority Order**: **{dir_name}** — check indices in order `{', '.join(str(x) for x in indices)}`.
- **Output**: `Maybe#(Bit#(3))`
  - Return `tagged Valid idx` for the highest-priority active bit `idx`.
  - If no bit is active (`req == {idle_vec}`), return `tagged Invalid`.
""",
        bsv_vs_verilog="Using `Maybe#(Bit#(3))` packs the valid flag and 3-bit index into a 4-bit result without separate valid/data port skew.",
        diagram=f"req[7:0] ({'active-0' if active_low else 'active-1'}) ---> [ Priority: {indices[0]} > {indices[1]} > ... > {indices[-1]} ] ---> Maybe#(Bit#(3))",
        interface_name="CpPrio8Ifc",
        module_name="mkCpPrio8",
        interface_def="""
interface CpPrio8Ifc;
    method Maybe#(Bit#(3)) encode(Bit#(8) req);
endinterface
""",
        snippet_template="""    method Maybe#(Bit#(3)) encode(Bit#(8) req);
        // === YOUR CODE HERE ===
        return tagged Invalid;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) tv[8] = {8'h00, 8'hFF, 8'h01, 8'h80, 8'h5A, 8'hA5, 8'h3C, 8'hF0};
        Bit#(8) req = tv[cycle];
        Maybe#(Bit#(3)) r = ref_dut.encode(req);
        Maybe#(Bit#(3)) u = user_dut.encode(req);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=req:0x%02h|ref=v:%0d,idx:%0d|user=v:%0d,idx:%0d|match=%0d|note=Prio8", cycle, req, isValid(r)?1:0, fromMaybe(0,r), isValid(u)?1:0, fromMaybe(0,u), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Check bits in priority order `{indices[0]}` to `{indices[-1]}` looking for `req[i] == 1'b{target_bit}`.",
            "You can use an `if / else if` chain or a `for` loop with a `Maybe#(Bit#(3))` accumulator.",
            f"Return `tagged Invalid` when `req == {idle_vec}`.",
        ],
    )


def _gen_modulo_counter(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    modulus = rng.choice([10, 12, 16, 20, 24, 30])
    step_val = rng.choice([1, 2, 3])
    init_val = rng.choice([0, 1, 2])
    wrap_to_init = rng.choice([True, False])
    wrap_target = init_val if wrap_to_init else 0

    pid = f"cp_modcnt_{seed}"
    ref_snip = f"""    Reg#(Bit#(8)) cnt <- mkReg(8'd{init_val});

    method Action tick(Bool en);
        if (en) begin
            if (cnt + 8'd{step_val} >= 8'd{modulus})
                cnt <= 8'd{wrap_target};
            else
                cnt <= cnt + 8'd{step_val};
        end
    endmethod

    method Action clear();
        cnt <= 8'd{init_val};
    endmethod

    method Bit#(8) read();
        return cnt;
    endmethod"""

    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Modulo-{modulus} Step-{step_val} Counter (Reset={init_val})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "Counter", "Modulo Arithmetic"],
        description=f"""
### Competitive Specification
Implement a synchronous **Modulo-{modulus} Step-{step_val} Counter** (`mkCpModCounter`):
- **Reset / Initial Value**: `8'd{init_val}`
- **`method Action tick(Bool en)`**:
  - When `en == True`:
    - If `cnt + 8'd{step_val} >= 8'd{modulus}`, wrap the counter to **`8'd{wrap_target}`**.
    - Otherwise, advance `cnt <= cnt + 8'd{step_val}`.
  - When `en == False`: hold `cnt` unchanged.
- **`method Action clear()`**: Reset `cnt <= 8'd{init_val}`.
- **`method Bit#(8) read()`**: Return current 8-bit `cnt`.
""",
        bsv_vs_verilog="Explicit width-safe comparison `cnt + step >= modulus` prevents off-by-one wrap hazards when `step > 1`.",
        diagram=f"[ cnt (init={init_val}) ] ---> (cnt + {step_val} >= {modulus}) ? {wrap_target} : (cnt + {step_val})",
        interface_name="CpModCounterIfc",
        module_name="mkCpModCounter",
        interface_def="""
interface CpModCounterIfc;
    method Action tick(Bool en);
    method Action clear();
    method Bit#(8) read();
endinterface
""",
        snippet_template=f"""    Reg#(Bit#(8)) cnt <- mkReg(8'd{init_val});

    method Action tick(Bool en);
        // === YOUR CODE HERE ===
    endmethod

    method Action clear();
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) read();
        return cnt;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) r = ref_dut.read();
        Bit#(8) u = user_dut.read();
        if (cycle == 9) begin
            ref_dut.clear();
            user_dut.clear();
        end else begin
            Bool en = (cycle != 4);
            ref_dut.tick(en);
            user_dut.tick(en);
        end
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=cyc:%0d|ref=cnt:%0d|user=cnt:%0d|match=%0d|note=ModCounter", cycle, cycle, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 11) begin
            $display("@SUMMARY total=12 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Initialize `Reg#(Bit#(8)) cnt <- mkReg(8'd{init_val});`.",
            f"In `tick(Bool en)`, when `en` is `True`, check `if (cnt + 8'd{step_val} >= 8'd{modulus}) cnt <= 8'd{wrap_target}; else cnt <= cnt + 8'd{step_val};`.",
            f"In `clear()`, set `cnt <= 8'd{init_val};`.",
        ],
    )


def _gen_regslice_transform(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    xor_mask = rng.choice([0x5A, 0xA5, 0x3C, 0xF0, 0xAA])
    add_const = rng.choice([3, 5, 7, 11, 13])
    swap_nibbles = rng.choice([True, False])

    if swap_nibbles:
        transform_expr = f"(( {x_var := 'x'}[3:0], {x_var}[7:4] ) ^ 8'h{xor_mask:02X})"
        transform_code = f"{{x[3:0], x[7:4]}} ^ 8'h{xor_mask:02X}"
        desc_op = f"swap the upper and lower 4-bit nibbles (`{{x[3:0], x[7:4]}}`) and XOR with `8'h{xor_mask:02X}`"
    else:
        transform_code = f"(x ^ 8'h{xor_mask:02X}) + 8'd{add_const}"
        desc_op = f"XOR `x` with `8'h{xor_mask:02X}` and add `8'd{add_const}` (`(x ^ 8'h{xor_mask:02X}) + 8'd{add_const}`)"

    pid = f"cp_regslice_{seed}"
    ref_snip = f"""    Reg#(Bit#(8)) payload <- mkReg(0);
    Reg#(Bool)    valid   <- mkReg(False);

    method Action enq(Bit#(8) x) if (!valid);
        payload <= {transform_code};
        valid   <= True;
    endmethod

    method Action deq() if (valid);
        valid <= False;
    endmethod

    method Bit#(8) first() if (valid);
        return payload;
    endmethod

    method Bool isValidData();
        return valid;
    endmethod"""

    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Guarded RegSlice Pipeline Stage with Inline Transform",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "RegSlice", "Method Guards"],
        description=f"""
### Competitive Specification
Design a 1-deep **Elastic RegSlice Stage** (`mkCpRegSlice`) with an inline datapath transform:
- State: `valid` (`Bool`, reset to `False`) and `payload` (`Bit#(8)`, reset to `0`).
- **`method Action enq(Bit#(8) x) if (!valid)`**:
  - Guarded by `!valid`.
  - Transforms `x`: **{desc_op}**, stores it into `payload`, and sets `valid <= True`.
- **`method Action deq() if (valid)`**:
  - Guarded by `valid`. Clears `valid <= False`.
- **`method Bit#(8) first() if (valid)`**:
  - Guarded by `valid`. Returns `payload`.
- **`method Bool isValidData()`**:
  - Unconditional value method returning `valid`.
""",
        bsv_vs_verilog="In BSV, attaching `if (!valid)` to `enq` and `if (valid)` to `deq`/`first` synthesizes the complete ready/valid RegSlice handshake automatically.",
        diagram=f"enq(x) [if !valid] ---> [ {transform_code} ] ---> [ payload | valid ] ---> first() / deq() [if valid]",
        interface_name="CpRegSliceIfc",
        module_name="mkCpRegSlice",
        interface_def="""
interface CpRegSliceIfc;
    method Action enq(Bit#(8) x);
    method Action deq();
    method Bit#(8) first();
    method Bool isValidData();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) payload <- mkReg(0);
    Reg#(Bool)    valid   <- mkReg(False);

    method Action enq(Bit#(8) x) if (!valid);
        // === YOUR CODE HERE ===
    endmethod

    method Action deq() if (valid);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) first() if (valid);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bool isValidData();
        return valid;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) din = 8'h12 + (cycle[7:0] * 8'h15);
        Bool rv = ref_dut.isValidData();
        Bool uv = user_dut.isValidData();
        Bit#(8) rf = rv ? ref_dut.first() : 0;
        Bit#(8) uf = uv ? user_dut.first() : 0;
        if (!rv && !uv) begin
            ref_dut.enq(din);
            user_dut.enq(din);
        end else if (rv && uv) begin
            ref_dut.deq();
            user_dut.deq();
        end
        Bool ok = (rv == uv) && (rf == uf);
        $display("@WAVE cycle=%0d|in=din:0x%02h|ref=v:%0d,out:0x%02h|user=v:%0d,out:0x%02h|match=%0d|note=RegSlice", cycle, din, rv?1:0, rf, uv?1:0, uf, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"In `enq(Bit#(8) x) if (!valid)`, compute `payload <= {transform_code};` and set `valid <= True;`.",
            "In `deq() if (valid)`, set `valid <= False;`.",
            "In `first() if (valid)`, `return payload;`.",
        ],
    )


def _gen_pattern_fsm(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    patterns = ["1011", "1101", "1010", "0110", "1001", "0101"]
    pat = rng.choice(patterns)
    overlapping = rng.choice([True, False])

    # Compute exact state transitions for prefix states 0, 1, 2, 3
    trans_table = {}
    for state_len in range(4):
        prefix = pat[:state_len]
        trans_table[state_len] = {}
        for bit in ("0", "1"):
            cand = prefix + bit
            if cand == pat:
                det = 1
                if overlapping:
                    # Longest proper suffix of pat that is a prefix of pat
                    next_s = 0
                    for k in range(3, 0, -1):
                        if pat.endswith(pat[:k]):
                            next_s = k
                            break
                else:
                    next_s = 0
            else:
                det = 0
                next_s = 0
                for k in range(min(3, len(cand)), 0, -1):
                    if cand.endswith(pat[:k]):
                        next_s = k
                        break
            trans_table[state_len][bit] = (next_s, det)

    case_lines = []
    table_md_lines = ["| Current State (Matched Prefix) | Input `din = 0` -> `(Next State, Out)` | Input `din = 1` -> `(Next State, Out)` |", "|---|---|---|"]
    for s in range(4):
        n0, d0 = trans_table[s]["0"]
        n1, d1 = trans_table[s]["1"]
        p_str = f'"{pat[:s]}"' if s > 0 else '"" (Idle)'
        table_md_lines.append(f"| `2'd{s}` ({p_str}) | `2'd{n0}`, out=`{d0}` | `2'd{n1}`, out=`{d1}` |")
        case_lines.append(
            f"            2'd{s}: begin\n"
            f"                state <= (din == 1) ? 2'd{n1} : 2'd{n0};\n"
            f"                det   =  (din == 1) ? 1'b{d1} : 1'b{d0};\n"
            f"            end"
        )

    ref_snip = (
        "    Reg#(Bit#(2)) state <- mkReg(0);\n\n"
        "    method ActionValue#(Bit#(1)) stepBit(Bit#(1) din);\n"
        "        Bit#(1) det = 0;\n"
        "        case (state)\n"
        + "\n".join(case_lines)
        + "\n        endcase\n"
        "        return det;\n"
        "    endmethod"
    )

    # Build a test bitstream that tests pat multiple times
    stream_str = pat + pat[1:] + "0" + pat
    stream_bits = [int(c) for c in stream_str[:12]]
    while len(stream_bits) < 12:
        stream_bits.append(1)
    bits_bsv = ", ".join(str(b) for b in stream_bits)

    pid = f"cp_fsm_{pat}_{seed}"
    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: {'Overlapping' if overlapping else 'Non-Overlapping'} `{pat}` Sequence Detector FSM",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-FSM", "Sequence Detector", "State Machine"],
        description=f"""
### Competitive Specification
Design a serial bit-stream **Sequence Detector FSM** (`mkCpSeqFsm`) that detects the 4-bit target pattern **`{pat}`** in **`{'OVERLAPPING' if overlapping else 'NON-OVERLAPPING'}`** mode!

- Hold state `Reg#(Bit#(2)) state <- mkReg(0);` (or an `enum` / shift-register) initialized to state `0` on reset.
- On each call to `stepBit(Bit#(1) din)`, transition according to the state table below and return `1'b1` when `{pat}` is completed (and `1'b0` otherwise):

{chr(10).join(table_md_lines)}
""",
        bsv_vs_verilog="Whether you implement this using a 4-state FSM (`Reg#(Bit#(2)) state`) or a shift register with bit-counter, our Golden Co-Simulator verifies your exact cycle-by-cycle `stepBit` output!",
        diagram=f"din ---> [ FSM Target='{pat}' ({'Overlapping' if overlapping else 'Non-Overlapping'}) ] ---> stepBit() (1 on match)",
        interface_name="CpSeqFsmIfc",
        module_name="mkCpSeqFsm",
        interface_def="""
interface CpSeqFsmIfc;
    method ActionValue#(Bit#(1)) stepBit(Bit#(1) din);
endinterface
""",
        snippet_template="""    Reg#(Bit#(2)) state <- mkReg(0);

    method ActionValue#(Bit#(1)) stepBit(Bit#(1) din);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body=f"""    rule test;
        Bit#(1) tv[12] = {{{bits_bsv}}};
        Bit#(1) b = tv[cycle];
        Bit#(1) r <- ref_dut.stepBit(b);
        Bit#(1) u <- user_dut.stepBit(b);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=din:%0d|ref=det:%0d|user=det:%0d|match=%0d|note=Pattern {pat}", cycle, b, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 11) begin
            $display("@SUMMARY total=12 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Track how many prefix bits of `{pat}` have been matched (`0`, `1`, `2`, or `3`) in `Reg#(Bit#(2)) state <- mkReg(0);`.",
            "Consult the state transition table in the problem description for each state `2'd0`..`2'd3`.",
            f"In state `2'd3`, when `din == 1'b{pat[3]}`, output `1` and transition to state `2'd{trans_table[3][pat[3]][0]}`!",
        ],
    )


def _gen_gray_codec(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    to_gray = rng.choice([True, False]) if difficulty != "Easy" else True
    if to_gray:
        title_mode = "Binary-to-Gray & Even-Parity Encoder"
        ref_snip = """    method Bit#(8) convert(Bit#(8) x);
        return x ^ (x >> 1);
    endmethod

    method Bit#(1) parity(Bit#(8) x);
        Bit#(1) p = 0;
        for (Integer i = 0; i < 8; i = i + 1) p = p ^ x[i];
        return p;
    endmethod"""
        desc = """
1. `convert(Bit#(8) x)`: Convert 8-bit binary input `x` into **8-bit Gray code**: `x ^ (x >> 1)`.
2. `parity(Bit#(8) x)`: Compute the 1-bit XOR reduction (even parity bit) of all 8 bits of `x` (`x[0] ^ x[1] ^ ... ^ x[7]`).
"""
    else:
        title_mode = "Gray-to-Binary & Even-Parity Decoder"
        ref_snip = """    method Bit#(8) convert(Bit#(8) g);
        Bit#(8) b = 0;
        b[7] = g[7];
        for (Integer i = 6; i >= 0; i = i - 1) begin
            b[i] = b[i+1] ^ g[i];
        end
        return b;
    endmethod

    method Bit#(1) parity(Bit#(8) g);
        Bit#(1) p = 0;
        for (Integer i = 0; i < 8; i = i + 1) p = p ^ g[i];
        return p;
    endmethod"""
        desc = """
1. `convert(Bit#(8) g)`: Convert 8-bit **Gray code** `g` back into **8-bit Binary** `b`, where `b[7] = g[7]` and for `i = 6` down to `0`, `b[i] = b[i+1] ^ g[i]` (or `g ^ (g >> 1) ^ (g >> 2) ^ (g >> 3) ^ (g >> 4) ^ (g >> 5) ^ (g >> 6) ^ (g >> 7)`).
2. `parity(Bit#(8) g)`: Compute the 1-bit XOR reduction of all 8 bits of `g`.
"""

    pid = f"cp_gray_{seed}"
    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 8-Bit {title_mode}",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "Gray Code", "CDC / VLSI"],
        description=f"### Competitive Specification\nGray codes are essential in VLSI asynchronous FIFO pointers (Clock Domain Crossing) because only 1 bit changes between adjacent counts.\n\n{desc}",
        bsv_vs_verilog="Static `for` loops in BSV make N-bit XOR trees and Gray-to-Binary prefix cascades concise and bug-free.",
        diagram="x[7:0] ---> [ Gray / Binary Codec ] ---> convert[7:0] & parity[0]",
        interface_name="CpGrayCodecIfc",
        module_name="mkCpGrayCodec",
        interface_def="""
interface CpGrayCodecIfc;
    method Bit#(8) convert(Bit#(8) x);
    method Bit#(1) parity(Bit#(8) x);
endinterface
""",
        snippet_template="""    method Bit#(8) convert(Bit#(8) x);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bit#(1) parity(Bit#(8) x);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) tv[8] = {8'h00, 8'h01, 8'h03, 8'h07, 8'h5A, 8'hA5, 8'hDB, 8'hFF};
        Bit#(8) x = tv[cycle];
        Bit#(8) rc = ref_dut.convert(x);
        Bit#(8) uc = user_dut.convert(x);
        Bit#(1) rp = ref_dut.parity(x);
        Bit#(1) up = user_dut.parity(x);
        Bool ok = (rc == uc) && (rp == up);
        $display("@WAVE cycle=%0d|in=x:0x%02h|ref=conv:0x%02h,par:%0d|user=conv:0x%02h,par:%0d|match=%0d|note=Gray codec", cycle, x, rc, rp, uc, up, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "For Binary-to-Gray, use `return x ^ (x >> 1);`. For Gray-to-Binary, set `b[7] = x[7]` and loop `for (Integer i = 6; i >= 0; i = i - 1) b[i] = b[i+1] ^ x[i];`.",
            "For `parity(x)`, XOR all 8 bits together in a loop or using `^x`.",
            "Both loop-based and shift-XOR tree implementations are accepted!",
        ],
    )


def _gen_barrel_rotator(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    rotate_left = rng.choice([True, False])
    dir_str = "Left" if rotate_left else "Right"
    if rotate_left:
        expr = "(x << shamt) | (x >> inv_sh)"
    else:
        expr = "(x >> shamt) | (x << inv_sh)"

    pid = f"cp_barrel_{seed}"
    ref_snip = f"""    method Bit#(8) rotate(Bit#(8) x, Bit#(3) shamt);
        Bit#(4) inv_sh = 4'd8 - zeroExtend(shamt);
        return (shamt == 0) ? x : ({expr});
    endmethod"""

    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: 8-Bit Combinational Barrel Rotator ({dir_str})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "Barrel Shifter", "Bit Manipulation"],
        description=f"""
### Competitive Specification
Implement an 8-bit combinational **Barrel Rotator ({dir_str})** (`mkCpBarrel`):
- `method Bit#(8) rotate(Bit#(8) x, Bit#(3) shamt)`:
  - Rotates the 8 bits of `x` **{dir_str.lower()}** by `shamt` positions (`0` to `7`).
  - Bits shifted out of one end wrap around to the other end!
""",
        bsv_vs_verilog="An 8-bit barrel rotator synthesizes to three layers of 2-to-1 multiplexers controlled by `shamt[0]`, `shamt[1]`, and `shamt[2]`.",
        diagram=f"x[7:0], shamt[2:0] ---> [ 8-Bit Rotate {dir_str} ] ---> out[7:0]",
        interface_name="CpBarrelIfc",
        module_name="mkCpBarrel",
        interface_def="""
interface CpBarrelIfc;
    method Bit#(8) rotate(Bit#(8) x, Bit#(3) shamt);
endinterface
""",
        snippet_template="""    method Bit#(8) rotate(Bit#(8) x, Bit#(3) shamt);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) x = 8'hA3 + (cycle[7:0] * 8'h11);
        Bit#(3) shamt = truncate(cycle);
        Bit#(8) r = ref_dut.rotate(x, shamt);
        Bit#(8) u = user_dut.rotate(x, shamt);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=x:0x%02h,sh:%0d|ref=out:0x%02h|user=out:0x%02h|match=%0d|note=Rotate %0d", cycle, x, shamt, r, u, ok ? 1 : 0, shamt);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Declare `Bit#(4) inv_sh = 4'd8 - zeroExtend(shamt);` and when `shamt == 0` return `x`, else `{expr}`.",
            "Alternatively, use a `case (shamt)` with concatenations `{x[6:0], x[7]}`, `{x[5:0], x[7:6]}`, etc.!",
            "Explicitly typing `Bit#(4) inv_sh = 4'd8 - zeroExtend(shamt);` tells `bsc` the exact target width of `zeroExtend`.",
        ],
    )


def _gen_saturating_alu(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    clamp_max = rng.choice([200, 240, 250, 255])
    pid = f"cp_satalu_{seed}"
    ref_snip = f"""    method Bit#(8) satAdd(Bit#(8) a, Bit#(8) b);
        Bit#(9) sum = zeroExtend(a) + zeroExtend(b);
        return (sum > 9'd{clamp_max}) ? 8'd{clamp_max} : truncate(sum);
    endmethod

    method Bit#(8) satSub(Bit#(8) a, Bit#(8) b);
        return (a > b) ? (a - b) : 8'd0;
    endmethod"""

    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Saturating Arithmetic Unit (Clamp Max = {clamp_max})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "Saturating ALU", "DSP / VLSI"],
        description=f"""
### Competitive Specification
In DSP, audio, and neural-network hardware, arithmetic overflow must **saturate (clamp)** instead of wrapping around modulo 256!

Implement `mkCpSatAlu`:
1. `satAdd(Bit#(8) a, Bit#(8) b)`: Compute `a + b` using 9-bit precision (`zeroExtend(a) + zeroExtend(b)`). If the sum exceeds **`{clamp_max}`**, return **`8'd{clamp_max}`**; otherwise return the 8-bit sum.
2. `satSub(Bit#(8) a, Bit#(8) b)`: If `a > b`, return `a - b`; otherwise clamp at **`8'd0`**.
""",
        bsv_vs_verilog="Using `Bit#(9) sum = zeroExtend(a) + zeroExtend(b);` cleanly captures the carry-out bit in `sum[8]` without implicit width rules.",
        diagram=f"a[7:0], b[7:0] ---> [ 9-bit + ] ---> (> {clamp_max} ? {clamp_max} : sum[7:0])",
        interface_name="CpSatAluIfc",
        module_name="mkCpSatAlu",
        interface_def="""
interface CpSatAluIfc;
    method Bit#(8) satAdd(Bit#(8) a, Bit#(8) b);
    method Bit#(8) satSub(Bit#(8) a, Bit#(8) b);
endinterface
""",
        snippet_template="""    method Bit#(8) satAdd(Bit#(8) a, Bit#(8) b);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bit#(8) satSub(Bit#(8) a, Bit#(8) b);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(8) va[8] = {8'd10, 8'd150, 8'd200, 8'd250, 8'd50, 8'd100, 8'd0,   8'd255};
        Bit#(8) vb[8] = {8'd20, 8'd100, 8'd80,  8'd20,  8'd90, 8'd100, 8'd255, 8'd10};
        Bit#(8) a = va[cycle];
        Bit#(8) b = vb[cycle];
        Bit#(8) r1 = ref_dut.satAdd(a, b);
        Bit#(8) u1 = user_dut.satAdd(a, b);
        Bit#(8) r2 = ref_dut.satSub(a, b);
        Bit#(8) u2 = user_dut.satSub(a, b);
        Bool ok = (r1 == u1) && (r2 == u2);
        $display("@WAVE cycle=%0d|in=a:%0d,b:%0d|ref=add:%0d,sub:%0d|user=add:%0d,sub:%0d|match=%0d|note=SatALU", cycle, a, b, r1, r2, u1, u2, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Compute `Bit#(9) sum = zeroExtend(a) + zeroExtend(b);` so `a + b` cannot overflow 8 bits.",
            f"Return `(sum > 9'd{clamp_max}) ? 8'd{clamp_max} : truncate(sum);` in `satAdd`.",
            "In `satSub`, return `(a > b) ? (a - b) : 8'd0;`.",
        ],
    )


def _gen_pwm_timer(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    period = rng.choice([6, 8, 10])
    default_duty = period // 2
    pid = f"cp_pwm_{seed}"
    ref_snip = f"""    Reg#(Bit#(8)) cnt  <- mkReg(0);
    Reg#(Bit#(8)) duty <- mkReg(8'd{default_duty});

    rule tick;
        cnt <= (cnt == 8'd{period - 1}) ? 0 : (cnt + 1);
    endrule

    method Action setDuty(Bit#(8) d);
        duty <= d;
    endmethod

    method Bit#(1) pwmOut();
        return (cnt < duty) ? 1'b1 : 1'b0;
    endmethod"""

    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Period-{period} Programmable PWM Generator",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "PWM", "Timer"],
        description=f"""
### Competitive Specification
Design a **Pulse-Width Modulation (PWM) Generator** (`mkCpPwm`) with period **`{period}` cycles**:
- Internal registers:
  - `cnt` (`Reg#(Bit#(8))`, reset to `0`): increments every clock cycle in an autonomous `rule`, wrapping from `{period - 1}` back to `0` (`0, 1, ..., {period - 1}, 0, ...`).
  - `duty` (`Reg#(Bit#(8))`, reset to **`8'd{default_duty}`**).
- `method Action setDuty(Bit#(8) d)`: Updates `duty <= d`.
- `method Bit#(1) pwmOut()`: Outputs `1'b1` when `cnt < duty`, and `1'b0` otherwise.
""",
        bsv_vs_verilog="Separating the autonomous timebase `rule tick` from the `setDuty` configuration method and `pwmOut` comparator keeps PWM hardware modular.",
        diagram=f"[ cnt: 0..{period - 1} ] ---> (cnt < duty) ---> pwmOut() (1'b1 or 1'b0)",
        interface_name="CpPwmIfc",
        module_name="mkCpPwm",
        interface_def="""
interface CpPwmIfc;
    method Action setDuty(Bit#(8) d);
    method Bit#(1) pwmOut();
endinterface
""",
        snippet_template=f"""    Reg#(Bit#(8)) cnt  <- mkReg(0);
    Reg#(Bit#(8)) duty <- mkReg(8'd{default_duty});

    // Write rule tick, method setDuty(d), and method pwmOut()
    // === YOUR CODE HERE ===
    method Action setDuty(Bit#(8) d);
    endmethod

    method Bit#(1) pwmOut();
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body=f"""    rule test;
        if (cycle == {period}) begin
            ref_dut.setDuty(8'd2);
            user_dut.setDuty(8'd2);
        end
        Bit#(1) r = ref_dut.pwmOut();
        Bit#(1) u = user_dut.pwmOut();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=cyc:%0d|ref=pwm:%0d|user=pwm:%0d|match=%0d|note=PWM period {period}", cycle, cycle, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 11) begin
            $display("@SUMMARY total=12 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"In `rule tick;`, update `cnt <= (cnt == 8'd{period - 1}) ? 0 : (cnt + 1);`.",
            "In `setDuty(Bit#(8) d)`, write `duty <= d;`.",
            "In `pwmOut()`, return `(cnt < duty) ? 1'b1 : 1'b0;`.",
        ],
    )


def _gen_arbiter_perm(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    order = [0, 1, 2, 3]
    rng.shuffle(order)
    order_str = " > ".join(f"Port {i}" for i in order)

    cond_lines = []
    for idx, p in enumerate(order):
        kw = "if" if idx == 0 else "else if"
        cond_lines.append(f"        {kw} (req[{p}] == 1) return 4'b{1 << p:04b};")
    cond_lines.append("        else return 4'b0000;")
    ref_snip = (
        "    method Bit#(4) grant(Bit#(4) req, Bit#(4) mask);\n"
        "        Bit#(4) eff = req & ~mask;\n"
        + "\n".join(c.replace("req[", "eff[") for c in cond_lines)
        + "\n    endmethod"
    )

    pid = f"cp_arb_{seed}"
    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Masked 4-Port Custom-Priority Arbiter ({order[0]}>{order[1]}>{order[2]}>{order[3]})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Combinational", "Arbiter", "One-Hot Grant"],
        description=f"""
### Competitive Specification
Design a 4-port **Masked Priority Arbiter** (`mkCpArbiter`):
- **Inputs**: `Bit#(4) req` (active-high request vector) and `Bit#(4) mask` (where `mask[i] == 1` disables/masks out port `i`).
- **Effective Requests**: `Bit#(4) eff = req & ~mask;`
- **Priority Order**: **{order_str}**
- **Output**: Return a **4-bit One-Hot Grant** (`Bit#(4)`) where `grant[winner] = 1` for the highest-priority unmasked requesting port, or `4'b0000` if `eff == 0`.
""",
        bsv_vs_verilog="Combining bit-masking `req & ~mask` with priority selection is a core building block of QoS hardware schedulers.",
        diagram=f"req & ~mask ---> [ Priority: {order_str} ] ---> grant[3:0] (One-Hot)",
        interface_name="CpArbiterIfc",
        module_name="mkCpArbiter",
        interface_def="""
interface CpArbiterIfc;
    method Bit#(4) grant(Bit#(4) req, Bit#(4) mask);
endinterface
""",
        snippet_template="""    method Bit#(4) grant(Bit#(4) req, Bit#(4) mask);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(4) vreq[8]  = {4'b1111, 4'b1111, 4'b1010, 4'b0101, 4'b1100, 4'b0011, 4'b1111, 4'b0000};
        Bit#(4) vmask[8] = {4'b0000, 4'b0101, 4'b0010, 4'b0001, 4'b0100, 4'b0000, 4'b1111, 4'b0000};
        Bit#(4) req = vreq[cycle];
        Bit#(4) msk = vmask[cycle];
        Bit#(4) r = ref_dut.grant(req, msk);
        Bit#(4) u = user_dut.grant(req, msk);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=req:0x%01h,msk:0x%01h|ref=gnt:0x%01h|user=gnt:0x%01h|match=%0d|note=Arbiter", cycle, req, msk, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "First compute the unmasked requests: `Bit#(4) eff = req & ~mask;`.",
            f"Check ports in exact order: `eff[{order[0]}]`, `eff[{order[1]}]`, `eff[{order[2]}]`, `eff[{order[3]}]`. ",
            f"Return `4'b{1 << order[0]:04b}` if `eff[{order[0]}] == 1`, etc., or `4'b0000` if none are active.",
        ],
    )


def _gen_mac_engine(rng: random.Random, seed: int, difficulty: str) -> Dict[str, Any]:
    weight = rng.choice([2, 3, 4, 5])
    init_acc = rng.choice([0, 10, 16])
    pid = f"cp_mac_{seed}"
    ref_snip = f"""    Reg#(Bit#(16)) acc <- mkReg(16'd{init_acc});

    method Action mac(Bit#(8) a, Bit#(8) b, Bool sub_mode);
        Bit#(16) prod = zeroExtend(a) * zeroExtend(b) * 16'd{weight};
        acc <= sub_mode ? (acc - prod) : (acc + prod);
    endmethod

    method Action resetAcc();
        acc <= 16'd{init_acc};
    endmethod

    method Bit#(16) readAcc();
        return acc;
    endmethod"""

    return _make_problem(
        pid=pid,
        number=seed % 1000,
        title=f"CP #{seed % 1000}: Scaled Multiply-Accumulate (MAC) Unit (Weight={weight}, Init={init_acc})",
        track_id="cp_arena",
        track_title="Competitive Hardware Arena",
        difficulty=difficulty,
        tags=["CP-Sequential", "MAC / DSP", "Datapath"],
        description=f"""
### Competitive Specification
Design a 16-bit **Scaled Multiply-Accumulate (MAC) Engine** (`mkCpMac`):
- State: `Reg#(Bit#(16)) acc <- mkReg(16'd{init_acc});`
- **`method Action mac(Bit#(8) a, Bit#(8) b, Bool sub_mode)`**:
  - Compute scaled product `Bit#(16) prod = zeroExtend(a) * zeroExtend(b) * 16'd{weight};`
  - If `sub_mode == False`, accumulate `acc <= acc + prod`.
  - If `sub_mode == True`, subtract `acc <= acc - prod`.
- **`method Action resetAcc()`**: Reset `acc <= 16'd{init_acc}`.
- **`method Bit#(16) readAcc()`**: Return current 16-bit `acc`.
""",
        bsv_vs_verilog="Zero-extending 8-bit operands `a` and `b` to 16 bits before multiplication ensures full 16-bit product precision in BSV.",
        diagram=f"a[7:0] * b[7:0] * {weight} ---> [ +/- acc (init={init_acc}) ] ---> readAcc()[15:0]",
        interface_name="CpMacIfc",
        module_name="mkCpMac",
        interface_def="""
interface CpMacIfc;
    method Action mac(Bit#(8) a, Bit#(8) b, Bool sub_mode);
    method Action resetAcc();
    method Bit#(16) readAcc();
endinterface
""",
        snippet_template=f"""    Reg#(Bit#(16)) acc <- mkReg(16'd{init_acc});

    method Action mac(Bit#(8) a, Bit#(8) b, Bool sub_mode);
        // === YOUR CODE HERE ===
    endmethod

    method Action resetAcc();
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(16) readAcc();
        return acc;
    endmethod""",
        reference_snippet=ref_snip,
        testbench_body="""    rule test;
        Bit#(16) r = ref_dut.readAcc();
        Bit#(16) u = user_dut.readAcc();
        Bit#(8) a = 8'd2 + truncate(cycle);
        Bit#(8) b = 8'd3 + truncate(cycle * 2);
        Bool sub_m = (cycle == 3 || cycle == 5);
        if (cycle == 6) begin
            ref_dut.resetAcc();
            user_dut.resetAcc();
        end else begin
            ref_dut.mac(a, b, sub_m);
            user_dut.mac(a, b, sub_m);
        end
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=a:%0d,b:%0d,sub:%0d|ref=acc:%0d|user=acc:%0d|match=%0d|note=MAC step", cycle, a, b, sub_m?1:0, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            f"Compute `Bit#(16) prod = zeroExtend(a) * zeroExtend(b) * 16'd{weight};`.",
            "Update `acc <= sub_mode ? (acc - prod) : (acc + prod);`.",
            f"In `resetAcc()`, set `acc <= 16'd{init_acc};`.",
        ],
    )
