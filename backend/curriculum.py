"""
Comprehensive Guided BSV Progression Curriculum (32 Problems across 6 Tracks).
Inspired by:
  - BSV by Example (R. S. Nikhil & K. R. Czeck)
  - Bluespec SystemVerilog Reference Manual & User Guide
  - HDLBits (01xz.net) Learn-by-Programming Progression
  - MIT 6.004 / 6.175 / 6.375 Constructive Computer Architecture
  - NPTEL Digital Circuits & Computer Architecture / GeeksforGeeks RTL Design
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


def _make_problem(
    pid: str,
    number: int,
    title: str,
    track_id: str,
    track_title: str,
    difficulty: str,
    tags: List[str],
    description: str,
    bsv_vs_verilog: str,
    diagram: str,
    interface_name: str,
    module_name: str,
    interface_def: str,
    snippet_template: str,
    reference_snippet: str,
    testbench_body: str,
    hints: List[str],
    package_imports: str = "import Vector::*; import FIFOF::*; import Ehr::*; import StmtFSM::*;",
    custom_harness_wrapper: Optional[str] = None,
    custom_ref_bsv: Optional[str] = None,
) -> Dict[str, Any]:
    """Construct a complete, self-contained curriculum problem dictionary."""
    if custom_harness_wrapper:
        harness_wrapper = custom_harness_wrapper
    else:
        harness_wrapper = (
            "package UserSolution;\n"
            "import ProblemTypes::*;\n"
            f"{package_imports}\n\n"
            f"module {module_name}({interface_name});\n"
            "{{USER_SNIPPET}}\n"
            "endmodule\n\n"
            "endpackage: UserSolution\n"
        )

    full_template = (
        f"module {module_name}({interface_name});\n"
        f"{snippet_template}\n"
        f"endmodule"
    )

    if custom_ref_bsv:
        reference_bsv = custom_ref_bsv
    else:
        reference_bsv = (
            "package RefSolution;\n"
            "import ProblemTypes::*;\n"
            f"{package_imports}\n\n"
            f"module {module_name}({interface_name});\n"
            f"{reference_snippet}\n"
            "endmodule\n\n"
            "endpackage: RefSolution\n"
        )

    testbench_bsv = (
        "package Testbench;\n"
        "import ProblemTypes::*;\n"
        f"{package_imports}\n"
        "import RefSolution::*;\n"
        "import UserSolution::*;\n\n"
        "(* synthesize *)\n"
        "module mkTestbench(Empty);\n"
        f"    {interface_name} ref_dut <- RefSolution::{module_name}();\n"
        f"    {interface_name} user_dut <- UserSolution::{module_name}();\n"
        "    Reg#(Bit#(32)) cycle <- mkReg(0);\n"
        "    Reg#(Bit#(32)) passed_cnt <- mkReg(0);\n"
        "    Reg#(Bit#(32)) total_cnt <- mkReg(0);\n\n"
        f"{testbench_body}\n"
        "endmodule\n"
        "endpackage: Testbench\n"
    )

    return {
        "id": pid,
        "number": number,
        "title": title,
        "track_id": track_id,
        "track_title": track_title,
        "difficulty": difficulty,
        "tags": tags,
        "description": description.strip(),
        "bsv_vs_verilog": bsv_vs_verilog.strip(),
        "diagram": diagram.strip(),
        "package_imports": package_imports,
        "interface_name": interface_name,
        "module_name": module_name,
        "interface_def": interface_def.strip(),
        "snippet_template": snippet_template.strip("\n"),
        "full_template": full_template.strip("\n"),
        "reference_snippet": reference_snippet.strip("\n"),
        "reference_bsv": reference_bsv,
        "harness_wrapper": harness_wrapper,
        "testbench_bsv": testbench_bsv,
        "hints": hints,
        "mode_type": "curriculum",
    }


CURRICULUM_TRACKS: List[Dict[str, str]] = [
    {
        "id": "track1_combinational",
        "title": "1. BSV Basics & Combinational Logic",
        "subtitle": "Wires, Value Methods, Logic Gates, Multiplexers, Bit Slicing & Adders",
    },
    {
        "id": "track2_types",
        "title": "2. Strong Types, Enums, Structs & Vectors",
        "subtitle": "Type-safe Hardware with Enums, Structs, Maybe#(t) Tagged Unions & Vectors",
    },
    {
        "id": "track3_sequential",
        "title": "3. Sequential Circuits, Registers & Rules",
        "subtitle": "D Flip-Flops (mkReg), Atomic Rules, Counters, LFSRs, Edge Detectors & Euclid's GCD",
    },
    {
        "id": "track4_concurrency",
        "title": "4. Concurrency, Scheduling, Ehr & FIFOs",
        "subtitle": "Rule Conflicts, RWire, Ephemeral History Registers (Ehr), and Elastic Pipelines",
    },
    {
        "id": "track5_fsms",
        "title": "5. Finite State Machines & StmtFSM",
        "subtitle": "Sequence Detectors, Traffic Controllers, UART Serial Framing & Microcoded StmtFSM",
    },
    {
        "id": "track6_architecture",
        "title": "6. RTL Protocols & Computer Architecture",
        "subtitle": "Round-Robin Arbiters, Credit Flow Control, AXI-Lite, Multiply, Cache & Mini RISC-V",
    },
]


def _build_all_problems() -> List[Dict[str, Any]]:
    problems: List[Dict[str, Any]] = []

    # =========================================================================
    # TRACK 1: BSV BASICS & COMBINATIONAL LOGIC
    # =========================================================================
    problems.append(_make_problem(
        pid="01_wire_zero",
        number=1,
        title="01. Constant Zero Output (Your First BSV Method)",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Syntax", "Value Method", "Bit#(1)"],
        description="""
Welcome to **BSVbits**! Just like HDLBits starts with building a wire that outputs `0`, we start by writing a **Value Method** in Bluespec SystemVerilog (BSV).

In BSV, hardware modules don't expose raw unwrapped input/output ports like Verilog's `output wire out`. Instead, every module implements an **Interface** made of **Methods**:
- A **Value Method** computes and returns a value combinationally (with zero clock latency):
```bsv
method Bit#(1) getZero();
    return 0;
endmethod
```
### Task
Complete the `getZero` method inside `mkWireZero` so that it always returns `1'b0` (or simply `0`).
""",
        bsv_vs_verilog="""
**Verilog**: `assign out = 1'b0;` inside a port list `module top(output out);`
**BSV**: Ports are grouped into strongly-typed `interface` methods. A value method `method Bit#(1) getZero()` synthesizes directly to an output wire tied to `1'b0`!
""",
        diagram="""
   +------------------+
   |    mkWireZero    |
   |                  |
   |        getZero() |---> 1'b0
   +------------------+
""",
        interface_name="WireZeroIfc",
        module_name="mkWireZero",
        interface_def="""
interface WireZeroIfc;
    method Bit#(1) getZero();
endinterface
""",
        snippet_template="""    // Write a value method getZero() that returns 0
    method Bit#(1) getZero();
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(1) getZero();
        return 0;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(1) r = ref_dut.getZero();
        Bit#(1) u = user_dut.getZero();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=none:0|ref=getZero:%0d|user=getZero:%0d|match=%0d|note=Constant zero check", cycle, r, u, ok ? 1 : 0);
        $display("@SUMMARY total=1 passed=%0d", ok ? 1 : 0);
        $finish(0);
    endrule""",
        hints=[
            "Replace `return ?;` with `return 0;` or `return 1'b0;`.",
            "In BSV, `Bit#(1)` is a 1-bit vector. Integer literals like `0` or sized literals like `1'b0` both work.",
            "Full method: `method Bit#(1) getZero(); return 0; endmethod`",
        ],
    ))

    problems.append(_make_problem(
        pid="02_wire_pass",
        number=2,
        title="02. Wire Pass-Through & Bitwise Inversion",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Combinational", "Value Method", "Bit#(8)"],
        description="""
A value method in BSV can also take arguments! Each argument synthesizes to an input port wire, and the return value synthesizes to an output port wire.

For example, a combinational method that takes an 8-bit input `x` and returns `x`:
```bsv
method Bit#(8) passThrough(Bit#(8) x);
    return x;
endmethod
```
To invert all bits (bitwise NOT), BSV uses the `~` operator, just like Verilog and C: `~x`.

### Task
Implement two combinational value methods in `mkWirePass`:
1. `pass(Bit#(8) x)` — returns `x` unchanged.
2. `invert(Bit#(8) x)` — returns the bitwise NOT (`~x`) of `x`.
""",
        bsv_vs_verilog="""
**Verilog**: Separate input/output ports `input [7:0] x, output [7:0] y`.
**BSV**: `method Bit#(8) invert(Bit#(8) x); return ~x; endmethod` — BSV automatically generates ports `invert_x[7:0]` (input) and `invert[7:0]` (output).
""",
        diagram="""
   x[7:0] ----+------------------> pass(x)   = x[7:0]
              |
              +---> [ ~ NOT ] ---> invert(x) = ~x[7:0]
""",
        interface_name="WirePassIfc",
        module_name="mkWirePass",
        interface_def="""
interface WirePassIfc;
    method Bit#(8) pass(Bit#(8) x);
    method Bit#(8) invert(Bit#(8) x);
