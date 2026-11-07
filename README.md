# BSVbits — Bluespec SystemVerilog Learning & Competitive Hardware Studio

**BSVbits** is an ultra-comprehensive learn-by-programming platform and competitive hardware design arena for **Bluespec SystemVerilog (BSV)**, Digital Electronics, VLSI Datapaths, DSP Arithmetic, Memory Subsystems, Clock Domain Crossing (CDC), Hardware Verification/Testbenches, Interconnect Protocols, and Computer Architecture — powered by the open-source **Bluespec Compiler (`bsc`)** and **Bluesim** cycle-accurate co-simulator.

Inspired by **HDLBits (01xz.net)**, **BSV by Example** (R. S. Nikhil & K. R. Czeck), **MIT 6.004 / 6.175 / 6.375 Constructive Computer Architecture**, **Bluespec Reference & User Guides**, and **NPTEL / GeeksforGeeks Digital Design**, BSVbits provides two tightly coupled workflows backed by a free, zero-config **SQLite3 Relational DBMS (`workspace/bsvbits.db`)** that synchronizes user state between the **VS Code IDE** and the **Web Studio** in real time:

1. **Mode 1 — Guided Progression (HDLBits Mode — 342 Stored Problems across 10 Comprehensive Tracks)**:
   - A finely graduated **342-problem curriculum across 10 progressive tracks** taking a complete beginner from a 1-bit wire all the way through combinational logic, strong types (`typedef enum`, `typedef struct`, `tagged union`, `Maybe#(t)`, `Tuple2`, `Vector` SIMD lanes, Hamming ECC, crossbars), sequential circuits (`mkReg`, `mkDReg`, counters, LFSRs, CRC-8, fractional dividers, debouncers, PWM, watchdogs, GCD), concurrency & scheduling (`PulseWire`, `RWire`, `descending_urgency`, `Ehr#(n, t)` / `CReg` multi-port registers, `FIFOF`, `mkBypassFIFOF`, `GetPut`/`Connectable`, gearboxes, token buckets, WFQ schedulers), FSMs & serial protocols (`StmtFSM`, Moore/Mealy detectors, traffic/elevator/vending FSMs, UART 8N1 TX/RX, SPI, I2C, Manchester, HDLC, AXI DMA burst engines), **Digital Arithmetic, VLSI Datapaths & DSP Engines** (saturating math, Q4.4 fixed-point, Booth/Wallace/CSA multipliers, non-restoring dividers, CORDIC, FIR/IIR/median filters, sorting networks), **Memory Subsystems, RegFiles, BRAMs, CAMs & Buffers** (1R1W/2R1W RegFiles, Read-First/Write-First BRAMs, banked interleaving, CAM, TCAM, circular FIFOs, LIFO stacks, free-list allocators, Bloom filters, Reorder Buffers), **Clock Domain Crossing (`Clocks` package: 2-FF/3-FF `SyncBit`, toggle `SyncPulse`, Reset Stretchers, glitch-free clock mux, Gray Async FIFO pointers & watermarks, 4-phase MCP handshakes)**, **Hardware Verification, Scoreboards, SVA Monitors & Bug Hunts** (reference scoreboards, FIFO/Arbiter/AXI/Credit invariant monitors, coverage trackers, and **10 progressive RTL Bug-Hunt repair labs**), and **Interconnect Protocols, Caches & Computer Architecture** (`AMBA APB3`, `AXI4-Lite`, `Wishbone`, `2D/3D Mesh NoC XY/XYZ Routers`, `Direct-Mapped / 2-Way LRU / Victim Caches`, `2-Bit BHT / Gshare / Tournament Predictors`, `Return Address Stack`, `5-Stage Hazard Forwarding`, `Scoreboard`, `Tomasulo Reservation Station`, `2-Way Superscalar Dual-Issue`, and a **Mini RISC-V RV32I Processor Core**).
   - Built-in **Spiral Reinforcement (`[Reinforce]`)**, **Cross-Track Revision (`[Revision]`)**, and **Multi-Topic Combination Labs (`[Combo Lab]`)** at the end of every sub-topic so concepts are continuously clubbed together and reinforced.

