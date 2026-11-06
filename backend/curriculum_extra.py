"""
Expanded Curriculum Problems for BSVbits (64 Additional Stored Problems across 10 Tracks).
Covers:
  - Granular beginner steps + multi-concept Combination Labs in Combinational, Arithmetic, Types & Sequential tracks
  - Advanced Concurrency: RWire, descending_urgency, 3-port CReg/Ehr, Bypass RegFile, ConfigReg, Token Bucket, Banked Memory
  - Advanced FIFOs & Standard Interfaces: SpecialFIFOs (mkBypassFIFOF, mkPipelineFIFOF), Watermark FIFO, GetPut, ClientServer, Connectable, Packet Firewall, 8-to-16 Gearbox
  - Clock Domain Crossing (CDC) & Clocks Package Principles: 2-FF SyncBit, Toggle SyncPulse, Gray Pointer Codec, Async FIFO Full/Empty in Gray domain, MCP Req/Ack Handshake, Reset Stretcher, Credit Crossing, Ping-Pong Bridge
  - Verification, Testbenches & Property Checkers Track: Stimulus Gen, Scoreboard, StmtFSM Driver, FIFO Invariant Monitor, Arbiter Mutex Checker, LFSR Coverage Fuzzer, Latency Profiler, Bug-Hunting Lab, Ready/Valid Stability Monitor
  - Peripheral & Interconnect Protocols: SPI Master, AMBA APB3 Slave, AXI4-Stream Framer, Wishbone Slave, 2D Mesh NoC XY Router
  - Computer Architecture: Restoring Divider, 2-Way Set-Associative LRU Cache, 2-Bit Branch Predictor (BHT), Pipeline Forwarding Unit, Reorder Buffer (ROB), RISC-V RV32I Immediate Generator
"""

from __future__ import annotations
from typing import Any, Dict, List

DEFAULT_IMPORTS = (
    "import Vector::*; import FIFOF::*; import SpecialFIFOs::*; import Ehr::*; "
    "import StmtFSM::*; import DReg::*; import ConfigReg::*; import GetPut::*; "
    "import ClientServer::*; import Connectable::*;"
)


