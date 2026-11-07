# 001. Constant Zero Output (Your First BSV Method)

- **ID**: `01_wire_zero` | **User**: `default` (SQLite DBMS Shared State)
- **Track**: 1. BSV Basics & Combinational Logic
- **Difficulty**: **Easy** | **Format**: `design_from_spec`
- **Tags**: `Syntax`, `Value Method`, `Bit#(1)`

## Hardware Diagram
```text
+------------------+
   |    mkWireZero    |
   |                  |
   |        getZero() |---> 1'b0
   +------------------+
```

## Problem Description
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

## BSV vs. Verilog Insight
> **Verilog**: `assign out = 1'b0;` inside a port list `module top(output out);`
**BSV**: Ports are grouped into strongly-typed `interface` methods. A value method `method Bit#(1) getZero()` synthesizes directly to an output wire tied to `1'b0`!

## Interface Definition
```bsv
interface WireZeroIfc;
    method Bit#(1) getZero();
endinterface
```

## Progressive Hints
1. Replace `return ?;` with `return 0;` or `return 1'b0;`.
2. In BSV, `Bit#(1)` is a 1-bit vector. Integer literals like `0` or sized literals like `1'b0` both work.
3. Full method: `method Bit#(1) getZero(); return 0; endmethod`