2. **Mode 2 — Competitive Hardware Programming Arena (80 Procedural Families × 7 Question Formats + Track-Targeted Reinforcement Sessions)**:
   - A LeetCode/Codeforces-style **procedural hardware problem synthesizer** (`backend/cp_generator.py`, `backend/cp_generator_extra.py`, `backend/cp_generator_bank.py`) covering **80 parameterized hardware, DSP, memory, CDC, verification, and computer architecture families** across **7 interactive question formats**:
     1. **RTL Module Design from Specification** (`design_from_spec`)
     2. **Hardware Bug Hunt & RTL Repair** (`bug_fix_rtl` — diagnose and fix an injected RTL bug in an existing BSV module)
     3. **Fill-in-the-Blanks Microarchitecture** (`fill_in_blanks` — complete missing expressions `/* TODO_BLANK */` in a partially written module)
     4. **Verification & Property Checking** (`verification_monitor` — write a cycle-accurate hardware assertion/invariant monitor)
     5. **Reverse-Engineer Mystery Circuit** (`reverse_engineer_mystery` — deduce and implement the hardware function from its I/O trace & diagram)
     6. **Spiral Track Reinforcement & Revision** (`spiral_reinforcement` — reinforce any Mode 1 curriculum track with fresh randomized parameters)
     7. **90-Second Blitz Speed-Coding Sprint** (`speed_coding_sprint` — rapid-fire completion under a 90s timer)
   - **Seamless Mode 1 ↔ Mode 2 Track Reinforcement**: Click **`🎯 CP Drill`** on any Mode 1 Track header in the Web Studio (or run `./bsvbits reinforce <1..10>`) to launch a **Track-Targeted CP Reinforcement Session** that procedurally generates fresh problems specifically reinforcing that track!

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
| `./bsvbits list` | List all **342 curriculum problems across 10 tracks** & solved status |
| `./bsvbits start <problem_id>` | Stage a problem into `workspace/current_problem.bsv` and `workspace/PROBLEM.md` |
| `./bsvbits submit` *(or `Ctrl+Shift+B` in VS Code)* | Compile with `bsc`, co-simulate in `Bluesim`, and write waveform/AI report to `workspace/last_result.md` |
| `./bsvbits reinforce <1..10>` | Launch a **Track-Targeted CP Reinforcement Session** for any Mode 1 Track (`1..10` or `track_id`) |
| `./bsvbits daily` | Launch today's deterministic **Daily Hardware Challenge** into VS Code & Web Studio |
| `./bsvbits session --time 20 --difficulty Mixed --count 3 --format all` | Generate a **Timed Practice Pack Session** tailored to your time budget, difficulty, and format |
| `./bsvbits generate --difficulty Medium --format bug_fix_rtl` | Dynamically generate a single Competitive Arena problem (supports all 80 families & 7 formats) |
| `./bsvbits user <username>` | Switch the active shared user profile in SQLite (`workspace/bsvbits.db`) |
| `./bsvbits hint` | Unlock progressive clues & live AST comparison against the Golden Solution |
| `./bsvbits next` | Advance to the next curriculum problem |
| `./bsvbits solution` | Inspect the Golden Reference BSV solution |
| `python3 scripts/verify_curriculum.py` | Run automated `bsc` + `Bluesim` verification across all **342 curriculum problems & 80 CP generator families** |

---

## Mode 1: Guided Progression (342 Stored Problems across 10 Tracks)

