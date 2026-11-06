# BSVbits — Bluespec SystemVerilog Learning & Competitive Hardware Studio

**BSVbits** is a comprehensive learn-by-programming platform and competitive hardware design arena for **Bluespec SystemVerilog (BSV)**, Digital Electronics, VLSI Principles, Interconnect Protocols, Hardware Verification, and Computer Architecture — powered by the open-source **Bluespec Compiler (`bsc`)** and **Bluesim** cycle-accurate co-simulator.

Inspired by **HDLBits (01xz.net)**, **BSV by Example** (R. S. Nikhil & K. R. Czeck), **MIT 6.004 / 6.175 / 6.375 Constructive Computer Architecture**, **Bluespec Reference & User Guides**, and **NPTEL / GeeksforGeeks Digital Design**, BSVbits provides two integrated workflows backed by a free, zero-config **SQLite3 Relational DBMS (`workspace/bsvbits.db`)** that synchronizes user state between the **VS Code IDE** and the **Web Studio** in real time:

1. **Mode 1 — Guided Progression (HDLBits Mode — 79 Stored Problems across 8 Tracks)**:
   - A structured **79-problem curriculum across 8 progressive tracks** taking a complete beginner from a 1-bit wire all the way through combinational logic & **Combination Synthesis Labs**, strong types (`typedef enum`, `typedef struct`, `Maybe#(t)`, `Tuple2`, `Vector`, higher-order `map`/`fold`), sequential circuits (`mkReg`, `mkRegU`, counters, timers, PWM, LFSRs, edge detectors), concurrency & scheduling (`PulseWire`, `RWire`, `DReg`, `Ehr#(n, t)` / `CReg` concurrent registers, `FIFOF`, `mkBypassFIFOF`, `GetPut` & `Connectable`, 8-to-16 Gearboxes), FSMs (`StmtFSM`, Mealy/Moore detectors, I2C, UART), **Clock Domain Crossing (`Clocks` package principles: 2-FF `SyncBit`, toggle `SyncPulse`, Reset Stretchers, Gray Async FIFO pointers, MCP handshakes)**, **Hardware Verification, Testbenches & Property Checkers** (scoreboards, FIFO invariant monitors, arbiter mutex monitors, AXI ready/valid stability monitors, LFSR functional coverage, and RTL bug-hunting labs), and **RTL Protocols & Computer Architecture** (`AMBA APB3`, `AXI4-Lite`, `SPI Mode-0`, `2D Mesh NoC XY Router`, `2-Way Set-Associative LRU Cache`, `2-Bit Saturating BHT Branch Predictor`, `5-Stage Pipeline Hazard Forwarding Unit`, `Scoreboard`, `Shift-and-Add Multiplier`, `RISC-V Immediate Generator`, and a **Mini RISC-V RV32I Processor Core**).
2. **Mode 2 — Competitive Hardware Programming Arena (32 Families × 5 Question Formats + Daily & Timed Practice Packs)**:
   - A LeetCode/Codeforces-style **procedural hardware problem generator** (`backend/cp_generator.py` & `backend/cp_generator_extra.py`) covering **32 hardware, protocol, verification, and computer architecture families** across **5 distinct question formats**:
     1. **RTL Module Design from Specification** (`design_from_spec`)
     2. **Hardware Bug Hunt & RTL Repair** (`bug_fix_rtl` — diagnose and fix a subtle off-by-one, polarity, or bit-width bug in an existing BSV module)
     3. **Fill-in-the-Blanks Microarchitecture** (`fill_in_blanks` — complete missing expressions `/* TODO_EXPR */` in a partially written module)
     4. **Verification & Specification Compliance** (`verification_monitor` — verify cycle-by-cycle invariants against a strict hardware property testbench)
     5. **Reverse-Engineer Mystery Specification** (`reverse_engineer_mystery` — deduce the hardware function from an I/O truth/cycle trace table and implement it)
   - Supports **Daily Hardware Challenges** (deterministic daily seed with streak tracking) and **Timed Practice Pack Sessions** (customizable by **Time Budget** `10m–60m`, **Problem Count** or auto-fit to time, **Difficulty** `Easy / Medium / Hard / Mixed`, **Question Format**, and **Hardware Family**).

---

## Key Features

