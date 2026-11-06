# BSVbits — Bluespec SystemVerilog Learning & Competitive Hardware Studio

**BSVbits** is a comprehensive learn-by-programming platform and competitive hardware design arena for **Bluespec SystemVerilog (BSV)** powered by the open-source **Bluespec Compiler (`bsc`)** and **Bluesim** cycle-accurate co-simulator.

Inspired by **HDLBits (01xz.net)**, **BSV by Example** (R. S. Nikhil & K. R. Czeck), **MIT 6.004 / 6.175 / 6.375 Constructive Computer Architecture**, **Bluespec Reference & User Guides**, and **NPTEL / GeeksforGeeks Digital Design**, BSVbits provides two integrated workflows:

1. **Mode 1 — Guided Progression (HDLBits Mode)**:
   - A stored, finite **32-problem curriculum across 6 progressive tracks** taking a complete beginner from a 1-bit wire all the way to combinational ALUs, strong types (`enum`, `struct`, `Maybe#(t)`, `Vector`), sequential registers (`mkReg`), atomic rules (`rule`), concurrency & bypassing (`PulseWire`, `Ehr#(n, t)`, `FIFOF`), FSMs (`StmtFSM`, UART, sequence detectors), bus protocols (`AXI4-Lite`, credit flow control, round-robin arbiters), caches, scoreboards, and a **Mini RISC-V RV32I processor core**.
2. **Mode 2 — Competitive Hardware Programming Arena (CP Generator Mode)**:
   - A LeetCode/Codeforces-style **procedural hardware problem generator** that dynamically synthesizes fresh, parameterized combinational and sequential RTL challenges (Priority Encoders, Modulo-N Step Counters, Guarded RegSlices, KMP Bit-Sequence Detector FSMs, Gray/Parity Codecs, Barrel Rotators, Saturating DSP ALUs, Programmable PWM Timers, Masked Arbiters, and Scaled MAC Units) along with on-hand Golden BSV Reference Solutions, cycle-accurate testbenches, and progressive clues.

---

## Key Features

- **HDLBits-Style Part-by-Part Snippet & Full-Module Evaluation**:
  - Write only the core method/rule snippet (or toggle to Full Module mode). BSVbits automatically wraps your snippet, compiles it with `bsc`, and co-simulates it cycle-by-cycle against the **Golden Reference Model** in `Bluesim`.
- **Smart Hybrid Evaluator (Compiler + Co-Simulator + AST Semantic / LLM Reviewer)**:
  - Accepts any valid internal register/rule/variable naming and alternative hardware structures (e.g., static `for` loops vs unrolled bit expressions, `case` vs ternary `? :`, multi-rule vs single-rule).
  - Includes an automatic **Interface Method Adapter** for minor naming variations, **Friendly BSC Error Explanations**, **Idiomatic BSV Scoring (`0–100`)**, **Progressive Clues (`1/3`, `2/3`, `3/3`)**, and optional **OpenAI / Gemini LLM API** enrichment.
- **Interactive Digital Waveform, Rule Schedule & Synthesized Verilog Viewers**:
  - Visualizes `CLK`, stimulus inputs, `Golden Ref Output`, `Your Output`, and `Mismatch` flags across cycles, plus `bsc -show-schedule` (`CAN_FIRE`, `WILL_FIRE`, conflict matrix, execution order) and `bsc -verilog` RTL output.
- **First-Class VS Code IDE & Web Studio Integration**:
  - Code directly inside **VS Code** via `workspace/current_problem.bsv` (with `.vscode/tasks.json` shortcuts, `.vscode/bsv.code-snippets`, and the bundled `vscode-extension/`) **or** inside the browser-based **Monaco Editor** studio with two-way live sync.

---

## Quickstart

### 1. Install / Verify Bluespec Compiler (`bsc`)
```bash
./scripts/setup_bsc.sh
```

### 2. Launch the Interactive BSVbits Studio Server
```bash
./bsvbits serve --port 8000
```
Open `http://localhost:8000` in your browser, or work directly in **VS Code** using the `workspace/` folder and CLI commands below!

---

## Using BSVbits in VS Code & CLI

| Command / Shortcut | Description |
|---|---|
| `./bsvbits list` | List all 32 curriculum problems across 6 tracks & solved status |
| `./bsvbits start <problem_id>` | Stage a problem into `workspace/current_problem.bsv` and `workspace/PROBLEM.md` |
| `./bsvbits submit` *(or `Ctrl+Shift+B` in VS Code)* | Compile with `bsc`, co-simulate in `Bluesim`, and write waveform/AI report to `workspace/last_result.md` |
| `./bsvbits hint` | Unlock progressive clues & live AST comparison against the Golden Solution |
| `./bsvbits generate --difficulty Medium` | Dynamically generate a fresh Competitive Arena hardware problem into VS Code |
| `./bsvbits next` | Advance to the next curriculum problem |
| `./bsvbits solution` | Inspect the Golden Reference BSV solution |
| `./bsvbits verify-all` | Run automated `bsc` + `Bluesim` verification across all 32 curriculum problems & 10 CP generators |

---

## Curriculum Overview (32 Stored Problems across 6 Tracks)

1. **Track 1: BSV Basics & Combinational Logic** (`01_wire_zero` – `07_seven_seg`)
2. **Track 2: Strong Types, Enums, Structs & Vectors** (`08_enum_alu` – `11_vector_popcount`)
3. **Track 3: Sequential Circuits, Registers & Rules** (`12_dff_reg` – `17_gcd_euclid`)
4. **Track 4: Concurrency, Scheduling, Ehr & FIFOs** (`18_conflict_updown` – `21_pipeline_skid_buffer`)
5. **Track 5: Finite State Machines & StmtFSM** (`22_fsm_seq_1011` – `25_stmtfsm_burst`)
6. **Track 6: RTL Protocols & Computer Architecture** (`26_arbiter_rr4` – `32_mini_riscv_alu_pc`)