def build_extra_problems(make_prob_fn: Any) -> List[Dict[str, Any]]:
    probs: List[Dict[str, Any]] = []

    def add(
        pid: str,
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
    ) -> None:
        probs.append(
            make_prob_fn(
                pid=pid,
                number=0,  # renumbered sequentially in curriculum.py
                title=title,
                track_id=track_id,
                track_title=track_title,
                difficulty=difficulty,
                tags=tags,
                description=description,
                bsv_vs_verilog=bsv_vs_verilog,
                diagram=diagram,
                interface_name=interface_name,
                module_name=module_name,
                interface_def=interface_def,
                snippet_template=snippet_template,
                reference_snippet=reference_snippet,
                testbench_body=testbench_body,
                hints=hints,
                package_imports=DEFAULT_IMPORTS,
            )
        )

    # =========================================================================
    # TRACK 1 ADDITIONS: COMBINATIONAL GATES & COMBINATION LABS
    # =========================================================================
    add(
        pid="01b_wire_constants",
        title="Sized Binary, Hex & Decimal Hardware Constants",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Literals", "Bit#(n)", "Syntax"],
        description="""
In BSV, hardware constants can be written with explicit bit-widths and bases just like Verilog:
- Binary: `4'b1010` (4 bits)
- Hexadecimal: `8'hA5` (8 bits)
- Decimal: `16'd1000` (16 bits)

### Task
Implement three constant value methods in `mkWireConstants`:
1. `constOne()` -> returns `1'b1` (`Bit#(1)`)
2. `constNibbles()` -> returns `8'hA5` (`Bit#(8)`)
3. `constMask()` -> returns `16'hFF00` (`Bit#(16)`)
""",
        bsv_vs_verilog="BSV checks that any sized literal `8'hA5` matches the exact `Bit#(8)` width of the target expression — catching accidental width mismatches at compile time!",
        diagram="mkWireConstants ---> constOne()=1'b1, constNibbles()=8'hA5, constMask()=16'hFF00",
        interface_name="WireConstantsIfc",
        module_name="mkWireConstants",
        interface_def="""
interface WireConstantsIfc;
    method Bit#(1)  constOne();
    method Bit#(8)  constNibbles();
    method Bit#(16) constMask();
endinterface
""",
        snippet_template="""    method Bit#(1) constOne();
        return ?;
    endmethod
    method Bit#(8) constNibbles();
        return ?;
    endmethod
    method Bit#(16) constMask();
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(1) constOne();
        return 1'b1;
    endmethod
    method Bit#(8) constNibbles();
        return 8'hA5;
    endmethod
    method Bit#(16) constMask();
        return 16'hFF00;
    endmethod""",
        testbench_body="""    rule test;
        Bool ok = (ref_dut.constOne() == user_dut.constOne()) &&
                  (ref_dut.constNibbles() == user_dut.constNibbles()) &&
                  (ref_dut.constMask() == user_dut.constMask());
        $display("@WAVE cycle=0|in=none:0|ref=c1:%0d,c8:0x%02h,c16:0x%04h|user=c1:%0d,c8:0x%02h,c16:0x%04h|match=%0d|note=Constants",
            ref_dut.constOne(), ref_dut.constNibbles(), ref_dut.constMask(),
            user_dut.constOne(), user_dut.constNibbles(), user_dut.constMask(), ok ? 1 : 0);
        $display("@SUMMARY total=1 passed=%0d", ok ? 1 : 0);
        $finish(0);
    endrule""",
        hints=[
            "Return `1'b1` from `constOne()`.",
            "Return `8'hA5` from `constNibbles()`.",
            "Return `16'hFF00` from `constMask()`.",
        ],
    )

    add(
        pid="03b_gates_universal",
        title="Universal Gates & Compound Logic (NOR, XNOR, AOI21)",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Universal Gates", "NOR", "XNOR", "AOI"],
        description="""
In CMOS VLSI cell libraries, **NOR**, **XNOR**, and **AND-OR-Invert (AOI21)** are fundamental standard cells because CMOS transistors naturally invert signals:
- `gateNor(a, b)` = `~(a | b)`
- `gateXnor(a, b)` = `~(a ^ b)`
- `gateAoi21(a, b, c)` = `~((a & b) | c)`

### Task
Implement `gateNor`, `gateXnor`, and `gateAoi21` on 4-bit inputs (`Bit#(4)`) in `mkGatesUniversal`.
""",
        bsv_vs_verilog="Parentheses around `~(a | b)` and `~((a & b) | c)` ensure bitwise inversion `~` is applied after `&` / `|`.",
        diagram="a, b, c ---> [ NOR: ~(a|b) ] [ XNOR: ~(a^b) ] [ AOI21: ~((a&b)|c) ]",
        interface_name="GatesUniversalIfc",
        module_name="mkGatesUniversal",
        interface_def="""
interface GatesUniversalIfc;
    method Bit#(4) gateNor(Bit#(4) a, Bit#(4) b);
    method Bit#(4) gateXnor(Bit#(4) a, Bit#(4) b);
    method Bit#(4) gateAoi21(Bit#(4) a, Bit#(4) b, Bit#(4) c);
endinterface
""",
        snippet_template="""    method Bit#(4) gateNor(Bit#(4) a, Bit#(4) b);
        return ?;
    endmethod
    method Bit#(4) gateXnor(Bit#(4) a, Bit#(4) b);
        return ?;
    endmethod
    method Bit#(4) gateAoi21(Bit#(4) a, Bit#(4) b, Bit#(4) c);
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(4) gateNor(Bit#(4) a, Bit#(4) b);
        return ~(a | b);
    endmethod
    method Bit#(4) gateXnor(Bit#(4) a, Bit#(4) b);
        return ~(a ^ b);
    endmethod
    method Bit#(4) gateAoi21(Bit#(4) a, Bit#(4) b, Bit#(4) c);
        return ~((a & b) | c);
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) a = truncate(cycle * 3);
        Bit#(4) b = truncate(cycle * 5 + 1);
        Bit#(4) c = truncate(cycle * 7 + 2);
        Bit#(4) r1 = ref_dut.gateNor(a, b);
        Bit#(4) r2 = ref_dut.gateXnor(a, b);
        Bit#(4) r3 = ref_dut.gateAoi21(a, b, c);
        Bit#(4) u1 = user_dut.gateNor(a, b);
        Bit#(4) u2 = user_dut.gateXnor(a, b);
        Bit#(4) u3 = user_dut.gateAoi21(a, b, c);
        Bool ok = (r1 == u1) && (r2 == u2) && (r3 == u3);
        $display("@WAVE cycle=%0d|in=a:0x%01h,b:0x%01h,c:0x%01h|ref=nor:0x%01h,xnor:0x%01h,aoi:0x%01h|user=nor:0x%01h,xnor:0x%01h,aoi:0x%01h|match=%0d|note=Universal", cycle, a, b, c, r1, r2, r3, u1, u2, u3, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use `return ~(a | b);` for `gateNor`.",
            "Use `return ~(a ^ b);` for `gateXnor`.",
            "Use `return ~((a & b) | c);` for `gateAoi21`.",
        ],
    )

    add(
        pid="03c_majority_voter",
        title="Triple-Modular Redundancy (TMR) 3-Input Majority Voter",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Majority Voter", "TMR", "Combinational"],
        description="""
In radiation-hardened spacecraft and safety-critical VLSI systems, **Triple Modular Redundancy (TMR)** runs three copies of a module (`a`, `b`, `c`) into a **Majority Voter**:
- For each bit position, output `1` if **at least 2 of the 3 inputs** are `1`:
  `maj = (a & b) | (b & c) | (a & c)`

### Task
Implement an 8-bit bitwise majority voter `vote(Bit#(8) a, Bit#(8) b, Bit#(8) c)` in `mkMajorityVoter`.
""",
        bsv_vs_verilog="Bitwise `(a & b) | (b & c) | (a & c)` votes on all 8 bit lanes simultaneously in parallel.",
        diagram="a[7:0], b[7:0], c[7:0] ---> [ (a&b) | (b&c) | (a&c) ] ---> vote[7:0]",
        interface_name="MajorityVoterIfc",
        module_name="mkMajorityVoter",
        interface_def="""
interface MajorityVoterIfc;
    method Bit#(8) vote(Bit#(8) a, Bit#(8) b, Bit#(8) c);
endinterface
""",
        snippet_template="""    method Bit#(8) vote(Bit#(8) a, Bit#(8) b, Bit#(8) c);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(8) vote(Bit#(8) a, Bit#(8) b, Bit#(8) c);
        return (a & b) | (b & c) | (a & c);
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) a = 8'hF0 ^ cycle[7:0];
        Bit#(8) b = 8'hCC ^ (cycle[7:0] * 3);
        Bit#(8) c = 8'hAA ^ (cycle[7:0] * 5);
        Bit#(8) r = ref_dut.vote(a, b, c);
        Bit#(8) u = user_dut.vote(a, b, c);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=a:0x%02h,b:0x%02h,c:0x%02h|ref=maj:0x%02h|user=maj:0x%02h|match=%0d|note=TMR Vote", cycle, a, b, c, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Combine pairwise ANDs with OR: `(a & b) | (b & c) | (a & c)`.",
            "Notice this is also the exact carry-out equation of a Full Adder!",
            "Return `(a & b) | (b & c) | (a & c);`.",
        ],
    )

    add(
        pid="03d_half_full_adder",
        title="1-Bit Half Adder & Full Adder Building Blocks",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Half Adder", "Full Adder", "Gates"],
        description="""
Before building multi-bit arithmetic units, let's master the two atomic adder cells:
1. **Half Adder (`halfAdd(a, b)`)**: Adds two 1-bit inputs `a` and `b`, returning 2-bit `{cout, sum}` where `sum = a ^ b` and `cout = a & b`.
2. **Full Adder (`fullAdd(a, b, cin)`)**: Adds three 1-bit inputs `a`, `b`, and `cin`, returning 2-bit `{cout, sum}` where `sum = a ^ b ^ cin` and `cout = (a & b) | (b & cin) | (a & cin)`.

### Task
Implement both `halfAdd` and `fullAdd` in `mkHalfFullAdder`.
""",
        bsv_vs_verilog="Returning `{cout, sum}` (`Bit#(2)`) lets you test or chain adder cells cleanly.",
        diagram="halfAdd(a,b) -> {a&b, a^b}   |   fullAdd(a,b,cin) -> {maj(a,b,cin), a^b^cin}",
        interface_name="HalfFullAdderIfc",
        module_name="mkHalfFullAdder",
        interface_def="""
interface HalfFullAdderIfc;
    method Bit#(2) halfAdd(Bit#(1) a, Bit#(1) b);
    method Bit#(2) fullAdd(Bit#(1) a, Bit#(1) b, Bit#(1) cin);
endinterface
""",
        snippet_template="""    method Bit#(2) halfAdd(Bit#(1) a, Bit#(1) b);
        return ?;
    endmethod

    method Bit#(2) fullAdd(Bit#(1) a, Bit#(1) b, Bit#(1) cin);
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(2) halfAdd(Bit#(1) a, Bit#(1) b);
        return {a & b, a ^ b};
    endmethod

    method Bit#(2) fullAdd(Bit#(1) a, Bit#(1) b, Bit#(1) cin);
        Bit#(1) s = a ^ b ^ cin;
        Bit#(1) c = (a & b) | (b & cin) | (a & cin);
        return {c, s};
    endmethod""",
        testbench_body="""    rule test;
        Bit#(1) a = cycle[0];
        Bit#(1) b = cycle[1];
        Bit#(1) cin = cycle[2];
        Bit#(2) rh = ref_dut.halfAdd(a, b);
        Bit#(2) uh = user_dut.halfAdd(a, b);
        Bit#(2) rf = ref_dut.fullAdd(a, b, cin);
        Bit#(2) uf = user_dut.fullAdd(a, b, cin);
        Bool ok = (rh == uh) && (rf == uf);
        $display("@WAVE cycle=%0d|in=a:%0d,b:%0d,cin:%0d|ref=ha:%0d,fa:%0d|user=ha:%0d,fa:%0d|match=%0d|note=HA/FA", cycle, a, b, cin, rh, rf, uh, uf, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `halfAdd`, return `{a & b, a ^ b};`.",
            "In `fullAdd`, compute `s = a ^ b ^ cin` and `c = (a & b) | (b & cin) | (a & cin)`, then return `{c, s}`.",
            "Make sure `cout` is in bit 1 (left side of `{c, s}`) and `sum` is in bit 0.",
        ],
    )

    add(
        pid="04b_demux_decoder",
        title="2-to-4 One-Hot Decoder & 1-to-4 Demultiplexer",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Decoder", "Demux", "One-Hot"],
        description="""
- A **2-to-4 One-Hot Decoder** takes a 2-bit index `sel` (`0`..`3`) and returns `4'b0001 << sel` (so exactly bit `sel` is `1`).
- A **1-to-4 Demultiplexer** routes a 1-bit input `din` to output lane `sel` while keeping all other lanes `0`: `din == 1 ? (4'b0001 << sel) : 4'b0000`.

### Task
Implement `decode2to4(Bit#(2) sel)` and `demux1to4(Bit#(1) din, Bit#(2) sel)` in `mkDemuxDecoder`.
""",
        bsv_vs_verilog="Left-shifting `4'b0001 << sel` is a concise, idiomatic way to express an N-to-2^N one-hot decoder.",
        diagram="sel[1:0] ---> [ 4'b0001 << sel ] ---> decode2to4[3:0] & demux1to4[3:0]",
        interface_name="DemuxDecoderIfc",
        module_name="mkDemuxDecoder",
        interface_def="""
interface DemuxDecoderIfc;
    method Bit#(4) decode2to4(Bit#(2) sel);
    method Bit#(4) demux1to4(Bit#(1) din, Bit#(2) sel);
endinterface
""",
        snippet_template="""    method Bit#(4) decode2to4(Bit#(2) sel);
        return ?;
    endmethod

    method Bit#(4) demux1to4(Bit#(1) din, Bit#(2) sel);
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(4) decode2to4(Bit#(2) sel);
        return 4'b0001 << sel;
    endmethod

    method Bit#(4) demux1to4(Bit#(1) din, Bit#(2) sel);
        return (din == 1) ? (4'b0001 << sel) : 4'b0000;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(2) sel = cycle[1:0];
        Bit#(1) din = cycle[2];
        Bit#(4) r1 = ref_dut.decode2to4(sel);
        Bit#(4) u1 = user_dut.decode2to4(sel);
        Bit#(4) r2 = ref_dut.demux1to4(din, sel);
        Bit#(4) u2 = user_dut.demux1to4(din, sel);
        Bool ok = (r1 == u1) && (r2 == u2);
        $display("@WAVE cycle=%0d|in=din:%0d,sel:%0d|ref=dec:0x%01h,dmx:0x%01h|user=dec:0x%01h,dmx:0x%01h|match=%0d|note=Demux/Dec", cycle, din, sel, r1, r2, u1, u2, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `decode2to4(sel)`, `return 4'b0001 << sel;` (or use a `case (sel)`).",
            "In `demux1to4(din, sel)`, return `(din == 1) ? (4'b0001 << sel) : 4'b0000;`.",
            "Both shift-based and `case`-based solutions are accepted!",
        ],
    )

    add(
        pid="04c_combo_lut4",
        title="Combination Lab: 4-Input FPGA Look-Up Table (LUT4) Cell",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Combination Lab", "FPGA LUT4", "Mux + Indexing"],
        description="""
**Combination Lab (Combining Bit Concatenation + Dynamic Bit Indexing / Muxing)**:
How does an FPGA implement *any* 4-input boolean function $f(i_3, i_2, i_1, i_0)$?
It uses a **16-bit configuration table `table_cfg[15:0]`** (a **LUT4**)!
The four 1-bit inputs `{i3, i2, i1, i0}` are concatenated into a 4-bit address `idx = {i3, i2, i1, i0}`, and the LUT simply outputs bit `table_cfg[idx]`!

### Task
Implement `evalLut4(Bit#(16) table_cfg, Bit#(1) i3, Bit#(1) i2, Bit#(1) i1, Bit#(1) i0)` returning `table_cfg[{i3, i2, i1, i0}]`.
""",
        bsv_vs_verilog="In BSV, indexing a bit-vector `table_cfg[idx]` with a 4-bit signal `idx` synthesizes directly into a 16-to-1 multiplexer tree — the exact hardware of an FPGA LUT4!",
        diagram="{i3, i2, i1, i0} (4b index) ---> [ 16:1 MUX over table_cfg[15:0] ] ---> out (1b)",
        interface_name="Lut4Ifc",
        module_name="mkLut4",
        interface_def="""
interface Lut4Ifc;
    method Bit#(1) evalLut4(Bit#(16) table_cfg, Bit#(1) i3, Bit#(1) i2, Bit#(1) i1, Bit#(1) i0);
endinterface
""",
        snippet_template="""    method Bit#(1) evalLut4(Bit#(16) table_cfg, Bit#(1) i3, Bit#(1) i2, Bit#(1) i1, Bit#(1) i0);
        // Combine {i3, i2, i1, i0} into a 4-bit index and select from table_cfg
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(1) evalLut4(Bit#(16) table_cfg, Bit#(1) i3, Bit#(1) i2, Bit#(1) i1, Bit#(1) i0);
        Bit#(4) idx = {i3, i2, i1, i0};
        return table_cfg[idx];
    endmethod""",
        testbench_body="""    rule test;
        Bit#(16) cfg = 16'h9669; // 4-input parity truth table!
        Bit#(4) idx = cycle[3:0];
        Bit#(1) r = ref_dut.evalLut4(cfg, idx[3], idx[2], idx[1], idx[0]);
        Bit#(1) u = user_dut.evalLut4(cfg, idx[3], idx[2], idx[1], idx[0]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=idx:0x%01h|ref=out:%0d|user=out:%0d|match=%0d|note=LUT4 idx=%0d", cycle, idx, r, u, ok ? 1 : 0, idx);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Concatenate the 4 single-bit inputs: `Bit#(4) idx = {i3, i2, i1, i0};`.",
            "Index into `table_cfg`: `return table_cfg[idx];`.",
            "Notice `{i3, i2, i1, i0}` puts `i3` as MSB and `i0` as LSB.",
        ],
    )

    add(
        pid="04d_combo_parity",
        title="Combination Lab: 8-Bit Even/Odd Parity Framer & Checker",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Combination Lab", "Parity", "Error Detection"],
        description="""
**Combination Lab (Combining XOR Reduction + Concatenation + Conditional Mux)**:
Communication links append a **Parity Bit** to an 8-bit byte `data` to form a 9-bit frame `{parity_bit, data[7:0]}`:
- Let `xor_all = data[0] ^ data[1] ^ ... ^ data[7]` (the even parity of `data`).
- If `odd_mode == False` (Even Parity): `parity_bit = xor_all`.
- If `odd_mode == True` (Odd Parity): `parity_bit = ~xor_all`.

### Task
Implement in `mkParityFramer`:
1. `frameByte(Bit#(8) data, Bool odd_mode)`: Returns 9-bit `{parity_bit, data}`.
2. `checkFrame(Bit#(9) frame, Bool odd_mode)`: Returns `True` if `frame[8]` matches the expected parity of `frame[7:0]`, else `False`.
""",
        bsv_vs_verilog="Combining a static `for` XOR loop with `{parity_bit, data}` concatenation and `Bool` equality creates a complete UART/memory parity codec.",
        diagram="data[7:0], odd_mode ---> [ XOR Tree ^ ] ---> {parity_bit, data[7:0]} (9b)",
        interface_name="ParityFramerIfc",
        module_name="mkParityFramer",
        interface_def="""
interface ParityFramerIfc;
    method Bit#(9) frameByte(Bit#(8) data, Bool odd_mode);
    method Bool    checkFrame(Bit#(9) frame, Bool odd_mode);
endinterface
""",
        snippet_template="""    method Bit#(9) frameByte(Bit#(8) data, Bool odd_mode);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bool checkFrame(Bit#(9) frame, Bool odd_mode);
        // === YOUR CODE HERE ===
        return False;
    endmethod""",
        reference_snippet="""    function Bit#(1) calcParity(Bit#(8) d, Bool odd_m);
        Bit#(1) p = 0;
        for (Integer i = 0; i < 8; i = i + 1) p = p ^ d[i];
        return odd_m ? ~p : p;
    endfunction

    method Bit#(9) frameByte(Bit#(8) data, Bool odd_mode);
        return {calcParity(data, odd_mode), data};
    endmethod

    method Bool checkFrame(Bit#(9) frame, Bool odd_mode);
        return frame[8] == calcParity(frame[7:0], odd_mode);
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) d = 8'h35 + (cycle[7:0] * 8'h19);
        Bool odd_m = (cycle[0] == 1);
        Bit#(9) rf = ref_dut.frameByte(d, odd_m);
        Bit#(9) uf = user_dut.frameByte(d, odd_m);
        Bit#(9) corrupted = rf ^ (cycle[1] == 1 ? 9'h004 : 9'h000);
        Bool rc = ref_dut.checkFrame(corrupted, odd_m);
        Bool uc = user_dut.checkFrame(corrupted, odd_m);
        Bool ok = (rf == uf) && (rc == uc);
        $display("@WAVE cycle=%0d|in=d:0x%02h,odd:%0d|ref=frm:0x%03h,ok:%0d|user=frm:0x%03h,ok:%0d|match=%0d|note=Parity", cycle, d, odd_m?1:0, rf, rc?1:0, uf, uc?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bit#(1) p = 0; for (Integer i = 0; i < 8; i = i + 1) p = p ^ data[i];`.",
            "Set `Bit#(1) pbit = odd_mode ? ~p : p;` and return `{pbit, data}` from `frameByte`.",
            "In `checkFrame`, check whether `frame[8]` equals the computed parity bit of `frame[7:0]`.",
        ],
    )

    add(
        pid="04e_combo_comparator",
        title="Combination Lab: 8-Bit Window & Magnitude Comparator",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["Combination Lab", "Comparator", "Range Check"],
        description="""
**Combination Lab**: Implement an 8-bit **Magnitude & Window Comparator** (`mkWindowComp`):
1. `compare(Bit#(8) a, Bit#(8) b)`: Returns 3-bit flag `{gt, eq, lt}` where:
   - bit 2 (`gt`) is `1` when `a > b`
   - bit 1 (`eq`) is `1` when `a == b`
   - bit 0 (`lt`) is `1` when `a < b`
2. `inWindow(Bit#(8) x, Bit#(8) low, Bit#(8) high)`: Returns `True` if `x >= low && x <= high`, else `False`.
""",
        bsv_vs_verilog="Packing `{gt, eq, lt}` via `(a > b ? 1'b1 : 1'b0)` or `pack(a > b)` cleanly bridges `Bool` comparisons and `Bit#(1)` wires.",
        diagram="a, b ---> [ > , == , < ] ---> {gt, eq, lt}   |   x, low, high ---> (low <= x <= high)",
        interface_name="WindowCompIfc",
        module_name="mkWindowComp",
        interface_def="""
interface WindowCompIfc;
    method Bit#(3) compare(Bit#(8) a, Bit#(8) b);
    method Bool    inWindow(Bit#(8) x, Bit#(8) low, Bit#(8) high);
endinterface
""",
        snippet_template="""    method Bit#(3) compare(Bit#(8) a, Bit#(8) b);
        // Return {gt, eq, lt}
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bool inWindow(Bit#(8) x, Bit#(8) low, Bit#(8) high);
        // === YOUR CODE HERE ===
        return False;
    endmethod""",
        reference_snippet="""    method Bit#(3) compare(Bit#(8) a, Bit#(8) b);
        return {pack(a > b), pack(a == b), pack(a < b)};
    endmethod

    method Bool inWindow(Bit#(8) x, Bit#(8) low, Bit#(8) high);
        return (x >= low) && (x <= high);
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) a = 8'd40 + (cycle[7:0] * 8'd10);
        Bit#(8) b = 8'd70;
        Bit#(3) rc = ref_dut.compare(a, b);
        Bit#(3) uc = user_dut.compare(a, b);
        Bool rw = ref_dut.inWindow(a, 8'd50, 8'd90);
        Bool uw = user_dut.inWindow(a, 8'd50, 8'd90);
        Bool ok = (rc == uc) && (rw == uw);
        $display("@WAVE cycle=%0d|in=a:%0d,b:%0d|ref=cmp:%03b,win:%0d|user=cmp:%03b,win:%0d|match=%0d|note=WindowComp", cycle, a, b, rc, rw?1:0, uc, uw?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In BSV, `pack(a > b)` converts `Bool` (`True`/`False`) into `Bit#(1)` (`1'b1`/`1'b0`)!",
            "So `return {pack(a > b), pack(a == b), pack(a < b)};` builds `{gt, eq, lt}` in one line.",
            "In `inWindow`, `return (x >= low) && (x <= high);`.",
        ],
    )

    # =========================================================================
    # TRACK 2 ADDITIONS: ARITHMETIC, EXTENSIONS, BCD, CLZ & COMBINATION LABS
    # =========================================================================
    add(
        pid="05b_sign_zero_extend",
        title="Width Conversions: `zeroExtend`, `signExtend` & `truncate`",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Easy",
        tags=["zeroExtend", "signExtend", "truncate"],
        description="""
Unlike Verilog (which silently pads or truncates mismatched widths), BSV requires **explicit width conversion functions**:
- `zeroExtend(x)`: Pads upper bits with `0`s.
- `signExtend(x)`: Copies the MSB sign bit `x[msb]` into all upper bits.
- `truncate(x)`: Keeps the lower LSB bits and drops upper bits.

### Task
Implement three methods in `mkWidthConv`:
1. `uext8to16(Bit#(8) x)` -> `zeroExtend(x)`
2. `sext8to16(Bit#(8) x)` -> `signExtend(x)`
3. `addSignedByte(Bit#(16) base, Bit#(8) offset)` -> `base + signExtend(offset)`
""",
        bsv_vs_verilog="In Verilog, `wire [15:0] y = base + offset;` zero-extends `offset` unless declared `signed` everywhere. In BSV, `base + signExtend(offset)` is unambiguous!",
        diagram="x[7:0] ---> [ zeroExtend / signExtend ] ---> Bit#(16)",
        interface_name="WidthConvIfc",
        module_name="mkWidthConv",
        interface_def="""
interface WidthConvIfc;
    method Bit#(16) uext8to16(Bit#(8) x);
    method Bit#(16) sext8to16(Bit#(8) x);
    method Bit#(16) addSignedByte(Bit#(16) base, Bit#(8) offset);
endinterface
""",
        snippet_template="""    method Bit#(16) uext8to16(Bit#(8) x);
        return ?;
    endmethod
    method Bit#(16) sext8to16(Bit#(8) x);
        return ?;
    endmethod
    method Bit#(16) addSignedByte(Bit#(16) base, Bit#(8) offset);
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(16) uext8to16(Bit#(8) x);
        return zeroExtend(x);
    endmethod
    method Bit#(16) sext8to16(Bit#(8) x);
        return signExtend(x);
    endmethod
    method Bit#(16) addSignedByte(Bit#(16) base, Bit#(8) offset);
        return base + signExtend(offset);
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) tv[6] = {8'h05, 8'h80, 8'hFF, 8'h7F, 8'hFE, 8'h10};
        Bit#(8) x = tv[cycle];
        Bit#(16) base = 16'h1000;
        Bool ok = (ref_dut.uext8to16(x) == user_dut.uext8to16(x)) &&
                  (ref_dut.sext8to16(x) == user_dut.sext8to16(x)) &&
                  (ref_dut.addSignedByte(base, x) == user_dut.addSignedByte(base, x));
        $display("@WAVE cycle=%0d|in=x:0x%02h|ref=sext:0x%04h,add:0x%04h|user=sext:0x%04h,add:0x%04h|match=%0d|note=SignExtend",
            cycle, x, ref_dut.sext8to16(x), ref_dut.addSignedByte(base, x), user_dut.sext8to16(x), user_dut.addSignedByte(base, x), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use `return zeroExtend(x);` in `uext8to16`.",
            "Use `return signExtend(x);` in `sext8to16`.",
            "Use `return base + signExtend(offset);` in `addSignedByte`.",
        ],
    )

    add(
        pid="06b_add_sub_overflow",
        title="8-Bit Two's Complement Adder-Subtractor with Overflow Flag",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Medium",
        tags=["Adder-Subtractor", "Two's Complement", "Overflow"],
        description="""
In computer architecture (like RISC-V and ARM ALUs), a single adder computes both `a + b` (`sub == False`) and `a - b` (`sub == True`) by inverting `b` (`b_eff = sub ? ~b : b`) with carry-in `cin = sub ? 1 : 0`:
- `res = a + b_eff + zeroExtend(pack(sub))`
- **Signed Two's Complement Overflow (`ovf`)** occurs when `a[7]` and `b_eff[7]` have the **same sign**, but `res[7]` has the **opposite sign**:
  `Bool ovf = (a[7] == b_eff[7]) && (res[7] != a[7]);`

### Task
Implement `addSub(Bit#(8) a, Bit#(8) b, Bool sub)` in `mkAddSubOvf` returning 9-bit `{pack(ovf), res[7:0]}`.
""",
        bsv_vs_verilog="Sharing one adder for ADD and SUB via `b ^ replicate(sub)` + `cin = sub` saves 50% of adder area in hardware ALUs.",
        diagram="a[7:0], (sub ? ~b : b), cin=sub ---> [ 8b Adder ] ---> {ovf, res[7:0]}",
        interface_name="AddSubOvfIfc",
        module_name="mkAddSubOvf",
        interface_def="""
interface AddSubOvfIfc;
    method Bit#(9) addSub(Bit#(8) a, Bit#(8) b, Bool sub);
endinterface
""",
        snippet_template="""    method Bit#(9) addSub(Bit#(8) a, Bit#(8) b, Bool sub);
        // Compute res and signed overflow flag ovf, return {pack(ovf), res}
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(9) addSub(Bit#(8) a, Bit#(8) b, Bool sub);
        Bit#(8) b_eff = sub ? ~b : b;
        Bit#(8) res = a + b_eff + (sub ? 8'd1 : 8'd0);
        Bool ovf = (a[7] == b_eff[7]) && (res[7] != a[7]);
        return {pack(ovf), res};
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) va[6] = {8'd100, 8'd50, 8'h80, 8'h7F, 8'd20, 8'h90};
        Bit#(8) vb[6] = {8'd50,  8'd30, 8'h01, 8'h01, 8'd40, 8'h80};
        Bool vsub[6]  = {False,  True,  True,  False, True,  False};
        Bit#(9) r = ref_dut.addSub(va[cycle], vb[cycle], vsub[cycle]);
        Bit#(9) u = user_dut.addSub(va[cycle], vb[cycle], vsub[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=a:0x%02h,b:0x%02h,sub:%0d|ref=ovf:%0d,res:0x%02h|user=ovf:%0d,res:0x%02h|match=%0d|note=AddSub", cycle, va[cycle], vb[cycle], vsub[cycle]?1:0, r[8], r[7:0], u[8], u[7:0], ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bit#(8) b_eff = sub ? ~b : b;` and `Bit#(8) res = a + b_eff + (sub ? 8'd1 : 8'd0);`.",
            "Signed overflow occurs when `a[7] == b_eff[7]` and `res[7] != a[7]`.",
            "Return `{pack(ovf), res};`.",
        ],
    )

    add(
        pid="06c_bcd_adder",
        title="Single-Digit BCD (Binary-Coded Decimal) Adder (`+6` Correction)",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Medium",
        tags=["BCD Adder", "Decimal Arithmetic", "HDLBits Classic"],
        description="""
A classic HDLBits & digital logic problem: in **Binary-Coded Decimal (BCD)**, each 4-bit nibble represents a decimal digit `0`..`9`.
When adding two BCD digits `a` (`0`..`9`), `b` (`0`..`9`), and `cin` (`0`..`1`):
- Compute the 5-bit binary sum: `Bit#(5) raw_sum = zeroExtend(a) + zeroExtend(b) + zeroExtend(cin);`
- If `raw_sum > 9`, we must add `5'd6` (`raw_sum + 5'd6`) to skip the 6 invalid hex codes (`A`..`F`) and generate a decimal carry-out!

### Task
Implement `bcdAdd(Bit#(4) a, Bit#(4) b, Bit#(1) cin)` returning 5-bit `{cout, bcd_digit[3:0]}` in `mkBcdAdder`.
""",
        bsv_vs_verilog="Using `Bit#(5) raw_sum` makes `raw_sum > 9` (which covers both `raw_sum[3:0] > 9` and `raw_sum[4] == 1`) a single clean comparison!",
        diagram="a[3:0] + b[3:0] + cin ---> raw_sum[4:0] ---> (raw_sum > 9 ? raw_sum + 6 : raw_sum)",
        interface_name="BcdAdderIfc",
        module_name="mkBcdAdder",
        interface_def="""
interface BcdAdderIfc;
    method Bit#(5) bcdAdd(Bit#(4) a, Bit#(4) b, Bit#(1) cin);
endinterface
""",
        snippet_template="""    method Bit#(5) bcdAdd(Bit#(4) a, Bit#(4) b, Bit#(1) cin);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(5) bcdAdd(Bit#(4) a, Bit#(4) b, Bit#(1) cin);
        Bit#(5) raw_sum = zeroExtend(a) + zeroExtend(b) + zeroExtend(cin);
        return (raw_sum > 5'd9) ? (raw_sum + 5'd6) : raw_sum;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) va[8] = {4'd0, 4'd3, 4'd5, 4'd8, 4'd9, 4'd9, 4'd4, 4'd7};
        Bit#(4) vb[8] = {4'd0, 4'd4, 4'd5, 4'd6, 4'd9, 4'd9, 4'd5, 4'd2};
        Bit#(1) vc[8] = {1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b1, 1'b1, 1'b0};
        Bit#(5) r = ref_dut.bcdAdd(va[cycle], vb[cycle], vc[cycle]);
        Bit#(5) u = user_dut.bcdAdd(va[cycle], vb[cycle], vc[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=a:%0d,b:%0d,c:%0d|ref=cout:%0d,d:%0d|user=cout:%0d,d:%0d|match=%0d|note=BCD Add", cycle, va[cycle], vb[cycle], vc[cycle], r[4], r[3:0], u[4], u[3:0], ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bit#(5) raw_sum = zeroExtend(a) + zeroExtend(b) + zeroExtend(cin);`.",
            "If `raw_sum > 5'd9`, return `raw_sum + 5'd6`; otherwise return `raw_sum`.",
            "Adding `6` when `raw_sum > 9` automatically sets bit 4 (`cout = 1`) and wraps the lower nibble modulo 10!",
        ],
    )

    add(
        pid="06d_leading_zero_cnt",
        title="8-Bit Count Leading Zeros (`CLZ`) Hardware Unit",
        track_id="track1_combinational",
        track_title="1. BSV Basics & Combinational Logic",
        difficulty="Medium",
        tags=["CLZ", "Bit Manipulation", "Floating-Point / ISA"],
        description="""
Every modern CPU instruction set (RISC-V `Zbb`, ARM `CLZ`, x86 `LZCNT`) and floating-point normalizer includes a **Count Leading Zeros (`CLZ`)** unit:
- Given an 8-bit input `x`, count how many consecutive `0` bits appear starting from the MSB (`x[7]`) down to the first `1` bit:
  - If `x[7] == 1` -> `0` leading zeros
  - If `x[7:6] == 2'b01` -> `1` leading zero
  - ...
  - If `x == 8'h00` -> `8` leading zeros (`4'd8`)

### Task
Implement `clz8(Bit#(8) x)` returning a 4-bit count (`0`..`8`) in `mkClz8`.
""",
        bsv_vs_verilog="A static `for (Integer i = 7; i >= 0; i = i - 1)` loop with a `Bool stop` flag unrolls into a priority-encoded CLZ tree.",
        diagram="x[7:0] ---> [ Scan from bit 7 down to bit 0 ] ---> clz8 (4'd0 .. 4'd8)",
        interface_name="Clz8Ifc",
        module_name="mkClz8",
        interface_def="""
interface Clz8Ifc;
    method Bit#(4) clz8(Bit#(8) x);
endinterface
""",
        snippet_template="""    method Bit#(4) clz8(Bit#(8) x);
        // Count leading zeros from MSB x[7] down to x[0]
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(4) clz8(Bit#(8) x);
        Bit#(4) cnt = 0;
        Bool seen_one = False;
        for (Integer i = 7; i >= 0; i = i - 1) begin
            if (!seen_one) begin
                if (x[i] == 1) seen_one = True;
                else cnt = cnt + 1;
            end
        end
        return cnt;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) tv[8] = {8'h80, 8'h40, 8'h2F, 8'h10, 8'h08, 8'h03, 8'h01, 8'h00};
        Bit#(8) x = tv[cycle];
        Bit#(4) r = ref_dut.clz8(x);
        Bit#(4) u = user_dut.clz8(x);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=x:0x%02h|ref=clz:%0d|user=clz:%0d|match=%0d|note=CLZ", cycle, x, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Loop from MSB to LSB: `for (Integer i = 7; i >= 0; i = i - 1)`.",
            "Keep `Bool seen_one = False;`. While `!seen_one`, if `x[i] == 1` set `seen_one = True`, else increment `cnt = cnt + 1`.",
            "Alternatively, an `if (x[7]==1) return 0; else if (x[6]==1) return 1; ... else return 8;` chain also works!",
        ],
    )

    add(
        pid="07b_combo_alu_flags",
        title="Combination Lab: 8-Bit Processor ALU with NZCV Condition Flags",
        track_id="track2_types",
        track_title="2. Strong Types, Enums, Structs & Vectors",
        difficulty="Medium",
        tags=["Combination Lab", "ALU", "NZCV Flags", "struct"],
        description="""
**Combination Lab (Combining Arithmetic + Bitwise + Structs + Condition Flags)**:
Processor architectures like ARM and x86 produce both an 8-bit `result` and four **Condition Code Flags (`N, Z, C, V`)** packed in a `struct`:
- `op == 2'd0` (ADD): `{carry, res} = zeroExtend(a) + zeroExtend(b)`, `ovf = (a[7] == b[7]) && (res[7] != a[7])`
- `op == 2'd1` (SUB): `{carry, res} = zeroExtend(a) + zeroExtend(~b) + 9'd1`, `ovf = (a[7] != b[7]) && (res[7] != a[7])`
- `op == 2'd2` (AND): `res = a & b`, `carry = 0`, `ovf = False`
- `op == 2'd3` (XOR): `res = a ^ b`, `carry = 0`, `ovf = False`
- For all operations: `neg = (res[7] == 1)` and `zero = (res == 0)`.

### Task
Implement `execAlu(Bit#(2) op, Bit#(8) a, Bit#(8) b)` returning `AluOut` in `mkAluFlags`.
""",
        bsv_vs_verilog="Returning a `typedef struct { Bit#(8) res; Bool n; Bool z; Bool c; Bool v; } AluOut` bundles the datapath result and status flags into a single self-documenting value.",
        diagram="op[1:0], a[7:0], b[7:0] ---> [ ALU Core ] ---> AluOut { res, n, z, c, v }",
        interface_name="AluFlagsIfc",
        module_name="mkAluFlags",
        interface_def="""
typedef struct {
    Bit#(8) res;
    Bool    n;
    Bool    z;
    Bool    c;
    Bool    v;
} AluOut deriving (Bits, Eq);

interface AluFlagsIfc;
    method AluOut execAlu(Bit#(2) op, Bit#(8) a, Bit#(8) b);
endinterface
""",
        snippet_template="""    method AluOut execAlu(Bit#(2) op, Bit#(8) a, Bit#(8) b);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method AluOut execAlu(Bit#(2) op, Bit#(8) a, Bit#(8) b);
        Bit#(9) wide = 0;
        Bool ovf = False;
        case (op)
            2'd0: begin
                wide = zeroExtend(a) + zeroExtend(b);
                ovf = (a[7] == b[7]) && (wide[7] != a[7]);
            end
            2'd1: begin
                Bit#(8) nb = ~b;
                wide = zeroExtend(a) + zeroExtend(nb) + 9'd1;
                ovf = (a[7] == nb[7]) && (wide[7] != a[7]);
            end
            2'd2: wide = {1'b0, a & b};
            2'd3: wide = {1'b0, a ^ b};
        endcase
        Bit#(8) r = wide[7:0];
        return AluOut {
            res: r,
            n: (r[7] == 1),
            z: (r == 0),
            c: (wide[8] == 1),
            v: ovf
        };
    endmethod""",
        testbench_body="""    rule test;
        Bit#(2) op = cycle[1:0];
        Bit#(8) a = 8'h7F + (cycle[7:0] * 8'h21);
        Bit#(8) b = 8'h01 + (cycle[7:0] * 8'h13);
        AluOut r = ref_dut.execAlu(op, a, b);
        AluOut u = user_dut.execAlu(op, a, b);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=op:%0d,a:0x%02h,b:0x%02h|ref=res:0x%02h,nzcv:%04b|user=res:0x%02h,nzcv:%04b|match=%0d|note=ALU Flags",
            cycle, op, a, b, r.res, {pack(r.n),pack(r.z),pack(r.c),pack(r.v)}, u.res, {pack(u.n),pack(u.z),pack(u.c),pack(u.v)}, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use a 9-bit `wide` variable for `2'd0` (`zeroExtend(a) + zeroExtend(b)`) and `2'd1` (`zeroExtend(a) + zeroExtend(~b) + 9'd1`).",
            "Extract `Bit#(8) r = wide[7:0];` and `Bool c = (wide[8] == 1);`.",
            "Set `n: (r[7] == 1)` and `z: (r == 0)` in `AluOut`.",
        ],
    )

    add(
        pid="08b_tagged_union_inst",
        title="Tagged Union Instruction Evaluator (`typedef union tagged`)",
        track_id="track2_types",
        track_title="2. Strong Types, Enums, Structs & Vectors",
        difficulty="Medium",
        tags=["Tagged Union", "Pattern Matching", "ISA"],
        description="""
BSV's **`typedef union tagged`** is one of its greatest advantages over Verilog! Different instruction formats carry completely different fields, and BSV enforces type-safe pattern matching (`case (inst) matches`):
```bsv
typedef union tagged {
    Bit#(8) LoadImm;
    struct { Bit#(8) a; Bit#(8) b; } AddPair;
    Bit#(8) InvertVal;
} MicroInst deriving (Bits, Eq);
```
You can pattern-match on `inst`:
```bsv
case (inst) matches
    tagged LoadImm .imm:     return imm;
    tagged AddPair .p:       return p.a + p.b;
    tagged InvertVal .v:     return ~v;
endcase
```

### Task
Implement `evalInst(MicroInst inst)` in `mkTaggedInst`.
""",
        bsv_vs_verilog="In SystemVerilog, unions are untagged by default in RTL synthesis, allowing accidental field misinterpretation. BSV automatically adds tag bits and checks pattern matches at compile time!",
        diagram="MicroInst ---> [ matches tagged LoadImm | AddPair | InvertVal ] ---> Bit#(8)",
        interface_name="TaggedInstIfc",
        module_name="mkTaggedInst",
        interface_def="""
typedef union tagged {
    Bit#(8) LoadImm;
    struct { Bit#(8) a; Bit#(8) b; } AddPair;
    Bit#(8) InvertVal;
} MicroInst deriving (Bits, Eq);

interface TaggedInstIfc;
    method Bit#(8) evalInst(MicroInst inst);
endinterface
""",
        snippet_template="""    method Bit#(8) evalInst(MicroInst inst);
        // Pattern match using `case (inst) matches`
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(8) evalInst(MicroInst inst);
        case (inst) matches
            tagged LoadImm .imm: return imm;
            tagged AddPair .p:   return p.a + p.b;
            tagged InvertVal .v: return ~v;
        endcase
    endmethod""",
        testbench_body="""    rule test;
        MicroInst tv[6] = {
            tagged LoadImm 8'h42,
            tagged AddPair { a: 8'd15, b: 8'd27 },
            tagged InvertVal 8'hF0,
            tagged LoadImm 8'h99,
            tagged AddPair { a: 8'd100, b: 8'd55 },
            tagged InvertVal 8'h55
        };
        MicroInst inst = tv[cycle];
        Bit#(8) r = ref_dut.evalInst(inst);
        Bit#(8) u = user_dut.evalInst(inst);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=raw:0x%05h|ref=out:0x%02h|user=out:0x%02h|match=%0d|note=TaggedUnion", cycle, pack(inst), r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use `case (inst) matches ... endcase` (don't forget the keyword `matches`!).",
            "Bind pattern variables with a leading dot: `tagged LoadImm .imm: return imm;`.",
            "For `tagged AddPair .p: return p.a + p.b;` and `tagged InvertVal .v: return ~v;`.",
        ],
    )

    add(
        pid="11b_vector_ops",
        title="SIMD Vector Lanes: Pairwise Add & Vector Reversal (`Vector#(4, Bit#(8))`)",
        track_id="track2_types",
        track_title="2. Strong Types, Enums, Structs & Vectors",
        difficulty="Easy",
        tags=["Vector", "SIMD", "Higher-Order Hardware"],
        description="""
In BSV, `Vector#(4, Bit#(8))` represents 4 parallel 8-bit lanes (like a 32-bit SIMD register).
Given `Vector#(4, Bit#(8)) va` and `Vector#(4, Bit#(8)) vb`:
1. `simdAdd(va, vb)`: Returns a `Vector#(4, Bit#(8))` where lane `i` is `va[i] + vb[i]`.
2. `reverseVec(va)`: Returns a `Vector#(4, Bit#(8))` with lanes in reverse order (`out[i] = va[3 - i]`, or `reverse(va)` from `Vector` library!).

### Task
Implement `simdAdd` and `reverseVec` in `mkVectorOps`.
""",
        bsv_vs_verilog="BSV's `Vector` package provides functional combinators like `reverse(va)` and `zipWith(\\+, va, vb)` that elaborate into parallel hardware lanes!",
        diagram="va[0..3], vb[0..3] ---> [ Lane-wise + ] ---> simdAdd[0..3]   |   [ Reverse ] ---> va[3..0]",
        interface_name="VectorOpsIfc",
        module_name="mkVectorOps",
        interface_def="""
interface VectorOpsIfc;
    method Vector#(4, Bit#(8)) simdAdd(Vector#(4, Bit#(8)) va, Vector#(4, Bit#(8)) vb);
    method Vector#(4, Bit#(8)) reverseVec(Vector#(4, Bit#(8)) va);
endinterface
""",
        snippet_template="""    method Vector#(4, Bit#(8)) simdAdd(Vector#(4, Bit#(8)) va, Vector#(4, Bit#(8)) vb);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Vector#(4, Bit#(8)) reverseVec(Vector#(4, Bit#(8)) va);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Vector#(4, Bit#(8)) simdAdd(Vector#(4, Bit#(8)) va, Vector#(4, Bit#(8)) vb);
        Vector#(4, Bit#(8)) res = newVector;
        for (Integer i = 0; i < 4; i = i + 1) res[i] = va[i] + vb[i];
        return res;
    endmethod

    method Vector#(4, Bit#(8)) reverseVec(Vector#(4, Bit#(8)) va);
        return reverse(va);
    endmethod""",
        testbench_body="""    rule test;
        Vector#(4, Bit#(8)) va = unpack(32'h11223344 + (cycle * 32'h01020304));
        Vector#(4, Bit#(8)) vb = unpack(32'h05060708);
        let r1 = ref_dut.simdAdd(va, vb);
        let u1 = user_dut.simdAdd(va, vb);
        let r2 = ref_dut.reverseVec(va);
        let u2 = user_dut.reverseVec(va);
        Bool ok = (r1 == u1) && (r2 == u2);
        $display("@WAVE cycle=%0d|in=va:0x%08h|ref=add:0x%08h,rev:0x%08h|user=add:0x%08h,rev:0x%08h|match=%0d|note=Vector SIMD", cycle, pack(va), pack(r1), pack(r2), pack(u1), pack(u2), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `simdAdd`, create `Vector#(4, Bit#(8)) res = newVector;` and loop `for (Integer i = 0; i < 4; i = i + 1) res[i] = va[i] + vb[i];`.",
            "In `reverseVec`, either call `return reverse(va);` (from `Vector::*`) or loop `res[i] = va[3 - i];`.",
            "Remember `newVector` initializes an empty `Vector` variable ready to be populated.",
        ],
    )

    add(
        pid="11d_combo_crossbar_2x2",
        title="Combination Lab: 2x2 Non-Blocking Packet Crossbar Switch",
        track_id="track2_types",
        track_title="2. Strong Types, Enums, Structs & Vectors",
        difficulty="Medium",
        tags=["Combination Lab", "Crossbar", "Struct + Maybe + Priority"],
        description="""
**Combination Lab (Combining `struct`, `Maybe#(t)`, and Priority Arbitration)**:
Design a combinational **2x2 Crossbar Switch** (`mkCrossbar2x2`) that routes two input packets (`in0` and `in1`, where **`in0` has higher priority than `in1`** if both target the same output port!):
- Each `SwPkt` has `Bit#(1) dst` (`0` = output port 0, `1` = output port 1) and `Bit#(8) data`.
- Inputs are `Maybe#(SwPkt) in0` and `Maybe#(SwPkt) in1`.
- Output port `out0`:
  - If `in0` is `tagged Valid .p0` and `p0.dst == 0`, output `tagged Valid p0`.
  - Else if `in1` is `tagged Valid .p1` and `p1.dst == 0`, output `tagged Valid p1`.
  - Else output `tagged Invalid`.
- Output port `out1`: Same priority logic for `dst == 1` (`in0` wins over `in1`).

### Task
Implement `route0` and `route1` in `mkCrossbar2x2`.
""",
        bsv_vs_verilog="Combining `Maybe#(SwPkt)` pattern matching with priority selection models an interconnect switch fabric without manual valid-bit book-keeping.",
        diagram="in0 (prio 0), in1 (prio 1) ---> [ 2x2 Crossbar Fabric ] ---> route0 (dst==0), route1 (dst==1)",
        interface_name="Crossbar2x2Ifc",
        module_name="mkCrossbar2x2",
        interface_def="""
typedef struct {
    Bit#(1) dst;
    Bit#(8) data;
} SwPkt deriving (Bits, Eq);

interface Crossbar2x2Ifc;
    method Maybe#(SwPkt) route0(Maybe#(SwPkt) in0, Maybe#(SwPkt) in1);
    method Maybe#(SwPkt) route1(Maybe#(SwPkt) in0, Maybe#(SwPkt) in1);
endinterface
""",
        snippet_template="""    method Maybe#(SwPkt) route0(Maybe#(SwPkt) in0, Maybe#(SwPkt) in1);
        // === YOUR CODE HERE ===
        return tagged Invalid;
    endmethod

    method Maybe#(SwPkt) route1(Maybe#(SwPkt) in0, Maybe#(SwPkt) in1);
        // === YOUR CODE HERE ===
        return tagged Invalid;
    endmethod""",
        reference_snippet="""    method Maybe#(SwPkt) route0(Maybe#(SwPkt) in0, Maybe#(SwPkt) in1);
        if (in0 matches tagged Valid .p0 &&& p0.dst == 0) return tagged Valid p0;
        else if (in1 matches tagged Valid .p1 &&& p1.dst == 0) return tagged Valid p1;
        else return tagged Invalid;
    endmethod

    method Maybe#(SwPkt) route1(Maybe#(SwPkt) in0, Maybe#(SwPkt) in1);
        if (in0 matches tagged Valid .p0 &&& p0.dst == 1) return tagged Valid p0;
        else if (in1 matches tagged Valid .p1 &&& p1.dst == 1) return tagged Valid p1;
        else return tagged Invalid;
    endmethod""",
        testbench_body="""    rule test;
        Maybe#(SwPkt) i0 = (cycle != 1) ? tagged Valid SwPkt { dst: cycle[0], data: 8'hA0 + cycle[7:0] } : tagged Invalid;
        Maybe#(SwPkt) i1 = (cycle != 4) ? tagged Valid SwPkt { dst: cycle[1], data: 8'hB0 + cycle[7:0] } : tagged Invalid;
        let r0 = ref_dut.route0(i0, i1);
        let u0 = user_dut.route0(i0, i1);
        let r1 = ref_dut.route1(i0, i1);
        let u1 = user_dut.route1(i0, i1);
        Bool ok = (r0 == u0) && (r1 == u1);
        $display("@WAVE cycle=%0d|in=i0:0x%03h,i1:0x%03h|ref=o0:0x%03h,o1:0x%03h|user=o0:0x%03h,o1:0x%03h|match=%0d|note=Crossbar2x2",
            cycle, pack(i0), pack(i1), pack(r0), pack(r1), pack(u0), pack(u1), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In BSV, you can use `if (in0 matches tagged Valid .p0 &&& p0.dst == 0)` OR `if (isValid(in0) && fromMaybe(?, in0).dst == 0)`!",
            "Notice the triple-ampersand `&&&` in BSV: it binds pattern variables like `.p0` and immediately tests `p0.dst == 0` in the same `if` condition!",
            "Check `in0` before `in1` so `in0` has priority when both target the same destination.",
        ],
    )

    # =========================================================================
    # TRACK 3 ADDITIONS: SEQUENTIAL REGISTERS, DREG, SHIFT & BCD COUNTERS
    # =========================================================================
    add(
        pid="12b_dreg_pulse",
        title="Transient 1-Cycle Pulse Register using BSV `DReg` (`mkDReg`)",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Easy",
        tags=["DReg", "Pulse Generator", "BSV Library"],
        description="""
In RTL design, we often want a register `valid_pulse` that automatically resets to `0` (`False`) on the next clock cycle unless explicitly written again — eliminating the bug of forgetting to clear a strobe signal!
BSV's standard `DReg` package (`import DReg::*;`) provides **`mkDReg(default_val)`**:
```bsv
Reg#(Bool) pulse <- mkDReg(False);
Reg#(Bit#(8)) last_data <- mkReg(0);
```
Whenever `trigger(Bit#(8) d)` sets `pulse <= True; last_data <= d;`, `pulse` will be `True` for **only the next 1 clock cycle**, then automatically revert to `False`!

### Task
Implement `mkDRegPulse` using `mkDReg(False)` for `pulse` and `mkReg(0)` for `last_data`.
""",
        bsv_vs_verilog="In Verilog, you must remember to put `pulse <= 1'b0;` at the top of `always @(posedge clk)`. In BSV, `mkDReg(False)` guarantees default-reset every cycle in hardware!",
        diagram="trigger(d) ---> [ pulse (mkDReg(False)) | last_data (mkReg(0)) ] ---> isPulsing(), data()",
        interface_name="DRegPulseIfc",
        module_name="mkDRegPulse",
        interface_def="""
interface DRegPulseIfc;
    method Action trigger(Bit#(8) d);
    method Bool   isPulsing();
    method Bit#(8) data();
endinterface
""",
        snippet_template="""    Reg#(Bool)    pulse     <- mkDReg(False);
    Reg#(Bit#(8)) last_data <- mkReg(0);

    method Action trigger(Bit#(8) d);
        // === YOUR CODE HERE ===
    endmethod

    method Bool isPulsing();
        return pulse;
    endmethod

    method Bit#(8) data();
        return last_data;
    endmethod""",
        reference_snippet="""    Reg#(Bool)    pulse     <- mkDReg(False);
    Reg#(Bit#(8)) last_data <- mkReg(0);

    method Action trigger(Bit#(8) d);
        pulse <= True;
        last_data <= d;
    endmethod

    method Bool isPulsing();
        return pulse;
    endmethod

    method Bit#(8) data();
        return last_data;
    endmethod""",
        testbench_body="""    rule test;
        if (cycle == 0 || cycle == 3 || cycle == 4) begin
            ref_dut.trigger(8'hA0 + cycle[7:0]);
            user_dut.trigger(8'hA0 + cycle[7:0]);
        end
        Bool rp = ref_dut.isPulsing();
        Bool up = user_dut.isPulsing();
        Bit#(8) rd = ref_dut.data();
        Bit#(8) ud = user_dut.data();
        Bool ok = (rp == up) && (rd == ud);
        $display("@WAVE cycle=%0d|in=trig:%0d|ref=pulse:%0d,d:0x%02h|user=pulse:%0d,d:0x%02h|match=%0d|note=DReg pulse",
            cycle, (cycle==0||cycle==3||cycle==4)?1:0, rp?1:0, rd, up?1:0, ud, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 6) begin
            $display("@SUMMARY total=7 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `trigger(Bit#(8) d)`, write `pulse <= True;` and `last_data <= d;`.",
            "Because `pulse` is instantiated with `mkDReg(False)`, it automatically clears back to `False` on any cycle where `trigger` is not called!",
            "Return `pulse` in `isPulsing()` and `last_data` in `data()`.",
        ],
    )

    add(
        pid="14b_bcd_counter_2digit",
        title="Two-Digit Cascaded BCD Decade Counter (`00` to `99`)",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Medium",
        tags=["BCD Counter", "Cascaded Counters", "HDLBits Classic"],
        description="""
Build a 2-digit **BCD (Binary-Coded Decimal) Decade Counter** (`mkBcdCounter99`) that counts from `00` to `99` and wraps back to `00`:
- Hold `Reg#(Bit#(4)) ones <- mkReg(0);` (`0`..`9`) and `Reg#(Bit#(4)) tens <- mkReg(0);` (`0`..`9`).
- Every clock cycle (`rule tick`):
  - If `ones == 9`: reset `ones <= 0`, and increment `tens <= (tens == 9) ? 0 : (tens + 1)`.
  - Else: increment `ones <= ones + 1`.
- `readBcd()` returns `{tens, ones}` (`Bit#(8)`).

### Task
Implement `mkBcdCounter99` with `rule tick` and `method Bit#(8) readBcd()`.
""",
        bsv_vs_verilog="Updating both `ones` and `tens` inside a single atomic `rule tick` makes synchronous decade cascading crystal clear.",
        diagram="[ ones (0..9) ] --(ones==9)--> [ tens (0..9) ] ---> readBcd() = {tens, ones}",
        interface_name="BcdCounter99Ifc",
        module_name="mkBcdCounter99",
        interface_def="""
interface BcdCounter99Ifc;
    method Bit#(8) readBcd();
endinterface
""",
        snippet_template="""    Reg#(Bit#(4)) ones <- mkReg(0);
    Reg#(Bit#(4)) tens <- mkReg(0);

    // Write rule tick to count 00..99 in BCD
    // === YOUR CODE HERE ===

    method Bit#(8) readBcd();
        return {tens, ones};
    endmethod""",
        reference_snippet="""    Reg#(Bit#(4)) ones <- mkReg(0);
    Reg#(Bit#(4)) tens <- mkReg(0);

    rule tick;
        if (ones == 9) begin
            ones <= 0;
            tens <= (tens == 9) ? 0 : (tens + 1);
        end else begin
            ones <= ones + 1;
        end
    endrule

    method Bit#(8) readBcd();
        return {tens, ones};
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) r = ref_dut.readBcd();
        Bit#(8) u = user_dut.readBcd();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=clk:1|ref=bcd:0x%02h|user=bcd:0x%02h|match=%0d|note=BCD %02h", cycle, r, u, ok ? 1 : 0, r);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 13) begin
            $display("@SUMMARY total=14 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `rule tick;`, check `if (ones == 9)`.",
            "When `ones == 9`, set `ones <= 0;` and `tens <= (tens == 9) ? 0 : (tens + 1);`.",
            "When `ones != 9`, set `ones <= ones + 1;`.",
        ],
    )

    add(
        pid="15b_shift_piso_sipo",
        title="Universal Shift Register (Load, Shift-Left, Shift-Right, Hold)",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Easy",
        tags=["Shift Register", "SIPO/PISO", "Sequential"],
        description="""
A **Universal Shift Register** (`mkUnivShift8`) supports 4 operations selected by `Bit#(2) mode` inside `method Action step(Bit#(2) mode, Bit#(8) par_in, Bit#(1) ser_in)`:
- `mode == 2'd0` (**Hold**): `sr` stays unchanged.
- `mode == 2'd1` (**Shift Left**): `sr <= {sr[6:0], ser_in};`
- `mode == 2'd2` (**Shift Right**): `sr <= {ser_in, sr[7:1]};`
- `mode == 2'd3` (**Parallel Load**): `sr <= par_in;`

### Task
Implement `step` and `read` in `mkUnivShift8`.
""",
        bsv_vs_verilog="Bit-slicing and concatenation `{sr[6:0], ser_in}` inside a `case (mode)` cleanly expresses all 4 shift register modes.",
        diagram="mode[1:0], par_in[7:0], ser_in ---> [ Hold | << | >> | Load ] ---> sr[7:0]",
        interface_name="UnivShift8Ifc",
        module_name="mkUnivShift8",
        interface_def="""
interface UnivShift8Ifc;
    method Action step(Bit#(2) mode, Bit#(8) par_in, Bit#(1) ser_in);
    method Bit#(8) read();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) sr <- mkReg(0);

    method Action step(Bit#(2) mode, Bit#(8) par_in, Bit#(1) ser_in);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) read();
        return sr;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) sr <- mkReg(0);

    method Action step(Bit#(2) mode, Bit#(8) par_in, Bit#(1) ser_in);
        case (mode)
            2'd1: sr <= {sr[6:0], ser_in};
            2'd2: sr <= {ser_in, sr[7:1]};
            2'd3: sr <= par_in;
            default: noAction;
        endcase
    endmethod

    method Bit#(8) read();
        return sr;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(2) modes[8] = {2'd3, 2'd1, 2'd1, 2'd0, 2'd2, 2'd2, 2'd3, 2'd1};
        Bit#(8) r = ref_dut.read();
        Bit#(8) u = user_dut.read();
        ref_dut.step(modes[cycle], 8'hA5, cycle[0]);
        user_dut.step(modes[cycle], 8'hA5, cycle[0]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=mode:%0d,ser:%0d|ref=sr:0x%02h|user=sr:0x%02h|match=%0d|note=UnivShift", cycle, modes[cycle], cycle[0], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Use `case (mode)` on `2'd1`, `2'd2`, `2'd3`.",
            "For `2'd1` (Shift Left): `sr <= {sr[6:0], ser_in};`. For `2'd2` (Shift Right): `sr <= {ser_in, sr[7:1]};`.",
            "In BSV, `noAction;` represents a do-nothing Action in a `default:` branch.",
        ],
    )

    # =========================================================================
    # TRACK 4 ADDITIONS: RWIRE, URGENCY, 3-PORT CREG/EHR, CONFIGREG,FIFOS & CONNECTABLE
    # =========================================================================
    add(
        pid="18a_rwire_forwarding",
        title="Single-Cycle Value Forwarding with `RWire#(t)` (`wset` & `wget`)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["RWire", "Intra-Cycle Wire", "BSV Primitives"],
        description="""
In BSV, **`RWire#(t)`** is a combinational intra-cycle wire that carries a `Maybe#(t)` value from a writer to a reader within the **same clock cycle**:
- `rw.wset(val)` (`Action` method): drives `val` onto the wire for the current cycle.
- `rw.wget()` (Value method returning `Maybe#(t)`): returns `tagged Valid val` if `wset` was called this cycle, or `tagged Invalid` if `wset` was NOT called this cycle!

### Task
In `mkRWireAccumulator`:
- Hold `Reg#(Bit#(16)) acc <- mkReg(0);` and `RWire#(Bit#(16)) add_w <- mkRWire;`.
- `method Action addNow(Bit#(16) x)`: calls `add_w.wset(x);`.
- `rule update_acc`: Every cycle, if `add_w.wget()` is `tagged Valid .v`, add `v` to `acc` (`acc <= acc + v;`); otherwise increment `acc` by `1` (`acc <= acc + 1;`).
- `method Bit#(16) readAcc()`: returns `acc`.
""",
        bsv_vs_verilog="`RWire#(t)` gives you a safe, typed intra-cycle wire whose `Maybe#(t)` return value automatically encodes whether the wire was driven this cycle!",
        diagram="addNow(x) ---> add_w.wset(x) ---> rule update_acc (Valid v ? acc+v : acc+1) ---> acc",
        interface_name="RWireAccIfc",
        module_name="mkRWireAccumulator",
        interface_def="""
interface RWireAccIfc;
    method Action addNow(Bit#(16) x);
    method Bit#(16) readAcc();
endinterface
""",
        snippet_template="""    Reg#(Bit#(16))   acc   <- mkReg(0);
    RWire#(Bit#(16)) add_w <- mkRWire;

    // Write rule update_acc, method addNow(x), and method readAcc()
    // === YOUR CODE HERE ===
    method Action addNow(Bit#(16) x);
    endmethod

    method Bit#(16) readAcc();
        return acc;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(16))   acc   <- mkReg(0);
    RWire#(Bit#(16)) add_w <- mkRWire;

    rule update_acc;
        if (add_w.wget() matches tagged Valid .v)
            acc <= acc + v;
        else
            acc <= acc + 1;
    endrule

    method Action addNow(Bit#(16) x);
        add_w.wset(x);
    endmethod

    method Bit#(16) readAcc();
        return acc;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(16) r = ref_dut.readAcc();
        Bit#(16) u = user_dut.readAcc();
        if (cycle % 2 == 1) begin
            ref_dut.addNow(16'd10);
            user_dut.addNow(16'd10);
        end
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=add10:%0d|ref=acc:%0d|user=acc:%0d|match=%0d|note=RWire wget", cycle, (cycle%2==1)?1:0, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `addNow(Bit#(16) x)`, call `add_w.wset(x);`.",
            "In `rule update_acc;`, check `if (add_w.wget() matches tagged Valid .v) acc <= acc + v; else acc <= acc + 1;`.",
            "You can also write `acc <= acc + fromMaybe(1, add_w.wget());` — a super concise 1-liner!",
        ],
    )

    add(
        pid="18b_urgency_scheduler",
        title="Rule Priority Scheduling with `(* descending_urgency *)`",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["descending_urgency", "Rule Scheduling", "BSC Attributes"],
        description="""
When two rules can both be enabled in the same clock cycle and both write to the same `Reg`, BSV lets you explicitly specify which rule takes priority using the **`(* descending_urgency = "high_rule, low_rule" *)`** attribute!

### Task
In `mkUrgencyTimer`:
- Hold `Reg#(Bit#(8)) timer <- mkReg(10);` and `Reg#(Bool) reload_req <- mkReg(False);`.
- Define two rules that both write `timer`:
  1. `rule do_reload (reload_req)`: sets `timer <= 10;` and `reload_req <= False;`.
  2. `rule do_countdown (timer > 0)`: decrements `timer <= timer - 1;`.
- Add `(* descending_urgency = "do_reload, do_countdown" *)` above the rules so that whenever `reload_req` is `True`, `do_reload` preempts `do_countdown` without any compiler warning!
""",
        bsv_vs_verilog="Instead of deeply nested `if/else` trees inside one giant `always @(posedge clk)` block, BSV lets you write independent rules and declare their priority declaratively with `(* descending_urgency *)`.",
        diagram="(* descending_urgency = \"do_reload, do_countdown\" *) ---> do_reload preempts do_countdown",
        interface_name="UrgencyTimerIfc",
        module_name="mkUrgencyTimer",
        interface_def="""
interface UrgencyTimerIfc;
    method Action requestReload();
    method Bit#(8) readTimer();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) timer      <- mkReg(10);
    Reg#(Bool)    reload_req <- mkReg(False);

    // Add (* descending_urgency = "do_reload, do_countdown" *) and the two rules
    // === YOUR CODE HERE ===

    method Action requestReload();
        reload_req <= True;
    endmethod

    method Bit#(8) readTimer();
        return timer;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) timer      <- mkReg(10);
    Reg#(Bool)    reload_req <- mkReg(False);

    (* descending_urgency = "do_reload, do_countdown" *)
    rule do_reload (reload_req);
        timer <= 10;
        reload_req <= False;
    endrule

    rule do_countdown (timer > 0);
        timer <= timer - 1;
    endrule

    method Action requestReload();
        reload_req <= True;
    endmethod

    method Bit#(8) readTimer();
        return timer;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) r = ref_dut.readTimer();
        Bit#(8) u = user_dut.readTimer();
        if (cycle == 3) begin
            ref_dut.requestReload();
            user_dut.requestReload();
        end
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=reload:%0d|ref=tmr:%0d|user=tmr:%0d|match=%0d|note=Urgency", cycle, (cycle==3)?1:0, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Place `(* descending_urgency = \"do_reload, do_countdown\" *)` directly above `rule do_reload (reload_req);`.",
            "In `do_reload`, set `timer <= 10; reload_req <= False;`.",
            "In `do_countdown (timer > 0)`, set `timer <= timer - 1;`.",
        ],
    )

    add(
        pid="19b_creg_3port_counter",
        title="3-Port Concurrent Register (`Ehr#(3, Bit#(8))` / `CReg`) Accumulator",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["CReg / Ehr#(3,t)", "Multi-Ported State", "Concurrency"],
        description="""
Using a 3-port Concurrent Register **`Ehr#(3, Bit#(8)) cnt <- mkEhr(0);`** (known in BSV as `CReg` / `Ehr`), three different methods can read and modify the same state in a single clock cycle with a well-defined intra-cycle chain:
- **Port 0 (`addA(Bit#(8) x)`)**: `cnt[0] <= cnt[0] + x;`
- **Port 1 (`subB(Bit#(8) y)`)**: `cnt[1] <= cnt[1] - y;` (sees the result of `addA` if `addA` was called in the same cycle!)
- **Port 2 (`readFinal()`)**: `return cnt[2];` (sees the result after both `addA` and `subB` in the same cycle!)

### Task
Implement `addA`, `subB`, and `readFinal` in `mkCReg3Counter` using `Ehr#(3, Bit#(8))`.
""",
        bsv_vs_verilog="A 3-port `Ehr#(3, Bit#(8))` creates a 2-stage combinational forwarding chain `[0] -> [1] -> [2]` feeding a single 8-bit flip-flop bank.",
        diagram="addA(x) on cnt[0] ---> subB(y) on cnt[1] ---> readFinal() on cnt[2] ---> [ Reg ]",
        interface_name="CReg3CounterIfc",
        module_name="mkCReg3Counter",
        interface_def="""
interface CReg3CounterIfc;
    method Action addA(Bit#(8) x);
    method Action subB(Bit#(8) y);
    method Bit#(8) readFinal();
endinterface
""",
        snippet_template="""    Ehr#(3, Bit#(8)) cnt <- mkEhr(0);

    method Action addA(Bit#(8) x);
        // Use port 0
        // === YOUR CODE HERE ===
    endmethod

    method Action subB(Bit#(8) y);
        // Use port 1
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) readFinal();
        // Use port 2
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Ehr#(3, Bit#(8)) cnt <- mkEhr(0);

    method Action addA(Bit#(8) x);
        cnt[0] <= cnt[0] + x;
    endmethod

    method Action subB(Bit#(8) y);
        cnt[1] <= cnt[1] - y;
    endmethod

    method Bit#(8) readFinal();
        return cnt[2];
    endmethod""",
        testbench_body="""    rule test;
        if (cycle % 2 == 0) begin
            ref_dut.addA(8'd10);
            user_dut.addA(8'd10);
        end
        if (cycle >= 2) begin
            ref_dut.subB(8'd3);
            user_dut.subB(8'd3);
        end
        Bit#(8) r = ref_dut.readFinal();
        Bit#(8) u = user_dut.readFinal();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=cyc:%0d|ref=final:%0d|user=final:%0d|match=%0d|note=3-Port Ehr", cycle, cycle, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `addA(Bit#(8) x)`, write `cnt[0] <= cnt[0] + x;`.",
            "In `subB(Bit#(8) y)`, write `cnt[1] <= cnt[1] - y;`.",
            "In `readFinal()`, `return cnt[2];`.",
        ],
    )

    add(
        pid="19c_bypass_regfile",
        title="Multi-Ported Bypass Register File (`Vector#(4, Ehr#(2, Bit#(16)))`)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Hard",
        tags=["Bypass RegFile", "Ehr + Vector", "Processor Datapath"],
        description="""
In a 5-stage pipelined CPU, the **Writeback (WB)** stage writes a destination register `wr(rd, data)` in the exact same clock cycle that the **Decode (ID)** stage reads source registers `rd1(rs1)` and `rd2(rs2)`!
If `rs1 == rd`, `rd1(rs1)` must immediately receive the newly written `data` (**Write-Before-Read Bypassing**).

By instantiating `Vector#(4, Ehr#(2, Bit#(16))) rf <- replicateM(mkEhr(0));`:
- `writeReg(Bit#(2) rd, Bit#(16) data)` writes to **port 0** (`rf[rd][0] <= data;`).
- `readReg1(Bit#(2) rs1)` and `readReg2(Bit#(2) rs2)` read from **port 1** (`return rf[rs1][1];`).

### Task
Implement `writeReg`, `readReg1`, and `readReg2` in `mkBypassRegFile`.
""",
        bsv_vs_verilog="Combining `Vector` and `Ehr#(2, Bit#(16))` gives you a multi-ported register file with built-in write-to-read bypassing in 3 lines of BSV!",
        diagram="writeReg(rd, d) ---> rf[rd][0] <= d ---> rf[rs1][1] (readReg1), rf[rs2][1] (readReg2)",
        interface_name="BypassRegFileIfc",
        module_name="mkBypassRegFile",
        interface_def="""
interface BypassRegFileIfc;
    method Action   writeReg(Bit#(2) rd, Bit#(16) data);
    method Bit#(16) readReg1(Bit#(2) rs1);
    method Bit#(16) readReg2(Bit#(2) rs2);
endinterface
""",
        snippet_template="""    Vector#(4, Ehr#(2, Bit#(16))) rf <- replicateM(mkEhr(0));

    method Action writeReg(Bit#(2) rd, Bit#(16) data);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(16) readReg1(Bit#(2) rs1);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bit#(16) readReg2(Bit#(2) rs2);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Vector#(4, Ehr#(2, Bit#(16))) rf <- replicateM(mkEhr(0));

    method Action writeReg(Bit#(2) rd, Bit#(16) data);
        rf[rd][0] <= data;
    endmethod

    method Bit#(16) readReg1(Bit#(2) rs1);
        return rf[rs1][1];
    endmethod

    method Bit#(16) readReg2(Bit#(2) rs2);
        return rf[rs2][1];
    endmethod""",
        testbench_body="""    rule test;
        Bit#(2) rd = cycle[1:0];
        Bit#(16) wdata = 16'h1000 + (cycle[15:0] * 16'h0101);
        ref_dut.writeReg(rd, wdata);
        user_dut.writeReg(rd, wdata);
        Bit#(16) r1 = ref_dut.readReg1(rd);
        Bit#(16) u1 = user_dut.readReg1(rd);
        Bit#(16) r2 = ref_dut.readReg2(rd - 1);
        Bit#(16) u2 = user_dut.readReg2(rd - 1);
        Bool ok = (r1 == u1) && (r2 == u2);
        $display("@WAVE cycle=%0d|in=rd:%0d,wdata:0x%04h|ref=r1:0x%04h,r2:0x%04h|user=r1:0x%04h,r2:0x%04h|match=%0d|note=BypassRF", cycle, rd, wdata, r1, r2, u1, u2, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `writeReg(rd, data)`, write to port 0 of register `rd`: `rf[rd][0] <= data;`.",
            "In `readReg1(rs1)`, read from port 1: `return rf[rs1][1];`.",
            "In `readReg2(rs2)`, read from port 1: `return rf[rs2][1];`.",
        ],
    )

    add(
        pid="21b_bypass_fifof",
        title="Zero-Latency Bypass FIFO vs Pipeline FIFO (`SpecialFIFOs`)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["SpecialFIFOs", "mkBypassFIFOF", "Zero-Latency"],
        description="""
BSV's standard `SpecialFIFOs` library (`import SpecialFIFOs::*;`) provides two critical 1-element FIFOs used throughout industry RTL:
1. **`mkBypassFIFOF`**: Has combinational forwarding (`enq < deq`). When empty, an item enqueued via `enq(x)` can be read via `first()` and dequeued via `deq()` in the **exact same clock cycle** (**0-cycle latency**)!
2. **`mkPipelineFIFOF`**: Has `deq < enq` ordering (a true **RegSlice**). When full, `deq()` frees space so `enq(x)` can fire in the **same clock cycle** (**100% 1-item/cycle throughput** with 1-cycle latency)!

### Task
In `mkZeroLatBuffer`, instantiate `FIFOF#(Bit#(16)) bq <- mkBypassFIFOF;`:
- `enq(Bit#(16) x)`: enqueues `x` into `bq`.
- `deqAndScale()`: dequeues `bq` and returns `bq.first() * 2`.
Because `bq` is a `mkBypassFIFOF`, calling `enq(x)` and `deqAndScale()` in the same cycle works with zero latency!
""",
        bsv_vs_verilog="`SpecialFIFOs::mkBypassFIFOF` and `mkPipelineFIFOF` save hours of debugging subtle ready/valid combinational loops in AXI/NoC designs.",
        diagram="enq(x) ---> [ bq <- mkBypassFIFOF (enq < deq, 0-cycle latency) ] ---> deqAndScale() = first()*2",
        interface_name="ZeroLatBufferIfc",
        module_name="mkZeroLatBuffer",
        interface_def="""
interface ZeroLatBufferIfc;
    method Action enq(Bit#(16) x);
    method ActionValue#(Bit#(16)) deqAndScale();
endinterface
""",
        snippet_template="""    FIFOF#(Bit#(16)) bq <- mkBypassFIFOF;

    method Action enq(Bit#(16) x);
        // === YOUR CODE HERE ===
    endmethod

    method ActionValue#(Bit#(16)) deqAndScale();
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    FIFOF#(Bit#(16)) bq <- mkBypassFIFOF;

    method Action enq(Bit#(16) x);
        bq.enq(x);
    endmethod

    method ActionValue#(Bit#(16)) deqAndScale();
        Bit#(16) v = bq.first();
        bq.deq();
        return v * 2;
    endmethod""",
        testbench_body="""    rule feed;
        Bit#(16) x = 16'd10 + cycle[15:0] * 16'd5;
        ref_dut.enq(x);
        user_dut.enq(x);
    endrule

    rule drain;
        Bit#(16) r <- ref_dut.deqAndScale();
        Bit#(16) u <- user_dut.deqAndScale();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=cyc:%0d|ref=out:%0d|user=out:%0d|match=%0d|note=BypassFIFOF 0-lat", cycle, cycle, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `enq(Bit#(16) x)`, call `bq.enq(x);`.",
            "In `deqAndScale()`, read `let v = bq.first();`, call `bq.deq();`, and `return v * 2;`.",
            "Notice in the waveform that `feed` and `drain` fire in the exact same cycle `0` because `mkBypassFIFOF` schedules `enq < deq`!",
        ],
    )

    add(
        pid="21e_getput_connectable",
        title="Standard `Get` / `Put` Sub-Interfaces & `mkConnection` (`Connectable`)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["GetPut", "Connectable", "Sub-Interfaces"],
        description="""
BSV's **`GetPut`** (`import GetPut::*;`) and **`Connectable`** (`import Connectable::*;`) libraries standardize streaming interfaces across modules:
- `Put#(t)` has `method Action put(t x);`
- `Get#(t)` has `method ActionValue#(t) get();`
- `toPut(fifof)` and `toGet(fifof)` automatically convert any `FIFOF#(t)` into a `Put#(t)` or `Get#(t)` interface!

### Task
In `mkGetPutStage`:
- Instantiate `FIFOF#(Bit#(8)) in_q <- mkFIFOF;` and `FIFOF#(Bit#(8)) out_q <- mkFIFOF;`.
- Write a `rule process` that dequeues `x` from `in_q` and enqueues `x + 8'h10` into `out_q`.
- Expose `interface Put request = toPut(in_q);` and `interface Get response = toGet(out_q);`!
""",
        bsv_vs_verilog="Any two modules exposing `Get#(t)` and `Put#(t)` can be wired together in 1 line using `mkConnection(prod.response, cons.request);`!",
        diagram="request (Put#(8)) ---> [ in_q ] ---> rule (+0x10) ---> [ out_q ] ---> response (Get#(8))",
        interface_name="GetPutStageIfc",
        module_name="mkGetPutStage",
        interface_def="""
interface GetPutStageIfc;
    interface Put#(Bit#(8)) request;
    interface Get#(Bit#(8)) response;
endinterface
""",
        snippet_template="""    FIFOF#(Bit#(8)) in_q  <- mkFIFOF;
    FIFOF#(Bit#(8)) out_q <- mkFIFOF;

    // Write rule process and return sub-interfaces `request` and `response`
    // === YOUR CODE HERE ===
    interface Put request = toPut(in_q);
    interface Get response = toGet(out_q);""",
        reference_snippet="""    FIFOF#(Bit#(8)) in_q  <- mkFIFOF;
    FIFOF#(Bit#(8)) out_q <- mkFIFOF;

    rule process;
        out_q.enq(in_q.first() + 8'h10);
        in_q.deq();
    endrule

    interface Put request = toPut(in_q);
    interface Get response = toGet(out_q);""",
        testbench_body="""    Reg#(Bit#(4)) sent <- mkReg(0);
    Reg#(Bit#(4)) recvd <- mkReg(0);

    rule send_in (sent < 6);
        Bit#(8) v = 8'h01 + zeroExtend(sent);
        ref_dut.request.put(v);
        user_dut.request.put(v);
        sent <= sent + 1;
    endrule

    rule recv_out (recvd < 6);
        Bit#(8) r <- ref_dut.response.get();
        Bit#(8) u <- user_dut.response.get();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=idx:%0d|ref=out:0x%02h|user=out:0x%02h|match=%0d|note=GetPut", cycle, recvd, r, u, ok ? 1 : 0);
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
        if (cycle > 40) $finish(0);
    endrule""",
        hints=[
            "Write `rule process; out_q.enq(in_q.first() + 8'h10); in_q.deq(); endrule`.",
            "Expose the sub-interfaces with `interface Put request = toPut(in_q);` and `interface Get response = toGet(out_q);`.",
            "`toPut` and `toGet` are built into `import GetPut::*;`!",
        ],
    )

    add(
        pid="21h_combo_gearbox_8to16",
        title="Combination Lab: 8-Bit to 16-Bit Streaming Width Converter (Gearbox)",
        track_id="track4_concurrency",
        track_title="4. Concurrency, Scheduling, Ehr & FIFOs",
        difficulty="Medium",
        tags=["Combination Lab", "Gearbox", "SerDes / Streaming"],
        description="""
**Combination Lab (Combining `FIFOF` + Holding Register + Phase Toggle)**:
In high-speed SerDes, PCIe, and DMA engines, a **Gearbox (Width Upsizer)** accepts a stream of 8-bit bytes via `putByte(Bit#(8) b)` and outputs 16-bit words `{second_byte, first_byte}` (little-endian: first byte in `[7:0]`, second byte in `[15:8]`):
- Hold `Reg#(Bit#(8)) low_byte <- mkReg(0);`, `Reg#(Bool) has_low <- mkReg(False);`, and `FIFOF#(Bit#(16)) out_q <- mkFIFOF;`.
- On `putByte(Bit#(8) b)`:
  - If `!has_low`: store `low_byte <= b; has_low <= True;`
  - If `has_low`: enqueue `{b, low_byte}` into `out_q` and set `has_low <= False;`
- On `getWord()`: dequeue and return `out_q.first()`.

### Task
Implement `putByte` and `getWord` in `mkGearbox8to16`.
""",
        bsv_vs_verilog="Because `out_q.enq({b, low_byte})` is called inside `putByte` when `has_low` is true, BSV automatically propagates `out_q.notFull` backpressure to `putByte`!",
        diagram="putByte(b0), putByte(b1) ---> [ low_byte | has_low ] ---> out_q.enq({b1, b0}) ---> getWord()",
        interface_name="Gearbox8to16Ifc",
        module_name="mkGearbox8to16",
        interface_def="""
interface Gearbox8to16Ifc;
    method Action putByte(Bit#(8) b);
    method ActionValue#(Bit#(16)) getWord();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8))    low_byte <- mkReg(0);
    Reg#(Bool)       has_low  <- mkReg(False);
    FIFOF#(Bit#(16)) out_q    <- mkFIFOF;

    method Action putByte(Bit#(8) b);
        // === YOUR CODE HERE ===
    endmethod

    method ActionValue#(Bit#(16)) getWord();
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8))    low_byte <- mkReg(0);
    Reg#(Bool)       has_low  <- mkReg(False);
    FIFOF#(Bit#(16)) out_q    <- mkFIFOF;

    method Action putByte(Bit#(8) b);
        if (!has_low) begin
            low_byte <= b;
            has_low <= True;
        end else begin
            out_q.enq({b, low_byte});
            has_low <= False;
        end
    endmethod

    method ActionValue#(Bit#(16)) getWord();
        Bit#(16) w = out_q.first();
        out_q.deq();
        return w;
    endmethod""",
        testbench_body="""    Reg#(Bit#(4)) sent <- mkReg(0);
    Reg#(Bit#(4)) recvd <- mkReg(0);

    rule push (sent < 8);
        Bit#(8) b = 8'h10 + zeroExtend(sent) * 8'h11;
        ref_dut.putByte(b);
        user_dut.putByte(b);
        sent <= sent + 1;
    endrule

    rule pop (recvd < 4);
        Bit#(16) r <- ref_dut.getWord();
        Bit#(16) u <- user_dut.getWord();
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=word:%0d|ref=w:0x%04h|user=w:0x%04h|match=%0d|note=Gearbox 8->16", cycle, recvd, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (recvd == 3) begin
            $display("@SUMMARY total=4 passed=%0d", np);
            $finish(0);
        end
        recvd <= recvd + 1;
    endrule

    rule tick;
        cycle <= cycle + 1;
        if (cycle > 40) $finish(0);
    endrule""",
        hints=[
            "In `putByte(Bit#(8) b)`, if `!has_low`, save `low_byte <= b; has_low <= True;`.",
            "Else (`has_low` is `True`), call `out_q.enq({b, low_byte});` and set `has_low <= False;`.",
            "In `getWord()`, call `out_q.deq();` and `return out_q.first();`.",
        ],
    )

    # =========================================================================
    # NEW TRACK 7: CLOCK DOMAIN CROSSING (CDC) & SYNCHRONIZERS (`Clocks` Principles)
    # =========================================================================
    add(
        pid="61_cdc_2ff_sync",
        title="CDC 1: Two-Flip-Flop Metastability Synchronizer (`SyncBit` Principle)",
        track_id="track7_cdc",
        track_title="7. Clock Domain Crossing (CDC) & Synchronizers",
        difficulty="Easy",
        tags=["CDC", "2-FF Synchronizer", "Clocks::mkSyncBit"],
        description="""
Welcome to **Track 7: Clock Domain Crossing (CDC)**!
When a 1-bit level signal crosses from a source clock domain (`src_clk`) into an asynchronous destination clock domain (`dst_clk`), sampling it directly can cause **metastability**.
In BSV's `Clocks` package (`mkSyncBit`), a single-bit synchronizer uses a **2-Flip-Flop Synchronizer Chain** (`sync_ff1` -> `sync_ff2`) in the destination clock domain to allow metastable states to settle:
- Every cycle on `sampleAsync(Bit#(1) async_in)`:
  - `ff1 <= async_in;`
  - `ff2 <= ff1;`
- `syncedOut()` returns `ff2` (a clean, 2-cycle synchronized signal).

### Task
Implement `sampleAsync` and `syncedOut` in `mkCdc2FFSync` with both `ff1` and `ff2` initialized to `0`.
""",
        bsv_vs_verilog="In multi-clock BSV (`import Clocks::*;`), `SyncBitIfc#(Bit#(1)) s <- mkSyncBit(sClk, sRst, dClk);` instantiates a hardware-verified 2-FF synchronizer and prevents accidental direct cross-clock reads at compile time!",
        diagram="async_in ---> [ ff1 (Meta-Hardened Reg) ] ---> [ ff2 (Sync Reg) ] ---> syncedOut()",
        interface_name="Cdc2FFSyncIfc",
        module_name="mkCdc2FFSync",
        interface_def="""
interface Cdc2FFSyncIfc;
    method Action sampleAsync(Bit#(1) async_in);
    method Bit#(1) syncedOut();
endinterface
""",
        snippet_template="""    Reg#(Bit#(1)) ff1 <- mkReg(0);
    Reg#(Bit#(1)) ff2 <- mkReg(0);

    method Action sampleAsync(Bit#(1) async_in);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(1) syncedOut();
        return ff2;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(1)) ff1 <- mkReg(0);
    Reg#(Bit#(1)) ff2 <- mkReg(0);

    method Action sampleAsync(Bit#(1) async_in);
        ff1 <= async_in;
        ff2 <= ff1;
    endmethod

    method Bit#(1) syncedOut();
        return ff2;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(1) tv[8] = {1, 1, 1, 0, 0, 1, 0, 1};
        Bit#(1) r = ref_dut.syncedOut();
        Bit#(1) u = user_dut.syncedOut();
        ref_dut.sampleAsync(tv[cycle]);
        user_dut.sampleAsync(tv[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=async:%0d|ref=sync:%0d|user=sync:%0d|match=%0d|note=2-FF CDC Sync", cycle, tv[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `sampleAsync(Bit#(1) async_in)`, shift `ff1 <= async_in;` and `ff2 <= ff1;`.",
            "Because `ff2 <= ff1` reads the old value of `ff1`, `async_in` takes 2 clock edges to appear at `ff2`.",
            "Return `ff2` in `syncedOut()`.",
        ],
    )

    add(
        pid="62_cdc_toggle_pulse",
        title="CDC 2: Toggle-to-Pulse Synchronizer (`Clocks::mkSyncPulse` Principle)",
        track_id="track7_cdc",
        track_title="7. Clock Domain Crossing (CDC) & Synchronizers",
        difficulty="Medium",
        tags=["CDC", "Pulse Synchronizer", "Toggle Encoding"],
        description="""
What if a 1-cycle pulse in a **fast** clock domain needs to cross into a **slower** clock domain? A simple 2-FF synchronizer might miss the narrow 1-cycle pulse completely!
Instead, `Clocks::mkSyncPulse` uses a **Toggle Synchronizer**:
1. **Source Domain**: When `sendPulse` is asserted (`in_pulse == 1`), flip a toggle flip-flop: `src_toggle <= ~src_toggle;` (converting a 1-cycle pulse into a level transition!).
2. **Destination Domain**: Pass `src_toggle` through a synchronizer and XOR with the previous cycle's synchronized value `prev_toggle` (`dst_pulse = sync_toggle ^ prev_toggle`) to reconstruct a clean 1-cycle pulse on every transition!

### Task
Implement `stepToggleSync(Bit#(1) in_pulse)` in `mkCdcTogglePulse`:
- Update `src_toggle <= (in_pulse == 1) ? ~src_toggle : src_toggle;`
- Sample the previous `src_toggle` into `dst_prev <= src_toggle;`
- Return `src_toggle ^ dst_prev` (detecting whenever `src_toggle` toggled in the previous cycle!).
""",
        bsv_vs_verilog="Toggle-to-XOR pulse synchronization guarantees that isolated pulses are converted into level edges that cannot be dropped between clock edges.",
        diagram="in_pulse ---> [ src_toggle <= ^in_pulse ] ---> [ dst_prev ] ---> out_pulse = src_toggle ^ dst_prev",
        interface_name="CdcTogglePulseIfc",
        module_name="mkCdcTogglePulse",
        interface_def="""
interface CdcTogglePulseIfc;
    method ActionValue#(Bit#(1)) stepToggleSync(Bit#(1) in_pulse);
endinterface
""",
        snippet_template="""    Reg#(Bit#(1)) src_toggle <- mkReg(0);
    Reg#(Bit#(1)) dst_prev   <- mkReg(0);

    method ActionValue#(Bit#(1)) stepToggleSync(Bit#(1) in_pulse);
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(1)) src_toggle <- mkReg(0);
    Reg#(Bit#(1)) dst_prev   <- mkReg(0);

    method ActionValue#(Bit#(1)) stepToggleSync(Bit#(1) in_pulse);
        src_toggle <= src_toggle ^ in_pulse;
        dst_prev   <= src_toggle;
        return src_toggle ^ dst_prev;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(1) tv[8] = {1, 0, 0, 1, 0, 1, 1, 0};
        Bit#(1) r <- ref_dut.stepToggleSync(tv[cycle]);
        Bit#(1) u <- user_dut.stepToggleSync(tv[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=pulse:%0d|ref=out:%0d|user=out:%0d|match=%0d|note=TogglePulse", cycle, tv[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Notice that `in_pulse == 1 ? ~src_toggle : src_toggle` is simply `src_toggle ^ in_pulse`!",
            "Update `src_toggle <= src_toggle ^ in_pulse;` and `dst_prev <= src_toggle;`.",
            "Return `src_toggle ^ dst_prev;`.",
        ],
    )

    add(
        pid="64_cdc_async_fifo_flags",
        title="CDC 3: Async Dual-Clock FIFO Gray-Code Full & Empty Detector",
        track_id="track7_cdc",
        track_title="7. Clock Domain Crossing (CDC) & Synchronizers",
        difficulty="Hard",
        tags=["CDC", "Async FIFO", "Gray Pointers", "Clocks::mkSyncFIFO"],
        description="""
In BSV's `Clocks::mkSyncFIFO` (and Cliff Cummings' classic Async FIFO paper), an 8-entry asynchronous FIFO uses **4-bit pointers** (`[3:0]`, where bit 3 is the wrap bit and bits `2:0` index the 8 entries) encoded in **Gray code** so only 1 bit changes per increment across clock domains!
Given the 4-bit Gray-coded write pointer `wptr_gray` and 4-bit Gray-coded read pointer `rptr_gray`:
1. **FIFO is Empty (`isEmpty`)**: When `wptr_gray == rptr_gray` (all 4 bits match!).
2. **FIFO is Full (`isFull`)**: In 4-bit Gray code, when the write pointer is 8 entries ahead of the read pointer, the **top TWO MSBs (`[3:2]`) are inverted**, while the **bottom bits (`[1:0]`) are equal**:
   `wptr_gray == {~rptr_gray[3:2], rptr_gray[1:0]}`!
3. **Binary-to-Gray (`binToGray(Bit#(4) b)`)**: `b ^ (b >> 1)`.

### Task
Implement `binToGray`, `isEmpty`, and `isFull` in `mkAsyncFifoFlags`.
""",
        bsv_vs_verilog="Why invert the top TWO bits of Gray code for `isFull`? Because in reflected Gray code, the 2nd MSB (`bit 2`) is symmetric around the halfway point, so a pointer difference of 2^N flips both bit 3 and bit 2!",
        diagram="Empty: wptr_gray == rptr_gray   |   Full: wptr_gray == {~rptr_gray[3:2], rptr_gray[1:0]}",
        interface_name="AsyncFifoFlagsIfc",
        module_name="mkAsyncFifoFlags",
        interface_def="""
interface AsyncFifoFlagsIfc;
    method Bit#(4) binToGray(Bit#(4) b);
    method Bool    isEmpty(Bit#(4) wptr_gray, Bit#(4) rptr_gray);
    method Bool    isFull(Bit#(4) wptr_gray, Bit#(4) rptr_gray);
endinterface
""",
        snippet_template="""    method Bit#(4) binToGray(Bit#(4) b);
        // === YOUR CODE HERE ===
        return ?;
    endmethod

    method Bool isEmpty(Bit#(4) wptr_gray, Bit#(4) rptr_gray);
        // === YOUR CODE HERE ===
        return False;
    endmethod

    method Bool isFull(Bit#(4) wptr_gray, Bit#(4) rptr_gray);
        // === YOUR CODE HERE ===
        return False;
    endmethod""",
        reference_snippet="""    method Bit#(4) binToGray(Bit#(4) b);
        return b ^ (b >> 1);
    endmethod

    method Bool isEmpty(Bit#(4) wptr_gray, Bit#(4) rptr_gray);
        return wptr_gray == rptr_gray;
    endmethod

    method Bool isFull(Bit#(4) wptr_gray, Bit#(4) rptr_gray);
        return wptr_gray == {~rptr_gray[3:2], rptr_gray[1:0]};
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) wb[6] = {4'd0, 4'd3, 4'd8, 4'd9, 4'd5, 4'd12};
        Bit#(4) rb[6] = {4'd0, 4'd1, 4'd0, 4'd1, 4'd5, 4'd4};
        Bit#(4) wg = ref_dut.binToGray(wb[cycle]);
        Bit#(4) rg = ref_dut.binToGray(rb[cycle]);
        Bit#(4) ug = user_dut.binToGray(wb[cycle]);
        Bool re = ref_dut.isEmpty(wg, rg);
        Bool ue = user_dut.isEmpty(wg, rg);
        Bool rf = ref_dut.isFull(wg, rg);
        Bool uf = user_dut.isFull(wg, rg);
        Bool ok = (wg == ug) && (re == ue) && (rf == uf);
        $display("@WAVE cycle=%0d|in=wb:%0d,rb:%0d|ref=g:0x%01h,emp:%0d,full:%0d|user=g:0x%01h,emp:%0d,full:%0d|match=%0d|note=AsyncFIFO Gray",
            cycle, wb[cycle], rb[cycle], wg, re?1:0, rf?1:0, ug, ue?1:0, uf?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `binToGray(Bit#(4) b)`, `return b ^ (b >> 1);`.",
            "In `isEmpty(wptr_gray, rptr_gray)`, `return wptr_gray == rptr_gray;`.",
            "In `isFull(wptr_gray, rptr_gray)`, `return wptr_gray == {~rptr_gray[3:2], rptr_gray[1:0]};`.",
        ],
    )

    add(
        pid="65_cdc_mcp_handshake",
        title="CDC 4: Closed-Loop Req/Ack Multi-Cycle Path (MCP) Bus Synchronizer",
        track_id="track7_cdc",
        track_title="7. Clock Domain Crossing (CDC) & Synchronizers",
        difficulty="Medium",
        tags=["CDC", "MCP Handshake", "Req/Ack"],
        description="""
When transferring a wide 16-bit data bus across clock domains without a full Async FIFO, designers use a **Closed-Loop 4-Phase Req/Ack Handshake Synchronizer** (`mkCdcReqAckSender`):
- Sender holds `Reg#(Bit#(16)) data_hold <- mkReg(0);` and `Reg#(Bool) req_reg <- mkReg(False);`.
- Sender can accept a new `send(Bit#(16) d)` **only when `!req_reg && !ack_sync`** (guarded by `if (!req_reg && !ack_sync)`):
  - Latches `data_hold <= d;` and asserts `req_reg <= True;`.
- On `stepAck(Bool ack_sync)`:
  - Updates `ack_seen <= ack_sync;`
  - If `req_reg && ack_sync`, de-asserts `req_reg <= False;` (completing the handshake!).

### Task
Implement `send`, `stepAck`, `reqOut`, and `dataOut` in `mkCdcReqAckSender`.
""",
        bsv_vs_verilog="Holding `data_hold` stable from `req_reg <= True` until `ack_sync` arrives guarantees zero bus skew across clock domains!",
        diagram="send(d) [if !req && !ack] ---> [ data_hold | req=1 ] --(ack_sync==1)--> [ req=0 ]",
        interface_name="CdcReqAckIfc",
        module_name="mkCdcReqAckSender",
        interface_def="""
interface CdcReqAckIfc;
    method Action   send(Bit#(16) d);
    method Action   stepAck(Bool ack_sync);
    method Bool     reqOut();
    method Bit#(16) dataOut();
endinterface
""",
        snippet_template="""    Reg#(Bit#(16)) data_hold <- mkReg(0);
    Reg#(Bool)     req_reg   <- mkReg(False);
    Reg#(Bool)     ack_seen  <- mkReg(False);

    method Action send(Bit#(16) d) if (!req_reg && !ack_seen);
        // === YOUR CODE HERE ===
    endmethod

    method Action stepAck(Bool ack_sync);
        // === YOUR CODE HERE ===
    endmethod

    method Bool reqOut();
        return req_reg;
    endmethod

    method Bit#(16) dataOut();
        return data_hold;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(16)) data_hold <- mkReg(0);
    Reg#(Bool)     req_reg   <- mkReg(False);
    Reg#(Bool)     ack_seen  <- mkReg(False);

    method Action send(Bit#(16) d) if (!req_reg && !ack_seen);
        data_hold <= d;
        req_reg   <= True;
    endmethod

    method Action stepAck(Bool ack_sync);
        ack_seen <= ack_sync;
        if (req_reg && ack_sync) begin
            req_reg <= False;
        end
    endmethod

    method Bool reqOut();
        return req_reg;
    endmethod

    method Bit#(16) dataOut();
        return data_hold;
    endmethod""",
        testbench_body="""    rule test;
        Bool acks[8] = {False, False, True, True, False, False, True, False};
        Bool r_req = ref_dut.reqOut();
        Bool u_req = user_dut.reqOut();
        Bit#(16) r_d = ref_dut.dataOut();
        Bit#(16) u_d = user_dut.dataOut();
        if (cycle == 0 || cycle == 5) begin
            ref_dut.send(16'hC000 + cycle[15:0]);
            user_dut.send(16'hC000 + cycle[15:0]);
        end else begin
            ref_dut.stepAck(acks[cycle]);
            user_dut.stepAck(acks[cycle]);
        end
        Bool ok = (r_req == u_req) && (r_d == u_d);
        $display("@WAVE cycle=%0d|in=ack:%0d|ref=req:%0d,d:0x%04h|user=req:%0d,d:0x%04h|match=%0d|note=CDC MCP", cycle, acks[cycle]?1:0, r_req?1:0, r_d, u_req?1:0, u_d, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `send(Bit#(16) d) if (!req_reg && !ack_seen)`, set `data_hold <= d; req_reg <= True;`.",
            "In `stepAck(Bool ack_sync)`, update `ack_seen <= ack_sync;` and `if (req_reg && ack_sync) req_reg <= False;`.",
            "Keep `reqOut()` returning `req_reg` and `dataOut()` returning `data_hold`.",
        ],
    )

    # =========================================================================
    # NEW TRACK 9: VERIFICATION, TESTBENCHES & PROPERTY CHECKING IN BSV
    # =========================================================================
    add(
        pid="77_tb_stimulus_gen",
        title="Verification 1: Self-Checking ALU Testbench Scoreboard",
        track_id="track9_verification",
        track_title="9. Verification, Testbenches & Property Checkers",
        difficulty="Easy",
        tags=["Verification", "Scoreboard", "Golden Model"],
        description="""
Welcome to **Track 9: Hardware Verification & Testbenches in BSV**!
Unlike Verilog (where testbenches use non-synthesizable `initial begin #5 ...` blocks), **BSV testbenches and scoreboards are themselves synthesizable hardware modules** that can even run at MHz speeds on an FPGA!

### Task
Implement a **Self-Checking ALU Verification Monitor** (`mkAluVerifier`) that verifies a Device-Under-Test (DUT) adder/subtractor:
- Hold `Reg#(Bit#(8)) err_cnt <- mkReg(0);`.
- In `method ActionValue#(Bool) checkCycle(Bit#(8) a, Bit#(8) b, Bool is_sub, Bit#(8) dut_out)`:
  - Compute expected golden output `Bit#(8) exp = is_sub ? (a - b) : (a + b);`.
  - If `dut_out != exp`, increment `err_cnt <= err_cnt + 1;` and return `False`.
  - Otherwise return `True`.
- `method Bit#(8) errorCount()` returns `err_cnt`.
""",
        bsv_vs_verilog="Because BSV verification monitors are regular synthesizable modules, you can synthesize your testbench + scoreboard onto an FPGA alongside your DUT for hardware-accelerated verification!",
        diagram="(a, b, is_sub, dut_out) ---> [ exp = is_sub ? a-b : a+b ] ---> (dut_out == exp) & err_cnt",
        interface_name="AluVerifierIfc",
        module_name="mkAluVerifier",
        interface_def="""
interface AluVerifierIfc;
    method ActionValue#(Bool) checkCycle(Bit#(8) a, Bit#(8) b, Bool is_sub, Bit#(8) dut_out);
    method Bit#(8) errorCount();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) err_cnt <- mkReg(0);

    method ActionValue#(Bool) checkCycle(Bit#(8) a, Bit#(8) b, Bool is_sub, Bit#(8) dut_out);
        // === YOUR CODE HERE ===
        return True;
    endmethod

    method Bit#(8) errorCount();
        return err_cnt;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) err_cnt <- mkReg(0);

    method ActionValue#(Bool) checkCycle(Bit#(8) a, Bit#(8) b, Bool is_sub, Bit#(8) dut_out);
        Bit#(8) exp = is_sub ? (a - b) : (a + b);
        if (dut_out != exp) begin
            err_cnt <= err_cnt + 1;
            return False;
        end else begin
            return True;
        end
    endmethod

    method Bit#(8) errorCount();
        return err_cnt;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) a = 8'd20 + cycle[7:0] * 3;
        Bit#(8) b = 8'd5 + cycle[7:0];
        Bool sub = (cycle[0] == 1);
        Bit#(8) gold = sub ? (a - b) : (a + b);
        // Inject simulated bug on cycles 2 and 5
        Bit#(8) dut_out = (cycle == 2 || cycle == 5) ? (gold ^ 8'h01) : gold;
        Bool r_ok <- ref_dut.checkCycle(a, b, sub, dut_out);
        Bool u_ok <- user_dut.checkCycle(a, b, sub, dut_out);
        Bit#(8) r_err = ref_dut.errorCount();
        Bit#(8) u_err = user_dut.errorCount();
        Bool ok = (r_ok == u_ok) && (r_err == u_err);
        $display("@WAVE cycle=%0d|in=dut:0x%02h|ref=pass:%0d,errs:%0d|user=pass:%0d,errs:%0d|match=%0d|note=Scoreboard", cycle, dut_out, r_ok?1:0, r_err, u_ok?1:0, u_err, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bit#(8) exp = is_sub ? (a - b) : (a + b);`.",
            "If `dut_out != exp`, increment `err_cnt <= err_cnt + 1;` and `return False;`.",
            "Otherwise `return True;`.",
        ],
    )

    add(
        pid="80_tb_fifo_invariant",
        title="Verification 2: FIFO Conservation & Overflow/Underflow Property Monitor",
        track_id="track9_verification",
        track_title="9. Verification, Testbenches & Property Checkers",
        difficulty="Medium",
        tags=["Verification", "Property Checker", "FIFO Invariants"],
        description="""
In formal & dynamic verification, we verify a FIFO of maximum capacity `MAX_DEPTH = 4` by monitoring its boundary events `(enq_en, deq_en, reported_empty, reported_full)` every cycle:
Track a shadow occupancy counter `Reg#(Bit#(4)) occ <- mkReg(0);` (`0`..`4`):
- **Property A (`full_ok`)**: `reported_full == (occ == 4)`
- **Property B (`empty_ok`)**: `reported_empty == (occ == 0)`
- **Property C (`no_overflow`)**: `!(occ == 4 && enq_en && !deq_en)`
- **Property D (`no_underflow`)**: `!(occ == 0 && deq_en && !enq_en)`
When all 4 properties hold (`ok = full_ok && empty_ok && no_overflow && no_underflow`), update `occ`:
- If `enq_en && !deq_en`: `occ <= occ + 1;`
- Else if `!enq_en && deq_en`: `occ <= occ - 1;`

### Task
Implement `observeCycle(Bool enq_en, Bool deq_en, Bool reported_empty, Bool reported_full)` returning `True` if all 4 properties hold in the current cycle, and `False` if any property is violated!
""",
        bsv_vs_verilog="Writing hardware property monitors as BSV rules/methods lets you verify protocol invariants in both Bluesim and FPGA emulation.",
        diagram="(enq_en, deq_en, emp, full) ---> [ Shadow Occupancy occ (0..4) ] ---> Check Props A,B,C,D",
        interface_name="FifoPropMonitorIfc",
        module_name="mkFifoPropMonitor",
        interface_def="""
interface FifoPropMonitorIfc;
    method ActionValue#(Bool) observeCycle(Bool enq_en, Bool deq_en, Bool reported_empty, Bool reported_full);
endinterface
""",
        snippet_template="""    Reg#(Bit#(4)) occ <- mkReg(0);

    method ActionValue#(Bool) observeCycle(Bool enq_en, Bool deq_en, Bool reported_empty, Bool reported_full);
        // Check full_ok, empty_ok, no_overflow, no_underflow and update occ
        // === YOUR CODE HERE ===
        return True;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(4)) occ <- mkReg(0);

    method ActionValue#(Bool) observeCycle(Bool enq_en, Bool deq_en, Bool reported_empty, Bool reported_full);
        Bool full_ok = (reported_full == (occ == 4));
        Bool empty_ok = (reported_empty == (occ == 0));
        Bool no_ovf = !(occ == 4 && enq_en && !deq_en);
        Bool no_udf = !(occ == 0 && deq_en && !enq_en);
        Bool all_ok = full_ok && empty_ok && no_ovf && no_udf;
        if (all_ok) begin
            if (enq_en && !deq_en) occ <= occ + 1;
            else if (!enq_en && deq_en) occ <= occ - 1;
        end
        return all_ok;
    endmethod""",
        testbench_body="""    rule test;
        // Sequence: enq, enq, enq+deq, deq, deq, illegal underflow deq!, enq, fake full!
        Bool venq[8]  = {True,  True,  True,  False, False, False, True,  False};
        Bool vdeq[8]  = {False, False, True,  True,  True,  True,  False, False};
        Bool vemp[8]  = {True,  False, False, False, False, True,  True,  False};
        Bool vfull[8] = {False, False, False, False, False, False, False, True};
        Bool r <- ref_dut.observeCycle(venq[cycle], vdeq[cycle], vemp[cycle], vfull[cycle]);
        Bool u <- user_dut.observeCycle(venq[cycle], vdeq[cycle], vemp[cycle], vfull[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=enq:%0d,deq:%0d|ref=prop_ok:%0d|user=prop_ok:%0d|match=%0d|note=FIFO Prop", cycle, venq[cycle]?1:0, vdeq[cycle]?1:0, r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Check the 4 booleans: `Bool full_ok = (reported_full == (occ == 4));`, `Bool empty_ok = (reported_empty == (occ == 0));`, `Bool no_ovf = !(occ == 4 && enq_en && !deq_en);`, `Bool no_udf = !(occ == 0 && deq_en && !enq_en);`.",
            "Combine `Bool all_ok = full_ok && empty_ok && no_ovf && no_udf;`.",
            "When `all_ok` is `True`, update `occ`: if `enq_en && !deq_en` increment `occ`, else if `!enq_en && deq_en` decrement `occ`.",
        ],
    )

    add(
        pid="81_tb_arbiter_mutex",
        title="Verification 3: Arbiter Mutual-Exclusion & Work-Conserving Property Checker",
        track_id="track9_verification",
        track_title="9. Verification, Testbenches & Property Checkers",
        difficulty="Medium",
        tags=["Verification", "Arbiter Properties", "One-Hot Assertion"],
        description="""
Any hardware arbiter taking a 4-bit request vector `req` and outputting a 4-bit grant vector `gnt` must obey **three fundamental hardware properties** every cycle:
1. **Property A — No Unsolicited Grants**: A port can only be granted if it requested (`(gnt & ~req) == 0`).
2. **Property B — Mutual Exclusion (At-Most-One-Hot)**: At most one bit of `gnt` is `1` (`(gnt & (gnt - 1)) == 0`!).
3. **Property C — Work Conserving**: If at least one request is active (`req != 0`), then at least one grant must be issued (`gnt != 0`).

### Task
Implement `verifyArbiter(Bit#(4) req, Bit#(4) gnt)` returning `True` if and only if all 3 properties (`A && B && C`) hold!
""",
        bsv_vs_verilog="The classic bit-hack `(gnt & (gnt - 1)) == 0` checks that `gnt` has at most one `1` bit (0 or 1-hot) in O(1) gates!",
        diagram="(req[3:0], gnt[3:0]) ---> [ (gnt & ~req)==0 ] & [ (gnt & (gnt-1))==0 ] & [ (req!=0) => (gnt!=0) ]",
        interface_name="ArbiterVerifierIfc",
        module_name="mkArbiterVerifier",
        interface_def="""
interface ArbiterVerifierIfc;
    method Bool verifyArbiter(Bit#(4) req, Bit#(4) gnt);
endinterface
""",
        snippet_template="""    method Bool verifyArbiter(Bit#(4) req, Bit#(4) gnt);
        // Check Property A (subset of req), Property B (at-most-1-hot), Property C (work-conserving)
        // === YOUR CODE HERE ===
        return False;
    endmethod""",
        reference_snippet="""    method Bool verifyArbiter(Bit#(4) req, Bit#(4) gnt);
        Bool prop_a = (gnt & ~req) == 0;
        Bool prop_b = (gnt & (gnt - 1)) == 0;
        Bool prop_c = (req == 0) || (gnt != 0);
        return prop_a && prop_b && prop_c;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) vreq[8] = {4'b0000, 4'b0101, 4'b0101, 4'b1111, 4'b1010, 4'b0010, 4'b0000, 4'b0110};
        Bit#(4) vgnt[8] = {4'b0000, 4'b0001, 4'b0101, 4'b0000, 4'b0100, 4'b0010, 4'b0001, 4'b0100};
        Bool r = ref_dut.verifyArbiter(vreq[cycle], vgnt[cycle]);
        Bool u = user_dut.verifyArbiter(vreq[cycle], vgnt[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=req:0x%01h,gnt:0x%01h|ref=valid:%0d|user=valid:%0d|match=%0d|note=Arb Mutex", cycle, vreq[cycle], vgnt[cycle], r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Property A: `Bool prop_a = (gnt & ~req) == 0;`.",
            "Property B (at most one bit set): `Bool prop_b = (gnt & (gnt - 1)) == 0;`.",
            "Property C (if `req != 0` then `gnt != 0`): `Bool prop_c = (req == 0) || (gnt != 0);`. Return `prop_a && prop_b && prop_c;`.",
        ],
    )

    add(
        pid="85_tb_ready_valid_monitor",
        title="Verification 4: AXI Ready/Valid Handshake Stability Protocol Monitor",
        track_id="track9_verification",
        track_title="9. Verification, Testbenches & Property Checkers",
        difficulty="Medium",
        tags=["Verification", "AXI Protocol", "Handshake Stability"],
        description="""
In the **AXI / AMBA Ready-Valid Handshake Specification**, a master must obey the **Valid/Data Stability Rule**:
> Once `valid == 1` is asserted on a cycle where `ready == 0` (meaning the transfer is **stalled / backpressured**), the master **MUST keep `valid == 1` AND keep `data` unchanged** on the very next clock cycle!

### Task
Implement `checkAxiBeat(Bool valid, Bool ready, Bit#(8) data)` in `mkAxiHandshakeMonitor`:
- Hold `Reg#(Bool) pending_stall <- mkReg(False);` and `Reg#(Bit#(8)) held_data <- mkReg(0);`.
- If `pending_stall` is `True` from the previous cycle, then this cycle is legal **only if** `valid == True && data == held_data`!
- Update `pending_stall <= (valid && !ready);` and if `valid && !ready`, latch `held_data <= data;`.
- Return `True` if the current beat obeys the AXI stability rule, and `False` if it violated it!
""",
        bsv_vs_verilog="This exact assertion (`valid && !ready |=> valid && $stable(data)`) is the #1 SystemVerilog Assertion (SVA) used in commercial AXI VIPs!",
        diagram="Cycle N: (valid=1, ready=0, data=D) ---> Cycle N+1 MUST have (valid=1, data==D)!",
        interface_name="AxiHandshakeMonitorIfc",
        module_name="mkAxiHandshakeMonitor",
        interface_def="""
interface AxiHandshakeMonitorIfc;
    method ActionValue#(Bool) checkAxiBeat(Bool valid, Bool ready, Bit#(8) data);
endinterface
""",
        snippet_template="""    Reg#(Bool)    pending_stall <- mkReg(False);
    Reg#(Bit#(8)) held_data     <- mkReg(0);

    method ActionValue#(Bool) checkAxiBeat(Bool valid, Bool ready, Bit#(8) data);
        // === YOUR CODE HERE ===
        return True;
    endmethod""",
        reference_snippet="""    Reg#(Bool)    pending_stall <- mkReg(False);
    Reg#(Bit#(8)) held_data     <- mkReg(0);

    method ActionValue#(Bool) checkAxiBeat(Bool valid, Bool ready, Bit#(8) data);
        Bool legal = !pending_stall || (valid && (data == held_data));
        pending_stall <= (valid && !ready);
        if (valid && !ready) held_data <= data;
        return legal;
    endmethod""",
        testbench_body="""    rule test;
        Bool v_val[8] = {True,  True,  True,  False, True,  True,  True,  False};
        Bool v_rdy[8] = {False, True,  False, False, False, False, True,  True};
        Bit#(8) vd[8] = {8'hA1, 8'hA1, 8'hB2, 8'hB2, 8'hC3, 8'hD4, 8'hD4, 8'h00};
        // Cycle 3 drops valid after stall (illegal!), Cycle 5 changes data from C3 to D4 during stall (illegal!)
        Bool r <- ref_dut.checkAxiBeat(v_val[cycle], v_rdy[cycle], vd[cycle]);
        Bool u <- user_dut.checkAxiBeat(v_val[cycle], v_rdy[cycle], vd[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=v:%0d,r:%0d,d:0x%02h|ref=legal:%0d|user=legal:%0d|match=%0d|note=AXI Stability",
            cycle, v_val[cycle]?1:0, v_rdy[cycle]?1:0, vd[cycle], r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Check `Bool legal = !pending_stall || (valid && (data == held_data));`.",
            "Update `pending_stall <= (valid && !ready);`.",
            "When `valid && !ready`, save `held_data <= data;`, and `return legal;`.",
        ],
    )

    # =========================================================================
    # TRACK 6 ADDITIONS: PROTOCOLS (SPI, APB, NOC XY ROUTER) & ARCHITECTURE (2-WAY CACHE, BHT, FORWARDING, ROB, RISC-V IMM)
    # =========================================================================
    add(
        pid="28b_apb_slave",
        title="AMBA APB3 Peripheral Register Slave (`PSEL`, `PENABLE`, `PWRITE`)",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Medium",
        tags=["AMBA APB", "Peripheral Protocol", "SoC Bus"],
        description="""
The **AMBA APB (Advanced Peripheral Bus)** protocol is used in every ARM & RISC-V SoC to configure timers, UARTs, and GPIOs.
An APB transfer has two phases:
1. **SETUP Phase**: `psel == 1 && penable == 0`
2. **ACCESS Phase**: `psel == 1 && penable == 1` — the actual read or write commits at the end of the ACCESS cycle!

### Task
In `mkApbSlave` (holding 4 registers `Vector#(4, Reg#(Bit#(16))) regs <- replicateM(mkReg(0))`):
- Implement `method ActionValue#(Bit#(16)) apbCycle(Bool psel, Bool penable, Bool pwrite, Bit#(2) paddr, Bit#(16) pwdata)`:
  - When `psel && penable && pwrite`: write `regs[paddr] <= pwdata;` and return `0`.
  - When `psel && !pwrite`: return `regs[paddr]`.
  - Otherwise return `0`.
""",
        bsv_vs_verilog="Modeling an APB slave in BSV requires zero manual state machine states when zero wait-states (`PREADY = 1`) are used: `psel && penable && pwrite` triggers the register write directly!",
        diagram="SETUP (psel=1, penable=0) ---> ACCESS (psel=1, penable=1) ---> Write/Read regs[paddr]",
        interface_name="ApbSlaveIfc",
        module_name="mkApbSlave",
        interface_def="""
interface ApbSlaveIfc;
    method ActionValue#(Bit#(16)) apbCycle(Bool psel, Bool penable, Bool pwrite, Bit#(2) paddr, Bit#(16) pwdata);
endinterface
""",
        snippet_template="""    Vector#(4, Reg#(Bit#(16))) regs <- replicateM(mkReg(0));

    method ActionValue#(Bit#(16)) apbCycle(Bool psel, Bool penable, Bool pwrite, Bit#(2) paddr, Bit#(16) pwdata);
        // === YOUR CODE HERE ===
        return 0;
    endmethod""",
        reference_snippet="""    Vector#(4, Reg#(Bit#(16))) regs <- replicateM(mkReg(0));

    method ActionValue#(Bit#(16)) apbCycle(Bool psel, Bool penable, Bool pwrite, Bit#(2) paddr, Bit#(16) pwdata);
        if (psel && penable && pwrite) begin
            regs[paddr] <= pwdata;
            return 0;
        end else if (psel && !pwrite) begin
            return regs[paddr];
        end else begin
            return 0;
        end
    endmethod""",
        testbench_body="""    rule test;
        Bool vsel[6] = {True,  True,  True,  True,  False, True};
        Bool vena[6] = {False, True,  False, True,  False, True};
        Bool vwr[6]  = {True,  True,  False, False, False, False};
        Bit#(2) va[6]= {2'd2,  2'd2,  2'd2,  2'd2,  2'd0,  2'd2};
        Bit#(16) r <- ref_dut.apbCycle(vsel[cycle], vena[cycle], vwr[cycle], va[cycle], 16'hCAFE);
        Bit#(16) u <- user_dut.apbCycle(vsel[cycle], vena[cycle], vwr[cycle], va[cycle], 16'hCAFE);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=sel:%0d,en:%0d,wr:%0d|ref=prdata:0x%04h|user=prdata:0x%04h|match=%0d|note=APB3",
            cycle, vsel[cycle]?1:0, vena[cycle]?1:0, vwr[cycle]?1:0, r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Only write `regs[paddr] <= pwdata;` when all three are true: `if (psel && penable && pwrite)`.",
            "When `psel && !pwrite`, return `regs[paddr];`.",
            "Otherwise `return 0;`.",
        ],
    )

    add(
        pid="28f_noc_xy_router",
        title="2D Mesh Network-on-Chip (NoC) Dimension-Ordered XY Router",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Medium",
        tags=["NoC", "XY Routing", "Interconnect Architecture"],
        description="""
In multi-core processors and AI accelerators, tiles communicate over a **2D Mesh Network-on-Chip (NoC)** using **Dimension-Ordered XY Routing** (which is mathematically proven to be deadlock-free!):
Given the current router's coordinates `(my_x, my_y)` and a flit's destination coordinates `(dst_x, dst_y)`:
1. First route along the **X (Horizontal) axis**:
   - If `dst_x > my_x` -> output `DIR_EAST`
   - Else if `dst_x < my_x` -> output `DIR_WEST`
2. Once `dst_x == my_x`, route along the **Y (Vertical) axis**:
   - If `dst_y > my_y` -> output `DIR_NORTH`
   - Else if `dst_y < my_y` -> output `DIR_SOUTH`
3. When `dst_x == my_x && dst_y == my_y`, the flit has arrived! Output `DIR_LOCAL`.

### Task
Implement `routeXY(Bit#(4) my_x, Bit#(4) my_y, Bit#(4) dst_x, Bit#(4) dst_y)` in `mkNocXYRouter`.
""",
        bsv_vs_verilog="Deadlock-free XY routing is a foundational theorem of computer architecture interconnects (Dally & Towles): because packets never turn from Y back to X, channel dependency cycles cannot form!",
        diagram="(my_x, my_y) vs (dst_x, dst_y) ---> [ X-Axis (E/W) first ] ---> [ Y-Axis (N/S) second ] ---> LOCAL",
        interface_name="NocXYRouterIfc",
        module_name="mkNocXYRouter",
        interface_def="""
typedef enum {
    DIR_LOCAL,
    DIR_NORTH,
    DIR_SOUTH,
    DIR_EAST,
    DIR_WEST
} NocDir deriving (Bits, Eq);

interface NocXYRouterIfc;
    method NocDir routeXY(Bit#(4) my_x, Bit#(4) my_y, Bit#(4) dst_x, Bit#(4) dst_y);
endinterface
""",
        snippet_template="""    method NocDir routeXY(Bit#(4) my_x, Bit#(4) my_y, Bit#(4) dst_x, Bit#(4) dst_y);
        // Route X first (DIR_EAST / DIR_WEST), then Y (DIR_NORTH / DIR_SOUTH), else DIR_LOCAL
        // === YOUR CODE HERE ===
        return DIR_LOCAL;
    endmethod""",
        reference_snippet="""    method NocDir routeXY(Bit#(4) my_x, Bit#(4) my_y, Bit#(4) dst_x, Bit#(4) dst_y);
        if (dst_x > my_x) return DIR_EAST;
        else if (dst_x < my_x) return DIR_WEST;
        else if (dst_y > my_y) return DIR_NORTH;
        else if (dst_y < my_y) return DIR_SOUTH;
        else return DIR_LOCAL;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(4) dx[6] = {4'd5, 4'd1, 4'd3, 4'd3, 4'd3, 4'd4};
        Bit#(4) dy[6] = {4'd2, 4'd4, 4'd7, 4'd0, 4'd3, 4'd3};
        NocDir r = ref_dut.routeXY(4'd3, 4'd3, dx[cycle], dy[cycle]);
        NocDir u = user_dut.routeXY(4'd3, 4'd3, dx[cycle], dy[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=dst_x:%0d,dst_y:%0d|ref=dir:%0d|user=dir:%0d|match=%0d|note=NoC XY", cycle, dx[cycle], dy[cycle], pack(r), pack(u), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Check X coordinates first: `if (dst_x > my_x) return DIR_EAST; else if (dst_x < my_x) return DIR_WEST;`.",
            "Next check Y coordinates: `else if (dst_y > my_y) return DIR_NORTH; else if (dst_y < my_y) return DIR_SOUTH;`.",
            "Finally `else return DIR_LOCAL;`.",
        ],
    )

    add(
        pid="30c_branch_predictor_2bit",
        title="2-Bit Saturating Counter Branch History Table (BHT Predictor)",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["Branch Predictor", "2-Bit Counter", "Computer Architecture"],
        description="""
In pipelined processors (MIT 6.175 Lab 6), a **1-bit branch predictor** mispredicts twice on every loop exit. A **2-Bit Saturating Counter Branch History Table (BHT)** fixes this!
Each entry in our 4-entry table (`Vector#(4, Reg#(Bit#(2))) bht <- replicateM(mkReg(2'b01))` — initialized to **Weakly Not-Taken `2'b01`**):
- States:
  - `2'b00`: Strongly Not-Taken (`predict = False`)
  - `2'b01`: Weakly Not-Taken (`predict = False`)
  - `2'b10`: Weakly Taken (`predict = True`)
  - `2'b11`: Strongly Taken (`predict = True`)
- Notice `predict(Bit#(2) pc_idx)` simply checks the MSB: `bht[pc_idx][1] == 1`!
- On `update(Bit#(2) pc_idx, Bool taken)`:
  - If `taken == True`: increment `bht[pc_idx]` saturating at `2'b11` (`val == 3 ? 3 : val + 1`).
  - If `taken == False`: decrement `bht[pc_idx]` saturating at `2'b00` (`val == 0 ? 0 : val - 1`).

### Task
Implement `predict` and `update` in `mkBranchPredictorBht`.
""",
        bsv_vs_verilog="Initializing BHT entries to `2'b01` (Weakly Not-Taken) and predicting via the MSB `bht[idx][1] == 1` is the canonical hardware BHT design.",
        diagram="bht[idx]: 00 (SNT) <-> 01 (WNT) <-> 10 (WT) <-> 11 (ST)   |   predict = bht[idx][1]",
        interface_name="BranchPredictorIfc",
        module_name="mkBranchPredictorBht",
        interface_def="""
interface BranchPredictorIfc;
    method Bool   predict(Bit#(2) pc_idx);
    method Action update(Bit#(2) pc_idx, Bool taken);
endinterface
""",
        snippet_template="""    Vector#(4, Reg#(Bit#(2))) bht <- replicateM(mkReg(2'b01));

    method Bool predict(Bit#(2) pc_idx);
        // === YOUR CODE HERE ===
        return False;
    endmethod

    method Action update(Bit#(2) pc_idx, Bool taken);
        // === YOUR CODE HERE ===
    endmethod""",
        reference_snippet="""    Vector#(4, Reg#(Bit#(2))) bht <- replicateM(mkReg(2'b01));

    method Bool predict(Bit#(2) pc_idx);
        return bht[pc_idx][1] == 1;
    endmethod

    method Action update(Bit#(2) pc_idx, Bool taken);
        Bit#(2) s = bht[pc_idx];
        if (taken)
            bht[pc_idx] <= (s == 2'b11) ? 2'b11 : (s + 1);
        else
            bht[pc_idx] <= (s == 2'b00) ? 2'b00 : (s - 1);
    endmethod""",
        testbench_body="""    rule test;
        Bool vtaken[8] = {True, True, True, False, True, False, False, False};
        Bool r = ref_dut.predict(2'd1);
        Bool u = user_dut.predict(2'd1);
        ref_dut.update(2'd1, vtaken[cycle]);
        user_dut.update(2'd1, vtaken[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=taken:%0d|ref=pred:%0d|user=pred:%0d|match=%0d|note=2-Bit BHT", cycle, vtaken[cycle]?1:0, r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `predict(pc_idx)`, `return bht[pc_idx][1] == 1;` (or `bht[pc_idx] >= 2'b10`).",
            "In `update(pc_idx, taken)`, read `Bit#(2) s = bht[pc_idx];`.",
            "If `taken`, saturate at `2'b11` (`(s == 3) ? 3 : (s + 1)`). If `!taken`, saturate at `2'b00` (`(s == 0) ? 0 : (s - 1)`).",
        ],
    )

    add(
        pid="31b_forwarding_unit",
        title="5-Stage Pipeline EX/MEM & MEM/WB Data Forwarding Controller",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["Forwarding / Bypassing", "5-Stage Pipeline", "Computer Architecture"],
        description="""
In a 5-stage RISC-V pipeline (`IF -> ID -> EX -> MEM -> WB`), the **Forwarding Unit** resolves Read-After-Write (RAW) hazards without stalling by selecting the newest value for an Execute stage operand `rs` (`Bit#(3)`):
1. **EX/MEM Hazard (Newest — Priority 1)**: If `mem_reg_write && (mem_rd != 0) && (mem_rd == rs)`, forward `mem_val`!
2. **MEM/WB Hazard (Priority 2)**: Else if `wb_reg_write && (wb_rd != 0) && (wb_rd == rs)`, forward `wb_val`!
3. **No Hazard (Default)**: Otherwise use the register file value `rf_val`.
*(Remember: `rd == 0` is RISC-V `x0` and must NEVER be forwarded!)*

### Task
Implement `resolveOperand` in `mkForwardingUnit`.
""",
        bsv_vs_verilog="Notice why `mem_rd == rs` MUST take priority over `wb_rd == rs`: if two consecutive instructions both write to `x3`, the instruction in `MEM` is younger (more recent) than the instruction in `WB`!",
        diagram="rs, rf_val, (MEM: rd, val, we), (WB: rd, val, we) ---> [ Priority: MEM > WB > RF ] ---> Bit#(16)",
        interface_name="ForwardingUnitIfc",
        module_name="mkForwardingUnit",
        interface_def="""
interface ForwardingUnitIfc;
    method Bit#(16) resolveOperand(
        Bit#(3)  rs,
        Bit#(16) rf_val,
        Bool     mem_reg_write,
        Bit#(3)  mem_rd,
        Bit#(16) mem_val,
        Bool     wb_reg_write,
        Bit#(3)  wb_rd,
        Bit#(16) wb_val
    );
endinterface
""",
        snippet_template="""    method Bit#(16) resolveOperand(
        Bit#(3)  rs,
        Bit#(16) rf_val,
        Bool     mem_reg_write,
        Bit#(3)  mem_rd,
        Bit#(16) mem_val,
        Bool     wb_reg_write,
        Bit#(3)  wb_rd,
        Bit#(16) wb_val
    );
        // === YOUR CODE HERE ===
        return rf_val;
    endmethod""",
        reference_snippet="""    method Bit#(16) resolveOperand(
        Bit#(3)  rs,
        Bit#(16) rf_val,
        Bool     mem_reg_write,
        Bit#(3)  mem_rd,
        Bit#(16) mem_val,
        Bool     wb_reg_write,
        Bit#(3)  wb_rd,
        Bit#(16) wb_val
    );
        if (mem_reg_write && (mem_rd != 0) && (mem_rd == rs))
            return mem_val;
        else if (wb_reg_write && (wb_rd != 0) && (wb_rd == rs))
            return wb_val;
        else
            return rf_val;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(3)  vrs[6]  = {3'd2, 3'd2, 3'd2, 3'd0, 3'd4, 3'd5};
        Bool     mwe[6]  = {True, True, False, True, False, True};
        Bit#(3)  mrd[6]  = {3'd2, 3'd2, 3'd2, 3'd0, 3'd1, 3'd5};
        Bool     wwe[6]  = {False, True, True, True, True, False};
        Bit#(3)  wrd[6]  = {3'd2, 3'd2, 3'd2, 3'd0, 3'd4, 3'd5};
        Bit#(16) r = ref_dut.resolveOperand(vrs[cycle], 16'h1111, mwe[cycle], mrd[cycle], 16'h2222, wwe[cycle], wrd[cycle], 16'h3333);
        Bit#(16) u = user_dut.resolveOperand(vrs[cycle], 16'h1111, mwe[cycle], mrd[cycle], 16'h2222, wwe[cycle], wrd[cycle], 16'h3333);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=rs:%0d|ref=fwd:0x%04h|user=fwd:0x%04h|match=%0d|note=Forwarding", cycle, vrs[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "First check EX/MEM forwarding: `if (mem_reg_write && (mem_rd != 0) && (mem_rd == rs)) return mem_val;`.",
            "Next check MEM/WB forwarding: `else if (wb_reg_write && (wb_rd != 0) && (wb_rd == rs)) return wb_val;`.",
            "Otherwise `return rf_val;`.",
        ],
    )

    add(
        pid="16b_combo_debounce_edge",
        title="Combination Lab: 3-Cycle Glitch Debouncer + Rising Edge Detector",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Medium",
        tags=["Combination Lab", "Debouncer", "Shift Register + Edge"],
        description="""
**Combination Lab (Combining Shift Registers, All-Ones/All-Zeros Filtering, and Edge Detection)**:
Mechanical pushbuttons and noisy board traces bounce between `0` and `1` before settling.
Build a **3-Sample Glitch Filter + Rising-Edge Detector** (`mkDebounceEdge`):
- Hold a 3-bit history shift register `Reg#(Bit#(3)) hist <- mkReg(0);` and filtered state `Reg#(Bool) clean <- mkReg(False);`.
- When `sample(Bit#(1) raw_in)` is called:
  - Next history is `Bit#(3) next_h = {hist[1:0], raw_in};` (`hist <= next_h;`).
  - Next filtered state `Bool next_c = (next_h == 3'b111) ? True : ((next_h == 3'b000) ? False : clean);` (`clean <= next_c;`).
  - Return `True` **only on a clean rising edge** (`!clean && next_c`), else `False`!

### Task
Implement `sample(Bit#(1) raw_in)` and `cleanLevel()` in `mkDebounceEdge`.
""",
        bsv_vs_verilog="Combining `next_h = {hist[1:0], raw_in}` and `next_c` inside an `ActionValue#(Bool)` method computes both the state update and single-cycle clean rising-edge pulse.",
        diagram="raw_in ---> [ 3b Shift hist ] ---> (111=>1, 000=>0, else hold) ---> (!clean && next_c) pulse",
        interface_name="DebounceEdgeIfc",
        module_name="mkDebounceEdge",
        interface_def="""
interface DebounceEdgeIfc;
    method ActionValue#(Bool) sample(Bit#(1) raw_in);
    method Bool cleanLevel();
endinterface
""",
        snippet_template="""    Reg#(Bit#(3)) hist  <- mkReg(0);
    Reg#(Bool)    clean <- mkReg(False);

    method ActionValue#(Bool) sample(Bit#(1) raw_in);
        // === YOUR CODE HERE ===
        return False;
    endmethod

    method Bool cleanLevel();
        return clean;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(3)) hist  <- mkReg(0);
    Reg#(Bool)    clean <- mkReg(False);

    method ActionValue#(Bool) sample(Bit#(1) raw_in);
        Bit#(3) next_h = {hist[1:0], raw_in};
        Bool next_c = (next_h == 3'b111) ? True : ((next_h == 3'b000) ? False : clean);
        hist  <= next_h;
        clean <= next_c;
        return (!clean && next_c);
    endmethod

    method Bool cleanLevel();
        return clean;
    endmethod""",
        testbench_body="""    rule test;
        // Glitchy sequence: 1, 0 (glitch!), 1, 1, 1 (clean rises!), 0, 1 (glitch!), 0
        Bit#(1) vraw[8] = {1'b1, 1'b0, 1'b1, 1'b1, 1'b1, 1'b0, 1'b1, 1'b0};
        Bool r_p <- ref_dut.sample(vraw[cycle]);
        Bool u_p <- user_dut.sample(vraw[cycle]);
        Bool r_c = ref_dut.cleanLevel();
        Bool u_c = user_dut.cleanLevel();
        Bool ok = (r_p == u_p) && (r_c == u_c);
        $display("@WAVE cycle=%0d|in=raw:%0d|ref=clean:%0d,rise:%0d|user=clean:%0d,rise:%0d|match=%0d|note=Debouncer",
            cycle, vraw[cycle], r_c?1:0, r_p?1:0, u_c?1:0, u_p?1:0, ok ? 1 : 0);
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
            "Compute `Bool next_c = (next_h == 3'b111) ? True : ((next_h == 3'b000) ? False : clean);`.",
            "Update `hist <= next_h; clean <= next_c;` and `return (!clean && next_c);`.",
        ],
    )

    add(
        pid="17b_combo_stopwatch",
        title="Combination Lab: Programmable Stopwatch with Start, Pause, Lap & Clear",
        track_id="track3_sequential",
        track_title="3. Sequential Circuits, Registers & Rules",
        difficulty="Medium",
        tags=["Combination Lab", "Stopwatch", "Control + Datapath"],
        description="""
**Combination Lab (Combining Control State, Counter, and Lap Shadow Register)**:
Build a digital **Stopwatch Controller** (`mkStopwatch`) with:
- `Reg#(Bit#(8)) ticks <- mkReg(0);` (main counter)
- `Reg#(Bit#(8)) lap_reg <- mkReg(0);` (frozen lap display)
- `Reg#(Bool) running <- mkReg(False);` and `Reg#(Bool) lap_frozen <- mkReg(False);`
- `cmd(Bit#(2) op)` (`Action` method — called instead of free-running tick):
  - First compute `Bit#(8) next_ticks = running ? (ticks + 1) : ticks;`
  - Depending on `op`:
    - `2'd0` (`CMD_NOP`): keep `running` unchanged, `ticks <= next_ticks;`
    - `2'd1` (`CMD_START_PAUSE`): toggle `running <= !running;`, `ticks <= next_ticks;`
    - `2'd2` (`CMD_LAP`): latch `lap_reg <= next_ticks; lap_frozen <= !lap_frozen; ticks <= next_ticks;`
    - `2'd3` (`CMD_CLEAR`): reset `ticks <= 0; lap_reg <= 0; running <= False; lap_frozen <= False;`
- `display()`: returns `lap_frozen ? lap_reg : ticks`.

### Task
Implement `cmd(Bit#(2) op)` and `display()` in `mkStopwatch`.
""",
        bsv_vs_verilog="Keeping `ticks` advancing in the background while `lap_frozen` displays `lap_reg` is how real digital sports timers work.",
        diagram="cmd(op) ---> [ running | ticks++ | lap_reg ] ---> display() = lap_frozen ? lap_reg : ticks",
        interface_name="StopwatchIfc",
        module_name="mkStopwatch",
        interface_def="""
interface StopwatchIfc;
    method Action cmd(Bit#(2) op);
    method Bit#(8) display();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) ticks      <- mkReg(0);
    Reg#(Bit#(8)) lap_reg    <- mkReg(0);
    Reg#(Bool)    running    <- mkReg(False);
    Reg#(Bool)    lap_frozen <- mkReg(False);

    method Action cmd(Bit#(2) op);
        // === YOUR CODE HERE ===
    endmethod

    method Bit#(8) display();
        return lap_frozen ? lap_reg : ticks;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) ticks      <- mkReg(0);
    Reg#(Bit#(8)) lap_reg    <- mkReg(0);
    Reg#(Bool)    running    <- mkReg(False);
    Reg#(Bool)    lap_frozen <- mkReg(False);

    method Action cmd(Bit#(2) op);
        Bit#(8) next_t = running ? (ticks + 1) : ticks;
        case (op)
            2'd0: ticks <= next_t;
            2'd1: begin
                running <= !running;
                ticks <= next_t;
            end
            2'd2: begin
                lap_reg <= next_t;
                lap_frozen <= !lap_frozen;
                ticks <= next_t;
            end
            2'd3: begin
                ticks <= 0;
                lap_reg <= 0;
                running <= False;
                lap_frozen <= False;
            end
        endcase
    endmethod

    method Bit#(8) display();
        return lap_frozen ? lap_reg : ticks;
    endmethod""",
        testbench_body="""    rule test;
        // Start, nop, nop, lap (freeze), nop, lap (unfreeze), start/pause, clear
        Bit#(2) ops[8] = {2'd1, 2'd0, 2'd0, 2'd2, 2'd0, 2'd2, 2'd1, 2'd3};
        Bit#(8) r = ref_dut.display();
        Bit#(8) u = user_dut.display();
        ref_dut.cmd(ops[cycle]);
        user_dut.cmd(ops[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=op:%0d|ref=disp:%0d|user=disp:%0d|match=%0d|note=Stopwatch", cycle, ops[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "First compute `Bit#(8) next_t = running ? (ticks + 1) : ticks;`.",
            "Use `case (op)` for `2'd0`..`2'd3`.",
            "In `2'd2` (LAP), set `lap_reg <= next_t; lap_frozen <= !lap_frozen; ticks <= next_t;`.",
        ],
    )

    add(
        pid="22b_fsm_mealy_moore_vending",
        title="Vending Machine Controller FSM with Dispense & Change Calculation",
        track_id="track5_fsms",
        track_title="5. Finite State Machines & StmtFSM",
        difficulty="Medium",
        tags=["FSM", "Vending Machine", "HDLBits Classic"],
        description="""
A classic HDLBits & university digital design problem: build a **Vending Machine Controller** (`mkVendingFsm`) where an item costs **`15` cents**:
- Hold `Reg#(Bit#(8)) balance <- mkReg(0);`.
- In `method ActionValue#(VendOut) insertCoin(Bit#(8) coin)` (where `coin` is `0`, `5`, `10`, or `25`):
  - Compute `Bit#(8) total = balance + coin;`.
  - If `total >= 15`:
    - Dispense the item (`dispense = True`), return change `change = total - 15`, and reset `balance <= 0;`.
  - Else (`total < 15`):
    - Do not dispense (`dispense = False`), `change = 0`, and accumulate `balance <= total;`.

### Task
Implement `insertCoin` and `currentBalance` in `mkVendingFsm`.
""",
        bsv_vs_verilog="Instead of enumerating 4 separate states (0c, 5c, 10c, 15c) with 12 transition arcs, a datapath-plus-control FSM in BSV computes `total = balance + coin` cleanly!",
        diagram="coin (5/10/25) ---> [ total = balance + coin ] --(total>=15)--> dispense=1, change=total-15, bal<=0",
        interface_name="VendingFsmIfc",
        module_name="mkVendingFsm",
        interface_def="""
typedef struct {
    Bool    dispense;
    Bit#(8) change;
} VendOut deriving (Bits, Eq);

interface VendingFsmIfc;
    method ActionValue#(VendOut) insertCoin(Bit#(8) coin);
    method Bit#(8) currentBalance();
endinterface
""",
        snippet_template="""    Reg#(Bit#(8)) balance <- mkReg(0);

    method ActionValue#(VendOut) insertCoin(Bit#(8) coin);
        // === YOUR CODE HERE ===
        return VendOut { dispense: False, change: 0 };
    endmethod

    method Bit#(8) currentBalance();
        return balance;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(8)) balance <- mkReg(0);

    method ActionValue#(VendOut) insertCoin(Bit#(8) coin);
        Bit#(8) total = balance + coin;
        if (total >= 15) begin
            balance <= 0;
            return VendOut { dispense: True, change: total - 15 };
        end else begin
            balance <= total;
            return VendOut { dispense: False, change: 0 };
        end
    endmethod

    method Bit#(8) currentBalance();
        return balance;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) coins[6] = {8'd5, 8'd5, 8'd10, 8'd10, 8'd25, 8'd0};
        VendOut r <- ref_dut.insertCoin(coins[cycle]);
        VendOut u <- user_dut.insertCoin(coins[cycle]);
        Bit#(8) rb = ref_dut.currentBalance();
        Bit#(8) ub = user_dut.currentBalance();
        Bool ok = (r == u) && (rb == ub);
        $display("@WAVE cycle=%0d|in=coin:%0d|ref=disp:%0d,chg:%0d|user=disp:%0d,chg:%0d|match=%0d|note=VendingFSM",
            cycle, coins[cycle], r.dispense?1:0, r.change, u.dispense?1:0, u.change, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Compute `Bit#(8) total = balance + coin;`.",
            "If `total >= 15`, set `balance <= 0;` and `return VendOut { dispense: True, change: total - 15 };`.",
            "Else set `balance <= total;` and `return VendOut { dispense: False, change: 0 };`.",
        ],
    )

    add(
        pid="23b_combo_spi_master",
        title="Combination Lab: SPI Mode-0 Master Shift Engine (`CS_N`, `SCLK`, `MOSI`)",
        track_id="track5_fsms",
        track_title="5. Finite State Machines & StmtFSM",
        difficulty="Hard",
        tags=["Combination Lab", "SPI Master", "Serial Protocol"],
        description="""
**Combination Lab (Combining Shift Register, Clock Divider Phase, and Protocol Framing)**:
Build a 4-bit **SPI Mode-0 Master** (`mkSpiMaster4`) that shifts out 4 bits MSB-first (`tx_reg[3]`):
- Registers:
  - `Reg#(Bit#(4)) tx_reg <- mkReg(0);`
  - `Reg#(Bit#(3)) bits_left <- mkReg(0);` (`0` = idle, `4`..`1` = active)
  - `Reg#(Bit#(1)) sclk_reg <- mkReg(0);`
- `startTx(Bit#(4) data) if (bits_left == 0)`:
  - Sets `tx_reg <= data; bits_left <= 4; sclk_reg <= 0;`
- `rule step_spi (bits_left > 0)`:
  - When `sclk_reg == 0` (rising SCLK edge): set `sclk_reg <= 1;`
  - When `sclk_reg == 1` (falling SCLK edge): set `sclk_reg <= 0; tx_reg <= tx_reg << 1; bits_left <= bits_left - 1;`
- Outputs:
  - `cs_n()`: `1'b0` when `bits_left > 0`, else `1'b1` (Active-Low Chip Select!)
  - `sclk()`: `sclk_reg`
  - `mosi()`: `(bits_left > 0) ? tx_reg[3] : 1'b0` (MSB first!)

### Task
Implement `mkSpiMaster4`.
""",
        bsv_vs_verilog="SPI Mode-0 (`CPOL=0, CPHA=0`) holds `MOSI` stable while `SCLK` rises (`0->1`) and shifts to the next bit on the falling edge (`1->0`).",
        diagram="startTx(d) ---> [ CS_N=0 | SCLK 0->1 (sample) | SCLK 1->0 (tx_reg<<1, bits_left--) ] ---> CS_N=1",
        interface_name="SpiMaster4Ifc",
        module_name="mkSpiMaster4",
        interface_def="""
interface SpiMaster4Ifc;
    method Action startTx(Bit#(4) data);
    method Bit#(1) cs_n();
    method Bit#(1) sclk();
    method Bit#(1) mosi();
endinterface
""",
        snippet_template="""    Reg#(Bit#(4)) tx_reg    <- mkReg(0);
    Reg#(Bit#(3)) bits_left <- mkReg(0);
    Reg#(Bit#(1)) sclk_reg  <- mkReg(0);

    // Write rule step_spi (bits_left > 0) and interface methods
    // === YOUR CODE HERE ===
    method Action startTx(Bit#(4) data) if (bits_left == 0);
    endmethod

    method Bit#(1) cs_n();
        return 1'b1;
    endmethod

    method Bit#(1) sclk();
        return sclk_reg;
    endmethod

    method Bit#(1) mosi();
        return 1'b0;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(4)) tx_reg    <- mkReg(0);
    Reg#(Bit#(3)) bits_left <- mkReg(0);
    Reg#(Bit#(1)) sclk_reg  <- mkReg(0);

    rule step_spi (bits_left > 0);
        if (sclk_reg == 0) begin
            sclk_reg <= 1;
        end else begin
            sclk_reg  <= 0;
            tx_reg    <= tx_reg << 1;
            bits_left <= bits_left - 1;
        end
    endrule

    method Action startTx(Bit#(4) data) if (bits_left == 0);
        tx_reg    <= data;
        bits_left <= 4;
        sclk_reg  <= 0;
    endmethod

    method Bit#(1) cs_n();
        return (bits_left > 0) ? 1'b0 : 1'b1;
    endmethod

    method Bit#(1) sclk();
        return sclk_reg;
    endmethod

    method Bit#(1) mosi();
        return (bits_left > 0) ? tx_reg[3] : 1'b0;
    endmethod""",
        testbench_body="""    rule test;
        if (cycle == 0) begin
            ref_dut.startTx(4'b1011);
            user_dut.startTx(4'b1011);
        end
        Bit#(3) r_pins = {ref_dut.cs_n(), ref_dut.sclk(), ref_dut.mosi()};
        Bit#(3) u_pins = {user_dut.cs_n(), user_dut.sclk(), user_dut.mosi()};
        Bool ok = (r_pins == u_pins);
        $display("@WAVE cycle=%0d|in=tx:1011|ref=cs:%0d,sclk:%0d,mosi:%0d|user=cs:%0d,sclk:%0d,mosi:%0d|match=%0d|note=SPI Mode0",
            cycle, r_pins[2], r_pins[1], r_pins[0], u_pins[2], u_pins[1], u_pins[0], ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 9) begin
            $display("@SUMMARY total=10 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "In `startTx(Bit#(4) data) if (bits_left == 0)`, set `tx_reg <= data; bits_left <= 4; sclk_reg <= 0;`.",
            "In `rule step_spi (bits_left > 0)`, if `sclk_reg == 0` set `sclk_reg <= 1;`, else set `sclk_reg <= 0; tx_reg <= tx_reg << 1; bits_left <= bits_left - 1;`.",
            "Return `(bits_left > 0) ? 1'b0 : 1'b1` for `cs_n()`, and `(bits_left > 0) ? tx_reg[3] : 1'b0` for `mosi()`.",
        ],
    )

    add(
        pid="63_cdc_reset_stretcher",
        title="CDC 5: Asynchronous Reset Assertion / Synchronous De-Assertion Stretcher",
        track_id="track7_cdc",
        track_title="7. Clock Domain Crossing (CDC) & Synchronizers",
        difficulty="Medium",
        tags=["CDC", "Reset Synchronizer", "Reset Stretcher"],
        description="""
In ASIC & FPGA clock-domain design (`Clocks` package `mkAsyncReset`), releasing a reset asynchronously can violate flip-flop recovery/removal timing and send a chip into a metastable state!
A **Reset Stretcher / Synchronizer** (`mkResetStretcher`) guarantees that whenever `ext_rst_active` is `True`, the output reset immediately asserts (`rst_active = True`) and **remains asserted for at least 3 clean clock cycles** after `ext_rst_active` goes `False`:
- Hold a 3-bit shift register `Reg#(Bit#(3)) rst_sr <- mkReg(3'b111);` (initialized in reset!).
- In `method ActionValue#(Bool) stepReset(Bool ext_rst_active)`:
  - If `ext_rst_active == True`: force all 3 stages into reset (`rst_sr <= 3'b111;`) and return `True`.
  - Else (`ext_rst_active == False`): shift in `0` (`rst_sr <= {rst_sr[1:0], 1'b0};`) and return `(rst_sr[2] == 1)`.

### Task
Implement `stepReset(Bool ext_rst_active)` in `mkResetStretcher`.
""",
        bsv_vs_verilog="BSV's `mkAsyncReset(stages, rst_in, clk_dst)` implements this exact reset-stretcher topology in silicon.",
        diagram="ext_rst_active=1 ---> [ rst_sr <= 3'b111 ] | ext_rst_active=0 ---> [ rst_sr <= {rst_sr[1:0], 0} ]",
        interface_name="ResetStretcherIfc",
        module_name="mkResetStretcher",
        interface_def="""
interface ResetStretcherIfc;
    method ActionValue#(Bool) stepReset(Bool ext_rst_active);
endinterface
""",
        snippet_template="""    Reg#(Bit#(3)) rst_sr <- mkReg(3'b111);

    method ActionValue#(Bool) stepReset(Bool ext_rst_active);
        // === YOUR CODE HERE ===
        return True;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(3)) rst_sr <- mkReg(3'b111);

    method ActionValue#(Bool) stepReset(Bool ext_rst_active);
        if (ext_rst_active) begin
            rst_sr <= 3'b111;
            return True;
        end else begin
            rst_sr <= {rst_sr[1:0], 1'b0};
            return (rst_sr[2] == 1);
        end
    endmethod""",
        testbench_body="""    rule test;
        Bool vrst[8] = {False, False, False, False, True, False, False, False};
        Bool r <- ref_dut.stepReset(vrst[cycle]);
        Bool u <- user_dut.stepReset(vrst[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=ext_rst:%0d|ref=sync_rst:%0d|user=sync_rst:%0d|match=%0d|note=ResetStretcher", cycle, vrst[cycle]?1:0, r?1:0, u?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "If `ext_rst_active` is `True`, set `rst_sr <= 3'b111;` and `return True;`.",
            "If `ext_rst_active` is `False`, shift `rst_sr <= {rst_sr[1:0], 1'b0};` and `return (rst_sr[2] == 1);`.",
        ],
    )

    add(
        pid="79_tb_lfsr_fuzzer_cov",
        title="Verification 5: LFSR Pseudo-Random Stimulus Generator & Functional Coverage Bin Tracker",
        track_id="track9_verification",
        track_title="9. Verification, Testbenches & Property Checkers",
        difficulty="Medium",
        tags=["Verification", "Functional Coverage", "LFSR Fuzzer"],
        description="""
In modern verification (UVM / Constrained-Random / BSV FPGA Fuzzing), we drive pseudo-random stimulus into a DUT and track **Functional Coverage Bins** to know when every corner case has been exercised!
Build a **4-Bin Functional Coverage Collector** (`mkCoverageTracker`) for an 8-bit stimulus `val`:
- Bin 0 (`bin_mask[0]`): `val == 8'h00` (Zero corner case)
- Bin 1 (`bin_mask[1]`): `val == 8'hFF` (All-ones corner case)
- Bin 2 (`bin_mask[2]`): `val > 8'h00 && val < 8'h80` (Positive / low range)
- Bin 3 (`bin_mask[3]`): `val >= 8'h80 && val < 8'hFF` (Negative / high range)
- Hold `Reg#(Bit#(4)) cov_bins <- mkReg(0);`.
- When `sampleVal(Bit#(8) val)` is called, set the corresponding bit in `cov_bins` (keeping previously hit bits set via bitwise OR `|`) and return `True` if **100% coverage (`next_bins == 4'b1111`)** is achieved!

### Task
Implement `sampleVal(Bit#(8) val)` and `coverageMask()` in `mkCoverageTracker`.
""",
        bsv_vs_verilog="Synthesizable coverage bitmasks let you run billion-cycle fuzzing on an FPGA and light an LED the instant `cov_bins == 4'b1111`!",
        diagram="val[7:0] ---> [ Classify into Bin 0/1/2/3 ] ---> cov_bins <= cov_bins | hit ---> (next == 4'b1111)",
        interface_name="CoverageTrackerIfc",
        module_name="mkCoverageTracker",
        interface_def="""
interface CoverageTrackerIfc;
    method ActionValue#(Bool) sampleVal(Bit#(8) val);
    method Bit#(4) coverageMask();
endinterface
""",
        snippet_template="""    Reg#(Bit#(4)) cov_bins <- mkReg(0);

    method ActionValue#(Bool) sampleVal(Bit#(8) val);
        // === YOUR CODE HERE ===
        return False;
    endmethod

    method Bit#(4) coverageMask();
        return cov_bins;
    endmethod""",
        reference_snippet="""    Reg#(Bit#(4)) cov_bins <- mkReg(0);

    method ActionValue#(Bool) sampleVal(Bit#(8) val);
        Bit#(4) hit = 0;
        if (val == 8'h00)      hit = 4'b0001;
        else if (val == 8'hFF) hit = 4'b0010;
        else if (val < 8'h80)  hit = 4'b0100;
        else                   hit = 4'b1000;
        Bit#(4) next_bins = cov_bins | hit;
        cov_bins <= next_bins;
        return (next_bins == 4'b1111);
    endmethod

    method Bit#(4) coverageMask();
        return cov_bins;
    endmethod""",
        testbench_body="""    rule test;
        Bit#(8) stim[6] = {8'h25, 8'h00, 8'h50, 8'hA0, 8'hFF, 8'h12};
        Bool r_done <- ref_dut.sampleVal(stim[cycle]);
        Bool u_done <- user_dut.sampleVal(stim[cycle]);
        Bit#(4) r_m = ref_dut.coverageMask();
        Bit#(4) u_m = user_dut.coverageMask();
        Bool ok = (r_done == u_done) && (r_m == u_m);
        $display("@WAVE cycle=%0d|in=val:0x%02h|ref=bins:%04b,full:%0d|user=bins:%04b,full:%0d|match=%0d|note=Coverage",
            cycle, stim[cycle], r_m, r_done?1:0, u_m, u_done?1:0, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Determine `Bit#(4) hit` for the 4 mutually exclusive ranges (`8'h00` -> `4'b0001`, `8'hFF` -> `4'b0010`, `< 8'h80` -> `4'b0100`, else `4'b1000`).",
            "Compute `Bit#(4) next_bins = cov_bins | hit;` and update `cov_bins <= next_bins;`.",
            "Return `(next_bins == 4'b1111);`.",
        ],
    )

    add(
        pid="83_tb_bug_hunt_fifo",
        title="Verification 6 (Bug Hunt): Fix the Off-By-One Wrap & Simultaneity Bug in a Ring Buffer",
        track_id="track9_verification",
        track_title="9. Verification, Testbenches & Property Checkers",
        difficulty="Medium",
        tags=["Bug Hunt", "Debugging", "Ring Buffer"],
        description="""
**Hardware Debugging Lab**: Below is a buggy 4-entry Ring Buffer Occupancy & Pointer Tracker (`mkBuggyRingTracker`) written by a junior engineer. It has **two classic RTL bugs**:
1. **Bug 1 (Pointer Wrap Bug)**: `wptr` and `rptr` are 2-bit pointers (`0..3`), yet the engineer wrote `wptr <= (wptr == 4) ? 0 : wptr + 1;` (which is impossible for a 2-bit number, though `wptr + 1` wraps modulo 4 naturally) AND forgot to advance `rptr` on simultaneous `do_enq && do_deq`!
2. **Bug 2 (Simultaneous Enq+Deq Occupancy Bug)**: When `do_enq && do_deq` both happen on the same cycle (when `count > 0`), `wptr` and `rptr` must **both** increment by 1, while `count` must **stay unchanged**!

### Specification
In `stepRing(Bool do_enq, Bool do_deq)`:
- Legal enqueue: `Bool enq_ok = do_enq && (count < 4 || do_deq);` (or simple: if `do_enq && !do_deq && count < 4`: `wptr <= wptr + 1; count <= count + 1;`; if `!do_enq && do_deq && count > 0`: `rptr <= rptr + 1; count <= count - 1;`; if `do_enq && do_deq && count > 0`: `wptr <= wptr + 1; rptr <= rptr + 1;` and `count` unchanged!).
- Return `{count, wptr, rptr}` (`Bit#(7)`).

### Task
Fix the buggy code in `mkBuggyRingTracker` so it passes verification!
""",
        bsv_vs_verilog="Forgetting the simultaneous `enq && deq` corner case is the #1 bug found by formal verification in hand-written RTL FIFOs!",
        diagram="(do_enq, do_deq) ---> [ Fix wptr, rptr, and count updates ] ---> {count[2:0], wptr[1:0], rptr[1:0]}",
        interface_name="BuggyRingIfc",
        module_name="mkBuggyRingTracker",
        interface_def="""
interface BuggyRingIfc;
    method Action stepRing(Bool do_enq, Bool do_deq);
    method Bit#(7) status();
endinterface
""",
        snippet_template="""    Reg#(Bit#(2)) wptr  <- mkReg(0);
    Reg#(Bit#(2)) rptr  <- mkReg(0);
    Reg#(Bit#(3)) count <- mkReg(0);

    method Action stepRing(Bool do_enq, Bool do_deq);
        // BUGGY CODE: Fix simultaneous do_enq && do_deq when count > 0!
        if (do_enq && !do_deq && count < 4) begin
            wptr  <= wptr + 1;
            count <= count + 1;
        end else if (!do_enq && do_deq && count > 0) begin
            rptr  <= rptr + 1;
            count <= count - 1;
        end
        // === FIX MISSING Simultaneous (do_enq && do_deq && count > 0) CASE HERE ===
    endmethod

    method Bit#(7) status();
        return {count, wptr, rptr};
    endmethod""",
        reference_snippet="""    Reg#(Bit#(2)) wptr  <- mkReg(0);
    Reg#(Bit#(2)) rptr  <- mkReg(0);
    Reg#(Bit#(3)) count <- mkReg(0);

    method Action stepRing(Bool do_enq, Bool do_deq);
        if (do_enq && !do_deq && count < 4) begin
            wptr  <= wptr + 1;
            count <= count + 1;
        end else if (!do_enq && do_deq && count > 0) begin
            rptr  <= rptr + 1;
            count <= count - 1;
        end else if (do_enq && do_deq && count > 0) begin
            wptr  <= wptr + 1;
            rptr  <= rptr + 1;
        end
    endmethod

    method Bit#(7) status();
        return {count, wptr, rptr};
    endmethod""",
        testbench_body="""    rule test;
        Bool venq[8] = {True, True, True, False, True, False, True, False};
        Bool vdeq[8] = {False, False, True, True, True, True, False, True};
        Bit#(7) r = ref_dut.status();
        Bit#(7) u = user_dut.status();
        ref_dut.stepRing(venq[cycle], vdeq[cycle]);
        user_dut.stepRing(venq[cycle], vdeq[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=enq:%0d,deq:%0d|ref=cnt:%0d,w:%0d,r:%0d|user=cnt:%0d,w:%0d,r:%0d|match=%0d|note=BugHunt FIFO",
            cycle, venq[cycle]?1:0, vdeq[cycle]?1:0, r[6:4], r[3:2], r[1:0], u[6:4], u[3:2], u[1:0], ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 7) begin
            $display("@SUMMARY total=8 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Look at what happens when `do_enq && do_deq && count > 0`.",
            "Add `else if (do_enq && do_deq && count > 0) begin wptr <= wptr + 1; rptr <= rptr + 1; end`.",
            "In that simultaneous case, `count` stays unchanged because 1 item enters and 1 item leaves!",
        ],
    )

    add(
        pid="30b_two_way_set_cache",
        title="2-Way Set-Associative Cache with LRU Replacement Policy",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Hard",
        tags=["2-Way Cache", "LRU Replacement", "Computer Architecture"],
        description="""
Direct-mapped caches suffer from conflict misses when two active addresses map to the same index. A **2-Way Set-Associative Cache with LRU (Least Recently Used) Replacement** (`mkCache2WaySet`) stores **two ways (Way 0 and Way 1)** in our single set:
- Registers:
  - `Reg#(Bool) v0 <- mkReg(False); Reg#(Bit#(8)) tag0 <- mkReg(0); Reg#(Bit#(16)) data0 <- mkReg(0);`
  - `Reg#(Bool) v1 <- mkReg(False); Reg#(Bit#(8)) tag1 <- mkReg(0); Reg#(Bit#(16)) data1 <- mkReg(0);`
  - `Reg#(Bit#(1)) lru_way <- mkReg(0);` (`0` = Way 0 is Least Recently Used, `1` = Way 1 is Least Recently Used)
- `access(Bit#(8) tag, Bool is_fill, Bit#(16) fill_data)`:
  - If `is_fill == False` (Read Lookup):
    - If `v0 && (tag0 == tag)`: Hit on Way 0! Set `lru_way <= 1;` (since Way 0 was just used, Way 1 is now LRU!) and return `tagged Valid data0`.
    - Else if `v1 && (tag1 == tag)`: Hit on Way 1! Set `lru_way <= 0;` and return `tagged Valid data1`.
    - Else: Miss! Return `tagged Invalid`.
  - If `is_fill == True` (Cache Line Allocation into `lru_way`):
    - If `lru_way == 0`: write `v0 <= True; tag0 <= tag; data0 <= fill_data; lru_way <= 1;`
    - Else (`lru_way == 1`): write `v1 <= True; tag1 <= tag; data1 <= fill_data; lru_way <= 0;`
    - Return `tagged Valid fill_data`.

### Task
Implement `access` in `mkCache2WaySet`.
""",
        bsv_vs_verilog="In a 2-way set-associative cache, a single 1-bit `lru_way` flip-flop per set tracks exact LRU: touching Way `w` sets `lru_way <= ~w`!",
        diagram="tag ---> [ Check Way 0 (v0, tag0) | Check Way 1 (v1, tag1) ] ---> Hit updates lru_way <= ~hit_way",
        interface_name="Cache2WaySetIfc",
        module_name="mkCache2WaySet",
        interface_def="""
interface Cache2WaySetIfc;
    method ActionValue#(Maybe#(Bit#(16))) access(Bit#(8) tag, Bool is_fill, Bit#(16) fill_data);
endinterface
""",
        snippet_template="""    Reg#(Bool)     v0      <- mkReg(False);
    Reg#(Bit#(8))  tag0    <- mkReg(0);
    Reg#(Bit#(16)) data0   <- mkReg(0);
    Reg#(Bool)     v1      <- mkReg(False);
    Reg#(Bit#(8))  tag1    <- mkReg(0);
    Reg#(Bit#(16)) data1   <- mkReg(0);
    Reg#(Bit#(1))  lru_way <- mkReg(0);

    method ActionValue#(Maybe#(Bit#(16))) access(Bit#(8) tag, Bool is_fill, Bit#(16) fill_data);
        // === YOUR CODE HERE ===
        return tagged Invalid;
    endmethod""",
        reference_snippet="""    Reg#(Bool)     v0      <- mkReg(False);
    Reg#(Bit#(8))  tag0    <- mkReg(0);
    Reg#(Bit#(16)) data0   <- mkReg(0);
    Reg#(Bool)     v1      <- mkReg(False);
    Reg#(Bit#(8))  tag1    <- mkReg(0);
    Reg#(Bit#(16)) data1   <- mkReg(0);
    Reg#(Bit#(1))  lru_way <- mkReg(0);

    method ActionValue#(Maybe#(Bit#(16))) access(Bit#(8) tag, Bool is_fill, Bit#(16) fill_data);
        if (!is_fill) begin
            if (v0 && (tag0 == tag)) begin
                lru_way <= 1;
                return tagged Valid data0;
            end else if (v1 && (tag1 == tag)) begin
                lru_way <= 0;
                return tagged Valid data1;
            end else begin
                return tagged Invalid;
            end
        end else begin
            if (lru_way == 0) begin
                v0 <= True; tag0 <= tag; data0 <= fill_data; lru_way <= 1;
            end else begin
                v1 <= True; tag1 <= tag; data1 <= fill_data; lru_way <= 0;
            end
            return tagged Valid fill_data;
        end
    endmethod""",
        testbench_body="""    rule test;
        // Fill A0 (way0), Fill B0 (way1), Read A0 (hits way0 -> way1 becomes LRU!), Fill C0 (evicts way1!), Read A0 (still hits!), Read B0 (misses!)
        Bit#(8)  vtag[6]  = {8'hA0, 8'hB0, 8'hA0, 8'hC0, 8'hA0, 8'hB0};
        Bool     vfill[6] = {True,  True,  False, True,  False, False};
        Bit#(16) vdata[6] = {16'h1111, 16'h2222, 16'h0, 16'h3333, 16'h0, 16'h0};
        let r <- ref_dut.access(vtag[cycle], vfill[cycle], vdata[cycle]);
        let u <- user_dut.access(vtag[cycle], vfill[cycle], vdata[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=tag:0x%02h,fill:%0d|ref=hit:%0d,d:0x%04h|user=hit:%0d,d:0x%04h|match=%0d|note=2Way LRU",
            cycle, vtag[cycle], vfill[cycle]?1:0, isValid(r)?1:0, fromMaybe(0,r), isValid(u)?1:0, fromMaybe(0,u), ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "When `!is_fill`, check `if (v0 && (tag0 == tag))` -> set `lru_way <= 1; return tagged Valid data0;`.",
            "Next check `else if (v1 && (tag1 == tag))` -> set `lru_way <= 0; return tagged Valid data1;`, else `return tagged Invalid;`.",
            "When `is_fill`, allocate into `lru_way == 0` (setting `lru_way <= 1`) or `lru_way == 1` (setting `lru_way <= 0`).",
        ],
    )

    add(
        pid="32a_riscv_imm_gen",
        title="RISC-V RV32I Immediate Generator (`I-Type`, `S-Type`, `B-Type`, `U-Type`)",
        track_id="track6_architecture",
        track_title="6. RTL Protocols & Computer Architecture",
        difficulty="Medium",
        tags=["RISC-V", "Immediate Decoder", "MIT 6.175"],
        description="""
Every RISC-V RV32I processor Decode stage includes an **Immediate Generator** (`mkRiscvImmGen`) that extracts and sign-extends the 32-bit immediate from a 32-bit instruction `inst[31:0]` based on its opcode `inst[6:0]`:
- **I-Type** (`inst[6:0] == 7'b0010011` or `7'b0000011`):
  `signExtend(inst[31:20])`
- **S-Type** (`inst[6:0] == 7'b0100011` — Stores):
  `signExtend({inst[31:25], inst[11:7]})`
- **B-Type** (`inst[6:0] == 7'b1100011` — Conditional Branches):
  `signExtend({inst[31], inst[7], inst[30:25], inst[11:8], 1'b0})`
- **U-Type** (`inst[6:0] == 7'b0110111` — `LUI` / `AUIPC`, default):
  `{inst[31:12], 12'b0}`

### Task
Implement `decodeImm(Bit#(32) inst)` in `mkRiscvImmGen`.
""",
        bsv_vs_verilog="Notice why RISC-V keeps the sign bit at `inst[31]` across ALL instruction formats: the sign-extension fanout tree starts from `inst[31]` before opcode decoding even finishes!",
        diagram="inst[31:0] ---> [ Match inst[6:0]: I-Type | S-Type | B-Type | U-Type ] ---> imm[31:0]",
        interface_name="RiscvImmGenIfc",
        module_name="mkRiscvImmGen",
        interface_def="""
interface RiscvImmGenIfc;
    method Bit#(32) decodeImm(Bit#(32) inst);
endinterface
""",
        snippet_template="""    method Bit#(32) decodeImm(Bit#(32) inst);
        // Decode I-Type, S-Type, B-Type, and U-Type (default) immediates
        // === YOUR CODE HERE ===
        return ?;
    endmethod""",
        reference_snippet="""    method Bit#(32) decodeImm(Bit#(32) inst);
        Bit#(7) opcode = inst[6:0];
        case (opcode)
            7'b0010011, 7'b0000011: return signExtend(inst[31:20]);
            7'b0100011:             return signExtend({inst[31:25], inst[11:7]});
            7'b1100011:             return signExtend({inst[31], inst[7], inst[30:25], inst[11:8], 1'b0});
            default:                return {inst[31:12], 12'b0};
        endcase
    endmethod""",
        testbench_body="""    rule test;
        Bit#(32) vinst[6] = {
            32'hFFF00093, // ADDI x1, x0, -1 (I-Type)
            32'h01400113, // ADDI x2, x0, 20 (I-Type)
            32'hFE20AFA3, // SW x2, -1(x1)   (S-Type)
            32'hFE208EE3, // BEQ x1, x2, -4  (B-Type)
            32'h123451B7, // LUI x3, 0x12345 (U-Type)
            32'h00802083  // LW x1, 8(x0)    (I-Type)
        };
        Bit#(32) r = ref_dut.decodeImm(vinst[cycle]);
        Bit#(32) u = user_dut.decodeImm(vinst[cycle]);
        Bool ok = (r == u);
        $display("@WAVE cycle=%0d|in=inst:0x%08h|ref=imm:0x%08h|user=imm:0x%08h|match=%0d|note=RV32I Imm", cycle, vinst[cycle], r, u, ok ? 1 : 0);
        let np = passed_cnt + (ok ? 1 : 0);
        passed_cnt <= np;
        if (cycle == 5) begin
            $display("@SUMMARY total=6 passed=%0d", np);
            $finish(0);
        end
        cycle <= cycle + 1;
    endrule""",
        hints=[
            "Slice `Bit#(7) opcode = inst[6:0];` and `case (opcode)`.",
            "For `7'b0010011, 7'b0000011:` return `signExtend(inst[31:20]);`.",
            "For `7'b0100011:` return `signExtend({inst[31:25], inst[11:7]});`, for `7'b1100011:` return `signExtend({inst[31], inst[7], inst[30:25], inst[11:8], 1'b0});`, and `default:` return `{inst[31:12], 12'b0};`.",
        ],
    )

    return probs