- **Bundled Free SQLite3 DBMS (`workspace/bsvbits.db`) with Shared VS Code + Web State**:
  - Tracks user profiles (`users`), solved curriculum problems (`curriculum_progress`), per-problem saved code (`saved_code`), compilation/simulation telemetry (`submissions`), generated CP challenges (`cp_problems`), and timed practice sessions (`cp_sessions`).
  - Switch user profiles anytime from the Web Topbar (`🗄 User: <name>`) or CLI (`./bsvbits user <username>`). Both VS Code (`workspace/current_problem.bsv`) and the Website share the exact same SQLite database state.
- **HDLBits-Style Part-by-Part Snippet & Full-Module Evaluation**:
  - Write only the core method/rule snippet (or toggle to Full Module mode). BSVbits automatically wraps your snippet, compiles it with `bsc`, and co-simulates it cycle-by-cycle against the **Golden Reference Model** in `Bluesim`.
- **Smart Hybrid Evaluator (Compiler + Co-Simulator + AST Semantic / LLM Reviewer)**:
  - Accepts any valid internal register/rule/variable naming and alternative hardware structures.
  - Includes an automatic **Interface Method Adapter**, **Friendly BSC Error Explanations**, **Idiomatic BSV Scoring (`0–100`)**, **Progressive Clues (`1/3`, `2/3`, `3/3`)**, and optional **OpenAI / Gemini LLM API** enrichment.
- **Interactive Digital Waveform, Rule Schedule & Synthesized Verilog Viewers**:
  - Visualizes `CLK`, stimulus inputs, `Golden Ref Output`, `Your Output`, and `Mismatch` flags across cycles, plus `bsc -show-schedule` (`CAN_FIRE`, `WILL_FIRE`, conflict matrix, execution order) and `bsc -verilog` RTL output.

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
| `./bsvbits list` | List all 79 curriculum problems across 8 tracks & solved status |
| `./bsvbits start <problem_id>` | Stage a problem into `workspace/current_problem.bsv` and `workspace/PROBLEM.md` |
| `./bsvbits submit` *(or `Ctrl+Shift+B` in VS Code)* | Compile with `bsc`, co-simulate in `Bluesim`, and write waveform/AI report to `workspace/last_result.md` |
| `./bsvbits daily` | Launch today's deterministic **Daily Hardware Challenge** into VS Code & Web Studio |
| `./bsvbits session --time 20 --difficulty Mixed --count 3 --format all` | Generate a **Timed Practice Pack Session** tailored to your time budget, difficulty, and format |
| `./bsvbits generate --difficulty Medium --format bug_fix_rtl` | Dynamically generate a single Competitive Arena problem (supports all 32 families & 5 formats) |
| `./bsvbits user <username>` | Switch the active shared user profile in SQLite (`workspace/bsvbits.db`) |
| `./bsvbits hint` | Unlock progressive clues & live AST comparison against the Golden Solution |
| `./bsvbits next` | Advance to the next curriculum problem |
| `./bsvbits solution` | Inspect the Golden Reference BSV solution |
| `python3 scripts/verify_curriculum.py` | Run automated `bsc` + `Bluesim` verification across all 79 curriculum problems & 32 CP generator families |

---

## Mode 1: Guided Progression (79 Stored Problems across 8 Tracks)

1. **Track 1: BSV Basics & Combinational Logic (15 Problems)**
   - `01_wire_zero` to `07_seven_seg` + `01b_wire_passthrough`, `02b_nand_nor_xnor`, `03b_mux2to1`, `04b_sign_zero_extend`, `05b_equality_comparator`, `06b_CarryLookahead4`, `07b_comb_alu_flags_combo`, `07c_comb_barrel_shifter_combo`
2. **Track 2: Strong Types, Enums, Structs & Vectors (11 Problems)**
   - `08_enum_alu` to `11_vector_popcount` + `08b_typedef_synonyms`, `09b_tagged_union_instr`, `10b_tuple_swap_minmax`, `10c_maybe_register_Forward`, `11b_vector_reverse_rotate`, `11c_vector_map_fold_max`, `11d_types_packet_classifier_combo`
3. **Track 3: Sequential Circuits, Registers & Atomic Rules (12 Problems)**
   - `12_dff_reg` to `17_gcd_euclid` + `12b_reg_sync_load_clear`, `13b_mod_n_counter`, `14b_saturating_counter`, `15b_shift_reg_siso_piso`, `16b_pwm_controller`, `17b_seq_stopwatch_combo`