| Track | Title | Problems | Highlights & Combination Labs |
|---|---|---|---|
| **Track 1** | **BSV Basics & Combinational Logic** | **47** | Wires, literals, Bool vs Bit, universal gates, 2:1/4:1/8:1 muxes, demux, encoders/decoders, ripple/carry-lookahead/carry-select adders, Gray/BCD/Excess-3 codecs, CLZ/CTZ, barrel shifters, ALU flags & `[Combo Lab]` syntheses |
| **Track 2** | **Strong Types, Enums, Structs & Vectors** | **36** | `typedef enum`, `typedef struct`, `tagged union`, `Maybe#(t)`, `Tuple2`, `Vector` map/fold/scan/zip, SIMD nibble lanes, Hamming (7,4) SEC-DED ECC, 4x4 crossbars, IPv4/VLAN packet parsers & classifiers |
| **Track 3** | **Sequential Circuits, Registers & Atomic Rules** | **38** | `mkReg`, `mkRegU`, `mkDReg`, up/down/modulo/saturating/BCD/Johnson/Gray/ping-pong counters, SISO/PISO/universal shift registers, LFSRs, serial/parallel CRC-8, Bresenham dividers, debouncers, PWM, watchdogs, exponential backoff & Euclid's GCD |
| **Track 4** | **Concurrency, Scheduling, CReg/Ehr & Advanced FIFOs** | **36** | `PulseWire`, `mkPulseWireOR`, `RWire`, `descending_urgency`, `Ehr#(2, t)` / `CReg` multi-port registers & register files, `mkBypassFIFOF`, `mkPipelineFIFOF`, elastic skid buffers, `GetPut`/`Connectable`, 8:16 & 16:8 gearboxes, token-bucket policers & WFQ schedulers |
| **Track 5** | **Finite State Machines, Serial Protocols & StmtFSM** | **32** | Moore/Mealy sequence detectors, traffic/elevator/vending/windowed-watchdog FSMs, UART 8N1 TX & oversampled RX, SPI Mode 0–3 master, I2C start/stop/address matcher, Manchester encoder, HDLC bit-stuffer, AXI burst engines & `StmtFSM` microcode |
| **Track 6** | **Digital Arithmetic, VLSI Datapaths & DSP Engines** | **31** | Signed/unsigned saturating arithmetic, Q4.4 fixed-point MAC & LERP, Carry-Save (CSA) & Wallace trees, Radix-2 Booth & sequential multipliers, non-restoring divider, integer sqrt, CORDIC micro-rotations, 3-tap/4-tap FIR, EWMA/leaky-integrator IIR, 1D median filter & bitonic sorting networks |
| **Track 7** | **Memory Subsystems, RegFiles, BRAMs, CAMs & Buffers** | **29** | Register RAMs, Read-First vs Write-First synchronous BRAMs, forwarding bypass RAMs, true dual-port & banked interleaved memories, binary CAM, ternary TCAM (ACL wildcard matching), circular buffers, LIFO call stack, bitmap free-list allocator, Bloom filter & Reorder Buffer (ROB) |
| **Track 8** | **Clock Domain Crossing (CDC), Resets & Multi-Clock** | **26** | `Clocks` package principles: 2-FF/3-FF `SyncBit` chains, toggle `SyncPulse` synchronizers, async-assert/sync-deassert Reset Stretchers, glitch-free clock mux, Gray counters, Async FIFO Gray pointer full/empty/watermark comparators, 2-phase/4-phase MCP Req/Ack handshakes & credit return sync |
| **Track 9** | **Hardware Verification, Scoreboards, SVA Monitors & Bug Hunts** | **29** | Self-checking ALU/FIFO/Credit conservation scoreboards, SVA bounded-liveness/mutex/AXI-stability assertion monitors, Gray single-bit step checkers, coverage bin trackers, plus **10 progressive `[Bug Hunt]` RTL debugging & repair labs** |
| **Track 10** | **Interconnect Protocols, Caches & Computer Architecture** | **38** | Fixed/Round-Robin/Matrix arbiters, credit flow control, AMBA APB3, AXI4-Lite WSTRB slave, Wishbone, 2D XY & 3D XYZ NoC routers, Direct-Mapped / 2-Way LRU / Victim caches, 2-Bit BHT / Gshare / Tournament / Tagged branch predictors, Return Address Stack (RAS), 5-Stage forwarding & load-use stall units, Scoreboard, Tomasulo Reservation Station, 2-Way Superscalar Dual-Issue & **Mini RISC-V RV32I Core** |