endinterface
""",
        snippet_template="""    method Bit#(8) pass(Bit#(8) x);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bit#(8) invert(Bit#(8) x);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(8) pass(Bit#(8) x);
        return x;
    endmethod

    method Bit#(8) invert(Bit#(8) x);
        return ~x;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) tv[6] = {8'h00, 8'hFF, 8'hA5, 8'h5A, 8'h0F, 8'h3C};
        Bit#(8) x = tv[cycle];
        Bit#(8) rp = ref_dut.pass(x);
        Bit#(8) ri = ref_dut.invert(x);
        Bit#(8) up = user_dut.pass(x);
        Bit#(8) ui = user_dut.invert(x);
        Bool ok = (rp == up) && (ri == ui);
        $display("@WAVE cycle=%0d|in=x:0x%02h|ref=pass:0x%02h,inv:0x%02h|user=pass:0x%02h,inv:0x%02h|match=%0d|note=Wire & NOT", cycle, x, rp, ri, up, ui, ok ? 1 : 0);
        let next_pass = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= next_pass;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", next_pass);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `pass(Bit#(8) x)`, simply `return x;`.",
            "In `invert(Bit#(8) x)`, use the bitwise complement operator `~`: `return ~x;`.",
            "Do not use `!` for bitwise inversion of `Bit#(8)` — `!` is for `Bool`, while `~` is for `Bit#(n)`.",
        ],
    ))

    problems.append(_make_problem(
        pid="03_gates_basic",
        number=3,
        title="03. Four Basic Logic Gates (AND, OR, XOR, NAND)",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Logic Gates", "Bitwise Operators", "Combinational"],
        description="""
Digital circuits are built from fundamental logic gates. In BSV, bitwise operators act on every bit position of `Bit#(n)` values in parallel:
- **AND**: `a & b`
- **OR**: `a | b`
- **XOR**: `a ^ b`
- **NAND**: `~(a & b)`

### Task
Implement the four 4-bit combinational gate methods inside `mkGatesBasic`:
1. `gateAnd(Bit#(4) a, Bit#(4) b)` -> `a & b`
2. `gateOr(Bit#(4) a, Bit#(4) b)` -> `a | b`
3. `gateXor(Bit#(4) a, Bit#(4) b)` -> `a ^ b`
4. `gateNand(Bit#(4) a, Bit#(4) b)` -> `~(a & b)`
""",
        bsv_vs_verilog="""
**BSV vs Verilog**: The bitwise operators `&`, `|`, `^`, `~` are identical to Verilog! However, BSV strictly prevents accidental implicit width truncations or mixing `Bool` (`&&`, `||`, `!`) with `Bit#(n)` (`&`, `|`, `~`).
""",
        diagram="""
   a[3:0], b[3:0] ---> [  &  ] ---> gateAnd
                  ---> [  |  ] ---> gateOr
                  ---> [  ^  ] ---> gateXor
                  ---> [ ~&  ] ---> gateNand
""",
        interface_name="GatesBasicIfc",
        module_name="mkGatesBasic",
        interface_def="""
interface GatesBasicIfc;
    method Bit#(4) gateAnd(Bit#(4) a, Bit#(4) b);
    method Bit#(4) gateOr(Bit#(4) a, Bit#(4) b);
    method Bit#(4) gateXor(Bit#(4) a, Bit#(4) b);
    method Bit#(4) gateNand(Bit#(4) a, Bit#(4) b);
endinterface
""",
        snippet_template="""    method Bit#(4) gateAnd(Bit#(4) a, Bit#(4) b);
        return ?;
    endmethod

    method Bit#(4) gateOr(Bit#(4) a, Bit#(4) b);
        return ?;
    endmethod

    method Bit#(4) gateXor(Bit#(4) a, Bit#(4) b);
        return ?;
    endmethod

    method Bit#(4) gateNand(Bit#(4) a, Bit#(4) b);
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(4) gateAnd(Bit#(4) a, Bit#(4) b);
        return a & b;
    endmethod

    method Bit#(4) gateOr(Bit#(4) a, Bit#(4) b);
        return a | b;
    endmethod

    method Bit#(4) gateXor(Bit#(4) a, Bit#(4) b);
        return a ^ b;
    endmethod

    method Bit#(4) gateNand(Bit#(4) a, Bit#(4) b);
        return ~(a & b);
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) va[8] = {4'h0, 4'hF, 4'hA, 4'h5, 4'h3, 4'hC, 4'h9, 4'h6};
        Bit#(4) vb[8] = {4'h0, 4'hF, 4'h5, 4'h5, 4'h6, 4'hA, 4'h3, 4'hF};
        Bit#(4) a = va[cycle];
        Bit#(4) b = vb[cycle];
        Bit#(4) r1 = ref_dut.gateAnd(a, b);
        Bit#(4) r2 = ref_dut.gateOr(a, b);
        Bit#(4) r3 = ref_dut.gateXor(a, b);
        Bit#(4) r4 = ref_dut.gateNand(a, b);
        Bit#(4) u1 = user_dut.gateAnd(a, b);
        Bit#(4) u2 = user_dut.gateOr(a, b);
        Bit#(4) u3 = user_dut.gateXor(a, b);
        Bit#(4) u4 = user_dut.gateNand(a, b);
        Bool ok = (r1 == u1) && (r2 == u2) && (r3 == u3) && (r4 == u4);
        $display("@WAVE cycle=%0d|in=a:0x%01h,b:0x%01h|ref=and:0x%01h,or:0x%01h,xor:0x%01h,nand:0x%01h|user=and:0x%01h,or:0x%01h,xor:0x%01h,nand:0x%01h|match=%0d|note=Gates", cycle, a, r1, r2, r3, r4, u1, u2, u3, u4, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use `a & b` for AND, `a | b` for OR, `a ^ b` for XOR.",
            "For NAND, invert the result of AND using parentheses: `~(a & b)`.",
            "Remember every method ends with `endmethod` and every statement ends with `;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="04_mux_4to1",
        number=4,
        title="04. 4-to-1 Multiplexer (Case & Conditional Logic)",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Multiplexer", "case", "Combinational"],
        description="""
A **Multiplexer (Mux)** selects one of several input signals based on a `sel` control signal.
In BSV, you can write a 4-to-1 mux using a `case` statement:
```bsv
case (sel)
    2'b00: return d0;
    2'b01: return d1;
    2'b10: return d2;
    default: return d3;
endcase
```
Or you can use nested ternary expressions `(sel == 0) ? d0 : ...` or `if / else if / else`.

### Task
Implement `mux4(Bit#(2) sel, Bit#(8) d0, Bit#(8) d1, Bit#(8) d2, Bit#(8) d3)` returning:
- `d0` when `sel == 2'd0`
- `d1` when `sel == 2'd1`
- `d2` when `sel == 2'd2`
- `d3` when `sel == 2'd3`
""",
        bsv_vs_verilog="""
**Verilog**: Requires `always @(*)` and declaring the output as `reg [7:0] out` just to use `case(sel)`!
**BSV**: No `always @(*)` or fake `reg` needed! You can use `case`, `if-else`, or local variables directly inside any combinational `method` or `function`.
""",
        diagram="""
   d0 [7:0] --->|00    |
   d1 [7:0] --->|01    |
   d2 [7:0] --->|10 MUX|---> out [7:0]
   d3 [7:0] --->|11    |
                  ^
                  | sel [1:0]
""",
        interface_name="Mux4Ifc",
        module_name="mkMux4",
        interface_def="""
interface Mux4Ifc;
    method Bit#(8) mux4(Bit#(2) sel, Bit#(8) d0, Bit#(8) d1, Bit#(8) d2, Bit#(8) d3);
endinterface
""",
        snippet_template="""    method Bit#(8) mux4(Bit#(2) sel, Bit#(8) d0, Bit#(8) d1, Bit#(8) d2, Bit#(8) d3);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(8) mux4(Bit#(2) sel, Bit#(8) d0, Bit#(8) d1, Bit#(8) d2, Bit#(8) d3);
        case (sel)
            2'd0: return d0;
            2'd1: return d1;
            2'd2: return d2;
            default: return d3;
        endcase
    endmethod""",
        testbench_body="""    rule test;
        Bit#(2) sel = truncate(cycle);
        Bit#(8) d0 = 8'h11 + truncate(cycle * 3);
        Bit#(8) d1 = 8'h22 + truncate(cycle * 5);
        Bit#(8) d2 = 8'h44 + truncate(cycle * 7);
        Bit#(8) d3 = 8'h88 + truncate(cycle * 9);
        Bit#(8) r = ref_dut.mux4(sel, d0, d1, d2, d3);
        Bit#(8) u = user_dut.mux4(sel, d0, d1, d2, d3);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=sel:%0d,d0:0x%02h,d1:0x%02h,d2:0x%02h,d3:0x%02h|ref=out:0x%02h|user=out:0x%02h|match=%0d|note=Mux sel=%0d", cycle, sel, d0, d1, d2, d3, r, u, ok ? 1 : 0, sel);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use `case (sel) ... endcase` or `if (sel == 0) return d0; else if ...`.",
            "In a `case` block, always include a `default:` branch so BSV knows all cases return a value.",
            "Both `case (sel)` and ternary `(sel == 0) ? d0 : (sel == 1) ? d1 : (sel == 2) ? d2 : d3` are accepted!",
        ],
    ))

    problems.append(_make_problem(
        pid="05_bit_slicing",
        number=5,
        title="05. Bit Slicing, Concatenation & Endian Byte Swap",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Bit Slicing", "Concatenation", "Endianness"],
        description="""
Manipulating bit fields is one of the most frequent operations in RTL design.
In BSV:
- **Bit Slicing**: `x[15:8]` extracts bits 15 down to 8 (an 8-bit value `Bit#(8)`).
- **Concatenation**: `{a, b}` joins `Bit#(n)` and `Bit#(m)` into `Bit#(n+m)` with `a` in the MSBs and `b` in the LSBs.

### Task
Given a 16-bit input `x` (`Bit#(16)`):
1. `swapBytes(Bit#(16) x)`: Swap the upper byte `x[15:8]` and lower byte `x[7:0]`, returning `{x[7:0], x[15:8]}`.
2. `rotateNibbles(Bit#(16) x)`: Rotate the four 4-bit nibbles left by one nibble: `{x[11:0], x[15:12]}`.
""",
        bsv_vs_verilog="""
**BSV vs Verilog**: `{a, b}` concatenation and `x[hi:lo]` slicing look just like Verilog, with a superpower: BSV checks at compile time that the concatenated width `{8 bits, 8 bits}` equals the exact return type `Bit#(16)`! Never lose bits silently again.
""",
        diagram="""
   x = [ Byte1 (15:8) | Byte0 (7:0) ]
           \\               /
            \\             /
             v           v
   swapBytes = [ Byte0 (7:0) | Byte1 (15:8) ]
""",
        interface_name="BitSliceIfc",
        module_name="mkBitSlice",
        interface_def="""
interface BitSliceIfc;
    method Bit#(16) swapBytes(Bit#(16) x);
    method Bit#(16) rotateNibbles(Bit#(16) x);
endinterface
""",
        snippet_template="""    method Bit#(16) swapBytes(Bit#(16) x);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bit#(16) rotateNibbles(Bit#(16) x);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(16) swapBytes(Bit#(16) x);
        return {x[7:0], x[15:8]};
    endmethod

    method Bit#(16) rotateNibbles(Bit#(16) x);
        return {x[11:0], x[15:12]};
    endmethod""",
        testbench_body="""    rule test;
        Bit#(16) tv[6] = {16'h1234, 16'hABCD, 16'h00FF, 16'hF00F, 16'hCAFE, 16'hBEEF};
        Bit#(16) x = tv[cycle];
        Bit#(16) r1 = ref_dut.swapBytes(x);
        Bit#(16) r2 = ref_dut.rotateNibbles(x);
        Bit#(16) u1 = user_dut.swapBytes(x);
        Bit#(16) u2 = user_dut.rotateNibbles(x);
        Bool ok = (r1 == u1) && (r2 == u2);
        $display("@WAVE cycle=%0d|in=x:0x%04h|ref=swap:0x%04h,rot:0x%04h|user=swap:0x%04h,rot:0x%04h|match=%0d|note=Bit concat", cycle, x, r1, r2, u1, u2, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use curly braces `{x[7:0], x[15:8]}` to concatenate the low byte ahead of the high byte.",
            "For `rotateNibbles(x)`, concatenate bits `11:0` with bits `15:12`: `{x[11:0], x[15:12]}`.",
            "Make sure the total width inside `{ ... }` adds up to 16 bits.",
        ],
    ))

    problems.append(_make_problem(
        pid="06_ripple_adder",
        number=6,
        title="06. 4-Bit Ripple-Carry Full Adder (Static For-Loop)",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Adder", "Static Elaboration", "for-loop"],
        description="""
In hardware design, a **Full Adder** takes bits `a`, `b`, and `cin`, producing:
- `sum = a ^ b ^ cin`
- `cout = (a & b) | (a & cin) | (b & cin)`

In BSV, you can chain 4 full adders using a **compile-time static elaboration loop** (`for (Integer i = 0; i < 4; i = i + 1)`):
```bsv
Bit#(4) sum = 0;
Bit#(5) c = 0;
c[0] = cin;
for (Integer i = 0; i < 4; i = i + 1) begin
    sum[i] = a[i] ^ b[i] ^ c[i];
    c[i+1] = (a[i] & b[i]) | (a[i] & c[i]) | (b[i] & c[i]);
end
return {c[4], sum};
```
*(Note: You can also write `{1'b0, a} + {1'b0, b} + zeroExtend(cin)` — our smart evaluator accepts both and compares your structure!)*

### Task
Implement `add4(Bit#(4) a, Bit#(4) b, Bit#(1) cin)` returning a 5-bit result `{cout, sum[3:0]}` (`Bit#(5)`).
""",
        bsv_vs_verilog="""
**Verilog**: Requires `genvar i; generate for (...)` blocks or careful `always @(*)` blocking assignments.
**BSV**: `for (Integer i = 0; i < 4; i = i + 1)` inside any method or rule is automatically unrolled by `bsc` during static elaboration into pure combinational logic!
""",
        diagram="""
         a[3] b[3]     a[2] b[2]     a[1] b[1]     a[0] b[0]
          |    |        |    |        |    |        |    |
          v    v        v    v        v    v        v    v
 cout <--[ FA 3 ]<--c3-[ FA 2 ]<--c2-[ FA 1 ]<--c1-[ FA 0 ]<-- cin
            |             |             |             |
          sum[3]        sum[2]        sum[1]        sum[0]
""",
        interface_name="RippleAdderIfc",
        module_name="mkRippleAdder",
        interface_def="""
interface RippleAdderIfc;
    method Bit#(5) add4(Bit#(4) a, Bit#(4) b, Bit#(1) cin);
endinterface
""",
        snippet_template="""    method Bit#(5) add4(Bit#(4) a, Bit#(4) b, Bit#(1) cin);
        // === YOUR CODE HERE ===
        // Tip: Use a `for (Integer i = 0; i < 4; i = i + 1)` ripple-carry loop!
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(5) add4(Bit#(4) a, Bit#(4) b, Bit#(1) cin);
        Bit#(4) sum = 0;
        Bit#(5) c = 0;
        c[0] = cin;
        for (Integer i = 0; i < 4; i = i + 1) begin
            sum[i] = a[i] ^ b[i] ^ c[i];
            c[i+1] = (a[i] & b[i]) | (a[i] & c[i]) | (b[i] & c[i]);
        end
        return {c[4], sum};
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) va[8] = {4'd0, 4'd3, 4'd7, 4'd15, 4'd9, 4'd12, 4'd8, 4'd15};
        Bit#(4) vb[8] = {4'd0, 4'd5, 4'd8, 4'd1,  4'd6, 4'd7,  4'd8, 4'd15};
        Bit#(1) vc[8] = {1'b0, 1'b0, 1'b1, 1'b0,  1'b1, 1'b0,  1'b1, 1'b1};
        Bit#(4) a = va[cycle];
        Bit#(4) b = vb[cycle];
        Bit#(1) cin = vc[cycle];
        Bit#(5) r = ref_dut.add4(a, b, cin);
        Bit#(5) u = user_dut.add4(a, b, cin);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=a:%0d,b:%0d,cin:%0d|ref=out:0x%02h|user=out:0x%02h|match=%0d|note=%0d+%0d+%0d=%0d", cycle, a, b, cin, r, u, ok ? 1 : 0, a, b, cin, r);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Declare `Bit#(4) sum = 0;` and `Bit#(5) c = 0; c[0] = cin;`.",
            "Loop with `for (Integer i = 0; i < 4; i = i + 1) begin ... end`.",
            "Inside the loop: `sum[i] = a[i] ^ b[i] ^ c[i];` and `c[i+1] = (a[i] & b[i]) | (a[i] & c[i]) | (b[i] & c[i]);`, then `return {c[4], sum};`.",
        ],
    ))

    problems.append(_make_problem(
        pid="07_seven_seg",
        number=7,
        title="07. 7-Segment Hex Decoder (Lookup Table)",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Decoder", "case", "7-Segment"],
        description="""
A **7-Segment Display Decoder** converts a 4-bit hexadecimal nibble `d` (`0x0`–`0xF`) into 7 active-high LED segment signals `segs[6:0] = {g, f, e, d, c, b, a}`.

Use the standard active-high encoding below:
| Hex | `segs[6:0]` (`7'b_gfedcba`) | Hex | `segs[6:0]` (`7'b_gfedcba`) |
|---|---|---|---|
| `4'h0` | `7'b0111111` (`0x3F`) | `4'h8` | `7'b1111111` (`0x7F`) |
| `4'h1` | `7'b0000110` (`0x06`) | `4'h9` | `7'b1101111` (`0x6F`) |
| `4'h2` | `7'b1011011` (`0x5B`) | `4'hA` | `7'b1110111` (`0x77`) |
| `4'h3` | `7'b1001111` (`0x4F`) | `4'hB` | `7'b1111100` (`0x7C`) |
| `4'h4` | `7'b1100110` (`0x66`) | `4'hC` | `7'b0111001` (`0x39`) |
| `4'h5` | `7'b1101101` (`0x6D`) | `4'hD` | `7'b1011110` (`0x5E`) |
| `4'h6` | `7'b1111101` (`0x7D`) | `4'hE` | `7'b1111001` (`0x79`) |
| `4'h7` | `7'b0000111` (`0x07`) | `4'hF` | `7'b1110001` (`0x71`) |

### Task
Complete `decode(Bit#(4) hex)` in `mkSevenSeg` to return the 7-bit segment pattern.
""",
        bsv_vs_verilog="""
**BSV Tip**: A `case (hex)` table in a combinational method synthesizes directly into a 16x7 ROM / LUT on an FPGA (using less than two 6-input LUTs!).
""",
        diagram="""
        --a--
       |     |
       f     b
       |     |
        --g--
       |     |
       e     c
       |     |
        --d--    segs = {g, f, e, d, c, b, a}
""",
        interface_name="SevenSegIfc",
        module_name="mkSevenSeg",
        interface_def="""
interface SevenSegIfc;
    method Bit#(7) decode(Bit#(4) hex);
endinterface
""",
        snippet_template="""    method Bit#(7) decode(Bit#(4) hex);
        case (hex)
            4'h0: return 7'h3F;
            4'h1: return 7'h06;
            4'h2: return 7'h5B;
            4'h3: return 7'h4F;
            // === YOUR CODE HERE (complete 4'h4 through 4'hF) ===
            default: return 7'h00;
        endcase
    endmethod""",
        reference_snippet="""    method Bit#(7) decode(Bit#(4) hex);
        case (hex)
            4'h0: return 7'h3F;
            4'h1: return 7'h06;
            4'h2: return 7'h5B;
            4'h3: return 7'h4F;
            4'h4: return 7'h66;
            4'h5: return 7'h6D;
            4'h6: return 7'h7D;
            4'h7: return 7'h07;
            4'h8: return 7'h7F;
            4'h9: return 7'h6F;
            4'hA: return 7'h77;
            4'hB: return 7'h7C;
            4'hC: return 7'h39;
            4'hD: return 7'h5E;
            4'hE: return 7'h79;
            default: return 7'h71;
        endcase
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) h = truncate(cycle);
        Bit#(7) r = ref_dut.decode(h);
        Bit#(7) u = user_dut.decode(h);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=hex:0x%01h|ref=segs:0x%02h|user=segs:0x%02h|match=%0d|note=Hex %01h", cycle, h, r, u, ok ? 1 : 0, h);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 15) begin
            $display("@SUMMARY total=16 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "You can write the segment values in hex (`7'h66`, `7'h6D`, ...) or binary (`7'b1100110`, ...).",
            "Check values: `4'h4: 7'h66`, `4'h5: 7'h6D`, `4'h6: 7'h7D`, `4'h7: 7'h07`, `4'h8: 7'h7F`, `4'h9: 7'h6F`.",
            "And for `A`–`F`: `4'hA: 7'h77`, `4'hB: 7'h7C`, `4'hC: 7'h39`, `4'hD: 7'h5E`, `4'hE: 7'h79`, `4'hF: 7'h71`.",
        ],
    ))

    # =========================================================================
    # TRACK 2: STRONG TYPES, ENUMS, STRUCTS & VECTORS
    # =========================================================================
    problems.append(_make_problem(
        pid="08_enum_alu",
        number=8,
        title="08. Type-Safe Combinational ALU (`typedef enum`)",
        track_id="track2_types",
        track_title="2. Strong Types, Enums, Structs & Vectors",
        difficulty="Easy",
        tags=["ALU", "enum", "deriving (Bits, Eq)"],
        description="""
Instead of magic numbers (`2'b00`, `2'b01`) for opcodes, BSV encourages **strongly-typed enumerations**:
```bsv
typedef enum {
    OP_ADD,
    OP_SUB,
    OP_AND,
    OP_OR,
    OP_XOR,
    OP_SLL
} AluOp deriving (Bits, Eq);
```
Notice two critical BSV rules:
1. Enum tags (`OP_ADD`, `OP_SUB`, ...) **must start with an uppercase letter**.
2. `deriving (Bits, Eq)` tells the compiler how to pack the enum into hardware wires (`Bits`) and compare two enum values with `==` or `case` (`Eq`).

### Task
Implement `compute(AluOp op, Bit#(8) a, Bit#(8) b)` in `mkEnumAlu`:
- `OP_ADD`: `a + b`
- `OP_SUB`: `a - b`
- `OP_AND`: `a & b`
- `OP_OR`:  `a | b`
- `OP_XOR`: `a ^ b`
- `OP_SLL`: `a << b[2:0]` (logical shift left by the lower 3 bits of `b`)
""",
        bsv_vs_verilog="""
**Verilog**: Passing an integer or wrong-width wire to an opcode port compiles silently with bugs.
**BSV**: `AluOp` is its own distinct type! Passing a raw `Bit#(3)` where an `AluOp` is expected is caught immediately at compile time.
""",
        diagram="""
   a[7:0] ----+
              |---> [   ALU   ] ---> compute[7:0]
   b[7:0] ----+        ^
                       | op (OP_ADD | OP_SUB | OP_AND | OP_OR | OP_XOR | OP_SLL)
""",
        interface_name="EnumAluIfc",
        module_name="mkEnumAlu",
        interface_def="""
typedef enum {
    OP_ADD,
    OP_SUB,
    OP_AND,
    OP_OR,
    OP_XOR,
    OP_SLL
} AluOp deriving (Bits, Eq);

interface EnumAluIfc;
    method Bit#(8) compute(AluOp op, Bit#(8) a, Bit#(8) b);
endinterface
""",
        snippet_template="""    method Bit#(8) compute(AluOp op, Bit#(8) a, Bit#(8) b);
        case (op)
            OP_ADD: return a + b;
            // === YOUR CODE HERE (handle OP_SUB, OP_AND, OP_OR, OP_XOR, OP_SLL) ===
            default: return 0;
        endcase
    endmethod""",
        reference_snippet="""    method Bit#(8) compute(AluOp op, Bit#(8) a, Bit#(8) b);
        case (op)
            OP_ADD: return a + b;
            OP_SUB: return a - b;
            OP_AND: return a & b;
            OP_OR:  return a | b;
            OP_XOR: return a ^ b;
            OP_SLL: return a << b[2:0];
        endcase
    endmethod""",
        testbench_body="""    rule test;
        AluOp ops[6] = {OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR, OP_SLL};
        Bit#(8) a = 8'h25 + truncate(cycle * 7);
        Bit#(8) b = 8'h03 + truncate(cycle * 2);
        AluOp op = ops[cycle];
        Bit#(8) r = ref_dut.compute(op, a, b);
        Bit#(8) u = user_dut.compute(op, a, b);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=op:%0d,a:0x%02h,b:0x%02h|ref=out:0x%02h|user=out:0x%02h|match=%0d|note=ALU op=%0d", cycle, pack(op), a, b, r, u, ok ? 1 : 0, pack(op));
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Match each enum tag in `case (op)`: `OP_SUB: return a - b;`, `OP_AND: return a & b;`, etc.",
            "For `OP_SLL`, shift `a` left by `b[2:0]`: `OP_SLL: return a << b[2:0];`.",
            "Remember enum tags in BSV are case-sensitive (`OP_ADD`, `OP_SUB`, `OP_AND`, `OP_OR`, `OP_XOR`, `OP_SLL`).",
        ],
    ))

    problems.append(_make_problem(
        pid="09_struct_packet",
        number=9,
        title="09. Network Packet Router (`typedef struct`)",
        track_id="track2_types",
        track_title="2. Strong Types, Enums, Structs & Vectors",
        difficulty="Easy",
        tags=["struct", "pack/unpack", "Networking"],
        description="""
In BSV, `typedef struct` lets you bundle related signals together and access them by field name (`pkt.dst`, `pkt.payload`) while still packing cleanly into a flat bit vector via `deriving (Bits, Eq)`:
```bsv
typedef struct {
    Bool     valid;
    Bit#(3)  dst;
    Bit#(8)  payload;
} Packet deriving (Bits, Eq);
```
You can construct a struct value using `Packet { valid: True, dst: 3'd2, payload: 8'hFF }`.

### Task
Implement two methods in `mkStructPacket`:
1. `unpackPacket(Bit#(12) raw)`: Convert a raw 12-bit wire `{valid, dst[2:0], payload[7:0]}` into a `Packet` struct (Hint: `unpack(raw)` or `Packet { valid: unpack(raw[11]), dst: raw[10:8], payload: raw[7:0] }`).
2. `routeHop(Packet pkt)`: If `pkt.valid` is `True` and `pkt.dst > 0`, return a new `Packet` with `dst: pkt.dst - 1` (decrementing TTL/hop distance) and the same `valid` and `payload`; otherwise return `pkt` unchanged.
""",
        bsv_vs_verilog="""
**BSV Power**: Because `Packet` derives `Bits#(Packet, 12)`, calling `unpack(raw)` automatically maps bit 11 to `valid`, bits 10:8 to `dst`, and bits 7:0 to `payload`!
""",
        diagram="""
   raw[11:0] ---> [ unpack(raw) ] ---> Packet { valid, dst, payload }
                                                |
                                       [ dst > 0 ? dst-1 : dst ]
""",
        interface_name="StructPacketIfc",
        module_name="mkStructPacket",
        interface_def="""
typedef struct {
    Bool     valid;
    Bit#(3)  dst;
    Bit#(8)  payload;
} Packet deriving (Bits, Eq);

interface StructPacketIfc;
    method Packet unpackPacket(Bit#(12) raw);
    method Packet routeHop(Packet pkt);
endinterface
""",
        snippet_template="""    method Packet unpackPacket(Bit#(12) raw);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Packet routeHop(Packet pkt);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Packet unpackPacket(Bit#(12) raw);
        return unpack(raw);
    endmethod

    method Packet routeHop(Packet pkt);
        if (pkt.valid && pkt.dst > 0) begin
            pkt.dst = pkt.dst - 1;
        end
        return pkt;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(12) raws[6] = {12'hB42, 12'h899, 12'h3AA, 12'hF01, 12'h955, 12'h0FF};
        Bit#(12) raw = raws[cycle];
        Packet rp1 = ref_dut.unpackPacket(raw);
        Packet up1 = user_dut.unpackPacket(raw);
        Packet rp2 = ref_dut.routeHop(rp1);
        Packet up2 = user_dut.routeHop(up1);
        Bool ok = (rp1 == up1) && (rp2 == up2);
        $display("@WAVE cycle=%0d|in=raw:0x%03h|ref=unpk:0x%03h,hop:0x%03h|user=unpk:0x%03h,hop:0x%03h|match=%0d|note=Struct hop", cycle, raw, pack(rp1), pack(rp2), pack(up1), pack(up2), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Because `Packet` has `deriving (Bits, Eq)`, `unpack(raw)` converts `Bit#(12)` directly into a `Packet`!",
            "In `routeHop(Packet pkt)`, you can modify a field copy (`if (pkt.valid && pkt.dst > 0) pkt.dst = pkt.dst - 1; return pkt;`) or return `Packet { valid: pkt.valid, dst: pkt.dst - 1, payload: pkt.payload }`.",
            "Remember `Bool` literals in BSV are capitalized: `True` and `False`.",
        ],
    ))

    problems.append(_make_problem(
        pid="10_maybe_priority",
        number=10,
        title="10. 4-to-2 Priority Encoder with `Maybe#(Bit#(2))`",
        track_id="track2_types",
        track_title="2. Strong Types, Enums, Structs & Vectors",
        difficulty="Easy",
        tags=["Priority Encoder", "Maybe", "Tagged Union"],
        description="""
In Verilog, a priority encoder usually outputs a separate `valid` wire and an `index` wire — and nothing stops downstream logic from reading `index` when `valid == 0`!

BSV solves this with the built-in polymorphic **Tagged Union** `Maybe#(t)`:
- `tagged Valid x` — indicates a valid value `x`
- `tagged Invalid` — indicates no valid value is present

### Task
Implement a 4-input priority encoder `encode(Bit#(4) req)` returning `Maybe#(Bit#(2))`:
- Highest priority is bit 3 (`req[3] == 1`) -> `return tagged Valid 2'd3;`
- Next is bit 2 (`req[2] == 1`) -> `return tagged Valid 2'd2;`
- Next is bit 1 (`req[1] == 1`) -> `return tagged Valid 2'd1;`
- Next is bit 0 (`req[0] == 1`) -> `return tagged Valid 2'd0;`
- If `req == 4'b0000` -> `return tagged Invalid;`
""",
        bsv_vs_verilog="""
**BSV vs Verilog**: In hardware, `Maybe#(Bit#(2))` compiles to a 3-bit bus `{valid_bit, idx[1:0]}`, where `tagged Valid idx` sets the MSB to `1` and `tagged Invalid` sets the MSB to `0`!
""",
        diagram="""
   req[3:0] ---> [ Priority 3 > 2 > 1 > 0 ] ---> Maybe#(Bit#(2))
                 req[3]==1 -> Valid 3
                 req[2]==1 -> Valid 2
                 req[1]==1 -> Valid 1
                 req[0]==1 -> Valid 0
                 else      -> Invalid
""",
        interface_name="PrioEnc4Ifc",
        module_name="mkPrioEnc4",
        interface_def="""
interface PrioEnc4Ifc;
    method Maybe#(Bit#(2)) encode(Bit#(4) req);
endinterface
""",
        snippet_template="""    method Maybe#(Bit#(2)) encode(Bit#(4) req);
        // === YOUR CODE HERE ===
        return tagged Invalid;
    endmethod""",
        reference_snippet="""    method Maybe#(Bit#(2)) encode(Bit#(4) req);
        if (req[3] == 1) return tagged Valid 2'd3;
        else if (req[2] == 1) return tagged Valid 2'd2;
        else if (req[1] == 1) return tagged Valid 2'd1;
        else if (req[0] == 1) return tagged Valid 2'd0;
        else return tagged Invalid;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) req = truncate(cycle);
        Maybe#(Bit#(2)) r = ref_dut.encode(req);
        Maybe#(Bit#(2)) u = user_dut.encode(req);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=req:0x%01h|ref=v:%0d,idx:%0d|user=v:%0d,idx:%0d|match=%0d|note=req=%04b", cycle, req, isValid(r)?1:0, fromMaybe(0,r), isValid(u)?1:0, fromMaybe(0,u), ok ? 1 : 0, req);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 15) begin
            $display("@SUMMARY total=16 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Check bits from MSB (`req[3]`) down to LSB (`req[0]`) using `if / else if / else`.",
            "Return `tagged Valid 2'd3` when `req[3] == 1`, down to `tagged Valid 2'd0` when `req[0] == 1`.",
            "When no bit of `req` is 1, return `tagged Invalid;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="11_vector_popcount",
        number=11,
        title="11. 8-Bit Population Count (`Vector` & Reduction)",
        track_id="track2_types",
        track_title="2. Strong Types, Enums, Structs & Vectors",
        difficulty="Easy",
        tags=["Vector", "PopCount", "Static Loop"],
        description="""
A **Population Counter (PopCount)** counts how many bits in an input word are equal to `1`.
In BSV, you can iterate over bits using a `for` loop or unpack `Bit#(8)` into `Vector#(8, Bit#(1))`:
```bsv
Bit#(4) count = 0;
for (Integer i = 0; i < 8; i = i + 1) begin
    count = count + zeroExtend(x[i]);
end
return count;
```
Notice `zeroExtend(x[i])`: since `x[i]` is `Bit#(1)` and `count` is `Bit#(4)` (because a count of 8 bits can be `0` to `8`, which requires 4 bits!), `zeroExtend` pads `x[i]` with zeros to match `Bit#(4)`.

### Task
Implement `popCount(Bit#(8) x)` returning the 4-bit count (`Bit#(4)`) of set bits in `x`.
""",
        bsv_vs_verilog="""
**BSV Type Safety**: An 8-bit input has up to 8 ones (`4'd8 = 4'b1000`), which needs 4 bits. `zeroExtend(x[i])` automatically infers the target width `Bit#(4)` from `count`!
""",
        diagram="""
   x[7:0] = 8'b1011_0101  --->  1+0+1+1+0+1+0+1  --->  count = 4'd5
""",
        interface_name="PopCount8Ifc",
        module_name="mkPopCount8",
        interface_def="""
interface PopCount8Ifc;
    method Bit#(4) popCount(Bit#(8) x);
endinterface
""",
        snippet_template="""    method Bit#(4) popCount(Bit#(8) x);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(4) popCount(Bit#(8) x);
        Bit#(4) count = 0;
        for (Integer i = 0; i < 8; i = i + 1) begin
            count = count + zeroExtend(x[i]);
        end
        return count;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) tv[8] = {8'h00, 8'hFF, 8'h01, 8'h80, 8'h55, 8'hAA, 8'h3C, 8'hE7};
        Bit#(8) x = tv[cycle];
        Bit#(4) r = ref_dut.popCount(x);
        Bit#(4) u = user_dut.popCount(x);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=x:0x%02h|ref=cnt:%0d|user=cnt:%0d|match=%0d|note=popcount(0x%02h)=%0d", cycle, x, r, u, ok ? 1 : 0, x, r);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Initialize `Bit#(4) count = 0;`.",
            "Loop `for (Integer i = 0; i < 8; i = i + 1)` and add `zeroExtend(x[i])` to `count`.",
            "Return `count` at the end of the method.",
        ],
    ))

    # =========================================================================
    # TRACK 3: SEQUENTIAL CIRCUITS, REGISTERS & ATOMIC RULES
    # =========================================================================
    problems.append(_make_problem(
        pid="12_dff_reg",
        number=12,
        title="12. Your First Register (`mkReg` & `Action` Methods)",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Easy",
        tags=["Reg", "Action Method", "Sequential"],
        description="""
Now we transition from combinational circuits to **Sequential Circuits** with clock-synchronized state!

In BSV, you never write `always @(posedge clk)`. Instead, state elements are **modules** instantiated with `<-`. The most fundamental state primitive is `Reg#(t)`:
```bsv
Reg#(Bit#(8)) val <- mkReg(0); // 8-bit register reset to 0
```
- **Reading a Register**: Just use `val` in any expression!
- **Writing a Register**: Use `val <= new_val;` inside an `Action` method or `rule`. The new value takes effect at the next rising clock edge.

### Task
In `mkDffReg`:
1. Instantiate an 8-bit register initialized to `8'h00` on reset (`Reg#(Bit#(8)) r <- mkReg(0);`).
2. Implement `method Action write(Bit#(8) d)` to update the register with `d`.
3. Implement `method Bit#(8) read()` to return the current register value.
""",
        bsv_vs_verilog="""
**Verilog**: `reg [7:0] r;` is just a variable — it only becomes a flip-flop if placed in `always @(posedge clk)`, and can accidentally become a latch if assigned in `always @(*)`!
**BSV**: `Reg#(Bit#(8)) r <- mkReg(0);` is ALWAYS a hardware register with clock `CLK` and reset `RST_N`. Accidental latches are impossible in BSV!
""",
        diagram="""
   d[7:0] ---> [D    Q] ---> read()[7:0]
   write_en -> [EN    ]
               [ >CLK ] (Reset = 0)
""",
        interface_name="DffRegIfc",
        module_name="mkDffReg",
        interface_def="""
interface DffRegIfc;
    method Action write(Bit#(8) d);
    method Bit#(8) read();
endinterface
""",
        snippet_template="""    // 1. Instantiate an 8-bit register reset to 0
    // === YOUR CODE HERE ===

    method Action write(Bit#(8) d);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) read();
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) r <- mkReg(0);

    method Action write(Bit#(8) d);
        r <= d;
    endmethod

    method Bit#(8) read();
        return r;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) d = 8'h10 + (cycle[7:0] * 8'h11);
        Bit#(8) r_val = ref_dut.read();
        Bit#(8) u_val = user_dut.read();
        if (cycle % 2 == 0) begin
            ref_dut.write(d);
            user_dut.write(d);
        end
        Bool ok = (r_val == u_val);
        $display("@WAVE cycle=%0d|in=wr_en:%0d,d:0x%02h|ref=q:0x%02h|user=q:0x%02h|match=%0d|note=Reg read/write", cycle, (cycle%2==0)?1:0, d, r_val, u_val, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Declare the register inside the module: `Reg#(Bit#(8)) r <- mkReg(0);`.",
            "Inside `method Action write(Bit#(8) d);`, assign to the register using `r <= d;`.",
            "Inside `method Bit#(8) read();`, return the register value with `return r;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="13_counter_up",
        number=13,
        title="13. Free-Running Up-Counter (`rule` Basics)",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Easy",
        tags=["rule", "Counter", "Sequential"],
        description="""
In BSV, internal behavior that happens autonomously on clock ticks is expressed using **Rules**:
```bsv
Reg#(Bit#(4)) cnt <- mkReg(0);

rule tick;
    cnt <= cnt + 1;
endrule
```
Every clock cycle where a rule's guard is true (and no higher-urgency conflicting rule/method blocks it), the rule **fires atomically**!

### Task
Design a 4-bit free-running up-counter `mkCounterUp`:
- Hold a 4-bit register initialized to `0`.
- Define an internal `rule` that increments the counter by `1` every clock cycle (`cnt <= cnt + 1;`).
- Implement `method Bit#(4) count()` returning the current counter value.
""",
        bsv_vs_verilog="""
**BSV Atomic Rules**: A `rule` is a declarative state transition. `bsc` automatically synthesizes its `CAN_FIRE` and `WILL_FIRE` control logic and connects it to the register's write-enable pin!
""",
        diagram="""
         +--- [ + 1 ] <---+
         |                |
         v                |
      [ cnt (Reg#(4)) ] --+---> count()[3:0]
""",
        interface_name="CounterUpIfc",
        module_name="mkCounterUp",
        interface_def="""
interface CounterUpIfc;
    method Bit#(4) count();
endinterface
""",
        snippet_template="""    // Instantiate a 4-bit register initialized to 0, a rule to increment it, and the count() method
    // === YOUR CODE HERE ===
    method Bit#(4) count();
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(4)) cnt <- mkReg(0);

    rule increment;
        cnt <= cnt + 1;
    endrule

    method Bit#(4) count();
        return cnt;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) r = ref_dut.count();
        Bit#(4) u = user_dut.count();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=clk:1|ref=cnt:%0d|user=cnt:%0d|match=%0d|note=Cycle %0d", cycle, r, u, ok ? 1 : 0, cycle);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 9) begin
            $display("@SUMMARY total=10 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Instantiate `Reg#(Bit#(4)) cnt <- mkReg(0);`.",
            "Add a rule: `rule inc; cnt <= cnt + 1; endrule`.",
            "Return `cnt` from `method Bit#(4) count()`.",
        ],
    ))

    problems.append(_make_problem(
        pid="14_counter_updown",
        number=14,
        title="14. Programmable Up/Down Counter with Step Control",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Easy",
        tags=["Counter", "Action Method", "Sequential"],
        description="""
Often a counter is controlled by external method calls (`step` and `load`) rather than ticking unconditionally every cycle.

### Task
Implement an 8-bit programmable counter `mkCounterUpDown` with register state initialized to `0`:
1. `method Action load(Bit#(8) val)`: Load `val` directly into the counter register.
2. `method Action step(Bool up)`: If `up` is `True`, increment the counter by `1` (`cnt <= cnt + 1`); if `up` is `False`, decrement by `1` (`cnt <= cnt - 1`).
3. `method Bit#(8) read()`: Return the current 8-bit counter value.
""",
        bsv_vs_verilog="""
**BSV Multiplexing**: When two `Action` methods (`load` and `step`) can write to the same `Reg`, `bsc` automatically synthesizes the priority/selector mux on the register's data input and ORs their enable signals into `cnt$EN`!
""",
        diagram="""
   load(val) ----->|       |
                   |  MUX  |---> [ cnt (Reg#(8)) ] ---> read()
   step(up)  ----->| +/- 1 |
""",
        interface_name="CounterUpDownIfc",
        module_name="mkCounterUpDown",
        interface_def="""
interface CounterUpDownIfc;
    method Action load(Bit#(8) val);
    method Action step(Bool up);
    method Bit#(8) read();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) cnt <- mkReg(0);

    method Action load(Bit#(8) val);
        // === YOUR CODE HERE ===
    endmethod

    method Action step(Bool up);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) read();
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) cnt <- mkReg(0);

    method Action load(Bit#(8) val);
        cnt <= val;
    endmethod

    method Action step(Bool up);
        cnt <= up ? (cnt + 1) : (cnt - 1);
    endmethod

    method Bit#(8) read();
        return cnt;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) r = ref_dut.read();
        Bit#(8) u = user_dut.read();
        if (cycle == 0) begin
            ref_dut.load(8'd10);
            user_dut.load(8'd10);
        end else if (cycle <= 4) begin
            ref_dut.step(True);
            user_dut.step(True);
        end else if (cycle == 5) begin
            ref_dut.load(8'd50);
            user_dut.load(8'd50);
        end else begin
            ref_dut.step(False);
            user_dut.step(False);
        end
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=cycle:%0d|ref=cnt:%0d|user=cnt:%0d|match=%0d|note=UpDown step", cycle, cycle, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 9) begin
            $display("@SUMMARY total=10 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `load(Bit#(8) val)`, write `cnt <= val;`.",
            "In `step(Bool up)`, write `if (up) cnt <= cnt + 1; else cnt <= cnt - 1;` (or `cnt <= up ? (cnt + 1) : (cnt - 1);`).",
            "In `read()`, `return cnt;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="15_shift_lfsr",
        number=15,
        title="15. 8-Bit Galois LFSR Pseudo-Random Generator",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Medium",
        tags=["LFSR", "Shift Register", "Sequential"],
        description="""
A **Linear Feedback Shift Register (LFSR)** generates pseudo-random bit sequences for built-in self-test (BIST), cryptography, and scramblers.

In an 8-bit right-shifting **Galois LFSR** with polynomial tap mask `8'hB8` (`8'b1011_1000`):
- The register `r` MUST be initialized to non-zero seed `8'h01` on reset (`Reg#(Bit#(8)) r <- mkReg(8'h01);`).
- On every clock cycle (`rule step`), shift `r` right by 1 (`r >> 1`), and if the outgoing LSB `r[0]` is `1`, XOR with `8'hB8`:
```bsv
r <= (r[0] == 1) ? ((r >> 1) ^ 8'hB8) : (r >> 1);
```

### Task
Implement `mkLfsr8` with `r` reset to `8'h01`, an autonomous `rule` updating `r` each cycle, and `method Bit#(8) value()` returning `r`.
""",
        bsv_vs_verilog="""
**Hardware Insight**: A Galois LFSR computes all XOR taps in parallel in a single gate delay (`(r >> 1) ^ 8'hB8`), allowing higher clock frequencies than Fibonacci LFSRs!
""",
        diagram="""
   r[0] --+--> [ ? ^ 8'hB8 : 0 ] ---> r_next[7:0]
          |                              ^
   r[7:1] ---> [    r >> 1     ] --------+
""",
        interface_name="Lfsr8Ifc",
        module_name="mkLfsr8",
        interface_def="""
interface Lfsr8Ifc;
    method Bit#(8) value();
endinterface
""",
        snippet_template="""    // Instantiate Reg#(Bit#(8)) r <- mkReg(8'h01); and Galois LFSR rule with mask 8'hB8
    // === YOUR CODE HERE ===
    method Bit#(8) value();
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) r <- mkReg(8'h01);

    rule shift;
        r <= (r[0] == 1) ? ((r >> 1) ^ 8'hB8) : (r >> 1);
    endrule

    method Bit#(8) value();
        return r;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) rv = ref_dut.value();
        Bit#(8) uv = user_dut.value();
        Bool ok = (rv == uv);
        $display("@WAVE cycle=%0d|in=clk:1|ref=lfsr:0x%02h|user=lfsr:0x%02h|match=%0d|note=LFSR step", cycle, rv, uv, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 9) begin
            $display("@SUMMARY total=10 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Make sure `r` is initialized to `8'h01`: `Reg#(Bit#(8)) r <- mkReg(8'h01);`.",
            "Write a `rule` that updates `r <= (r[0] == 1) ? ((r >> 1) ^ 8'hB8) : (r >> 1);`.",
            "Return `r` in `method Bit#(8) value()`.",
        ],
    ))

    problems.append(_make_problem(
        pid="16_edge_detector",
        number=16,
        title="16. Rising-Edge & Falling-Edge Detector",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Easy",
        tags=["Edge Detector", "ActionValue", "Sequential"],
        description="""
An **Edge Detector** remembers the previous cycle's 1-bit input `prev` (initialized to `0`) and compares it with the current input `sig`:
- **Rising Edge**: `sig == 1 && prev == 0` (or `sig & ~prev`)
- **Falling Edge**: `sig == 0 && prev == 1` (or `~sig & prev`)

In BSV, a method that **both** updates state (`prev <= sig`) **and** returns a value in the same cycle is an **`ActionValue#(t)`** method:
```bsv
method ActionValue#(Bit#(2)) sample(Bit#(1) sig);
    prev <= sig;
    Bit#(1) rise = sig & ~prev;
    Bit#(1) fall = ~sig & prev;
    return {fall, rise};
endmethod
```

### Task
Implement `mkEdgeDetector` with `prev` initialized to `1'b0`, and `method ActionValue#(Bit#(2)) sample(Bit#(1) sig)` returning `{fall, rise}` where bit 0 is `rise` and bit 1 is `fall`.
""",
        bsv_vs_verilog="""
**BSV `ActionValue#(t)`**: Combines a state transition (`Action`) and a combinational return value (`t`) into a single atomic method! Callers invoke it using `let res <- dut.sample(sig);`.
""",
        diagram="""
   sig ----+-----------------------> & ---> rise (bit 0)
           |                         ^
           +---> [ prev (Reg) ] -> ~-+
""",
        interface_name="EdgeDetectorIfc",
        module_name="mkEdgeDetector",
        interface_def="""
interface EdgeDetectorIfc;
    method ActionValue#(Bit#(2)) sample(Bit#(1) sig);
endinterface
""",
        snippet_template="""    Reg#(Bit#(1)) prev <- mkReg(0);

    method ActionValue#(Bit#(2)) sample(Bit#(1) sig);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(1)) prev <- mkReg(0);

    method ActionValue#(Bit#(2)) sample(Bit#(1) sig);
        prev <= sig;
        Bit#(1) rise = sig & ~prev;
        Bit#(1) fall = ~sig & prev;
        return {fall, rise};
    endmethod""",
        testbench_body="""    rule test;
        Bit#(1) stream[10] = {1'b0, 1'b1, 1'b1, 1'b0, 1'b0, 1'b1, 1'b0, 1'b1, 1'b1, 1'b0};
        Bit#(1) s = stream[cycle];
        Bit#(2) r <- ref_dut.sample(s);
        Bit#(2) u <- user_dut.sample(s);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=sig:%0d|ref=fall_rise:0x%01h|user=fall_rise:0x%01h|match=%0d|note=Edge detect", cycle, s, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 9) begin
            $display("@SUMMARY total=10 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Inside `sample(Bit#(1) sig)`, update `prev <= sig;`.",
            "Remember that in BSV, reading `prev` in the same cycle still gives the OLD value of `prev` before the clock edge!",
            "Compute `Bit#(1) rise = sig & ~prev;` and `Bit#(1) fall = ~sig & prev;`, then `return {fall, rise};`.",
        ],
    ))

    problems.append(_make_problem(
        pid="17_gcd_euclid",
        number=17,
        title="17. Euclid's GCD Engine (Guard Conditions & Multi-Rule Hardware)",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Medium",
        tags=["GCD", "Implicit Guards", "BSV by Example", "MIT 6.175"],
        description="""
**Euclid's Greatest Common Divisor (GCD)** is the signature introductory design in *BSV by Example* (Nikhil & Czeck) and MIT 6.175!
Given two registers `x` and `y` (`Reg#(Bit#(16))`) and a `busy` flag (`Reg#(Bool) busy <- mkReg(False)`):
- While `busy && (y != 0)`:
  - If `x >= y`, replace `x <= x - y;`
  - If `x < y`, swap them: `x <= y; y <= x;`
- When `busy && (y == 0)`, the answer is ready in `x`!

Look at how **Method Guards** work in BSV:
- `method Action start(Bit#(16) a, Bit#(16) b) if (!busy);` — can only be called when `!busy`!
- `method ActionValue#(Bit#(16)) getResult() if (busy && (y == 0));` — can only be called when the GCD calculation has finished (`y == 0`), and clears `busy <= False;` while returning `x`!

### Task
Complete `mkGcdEuclid` using `x`, `y`, and `busy` registers, a computation `rule` (or two rules `subtract` and `swap`), and guarded `start` / `getResult` methods.
""",
        bsv_vs_verilog="""
**Why BSV Shines Here**: In Verilog, you must manually design ready/valid state machines and control signals (`start_rdy`, `result_rdy`). In BSV, writing `if (busy && y == 0)` on `getResult()` automatically generates the `RDY_getResult` hardware signal and stalls any caller rule until `y == 0`!
""",
        diagram="""
   start(a,b) [if !busy] ---> [ x, y, busy=True ]
                                  |        ^
                                  +--------+ rule step (if busy && y != 0):
                                  |            x >= y ? x <= x-y : swap(x,y)
                                  v
   getResult() [if busy && y==0] -> returns x, sets busy <= False
""",
        interface_name="GcdEuclidIfc",
        module_name="mkGcdEuclid",
        interface_def="""
interface GcdEuclidIfc;
    method Action start(Bit#(16) a, Bit#(16) b);
    method ActionValue#(Bit#(16)) getResult();
endinterface
""",
        snippet_template="""    Reg#(Bit#(16)) x <- mkReg(0);
    Reg#(Bit#(16)) y <- mkReg(0);
    Reg#(Bool) busy <- mkReg(False);

    // Write rule(s) to compute Euclid's GCD when busy && y != 0
    // === YOUR CODE HERE ===

    method Action start(Bit#(16) a, Bit#(16) b) if (!busy);
        // === YOUR CODE HERE ===
    endmethod

    method ActionValue#(Bit#(16)) getResult() if (busy && (y == 0));
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(16)) x <- mkReg(0);
    Reg#(Bit#(16)) y <- mkReg(0);
    Reg#(Bool) busy <- mkReg(False);

    rule calc (busy && (y != 0));
        if (x >= y) begin
            x <= x - y;
        end else begin
            x <= y;
            y <= x;
        end
    endrule

    method Action start(Bit#(16) a, Bit#(16) b) if (!busy);
        x <= a;
        y <= b;
        busy <= True;
    endmethod

    method ActionValue#(Bit#(16)) getResult() if (busy && (y == 0));
        busy <= False;
        return x;
    endmethod""",
        testbench_body="""    Reg#(Bit#(4)) test_idx <- mkReg(0);
    Reg#(Bool) waiting <- mkReg(False);

    rule feed (!waiting && test_idx < 4);
        Bit#(16) va[4] = {16'd24, 16'd105, 16'd48, 16'd17};
        Bit#(16) vb[4] = {16'd18, 16'd45,  16'd180, 16'd13};
        ref_dut.start(va[test_idx], vb[test_idx]);
        user_dut.start(va[test_idx], vb[test_idx]);
        waiting <= True;
    endrule

    rule collect (waiting);
        Bit#(16) r <- ref_dut.getResult();
        Bit#(16) u <- user_dut.getResult();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=test:%0d|ref=gcd:%0d|user=gcd:%0d|match=%0d|note=GCD test %0d", cycle, test_idx, r, u, ok ? 1 : 0, test_idx);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        waiting <= False;
        if (test_idx == 3) begin
            $display("@SUMMARY total=4 passed=%0d", np);
            $finish(0);
        end
        test_idx <= test_idx + 1;
    endrule

    rule tick;
        cycle <= cycle + 1;
        if (cycle > 200) begin
            $display("@SUMMARY total=4 passed=%0d", passed_cnt);
            $finish(0);
        end
    endrule""",
        hints=[
            "Add a rule with guard `(busy && (y != 0))`: if `x >= y` do `x <= x - y;`, else swap `x <= y; y <= x;`.",
            "In `start(Bit#(16) a, Bit#(16) b) if (!busy)`, load `x <= a; y <= b; busy <= True;`.",
            "In `getResult() if (busy && (y == 0))`, set `busy <= False;` and `return x;`.",
        ],
    ))

    # =========================================================================
    # TRACK 4: CONCURRENCY, SCHEDULING, EHR & FIFOS
    # =========================================================================
    problems.append(_make_problem(
        pid="18_conflict_updown",
        number=18,
        title="18. Conflict-Free Concurrent Up/Down Counter (`PulseWire`)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["Concurrency", "PulseWire", "Rule Scheduling"],
        description="""
What happens if two separate rules or external clients want to call `inc()` and `dec()` on a counter **in the exact same clock cycle**?
If `inc()` does `cnt <= cnt + 1` and `dec()` does `cnt <= cnt - 1`, `bsc` reports a **Double-Write Conflict** because a standard `Reg` only has one write port!

How do we make `inc()` and `dec()` **Conflict-Free (CF)** so both can be called simultaneously?
Use `PulseWire` (built into BSV prelude)!
```bsv
Reg#(Bit#(8)) cnt <- mkReg(0);
PulseWire inc_wire <- mkPulseWire;
PulseWire dec_wire <- mkPulseWire;

rule canonicalize;
    if (inc_wire && !dec_wire)      cnt <= cnt + 1;
    else if (!inc_wire && dec_wire) cnt <= cnt - 1;
    // if both inc_wire and dec_wire pulse, net change is 0!
endrule
```
In `inc()`, call `inc_wire.send();`. In `dec()`, call `dec_wire.send();`.

### Task
Implement `mkConcurrentCounter` so `inc()` and `dec()` can be invoked in the same clock cycle without conflicting!
""",
        bsv_vs_verilog="""
**BSV Concurrency Pattern**: `PulseWire` (a 1-bit `RWire`) lets multiple methods signal an event within a clock cycle, while a single canonicalizing `rule` computes the combined state update at the end of the cycle!
""",
        diagram="""
   inc() ---> [ inc_wire.send() ] ---+
                                     |---> [ rule update ] ---> [ cnt (Reg#(8)) ]
   dec() ---> [ dec_wire.send() ] ---+
""",
        interface_name="ConcurrentCounterIfc",
        module_name="mkConcurrentCounter",
        interface_def="""
interface ConcurrentCounterIfc;
    method Action inc();
    method Action dec();
    method Bit#(8) read();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) cnt <- mkReg(0);
    PulseWire inc_w <- mkPulseWire;
    PulseWire dec_w <- mkPulseWire;

    // Write a rule that updates `cnt` based on `inc_w` and `dec_w`, plus inc(), dec(), read()
    // === YOUR CODE HERE ===
    method Action inc();
    endmethod

    method Action dec();
    endmethod

    method Bit#(8) read();
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) cnt <- mkReg(0);
    PulseWire inc_w <- mkPulseWire;
    PulseWire dec_w <- mkPulseWire;

    rule update;
        if (inc_w && !dec_w) cnt <= cnt + 1;
        else if (!inc_w && dec_w) cnt <= cnt - 1;
    endrule

    method Action inc();
        inc_w.send();
    endmethod

    method Action dec();
        dec_w.send();
    endmethod

    method Bit#(8) read();
        return cnt;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) r = ref_dut.read();
        Bit#(8) u = user_dut.read();
        // Test inc only, both inc+dec in same cycle!, and dec only
        if (cycle < 3) begin
            ref_dut.inc();
            user_dut.inc();
        end else if (cycle < 6) begin
            ref_dut.inc();
            ref_dut.dec();
            user_dut.inc();
            user_dut.dec();
        end else begin
            ref_dut.dec();
            user_dut.dec();
        end
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=mode:%0d|ref=cnt:%0d|user=cnt:%0d|match=%0d|note=Concurrent inc/dec", cycle, cycle/3, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 8) begin
            $display("@SUMMARY total=9 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `inc()`, call `inc_w.send();`. In `dec()`, call `dec_w.send();`.",
            "In `rule update;`, check `if (inc_w && !dec_w) cnt <= cnt + 1; else if (!inc_w && dec_w) cnt <= cnt - 1;`.",
            "When both `inc()` and `dec()` are called in the same cycle, both `inc_w` and `dec_w` are `True`, so `cnt` stays unchanged!",
        ],
    ))

    problems.append(_make_problem(
        pid="19_ehr_bypass",
        number=19,
        title="19. Intra-Cycle Bypass Register (`Ehr#(2, Bit#(16))`)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["Ehr", "Bypassing", "MIT 6.175"],
        description="""
In pipelined processors (like MIT 6.175 RISC-V labs), we frequently need a **Bypass Register**:
- If `write(x)` and `read()` happen in the **same clock cycle**, `read()` should immediately see the newly written value `x` (forwarding/bypassing)!
- If `write(x)` is NOT called in this cycle, `read()` returns the value stored in the register from previous cycles.

Using our `Ehr#(2, Bit#(16))` (Ephemeral History Register) library (`import Ehr::*;`):
```bsv
Ehr#(2, Bit#(16)) ehr <- mkEhr(0);
```
Port ordering inside a single clock cycle is guaranteed:
`ehr[0]._read < ehr[0]._write < ehr[1]._read < ehr[1]._write`
- If `write(d)` writes to **port 0** (`ehr[0] <= d;`), then any call to `read()` that reads from **port 1** (`return ehr[1];`) in the same cycle automatically receives `d`!

### Task
Implement `mkBypassReg16` using `Ehr#(2, Bit#(16))` so that `write(d)` happens before `read()` in the same cycle and forwards `d` to `read()`.
""",
        bsv_vs_verilog="""
**MIT 6.175 Key Concept**: An `Ehr#(2, t)` synthesizes to a register with a combinational bypass mux between port 0's write wire and port 1's read port — eliminating manual bypass mux wiring bugs!
""",
        diagram="""
   write(d) ---> ehr[0] <= d ---+---> [ MUX ] ---> ehr[1] (read() sees d in same cycle!)
                                |        ^
                  [ Reg r ] ----+--------+
""",
        interface_name="BypassReg16Ifc",
        module_name="mkBypassReg16",
        interface_def="""
interface BypassReg16Ifc;
    method Action write(Bit#(16) d);
    method Bit#(16) read();
endinterface
""",
        snippet_template="""    Ehr#(2, Bit#(16)) ehr <- mkEhr(0);

    method Action write(Bit#(16) d);
        // Write to port 0 of ehr
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(16) read();
        // Read from port 1 of ehr so same-cycle writes are bypassed!
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Ehr#(2, Bit#(16)) ehr <- mkEhr(0);

    method Action write(Bit#(16) d);
        ehr[0] <= d;
    endmethod

    method Bit#(16) read();
        return ehr[1];
    endmethod""",
        testbench_body="""    rule test;
        Bit#(16) d = 16'hA000 + (cycle[15:0] * 16'h0111);
        if (cycle % 2 == 0) begin
            ref_dut.write(d);
            user_dut.write(d);
        end
        Bit#(16) r = ref_dut.read();
        Bit#(16) u = user_dut.read();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=wr:%0d,d:0x%04h|ref=rd:0x%04h|user=rd:0x%04h|match=%0d|note=Ehr bypass", cycle, (cycle%2==0)?1:0, d, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `write(Bit#(16) d)`, write to port 0: `ehr[0] <= d;`.",
            "In `read()`, return port 1: `return ehr[1];`.",
            "Because `ehr[0]._write < ehr[1]._read`, reading `ehr[1]` in the same cycle sees the value written to `ehr[0]`!",
        ],
    ))

    problems.append(_make_problem(
        pid="20_fifo_one_elem",
        number=20,
        title="20. 1-Element Elastic FIFO from Scratch (Implicit Method Guards)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["FIFO", "Method Guards", "Flow Control"],
        description="""
FIFOs (First-In, First-Out queues) are the glue of elastic hardware pipelines. Let's build a 1-element FIFO from scratch using a data register `data_reg` (`Reg#(Bit#(8))`) and a full bit `full_reg` (`Reg#(Bool)` initialized to `False`):
- `method Action enq(Bit#(8) x) if (!full_reg);` — stores `x` into `data_reg` and sets `full_reg <= True`.
- `method Action deq() if (full_reg);` — sets `full_reg <= False`.
- `method Bit#(8) first() if (full_reg);` — returns `data_reg`.
- `method Bool notEmpty();` — returns `full_reg`.
- `method Bool notFull();` — returns `!full_reg`.

### Task
Implement all 5 methods of `mkOneElemFifo` with their appropriate implicit guards (`if (!full_reg)` / `if (full_reg)`).
""",
        bsv_vs_verilog="""
**Automatic Handshaking**: In Verilog, a FIFO consumer can accidentally read garbage when `empty == 1`. In BSV, the guard `if (full_reg)` on `first()` and `deq()` prevents any rule from firing unless the FIFO has valid data!
""",
        diagram="""
   enq(x) [if !full] ---> [ data_reg (8b) | full_reg (Bool) ] ---> first() [if full]
                                                              ---> deq()   [if full]
""",
        interface_name="OneElemFifoIfc",
        module_name="mkOneElemFifo",
        interface_def="""
interface OneElemFifoIfc;
    method Action enq(Bit#(8) x);
    method Action deq();
    method Bit#(8) first();
    method Bool notEmpty();
    method Bool notFull();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) data_reg <- mkReg(0);
    Reg#(Bool) full_reg <- mkReg(False);

    method Action enq(Bit#(8) x) if (!full_reg);
        // === YOUR CODE HERE ===
    endmethod

    method Action deq() if (full_reg);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) first() if (full_reg);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bool notEmpty();
        return full_reg;
    endmethod

    method Bool notFull();
        return !full_reg;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) data_reg <- mkReg(0);
    Reg#(Bool) full_reg <- mkReg(False);

    method Action enq(Bit#(8) x) if (!full_reg);
        data_reg <= x;
        full_reg <= True;
    endmethod

    method Action deq() if (full_reg);
        full_reg <= False;
    endmethod

    method Bit#(8) first() if (full_reg);
        return data_reg;
    endmethod

    method Bool notEmpty();
        return full_reg;
    endmethod

    method Bool notFull();
        return !full_reg;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) val = 8'hC0 + truncate(cycle);
        Bool r_ne = ref_dut.notEmpty();
        Bool u_ne = user_dut.notEmpty();
        Bool r_nf = ref_dut.notFull();
        Bool u_nf = user_dut.notFull();
        Bit#(8) r_f = r_ne ? ref_dut.first() : 8'h00;
        Bit#(8) u_f = u_ne ? user_dut.first() : 8'h00;

        if (cycle % 2 == 0 && r_nf && u_nf) begin
            ref_dut.enq(val);
            user_dut.enq(val);
        end else if (cycle % 2 == 1 && r_ne && u_ne) begin
            ref_dut.deq();
            user_dut.deq();
        end

        Bool ok = (r_ne == u_ne) && (r_nf == u_nf) && (r_f == u_f);
        $display("@WAVE cycle=%0d|in=val:0x%02h|ref=ne:%0d,first:0x%02h|user=ne:%0d,first:0x%02h|match=%0d|note=FIFO enq/deq", cycle, val, r_ne?1:0, r_f, u_ne?1:0, u_f, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `enq(Bit#(8) x) if (!full_reg)`, set `data_reg <= x;` and `full_reg <= True;`.",
            "In `deq() if (full_reg)`, set `full_reg <= False;`.",
            "In `first() if (full_reg)`, `return data_reg;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="21_pipeline_skid_buffer",
        number=21,
        title="21. 2-Stage Elastic Compute Pipeline (`FIFOF`)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["FIFOF", "Pipeline", "Elastic Design"],
        description="""
Using BSV's standard `FIFOF` library (`FIFOF#(t) q <- mkFIFOF;`), building a multi-stage elastic pipeline with automatic backpressure is remarkably clean!
A `FIFOF` provides `.enq(x)`, `.deq()`, `.first()`, `.notEmpty()`, and `.notFull()`.

### Task
Build a 2-stage arithmetic pipeline `mkElasticPipe` that computes `y = (x * 3) + 7` across two FIFO stages (`in_q` and `out_q` of type `FIFOF#(Bit#(16))`):
- `method Action put(Bit#(16) x)`: Enqueues `x` into `in_q`.
- `rule stage_compute`: Reads `in_q.first()`, dequeues `in_q`, and enqueues `(in_q.first() * 3) + 7` into `out_q`.
- `method ActionValue#(Bit#(16)) get()`: Dequeues `out_q` and returns `out_q.first()`.
""",
        bsv_vs_verilog="""
**Why Designers Love BSV Pipelines**: Notice you didn't write a single `if (in_q.notEmpty && out_q.notFull)` condition on `rule stage_compute`! Because `in_q.first()`, `in_q.deq()`, and `out_q.enq(...)` have implicit guards, `bsc` automatically fires `stage_compute` if and only if `in_q` has data AND `out_q` has space!
""",
        diagram="""
   put(x) ---> [ in_q (FIFOF) ] ---> rule stage_compute (x*3 + 7) ---> [ out_q (FIFOF) ] ---> get()
""",
        interface_name="ElasticPipeIfc",
        module_name="mkElasticPipe",
        interface_def="""
interface ElasticPipeIfc;
    method Action put(Bit#(16) x);
    method ActionValue#(Bit#(16)) get();
endinterface
""",
        snippet_template="""    FIFOF#(Bit#(16)) in_q <- mkFIFOF;
    FIFOF#(Bit#(16)) out_q <- mkFIFOF;

    // Write rule stage_compute, method put(x), and method get()
    // === YOUR CODE HERE ===
    method Action put(Bit#(16) x);
    endmethod

    method ActionValue#(Bit#(16)) get();
        return ?;
    endmethod""",
        reference_snippet="""    FIFOF#(Bit#(16)) in_q <- mkFIFOF;
    FIFOF#(Bit#(16)) out_q <- mkFIFOF;

    rule stage_compute;
        Bit#(16) x = in_q.first();
        in_q.deq();
        out_q.enq((x * 3) + 7);
    endrule

    method Action put(Bit#(16) x);
        in_q.enq(x);
    endmethod

    method ActionValue#(Bit#(16)) get();
        Bit#(16) y = out_q.first();
        out_q.deq();
        return y;
    endmethod""",
        testbench_body="""    Reg#(Bit#(4)) sent <- mkReg(0);
    Reg#(Bit#(4)) recvd <- mkReg(0);

    rule feed (sent < 6);
        Bit#(16) x = zeroExtend(sent) * 16'd5 + 16'd2;
        ref_dut.put(x);
        user_dut.put(x);
        sent <= sent + 1;
    endrule

    rule drain (recvd < 6);
        Bit#(16) r <- ref_dut.get();
        Bit#(16) u <- user_dut.get();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=item:%0d|ref=out:%0d|user=out:%0d|match=%0d|note=Pipe item %0d", cycle, recvd, r, u, ok ? 1 : 0, recvd);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (recvd == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        recvd <= recvd + 1;
    endrule

    rule tick;
        cycle <= cycle + 1;
        if (cycle > 50) begin
            $display("@SUMMARY total=6 passed=%0d", passed_cnt);
            $finish(0);
        end
    endrule""",
        hints=[
            "In `rule stage_compute;`, read `let x = in_q.first();`, call `in_q.deq();`, and call `out_q.enq((x * 3) + 7);`.",
            "In `put(Bit#(16) x)`, call `in_q.enq(x);`.",
            "In `get()`, call `out_q.deq();` and `return out_q.first();`.",
        ],
    ))

    # =========================================================================
    # TRACK 5: FINITE STATE MACHINES (FSMs) & StmtFSM
    # =========================================================================
    problems.append(_make_problem(
        pid="22_fsm_seq_1011",
        number=22,
        title="22. Overlapping `1011` Sequence Detector FSM",
        track_id="track5_fsms",
        track_title="5. Finite State Machines & StmtFSM",
        difficulty="Medium",
        tags=["FSM", "Sequence Detector", "Mealy/Moore"],
        description="""
A classic digital logic interview & HDLBits problem: detect the bit pattern **`1011`** in a serial 1-bit stream `din` (with **overlapping** sequences allowed, so `1011011` triggers twice!).

Let's use a 4-state `enum` tracking how many prefix bits of `1011` we have matched so far:
- `S_IDLE`: matched nothing (`""`). On `1` -> `S_1`, on `0` -> `S_IDLE`.
- `S_1`: matched `"1"`. On `0` -> `S_10`, on `1` -> `S_1`.
- `S_10`: matched `"10"`. On `1` -> `S_101`, on `0` -> `S_IDLE`.
- `S_101`: matched `"101"`.
  - If `din == 1`, we have completed `"1011"`! Output `1'b1` (`detected = 1`) and transition to `S_1` (since the trailing `1` can start the next `"1011"`!).
  - If `din == 0`, output `1'b0` and transition to `S_10` (since `"101"` + `"0"` ends in `"10"`!).

### Task
Implement `method ActionValue#(Bit#(1)) pushBit(Bit#(1) din)` in `mkSeq1011` returning `1` in the exact cycle `1011` is completed, and `0` otherwise.
""",
        bsv_vs_verilog="""
**Type-Safe FSMs**: In BSV, `Reg#(SeqState) state <- mkReg(S_IDLE);` uses a strongly-typed enum rather than error-prone `localparam` numbers.
""",
        diagram="""
          0            1             0            1 (out=1!)
        +---+        +---+         +---+        +----------+
        v   |        v   |         |   v        v          |
      (S_IDLE) -1-> ( S_1 ) -0-> ( S_10 ) -1-> ( S_101 ) --+
        ^                            |            |
        +-------------0--------------+            +--0--> back to S_10
""",
        interface_name="Seq1011Ifc",
        module_name="mkSeq1011",
        interface_def="""
typedef enum {
    S_IDLE,
    S_1,
    S_10,
    S_101
} SeqState deriving (Bits, Eq);

interface Seq1011Ifc;
    method ActionValue#(Bit#(1)) pushBit(Bit#(1) din);
endinterface
""",
        snippet_template="""    Reg#(SeqState) state <- mkReg(S_IDLE);

    method ActionValue#(Bit#(1)) pushBit(Bit#(1) din);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet="""    Reg#(SeqState) state <- mkReg(S_IDLE);

    method ActionValue#(Bit#(1)) pushBit(Bit#(1) din);
        Bit#(1) det = 0;
        case (state)
            S_IDLE: state <= (din == 1) ? S_1 : S_IDLE;
            S_1:    state <= (din == 0) ? S_10 : S_1;
            S_10:   state <= (din == 1) ? S_101 : S_IDLE;
            S_101: begin
                if (din == 1) begin
                    det = 1;
                    state <= S_1;
                end else begin
                    state <= S_10;
                end
            end
        endcase
        return det;
    endmethod""",
        testbench_body="""    rule test;
        // Bitstream: 1, 0, 1, 1 (det!), 0, 1, 1 (det!), 0, 0, 1, 0, 1, 1 (det!)
        Bit#(1) bits[13] = {1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1};
        Bit#(1) b = bits[cycle];
        Bit#(1) r <- ref_dut.pushBit(b);
        Bit#(1) u <- user_dut.pushBit(b);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=din:%0d|ref=det:%0d|user=det:%0d|match=%0d|note=Seq 1011", cycle, b, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 12) begin
            $display("@SUMMARY total=13 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use `case (state)` with branches for `S_IDLE`, `S_1`, `S_10`, and `S_101`.",
            "In `S_101`, when `din == 1`, return `1` and set `state <= S_1;`. When `din == 0`, return `0` and set `state <= S_10;`.",
            "Check carefully: from `S_101` with `din == 0`, the last two bits seen are `10`, so the next state is `S_10`!",
        ],
    ))

    problems.append(_make_problem(
        pid="23_fsm_traffic",
        number=23,
        title="23. Multi-Cycle Traffic Light Controller FSM",
        track_id="track5_fsms",
        track_title="5. Finite State Machines & StmtFSM",
        difficulty="Medium",
        tags=["FSM", "Timer", "Controller"],
        description="""
Real hardware FSMs often stay in each state for a specific number of clock cycles using a cycle timer register `timer`.

Design a traffic intersection controller `mkTrafficLight` that cycles through 4 states:
1. `NS_GREEN` — lasts **3 cycles** (`timer` counts `0, 1, 2`), then transitions to `NS_YELLOW` (`timer <= 0`)
2. `NS_YELLOW` — lasts **1 cycle** (`timer == 0`), then transitions to `EW_GREEN` (`timer <= 0`)
3. `EW_GREEN` — lasts **3 cycles** (`timer` counts `0, 1, 2`), then transitions to `EW_YELLOW` (`timer <= 0`)
4. `EW_YELLOW` — lasts **1 cycle** (`timer == 0`), then transitions back to `NS_GREEN` (`timer <= 0`)

### Task
Implement `mkTrafficLight` starting in `NS_GREEN` with `timer = 0` on reset, an autonomous `rule tick` advancing the state/timer every clock cycle, and `method TrafficState currentLight()` returning the current state.
""",
        bsv_vs_verilog="""
**Clean State + Timer Separation**: Combining `Reg#(TrafficState) state` and `Reg#(Bit#(2)) timer` inside one `rule tick` makes multi-cycle timing crystal clear.
""",
        diagram="""
   [ NS_GREEN (3 cyc) ] ---> [ NS_YELLOW (1 cyc) ] ---> [ EW_GREEN (3 cyc) ] ---> [ EW_YELLOW (1 cyc) ]
            ^                                                                               |
            +-------------------------------------------------------------------------------+
""",
        interface_name="TrafficLightIfc",
        module_name="mkTrafficLight",
        interface_def="""
typedef enum {
    NS_GREEN,
    NS_YELLOW,
    EW_GREEN,
    EW_YELLOW
} TrafficState deriving (Bits, Eq);

interface TrafficLightIfc;
    method TrafficState currentLight();
endinterface
""",
        snippet_template="""    Reg#(TrafficState) state <- mkReg(NS_GREEN);
    Reg#(Bit#(2)) timer <- mkReg(0);

    // Write a rule that advances `timer` and transitions `state`
    // === YOUR CODE HERE ===

    method TrafficState currentLight();
        return state;
    endmethod""",
        reference_snippet="""    Reg#(TrafficState) state <- mkReg(NS_GREEN);
    Reg#(Bit#(2)) timer <- mkReg(0);

    rule tick;
        case (state)
            NS_GREEN: begin
                if (timer == 2) begin state <= NS_YELLOW; timer <= 0; end
                else timer <= timer + 1;
            end
            NS_YELLOW: begin
                state <= EW_GREEN;
                timer <= 0;
            end
            EW_GREEN: begin
                if (timer == 2) begin state <= EW_YELLOW; timer <= 0; end
                else timer <= timer + 1;
            end
            EW_YELLOW: begin
                state <= NS_GREEN;
                timer <= 0;
            end
        endcase
    endrule

    method TrafficState currentLight();
        return state;
    endmethod""",
        testbench_body="""    rule test;
        TrafficState r = ref_dut.currentLight();
        TrafficState u = user_dut.currentLight();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=clk:1|ref=light:%0d|user=light:%0d|match=%0d|note=Traffic FSM", cycle, pack(r), pack(u), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 11) begin
            $display("@SUMMARY total=12 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "A state lasting 3 cycles has `timer` values `0`, `1`, `2`. When `timer == 2`, reset `timer <= 0` and move to the next state!",
            "A state lasting 1 cycle (`NS_YELLOW` and `EW_YELLOW`) transitions immediately on the next clock edge and keeps `timer <= 0`.",
            "Return `state` in `method TrafficState currentLight()`.",
        ],
    ))

    problems.append(_make_problem(
        pid="24_uart_tx_fsm",
        number=24,
        title="24. UART 8N1 Serial Transmitter FSM",
        track_id="track5_fsms",
        track_title="5. Finite State Machines & StmtFSM",
        difficulty="Medium",
        tags=["UART", "Serial Protocol", "FSM"],
        description="""
A **UART 8N1 Transmitter** serializes an 8-bit byte `data` onto a single wire `tx`:
- **Idle State**: `tx` wire is held HIGH (`1'b1`), and `busy` is `False`.
- When `send(Bit#(8) data)` is called (guarded by `if (!busy)`):
  - Load shift register with `{1'b1, data, 1'b0}` (10 bits: LSB is Start bit `0`, followed by `data[0]`..`data[7]`, and MSB is Stop bit `1`), set bit counter `rem <= 10`, and `busy <= True`.
- Every clock cycle while `busy` (`rem > 0`):
  - `tx()` outputs `shift_reg[0]` (when `!busy`, `tx()` outputs `1'b1`).
  - `rule shift_out (busy)` shifts `shift_reg <= (shift_reg >> 1) | 10'h200;` and decrements `rem <= rem - 1` (setting `busy <= False` when `rem == 1`).

### Task
Implement `mkUartTx` with `send(Bit#(8) data) if (!busy)`, `tx()`, and `isBusy()`.
""",
        bsv_vs_verilog="""
**Framing Hardware Trick**: Packing `{stop_bit (1'b1), data[7:0], start_bit (1'b0)}` into a 10-bit shift register lets a single right-shift rule transmit Start, 8 Data bits, and Stop bit seamlessly!
""",
        diagram="""
   Idle (1) | Start (0) | d0 | d1 | d2 | d3 | d4 | d5 | d6 | d7 | Stop (1) | Idle (1)
   ---------+-----------+----+----+----+----+----+----+----+----+----------+---------
""",
        interface_name="UartTxIfc",
        module_name="mkUartTx",
        interface_def="""
interface UartTxIfc;
    method Action send(Bit#(8) data);
    method Bit#(1) tx();
    method Bool isBusy();
endinterface
""",
        snippet_template="""    Reg#(Bit#(10)) shift_reg <- mkReg(10'h3FF);
    Reg#(Bit#(4))  rem       <- mkReg(0);
    Reg#(Bool)     busy      <- mkReg(False);

    // Write rule shift_out (when busy), method send(data) if (!busy), method tx(), and method isBusy()
    // === YOUR CODE HERE ===
    method Action send(Bit#(8) data) if (!busy);
    endmethod

    method Bit#(1) tx();
        return 1;
    endmethod

    method Bool isBusy();
        return busy;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(10)) shift_reg <- mkReg(10'h3FF);
    Reg#(Bit#(4))  rem       <- mkReg(0);
    Reg#(Bool)     busy      <- mkReg(False);

    rule shift_out (busy);
        shift_reg <= (shift_reg >> 1) | 10'h200;
        if (rem == 1) begin
            busy <= False;
            rem <= 0;
        end else begin
            rem <= rem - 1;
        end
    endrule

    method Action send(Bit#(8) data) if (!busy);
        shift_reg <= {1'b1, data, 1'b0};
        rem <= 10;
        busy <= True;
    endmethod

    method Bit#(1) tx();
        return busy ? shift_reg[0] : 1'b1;
    endmethod

    method Bool isBusy();
        return busy;
    endmethod""",
        testbench_body="""    rule test;
        if (cycle == 0) begin
            ref_dut.send(8'hA5);
            user_dut.send(8'hA5);
        end
        Bit#(1) r_tx = ref_dut.tx();
        Bit#(1) u_tx = user_dut.tx();
        Bool r_b = ref_dut.isBusy();
        Bool u_b = user_dut.isBusy();
        Bool ok = (r_tx == u_tx) && (r_b == u_b);
        $display("@WAVE cycle=%0d|in=byte:0xA5|ref=tx:%0d,busy:%0d|user=tx:%0d,busy:%0d|match=%0d|note=UART bit", cycle, r_tx, r_b?1:0, u_tx, u_b?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 12) begin
            $display("@SUMMARY total=13 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `send(Bit#(8) data) if (!busy)`, set `shift_reg <= {1'b1, data, 1'b0}; rem <= 10; busy <= True;`.",
            "In `rule shift_out (busy);`, shift `shift_reg <= (shift_reg >> 1) | 10'h200;` and if `rem == 1` set `busy <= False; rem <= 0;` else `rem <= rem - 1;`.",
            "In `tx()`, return `busy ? shift_reg[0] : 1'b1;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="25_stmtfsm_burst",
        number=25,
        title="25. Microcoded 4-Step Burst Sequence (`StmtFSM`)",
        track_id="track5_fsms",
        track_title="5. Finite State Machines & StmtFSM",
        difficulty="Medium",
        tags=["StmtFSM", "seq/endseq", "Microcode"],
        description="""
Writing large multi-step control FSMs by hand can be tedious. BSV includes the **`StmtFSM`** library (`import StmtFSM::*;`), which compiles C-like `seq ... endseq` blocks directly into a synthesized hardware FSM!
```bsv
Stmt burst_seq = seq
    acc <= seed;
    acc <= acc * 2;
    acc <= acc + 10;
    acc <= acc ^ 16'h00FF;
endseq;
FSM fsm <- mkFSM(burst_seq);
```
- `fsm.start()` (an `Action` guarded by `fsm.done()`) starts the sequence.
- Each statement inside `seq ... endseq` executes in **1 clock cycle**!
- `fsm.done()` returns `True` when the FSM is idle/finished.

### Task
Use `StmtFSM` (or an explicit 4-step FSM) in `mkBurstSeq` so that calling `start(Bit#(16) seed)` runs the 4-cycle sequence:
1. Cycle 1: `acc <= seed;`
2. Cycle 2: `acc <= acc * 2;`
3. Cycle 3: `acc <= acc + 10;`
4. Cycle 4: `acc <= acc ^ 16'h00FF;`
And `result()` (guarded by `if (fsm.done())`) returns `acc`.
""",
        bsv_vs_verilog="""
**Unique to BSV (`StmtFSM`)**: Verilog has no synthesizable sequential statement sub-language (`#10` delays are simulation-only!). BSV's `StmtFSM` compiles `seq`, `par`, `if`, `while`, and `for` statements into real, synthesizable RTL state machines!
""",
        diagram="""
   start(seed) ---> [Step 1: acc<=seed] -> [Step 2: acc*2] -> [Step 3: acc+10] -> [Step 4: acc^0xFF] ---> result()
""",
        interface_name="BurstSeqIfc",
        module_name="mkBurstSeq",
        interface_def="""
interface BurstSeqIfc;
    method Action start(Bit#(16) seed);
    method Bit#(16) result();
endinterface
""",
        snippet_template="""    Reg#(Bit#(16)) seed_reg <- mkReg(0);
    Reg#(Bit#(16)) acc      <- mkReg(0);

    Stmt s = seq
        // === YOUR CODE HERE (4 sequential steps updating acc from seed_reg) ===
        acc <= seed_reg;
    endseq;
    FSM fsm <- mkFSM(s);

    method Action start(Bit#(16) seed) if (fsm.done());
        seed_reg <= seed;
        fsm.start();
    endmethod

    method Bit#(16) result() if (fsm.done());
        return acc;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(16)) seed_reg <- mkReg(0);
    Reg#(Bit#(16)) acc      <- mkReg(0);

    Stmt s = seq
        acc <= seed_reg;
        acc <= acc * 2;
        acc <= acc + 10;
        acc <= acc ^ 16'h00FF;
    endseq;
    FSM fsm <- mkFSM(s);

    method Action start(Bit#(16) seed) if (fsm.done());
        seed_reg <= seed;
        fsm.start();
    endmethod

    method Bit#(16) result() if (fsm.done());
        return acc;
    endmethod""",
        testbench_body="""    Reg#(Bool) started <- mkReg(False);

    rule kick (!started);
        ref_dut.start(16'd25);
        user_dut.start(16'd25);
        started <= True;
    endrule

    rule check (started);
        Bit#(16) r = ref_dut.result();
        Bit#(16) u = user_dut.result();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=seed:25|ref=res:0x%04h|user=res:0x%04h|match=%0d|note=StmtFSM done", cycle, r, u, ok ? 1 : 0);
        $display("@SUMMARY total=1 passed=%0d", ok ? 1 : 0);
        $finish(0);
    endrule

    rule tick;
        cycle <= cycle + 1;
        if (cycle > 30) begin
            $display("@SUMMARY total=1 passed=0");
            $finish(0);
        end
    endrule""",
        hints=[
            "Inside `Stmt s = seq ... endseq;`, write the 4 actions one after another.",
            "Step 1: `acc <= seed_reg;` Step 2: `acc <= acc * 2;` Step 3: `acc <= acc + 10;` Step 4: `acc <= acc ^ 16'h00FF;`.",
            "Because `result()` is guarded by `if (fsm.done())`, the testbench automatically waits until all 4 steps complete!",
        ],
    ))

    # =========================================================================
    # TRACK 6: RTL PROTOCOLS & COMPUTER ARCHITECTURE
    # =========================================================================
    problems.append(_make_problem(
        pid="26_arbiter_rr4",
        number=26,
        title="26. 4-Port Round-Robin Hardware Arbiter",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["Arbiter", "Round-Robin", "Interconnect"],
        description="""
A **Fixed-Priority Arbiter** can starve low-priority requesters. Industry interconnects (AXI, NoCs, PCIe switches) use a **Round-Robin Arbiter** with a rotating priority pointer `prio` (`Reg#(Bit#(2)) prio <- mkReg(0)`):
- Given a 4-bit request vector `req` (`Bit#(4)`), search the 4 ports starting at `prio`:
  `idx = prio + offset` (for `offset = 0, 1, 2, 3`, wrapping modulo 4).
- The **first** port `idx` with `req[idx] == 1` wins the grant:
  - Return a 1-hot grant vector `grant` (`1 << idx`)
  - Update `prio <= idx + 1` (so the newly granted requester has the lowest priority next cycle!).
- If `req == 4'b0000`, return `4'b0000` and leave `prio` unchanged.

### Task
Implement `method ActionValue#(Bit#(4)) arbitrate(Bit#(4) req)` in `mkArbiterRR4`.
""",
        bsv_vs_verilog="""
**Static Loop + Modulo Indexing**: In BSV, `Bit#(2) idx = prio + fromInteger(i);` automatically wraps modulo 4 because `Bit#(2)` arithmetic is modulo-4!
""",
        diagram="""
   req[3:0] ---> [ Search from prio, prio+1, prio+2, prio+3 (mod 4) ] ---> grant[3:0] (1-hot)
                           |
                    [ prio <= winning_idx + 1 ]
""",
        interface_name="ArbiterRR4Ifc",
        module_name="mkArbiterRR4",
        interface_def="""
interface ArbiterRR4Ifc;
    method ActionValue#(Bit#(4)) arbitrate(Bit#(4) req);
endinterface
""",
        snippet_template="""    Reg#(Bit#(2)) prio <- mkReg(0);

    method ActionValue#(Bit#(4)) arbitrate(Bit#(4) req);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(2)) prio <- mkReg(0);

    method ActionValue#(Bit#(4)) arbitrate(Bit#(4) req);
        Bit#(4) grant = 0;
        Bit#(2) next_prio = prio;
        Bool found = False;
        for (Integer i = 0; i < 4; i = i + 1) begin
            Bit#(2) idx = prio + fromInteger(i);
            if (!found && (req[idx] == 1)) begin
                grant[idx] = 1;
                next_prio = idx + 1;
                found = True;
            end
        end
        prio <= next_prio;
        return grant;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) reqs[8] = {4'b1111, 4'b1111, 4'b1111, 4'b1111, 4'b1010, 4'b1010, 4'b0100, 4'b0000};
        Bit#(4) req = reqs[cycle];
        Bit#(4) r <- ref_dut.arbitrate(req);
        Bit#(4) u <- user_dut.arbitrate(req);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=req:0x%01h|ref=gnt:0x%01h|user=gnt:0x%01h|match=%0d|note=RR Arbiter", cycle, req, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Loop `for (Integer i = 0; i < 4; i = i + 1)` and compute `Bit#(2) idx = prio + fromInteger(i);`.",
            "Use a `Bool found = False;` variable so only the first matching `req[idx] == 1` sets `grant[idx] = 1` and `next_prio = idx + 1`.",
            "Update `prio <= next_prio;` and `return grant;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="27_credit_flow_ctrl",
        number=27,
        title="27. Credit-Based Flow Control Transmitter",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Medium",
        tags=["Flow Control", "Credits", "NoC/PCIe"],
        description="""
In high-speed chip interconnects (PCIe, CXL, Network-on-Chip), a transmitter tracks how many free buffer slots (**credits**) the downstream receiver currently has:
- On reset, `credits` (`Reg#(Bit#(4))`) starts at `4'd4` (downstream has 4 free buffer slots).
- `sendFlit()` (`Action` method, guarded by `if (credits > 0)`): consumes 1 credit.
- `creditReturn()` (`Action` method): replenishes 1 credit from downstream.
- **Crucial Concurrency Requirement**: Both `sendFlit()` and `creditReturn()` can be called in the **same clock cycle**! (If both happen in the same cycle, `credits` stays unchanged!).

### Task
Implement `mkCreditTx` using `PulseWire` (or `Ehr`) so `sendFlit()` and `creditReturn()` are conflict-free and `availableCredits()` returns the current credit count.
""",
        bsv_vs_verilog="""
**Zero-Bubble Flow Control**: Using `PulseWire` for `send_w` and `ret_w` lets the transmitter send a flit and receive a returned credit simultaneously without losing a credit!
""",
        diagram="""
   sendFlit() [if credits > 0] ---> [ credits - 1 ]
                                    [   Reg = 4   ] ---> availableCredits()
   creditReturn() ----------------> [ credits + 1 ]
""",
        interface_name="CreditTxIfc",
        module_name="mkCreditTx",
        interface_def="""
interface CreditTxIfc;
    method Action sendFlit();
    method Action creditReturn();
    method Bit#(4) availableCredits();
endinterface
""",
        snippet_template="""    Reg#(Bit#(4)) credits <- mkReg(4);
    PulseWire send_w <- mkPulseWire;
    PulseWire ret_w  <- mkPulseWire;

    // Write rule update_credits and the interface methods
    // === YOUR CODE HERE ===
    method Action sendFlit() if (credits > 0);
    endmethod

    method Action creditReturn();
    endmethod

    method Bit#(4) availableCredits();
        return credits;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(4)) credits <- mkReg(4);
    PulseWire send_w <- mkPulseWire;
    PulseWire ret_w  <- mkPulseWire;

    rule update_credits;
        if (send_w && !ret_w) credits <= credits - 1;
        else if (!send_w && ret_w) credits <= credits + 1;
    endrule

    method Action sendFlit() if (credits > 0);
        send_w.send();
    endmethod

    method Action creditReturn();
        ret_w.send();
    endmethod

    method Bit#(4) availableCredits();
        return credits;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) r_c = ref_dut.availableCredits();
        Bit#(4) u_c = user_dut.availableCredits();
        if (cycle < 3) begin
            ref_dut.sendFlit();
            user_dut.sendFlit();
        end else if (cycle < 5) begin
            ref_dut.sendFlit();
            ref_dut.creditReturn();
            user_dut.sendFlit();
            user_dut.creditReturn();
        end else begin
            ref_dut.creditReturn();
            user_dut.creditReturn();
        end
        Bool ok = (r_c == u_c);
        $display("@WAVE cycle=%0d|in=cyc:%0d|ref=cred:%0d|user=cred:%0d|match=%0d|note=Credit flow", cycle, cycle, r_c, u_c, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `sendFlit() if (credits > 0)`, call `send_w.send();`.",
            "In `creditReturn()`, call `ret_w.send();`.",
            "In `rule update_credits;`, if `send_w && !ret_w` do `credits <= credits - 1;`, else if `!send_w && ret_w` do `credits <= credits + 1;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="28_axi_lite_slave",
        number=28,
        title="28. AXI4-Lite 4-Register Slave Bank with Write Strobe",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["AXI4-Lite", "Register File", "Byte Strobe"],
        description="""
Almost every memory-mapped peripheral IP block exposes an **AXI4-Lite Slave Register Bank** with byte-enable write strobes (`wstrb`):
- Hold 4 registers of 32 bits (`Vector#(4, Reg#(Bit#(32))) regs <- replicateM(mkReg(0));`).
- `writeReq(Bit#(2) addr, Bit#(32) wdata, Bit#(4) wstrb)`:
  - Updates `regs[addr]` byte-by-byte according to `wstrb[3:0]`:
    - If `wstrb[0] == 1`, update bits `[7:0]` with `wdata[7:0]`
    - If `wstrb[1] == 1`, update bits `[15:8]` with `wdata[15:8]`
    - If `wstrb[2] == 1`, update bits `[23:16]` with `wdata[23:16]`
    - If `wstrb[3] == 1`, update bits `[31:24]` with `wdata[31:24]`
- `readReq(Bit#(2) addr)`: Returns the 32-bit value of `regs[addr]`.

### Task
Implement `writeReq` and `readReq` in `mkAxiLiteSlave`.
""",
        bsv_vs_verilog="""
**Vector of Registers (`replicateM`)**: In BSV, `Vector#(4, Reg#(Bit#(32))) regs <- replicateM(mkReg(0));` instantiates a 4-element array of 32-bit registers in a single line!
""",
        diagram="""
   addr[1:0], wdata[31:0], wstrb[3:0] ---> [ Byte-Mask Merge ] ---> regs[addr] ---> readReq(addr)
""",
        interface_name="AxiLiteSlaveIfc",
        module_name="mkAxiLiteSlave",
        interface_def="""
interface AxiLiteSlaveIfc;
    method Action writeReq(Bit#(2) addr, Bit#(32) wdata, Bit#(4) wstrb);
    method Bit#(32) readReq(Bit#(2) addr);
endinterface
""",
        snippet_template="""    Vector#(4, Reg#(Bit#(32))) regs <- replicateM(mkReg(0));

    method Action writeReq(Bit#(2) addr, Bit#(32) wdata, Bit#(4) wstrb);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(32) readReq(Bit#(2) addr);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Vector#(4, Reg#(Bit#(32))) regs <- replicateM(mkReg(0));

    method Action writeReq(Bit#(2) addr, Bit#(32) wdata, Bit#(4) wstrb);
        Bit#(32) old_val = regs[addr];
        Bit#(8) b0 = (wstrb[0] == 1) ? wdata[7:0]   : old_val[7:0];
        Bit#(8) b1 = (wstrb[1] == 1) ? wdata[15:8]  : old_val[15:8];
        Bit#(8) b2 = (wstrb[2] == 1) ? wdata[23:16] : old_val[23:16];
        Bit#(8) b3 = (wstrb[3] == 1) ? wdata[31:24] : old_val[31:24];
        regs[addr] <= {b3, b2, b1, b0};
    endmethod

    method Bit#(32) readReq(Bit#(2) addr);
        return regs[addr];
    endmethod""",
        testbench_body="""    rule test;
        Bit#(2) r_addr = truncate(cycle);
        Bit#(32) r_val = ref_dut.readReq(r_addr);
        Bit#(32) u_val = user_dut.readReq(r_addr);
        if (cycle == 0) begin
            ref_dut.writeReq(2'd0, 32'hDEADBEEF, 4'b1111);
            user_dut.writeReq(2'd0, 32'hDEADBEEF, 4'b1111);
        end else if (cycle == 1) begin
            ref_dut.writeReq(2'd0, 32'h1234CAFE, 4'b0011);
            user_dut.writeReq(2'd0, 32'h1234CAFE, 4'b0011);
        end else if (cycle == 2) begin
            ref_dut.writeReq(2'd1, 32'hAABBCCDD, 4'b1010);
            user_dut.writeReq(2'd1, 32'hAABBCCDD, 4'b1010);
        end
        Bit#(32) r0 = ref_dut.readReq(0);
        Bit#(32) u0 = user_dut.readReq(0);
        Bit#(32) r1 = ref_dut.readReq(1);
        Bit#(32) u1 = user_dut.readReq(1);
        Bool ok = (r0 == u0) && (r1 == u1) && (r_val == u_val);
        $display("@WAVE cycle=%0d|in=addr:%0d|ref=reg0:0x%08h,reg1:0x%08h|user=reg0:0x%08h,reg1:0x%08h|match=%0d|note=AXI-Lite WSTRB", cycle, r_addr, r0, r1, u0, u1, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Read the existing register value first: `Bit#(32) old_val = regs[addr];`.",
            "Select each byte `b0`..`b3` based on `wstrb[0]`..`wstrb[3]`.",
            "Write back `regs[addr] <= {b3, b2, b1, b0};`, and in `readReq(addr)` return `regs[addr]`.",
        ],
    ))

    problems.append(_make_problem(
        pid="29_booth_mult",
        number=29,
        title="29. Multi-Cycle Shift-and-Add 8x8 Multiplier",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["Multiplier", "Datapath", "MIT 6.175"],
        description="""
In area-constrained ASICs or multi-cycle functional units (MIT 6.175 Lab 2), an 8x8 multiplier is implemented sequentially over 8 clock cycles using **Shift-and-Add**:
- Registers:
  - `Reg#(Bit#(16)) mcand <- mkReg(0)` (multiplicand, zero-extended to 16 bits)
  - `Reg#(Bit#(8))  mplier <- mkReg(0)` (multiplier)
  - `Reg#(Bit#(16)) prod <- mkReg(0)` (accumulated product)
  - `Reg#(Bit#(4))  step <- mkReg(8)` (starts at 8 = idle/done!)
- `start(Bit#(8) a, Bit#(8) b) if (step == 8)`:
  - Sets `mcand <= zeroExtend(a); mplier <= b; prod <= 0; step <= 0;`
- `rule calc (step < 8)`:
  - If `mplier[0] == 1`, `prod <= prod + mcand;`
  - Shift `mcand <= mcand << 1;` and `mplier <= mplier >> 1;`
  - Increment `step <= step + 1;`
- `getResult() if (step == 8)`: returns `prod`.

### Task
Implement `mkShiftAddMult` with `start`, `rule calc`, and `getResult`.
""",
        bsv_vs_verilog="""
**Clean Datapath Control**: The single condition `step == 8` acts as the implicit ready guard for both `start` and `getResult`, while `step < 8` drives the 8-cycle shift-and-add loop!
""",
        diagram="""
   mcand[15:0] <-- (<< 1)       mplier[7:0] --> (>> 1)
        |                            | mplier[0]
        +---> [ + prod ] <-----------+
""",
        interface_name="ShiftAddMultIfc",
        module_name="mkShiftAddMult",
        interface_def="""
interface ShiftAddMultIfc;
    method Action start(Bit#(8) a, Bit#(8) b);
    method Bit#(16) getResult();
endinterface
""",
        snippet_template="""    Reg#(Bit#(16)) mcand  <- mkReg(0);
    Reg#(Bit#(8))  mplier <- mkReg(0);
    Reg#(Bit#(16)) prod   <- mkReg(0);
    Reg#(Bit#(4))  step   <- mkReg(8);

    // Write rule calc (step < 8), method start(a, b) if (step == 8), and method getResult() if (step == 8)
    // === YOUR CODE HERE ===
    method Action start(Bit#(8) a, Bit#(8) b) if (step == 8);
    endmethod

    method Bit#(16) getResult() if (step == 8);
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(16)) mcand  <- mkReg(0);
    Reg#(Bit#(8))  mplier <- mkReg(0);
    Reg#(Bit#(16)) prod   <- mkReg(0);
    Reg#(Bit#(4))  step   <- mkReg(8);

    rule calc (step < 8);
        if (mplier[0] == 1) begin
            prod <= prod + mcand;
        end
        mcand <= mcand << 1;
        mplier <= mplier >> 1;
        step <= step + 1;
    endrule

    method Action start(Bit#(8) a, Bit#(8) b) if (step == 8);
        mcand <= zeroExtend(a);
        mplier <= b;
        prod <= 0;
        step <= 0;
    endmethod

    method Bit#(16) getResult() if (step == 8);
        return prod;
    endmethod""",
        testbench_body="""    Reg#(Bit#(3)) idx <- mkReg(0);
    Reg#(Bool) running <- mkReg(False);

    rule issue (!running && idx < 4);
        Bit#(8) va[4] = {8'd12, 8'd25, 8'd255, 8'd0};
        Bit#(8) vb[4] = {8'd11, 8'd16, 8'd255, 8'd99};
        ref_dut.start(va[idx], vb[idx]);
        user_dut.start(va[idx], vb[idx]);
        running <= True;
    endrule

    rule check (running);
        Bit#(16) r = ref_dut.getResult();
        Bit#(16) u = user_dut.getResult();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=test:%0d|ref=prod:%0d|user=prod:%0d|match=%0d|note=Mult test %0d", cycle, idx, r, u, ok ? 1 : 0, idx);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        running <= False;
        if (idx == 3) begin
            $display("@SUMMARY total=4 passed=%0d", np);
            $finish(0);
        end
        idx <= idx + 1;
    endrule

    rule tick;
        cycle <= cycle + 1;
        if (cycle > 100) begin
            $display("@SUMMARY total=4 passed=%0d", passed_cnt);
            $finish(0);
        end
    endrule""",
        hints=[
            "In `start(a, b) if (step == 8)`, set `mcand <= zeroExtend(a); mplier <= b; prod <= 0; step <= 0;`.",
            "In `rule calc (step < 8)`, add `mcand` to `prod` when `mplier[0] == 1`, shift `mcand <= mcand << 1;`, `mplier <= mplier >> 1;`, and `step <= step + 1;`.",
            "In `getResult() if (step == 8)`, `return prod;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="30_direct_mapped_cache",
        number=30,
        title="30. Direct-Mapped Cache Tag & Data Lookup Engine",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["Cache", "Computer Architecture", "Maybe"],
        description="""
A **Direct-Mapped Cache** maps each memory address `addr[7:0]` into:
- **Tag**: upper 6 bits `addr[7:2]` (`Bit#(6)`)
- **Index**: lower 2 bits `addr[1:0]` (`Bit#(2)`, selecting 1 of 4 cache lines)

The cache holds three 4-element arrays initialized to `False` / `0`:
- `Vector#(4, Reg#(Bool)) valid_arr <- replicateM(mkReg(False));`
- `Vector#(4, Reg#(Bit#(6))) tag_arr <- replicateM(mkReg(0));`
- `Vector#(4, Reg#(Bit#(16))) data_arr <- replicateM(mkReg(0));`

### Task
Implement two methods in `mkDirectCache`:
1. `lookup(Bit#(8) addr)`: Extract `idx = addr[1:0]` and `tag = addr[7:2]`. If `valid_arr[idx] && (tag_arr[idx] == tag)`, return `tagged Valid data_arr[idx]` (Cache Hit!); otherwise return `tagged Invalid` (Cache Miss!).
2. `fillLine(Bit#(8) addr, Bit#(16) data)`: Populate cache line `idx = addr[1:0]` with `valid_arr[idx] <= True`, `tag_arr[idx] <= addr[7:2]`, and `data_arr[idx] <= data`.
""",
        bsv_vs_verilog="""
**Tagged Union Cache Lookup**: Returning `Maybe#(Bit#(16))` from `lookup(addr)` encodes both the Hit/Miss signal and the 16-bit read data in a single type-safe return value!
""",
        diagram="""
   addr[7:0] = { tag[5:0], idx[1:0] }
                              |
                              v
                 [ valid[idx] | tag[idx] | data[idx] ]
                              |
              (valid && tag == req_tag) ? Valid data[idx] : Invalid
""",
        interface_name="DirectCacheIfc",
        module_name="mkDirectCache",
        interface_def="""
interface DirectCacheIfc;
    method Maybe#(Bit#(16)) lookup(Bit#(8) addr);
    method Action fillLine(Bit#(8) addr, Bit#(16) data);
endinterface
""",
        snippet_template="""    Vector#(4, Reg#(Bool))     valid_arr <- replicateM(mkReg(False));
    Vector#(4, Reg#(Bit#(6)))  tag_arr   <- replicateM(mkReg(0));
    Vector#(4, Reg#(Bit#(16))) data_arr  <- replicateM(mkReg(0));

    method Maybe#(Bit#(16)) lookup(Bit#(8) addr);
        // === YOUR CODE HERE ===
        return tagged Invalid;
    endmethod

    method Action fillLine(Bit#(8) addr, Bit#(16) data);
        // === YOUR CODE HERE ===
    endmethod""",
        reference_snippet="""    Vector#(4, Reg#(Bool))     valid_arr <- replicateM(mkReg(False));
    Vector#(4, Reg#(Bit#(6)))  tag_arr   <- replicateM(mkReg(0));
    Vector#(4, Reg#(Bit#(16))) data_arr  <- replicateM(mkReg(0));

    method Maybe#(Bit#(16)) lookup(Bit#(8) addr);
        Bit#(2) idx = addr[1:0];
        Bit#(6) tag = addr[7:2];
        if (valid_arr[idx] && (tag_arr[idx] == tag))
            return tagged Valid data_arr[idx];
        else
            return tagged Invalid;
    endmethod

    method Action fillLine(Bit#(8) addr, Bit#(16) data);
        Bit#(2) idx = addr[1:0];
        Bit#(6) tag = addr[7:2];
        valid_arr[idx] <= True;
        tag_arr[idx]   <= tag;
        data_arr[idx]  <= data;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) q_addrs[6] = {8'h10, 8'h10, 8'h14, 8'h14, 8'h10, 8'h21};
        Bit#(8) qa = q_addrs[cycle];
        Maybe#(Bit#(16)) r = ref_dut.lookup(qa);
        Maybe#(Bit#(16)) u = user_dut.lookup(qa);
        if (cycle == 0) begin
            ref_dut.fillLine(8'h10, 16'hCAFE);
            user_dut.fillLine(8'h10, 16'hCAFE);
        end else if (cycle == 2) begin
            // Alias to same cache line index 0 (0x14 = tag 5, idx 0) -> evicts 0x10!
            ref_dut.fillLine(8'h14, 16'hBEEF);
            user_dut.fillLine(8'h14, 16'hBEEF);
        end
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=addr:0x%02h|ref=hit:%0d,data:0x%04h|user=hit:%0d,data:0x%04h|match=%0d|note=Cache lookup", cycle, qa, isValid(r)?1:0, fromMaybe(0,r), isValid(u)?1:0, fromMaybe(0,u), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Slice `Bit#(2) idx = addr[1:0];` and `Bit#(6) tag = addr[7:2];`.",
            "In `lookup`, if `valid_arr[idx] && (tag_arr[idx] == tag)` return `tagged Valid data_arr[idx];`, else `return tagged Invalid;`.",
            "In `fillLine`, set `valid_arr[idx] <= True; tag_arr[idx] <= addr[7:2]; data_arr[idx] <= data;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="31_pipeline_hazard_scoreboard",
        number=31,
        title="31. Processor Pipeline Scoreboard (RAW Hazard Tracker)",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["Scoreboard", "Hazards", "Processor Pipeline"],
        description="""
In an in-order or out-of-order pipelined CPU, a **Scoreboard** tracks which registers (`r0`..`r7`, 3-bit register IDs) have pending writes in flight so the Decode stage can stall on Read-After-Write (RAW) data hazards!
Note that register `r0` (`3'd0`, like RISC-V `x0`) is hardwired to zero and **never causes a hazard** (`busy[0]` is always `False`).

### Task
Using an 8-bit busy bitmask `Reg#(Bit#(8)) busy_mask <- mkReg(0);`:
1. `searchHazard(Bit#(3) src1, Bit#(3) src2)`: Returns `True` if `(src1 != 0 && busy_mask[src1] == 1) || (src2 != 0 && busy_mask[src2] == 1)`, else `False`.
2. `insertDest(Bit#(3) dst)`: If `dst != 0`, sets `busy_mask[dst] <= 1`.
3. `clearDest(Bit#(3) dst)`: Clears `busy_mask[dst] <= 0`.
*(Note: `insertDest` and `clearDest` will not be called in the same cycle in this basic scoreboard).*
""",
        bsv_vs_verilog="""
**Bitmask Scoreboard**: Using `Bit#(8)` bit-indexing `busy_mask[src1]` creates a fast, single-cycle combinational hazard lookup for two source operands in parallel!
""",
        diagram="""
   src1, src2 ---> [ busy_mask (8b) ] ---> searchHazard() (True = Stall!)
   insertDest ---> sets bit[dst] (if dst != 0)
   clearDest  ---> clears bit[dst]
""",
        interface_name="ScoreboardIfc",
        module_name="mkScoreboard",
        interface_def="""
interface ScoreboardIfc;
    method Bool searchHazard(Bit#(3) src1, Bit#(3) src2);
    method Action insertDest(Bit#(3) dst);
    method Action clearDest(Bit#(3) dst);
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) busy_mask <- mkReg(0);

    method Bool searchHazard(Bit#(3) src1, Bit#(3) src2);
        // === YOUR CODE HERE ===
        return False;
    endmethod

    method Action insertDest(Bit#(3) dst);
        // === YOUR CODE HERE ===
    endmethod

    method Action clearDest(Bit#(3) dst);
        // === YOUR CODE HERE ===
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) busy_mask <- mkReg(0);

    method Bool searchHazard(Bit#(3) src1, Bit#(3) src2);
        Bool h1 = (src1 != 0) && (busy_mask[src1] == 1);
        Bool h2 = (src2 != 0) && (busy_mask[src2] == 1);
        return h1 || h2;
    endmethod

    method Action insertDest(Bit#(3) dst);
        if (dst != 0) begin
            Bit#(8) m = busy_mask;
            m[dst] = 1;
            busy_mask <= m;
        end
    endmethod

    method Action clearDest(Bit#(3) dst);
        Bit#(8) m = busy_mask;
        m[dst] = 0;
        busy_mask <= m;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(3) s1[6] = {3'd0, 3'd1, 3'd2, 3'd3, 3'd3, 3'd0};
        Bit#(3) s2[6] = {3'd1, 3'd2, 3'd3, 3'd4, 3'd0, 3'd0};
        Bool r_h = ref_dut.searchHazard(s1[cycle], s2[cycle]);
        Bool u_h = user_dut.searchHazard(s1[cycle], s2[cycle]);
        if (cycle == 0) begin
            ref_dut.insertDest(3'd0); // x0 ignored!
            user_dut.insertDest(3'd0);
        end else if (cycle == 1) begin
            ref_dut.insertDest(3'd3);
            user_dut.insertDest(3'd3);
        end else if (cycle == 3) begin
            ref_dut.clearDest(3'd3);
            user_dut.clearDest(3'd3);
        end
        Bool ok = (r_h == u_h);
        $display("@WAVE cycle=%0d|in=s1:%0d,s2:%0d|ref=haz:%0d|user=haz:%0d|match=%0d|note=Scoreboard RAW", cycle, s1[cycle], s2[cycle], r_h?1:0, u_h?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `searchHazard(src1, src2)`, return `((src1 != 0) && (busy_mask[src1] == 1)) || ((src2 != 0) && (busy_mask[src2] == 1));`.",
            "In `insertDest(dst)`, if `dst != 0`, copy `Bit#(8) m = busy_mask; m[dst] = 1; busy_mask <= m;`.",
            "In `clearDest(dst)`, copy `Bit#(8) m = busy_mask; m[dst] = 0; busy_mask <= m;`.",
        ],
    ))

    problems.append(_make_problem(
        pid="32_mini_riscv_alu_pc",
        number=32,
        title="32. Capstone: Mini RISC-V Datapath Core (PC + RegFile + Execute)",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["RISC-V", "Processor", "Capstone", "MIT 6.175"],
        description="""
Congratulations on reaching the **Curriculum Capstone**! Let's build an executable single-cycle **Mini RISC-V Datapath** (`mkMiniRiscv`) with:
- A 16-bit Program Counter: `Reg#(Bit#(16)) pc <- mkReg(0);`
- A 4-register 16-bit architectural register file (`x0`..`x3`): `Vector#(4, Reg#(Bit#(16))) rf <- replicateM(mkReg(0));` (where `x0` is always read as `0` and never written!).

Each instruction `MiniInst` has fields:
- `RvOp op`: `RV_ADDI`, `RV_ADD`, `RV_SUB`, or `RV_BEQ`
- `Bit#(2) rd`, `Bit#(2) rs1`, `Bit#(2) rs2`
- `Bit#(16) imm`

When `stepInst(MiniInst inst)` is called:
- Read `v1 = (inst.rs1 == 0) ? 0 : rf[inst.rs1]` and `v2 = (inst.rs2 == 0) ? 0 : rf[inst.rs2]`.
- Execute `inst.op`:
  - `RV_ADDI`: write `v1 + inst.imm` to `rf[inst.rd]` (if `inst.rd != 0`), and advance `pc <= pc + 4`.
  - `RV_ADD`: write `v1 + v2` to `rf[inst.rd]` (if `inst.rd != 0`), and advance `pc <= pc + 4`.
  - `RV_SUB`: write `v1 - v2` to `rf[inst.rd]` (if `inst.rd != 0`), and advance `pc <= pc + 4`.
  - `RV_BEQ`: do not write `rf`; if `v1 == v2`, branch `pc <= pc + inst.imm`, else `pc <= pc + 4`.

### Task
Implement `stepInst(MiniInst inst)`, `getPc()`, and `readReg(Bit#(2) r)` in `mkMiniRiscv`.
""",
        bsv_vs_verilog="""
**From Wire Zero to a RISC-V Core!**: Look how clean a processor execute stage is in BSV using `struct`, `enum`, `Vector#(4, Reg#(Bit#(16)))`, and atomic state transitions!
""",
        diagram="""
   inst ---> [ Decode rs1, rs2 ] ---> [ ALU (ADDI/ADD/SUB/BEQ) ] ---> rf[rd] (if rd != 0)
                                                 |
                                                 +------------------> pc <= (BEQ taken ? pc+imm : pc+4)
""",
        interface_name="MiniRiscvIfc",
        module_name="mkMiniRiscv",
        interface_def="""
typedef enum {
    RV_ADDI,
    RV_ADD,
    RV_SUB,
    RV_BEQ
} RvOp deriving (Bits, Eq);

typedef struct {
    RvOp     op;
    Bit#(2)  rd;
    Bit#(2)  rs1;
    Bit#(2)  rs2;
    Bit#(16) imm;
} MiniInst deriving (Bits, Eq);

interface MiniRiscvIfc;
    method Action stepInst(MiniInst inst);
    method Bit#(16) getPc();
    method Bit#(16) readReg(Bit#(2) r);
endinterface
""",
        snippet_template="""    Reg#(Bit#(16)) pc <- mkReg(0);
    Vector#(4, Reg#(Bit#(16))) rf <- replicateM(mkReg(0));

    method Action stepInst(MiniInst inst);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(16) getPc();
        return pc;
    endmethod

    method Bit#(16) readReg(Bit#(2) r);
        return (r == 0) ? 0 : rf[r];
    endmethod""",
        reference_snippet="""    Reg#(Bit#(16)) pc <- mkReg(0);
    Vector#(4, Reg#(Bit#(16))) rf <- replicateM(mkReg(0));

    method Action stepInst(MiniInst inst);
        Bit#(16) v1 = (inst.rs1 == 0) ? 0 : rf[inst.rs1];
        Bit#(16) v2 = (inst.rs2 == 0) ? 0 : rf[inst.rs2];
        case (inst.op)
            RV_ADDI: begin
                if (inst.rd != 0) rf[inst.rd] <= v1 + inst.imm;
                pc <= pc + 4;
            end
            RV_ADD: begin
                if (inst.rd != 0) rf[inst.rd] <= v1 + v2;
                pc <= pc + 4;
            end
            RV_SUB: begin
                if (inst.rd != 0) rf[inst.rd] <= v1 - v2;
                pc <= pc + 4;
            end
            RV_BEQ: begin
                pc <= (v1 == v2) ? (pc + inst.imm) : (pc + 4);
            end
        endcase
    endmethod

    method Bit#(16) getPc();
        return pc;
    endmethod

    method Bit#(16) readReg(Bit#(2) r);
        return (r == 0) ? 0 : rf[r];
    endmethod""",
        testbench_body="""    rule test;
        MiniInst prog[6] = {
            MiniInst { op: RV_ADDI, rd: 1, rs1: 0, rs2: 0, imm: 16'd10 }, // x1 = 10
            MiniInst { op: RV_ADDI, rd: 2, rs1: 0, rs2: 0, imm: 16'd25 }, // x2 = 25
            MiniInst { op: RV_ADD,  rd: 3, rs1: 1, rs2: 2, imm: 16'd0  }, // x3 = 35
            MiniInst { op: RV_SUB,  rd: 1, rs1: 3, rs2: 1, imm: 16'd0  }, // x1 = 25
            MiniInst { op: RV_BEQ,  rd: 0, rs1: 1, rs2: 2, imm: 16'd16 }, // x1==x2 (25==25) -> pc += 16
            MiniInst { op: RV_ADDI, rd: 0, rs1: 1, rs2: 0, imm: 16'd99 }  // write to x0 ignored
        };
        MiniInst inst = prog[cycle];
        ref_dut.stepInst(inst);
        user_dut.stepInst(inst);

        Bit#(16) r_pc = ref_dut.getPc();
        Bit#(16) u_pc = user_dut.getPc();
        Bit#(16) r_x1 = ref_dut.readReg(1);
        Bit#(16) u_x1 = user_dut.readReg(1);
        Bit#(16) r_x3 = ref_dut.readReg(3);
        Bit#(16) u_x3 = user_dut.readReg(3);
        Bit#(16) r_x0 = ref_dut.readReg(0);
        Bit#(16) u_x0 = user_dut.readReg(0);
        Bool ok = (r_pc == u_pc) && (r_x1 == u_x1) && (r_x3 == u_x3) && (r_x0 == u_x0);
        $display("@WAVE cycle=%0d|in=op:%0d,rd:%0d|ref=pc:0x%02h,x1:%0d,x3:%0d|user=pc:0x%02h,x1:%0d,x3:%0d|match=%0d|note=RISC-V exec", cycle, pack(inst.op), inst.rd, r_pc, r_x1, r_x3, u_pc, u_x1, u_x3, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Read `v1 = (inst.rs1 == 0) ? 0 : rf[inst.rs1];` and `v2 = (inst.rs2 == 0) ? 0 : rf[inst.rs2];`.",
            "For `RV_ADDI`, `RV_ADD`, `RV_SUB`, guard the register write with `if (inst.rd != 0) rf[inst.rd] <= ...;` and update `pc <= pc + 4;`.",
            "For `RV_BEQ`, update `pc <= (v1 == v2) ? (pc + inst.imm) : (pc + 4);`.",
        ],
    ))

    return problems


CURRICULUM_PROBLEMS: List[Dict[str, Any]] = _build_all_problems()
CURRICULUM_BY_ID: Dict[str, Dict[str, Any]] = {p["id"]: p for p in CURRICULUM_PROBLEMS}