4. **Track 4: Concurrency, Scheduling, Ehr, CRegs & Advanced FIFOs (11 Problems)**
   - `18_conflict_updown` to `21_pipeline_skid_buffer` + `18b_rwire_bypass_forwarding`, `18c_dreg_pulse_generator`, `19b_urgency_arbiter_rules`, `19c_creg_3port_regfile`, `20b_bypass_lockstep_fifo`, `21b_getput_connectable_pipe`, `21c_fifo_gearbox_8to16_combo`
5. **Track 5: Finite State Machines & StmtFSM (8 Problems)**
   - `22_fsm_seq_1011` to `25_stmtfsm_burst` + `22b_mealy_vending_machine`, `23b_i2c_start_stop_fsm`, `24b_uart_rx_oversample`, `25b_fsm_cmd_processor_combo`
6. **Track 6: Clock Domain Crossing (CDC), Resets & Multi-Clock Primitives (6 Problems)**
   - `33_cdc_2ff_syncbit`, `34_cdc_toggle_pulse_sync`, `35_cdc_reset_stretcher`, `36_cdc_gray_counter_async`, `37_cdc_async_fifo_flags`, `38_cdc_mcp_handshake_combo`
7. **Track 7: Hardware Verification, Testbenches & Property Checkers (6 Problems)**
   - `39_verif_alu_scoreboard`, `40_verif_fifo_invariant_monitor`, `41_verif_arbiter_mutex_checker`, `42_verif_axi_handshake_monitor`, `43_verif_lfsr_coverage_tracker`, `44_verif_bug_hunt_fifo_fix`
8. **Track 8: RTL Protocols & Computer Architecture (10 Problems)**
   - `26_arbiter_rr4` to `32_mini_riscv_alu_pc` + `27b_apb3_slave_peripheral`, `28b_spi_master_shift`, `29b_noc_xy_router_flit`, `30b_cache_2way_lru`, `31b_branch_predictor_2bit_bht`, `31c_pipeline_forwarding_unit`, `32b_riscv_imm_decoder`

---

## Mode 2: Competitive Hardware Programming Arena (32 Procedural Families)

- **Combinational & Bit-Manipulation**: Priority Encoders (`prio_encoder`), Binary/Gray/Parity Codecs (`gray_codec`), Barrel Rotators (`barrel_rotator`), Saturating DSP ALUs (`saturating_alu`), CLZ/CTZ Leading/Trailing Zero Detectors (`clz_ctz_detector`), One-Hot/Thermometer Codecs (`onehot_therm_codec`), Programmable Window Comparators (`window_comparator`), Configurable Multi-Lane Parity Generators (`crc_parity_gen`)
- **Sequential, Counters & Timers**: Modulo-N Counters (`modulo_counter`), Programmable PWM Timers (`pwm_timer`), Saturating Up/Down Counters (`updown_sat_counter`), Johnson/Ring Counters (`johnson_ring_counter`), Galois LFSR Scramblers (`lfsr_scrambler`), N-Cycle Glitch Debouncers (`debounce_glitch_filter`), Programmable Watchdog Timers (`watchdog_timer`)
- **Pipelines, FIFOs & Flow Control**: Guarded RegSlices (`regslice_transform`), Scaled MAC Engines (`mac_engine`), Credit Flow-Control Trackers (`skid_credit_fifo`), 8-to-16 Serializer Gearboxes (`gearbox_serializer`), Hardware Packet Firewalls (`packet_firewall`)
- **FSMs & Controllers**: KMP Bit-Stream Sequence Detectors (`pattern_fsm`), Parameterized Mealy Vending FSMs (`vending_mealy_fsm`)
- **Interconnect & Peripheral Protocols**: Custom-Permutation Masked Arbiters (`arbiter_perm`), Round-Robin Arbiters (`round_robin_arbiter`), AMBA APB3 Slave Peripherals (`apb_slave_periph`), AXI4-Lite Write Strobe Mergers (`axi_wstrb_merger`), 2D Mesh NoC XY Routers (`noc_xy_router`)
- **Computer Architecture**: 2-Bit Saturating BHT Branch Predictors (`branch_predictor_bht`), 5-Stage Pipeline Hazard Forwarding Units (`pipeline_forwarding`)
- **Hardware Verification & Assertion Monitors**: Arbiter Mutual-Exclusion Checkers (`verif_arbiter_checker`), AXI Ready/Valid Stability Monitors (`verif_axi_handshake`), FIFO Occupancy Conservation Monitors (`verif_fifo_conservation`)