---

## Mode 2: Competitive Hardware Programming Arena (80 Procedural Families × 7 Formats)

- **80 Parameterized Hardware Families across all 10 Tracks**:
  - **Combinational & Bitwise (12 Families)**: `prio_encoder`, `clz_ctz_detector`, `onehot_therm_codec`, `gray_codec`, `crc_parity_gen`, `barrel_rotator`, `window_comparator`, `bit_reversal_permute`, `bcd_excess3_codec`, `carry_save_compressor`, `majority_voter_tmr`, `popcount_threshold`
  - **Strong Types, SIMD Vectors, ECC & Crossbars (6 Families)**: `simd_vector_alu`, `hamming_secded_codec`, `crossbar_switch_4x4`, `prefix_scan_network`, `ipv4_header_validator`, `packet_firewall`
  - **Sequential, Counters, LFSR, CRC & Timers (12 Families)**: `modulo_counter`, `updown_sat_counter`, `johnson_ring_counter`, `lfsr_scrambler`, `debounce_glitch_filter`, `pwm_timer`, `watchdog_timer`, `crc8_serial_parallel`, `clk_divider_fractional`, `ping_pong_wave_gen`, `exp_backoff_controller`, `piso_sipo_transceiver`
  - **Concurrency, Ehr, FIFOs, Gearboxes & QoS (8 Families)**: `regslice_transform`, `skid_credit_fifo`, `gearbox_serializer`, `ehr_bypass_pipeline`, `token_bucket_shaper`, `wfq_weighted_scheduler`, `gearbox_16to8_unpacker`, `coalescing_irq_ctrl`
  - **FSMs, Serial Protocols & Bus Controllers (7 Families)**: `pattern_fsm`, `vending_mealy_fsm`, `uart_rx_oversampler`, `spi_cpol_cpha_master`, `i2c_addr_matcher_fsm`, `hdlc_zero_stuffer_fsm`, `axi_burst_chopper_fsm`
  - **Digital Arithmetic & DSP Datapaths (7 Families)**: `saturating_alu`, `mac_engine`, `q4_4_fixed_point_mac`, `cordic_stage_rotator`, `fir_3tap_symmetric`, `ewma_iir_filter`, `sorting_network_4elem`
  - **Memory Subsystems, BRAM, CAM, TCAM, LIFO & Bloom (6 Families)**: `bram_write_first_bypass`, `cam_4entry_lookup`, `tcam_wildcard_matcher`, `lifo_hardware_stack`, `bitmap_freelist_alloc`, `bloom_filter_2hash`
  - **Clock Domain Crossing & Multi-Clock (5 Families)**: `cdc_syncbit_chain`, `cdc_toggle_pulse_sync`, `cdc_reset_stretcher`, `cdc_async_fifo_gray_occ`, `cdc_mcp_req_ack_fsm`
  - **Hardware Verification, SVA & Coverage (7 Families)**: `verif_arbiter_checker`, `verif_axi_handshake`, `verif_fifo_conservation`, `verif_bounded_liveness`, `verif_credit_conservation`, `verif_gray_transition`, `verif_coverage_bin_tracker`
  - **Interconnect Protocols & Computer Architecture (10 Families)**: `arbiter_perm`, `round_robin_arbiter`, `apb_slave_periph`, `axi_wstrb_merger`, `noc_xy_router`, `noc_3d_xyz_router`, `branch_predictor_bht`, `gshare_branch_predictor`, `pipeline_forwarding`, `superscalar_dual_issue`
