"""
Helper builders for fine-grained BSVbits Curriculum Problems, Reinforcement Drills,
Spiral Revision Labs, and Cross-Topic Combination Labs.
Every problem built by these helpers produces a complete `_make_problem(...)` dictionary
with a real BSV `interface_def`, `snippet_template`, `reference_snippet`, `reference_bsv`,
and cycle-accurate Bluesim co-simulation `testbench_bsv`.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Tuple


def make_comb1_problem(
    make_fn: Callable[..., Dict[str, Any]],
    pid: str,
    title: str,
    track_id: str,
    difficulty: str,
    tags: List[str],
    in_type: str,
    in_name: str,
    out_type: str,
    method_name: str,
    module_name: str,
    ifc_name: str,
    ref_body: str,
    stimuli: List[str],
    description: str,
    bsv_vs_verilog: str,
    diagram: str,
    hints: List[str],
    extra_typedefs: str = "",
    starter_body: str = "",
) -> Dict[str, Any]:
    """Build a 1-input combinational/type/datapath BSV curriculum problem."""
    ifc_def = ""
    if extra_typedefs.strip():
        ifc_def += extra_typedefs.strip() + "\n\n"
    ifc_def += (
        f"interface {ifc_name};\n"
        f"    method {out_type} {method_name}({in_type} {in_name});\n"
        f"endinterface"
    )

    if not starter_body:
        starter_body = "        return ?;"

    snippet_template = (
        f"    // Implement {method_name}({in_type} {in_name}) -> {out_type}\n"
        f"    // === YOUR CODE HERE ===\n"
        f"    method {out_type} {method_name}({in_type} {in_name});\n"
        f"{starter_body}\n"
        f"    endmethod"
    )

    reference_snippet = (
        f"    method {out_type} {method_name}({in_type} {in_name});\n"
        f"{ref_body}\n"
        f"    endmethod"
    )

    n = len(stimuli)
    arr_items = ", ".join(stimuli)
    tb_body = (
        f"    rule test;\n"
        f"        {in_type} vec[{n}] = {{{arr_items}}};\n"
        f"        {in_type} x = vec[cycle];\n"
        f"        {out_type} r = ref_dut.{method_name}(x);\n"
        f"        {out_type} u = user_dut.{method_name}(x);\n"
        f"        Bool ok = (pack(r) == pack(u));\n"
        f"        $display(\"@WAVE cycle=%0d|in={in_name}:0x%0h|ref=out:0x%0h|user=out:0x%0h|match=%0d|note={pid}\", cycle, pack(x), pack(r), pack(u), ok ? 1 : 0);\n"
        f"        let np = passed_cnt + (ok ? 1 : 0);\n"
        f"        passed_cnt <= np;\n"
        f"        if (cycle == {n - 1}) begin\n"
        f"            $display(\"@SUMMARY total={n} passed=%0d\", np);\n"
        f"            $finish(0);\n"
        f"        end\n"
        f"        cycle <= cycle + 1;\n"
        f"    endrule"
    )

    return make_fn(
        pid=pid,
        number=0,
        title=title,
        track_id=track_id,
        track_title="",
        difficulty=difficulty,
        tags=tags,
        description=description,
        bsv_vs_verilog=bsv_vs_verilog,
        diagram=diagram,
        interface_name=ifc_name,
        module_name=module_name,
        interface_def=ifc_def,
        snippet_template=snippet_template,
        reference_snippet=reference_snippet,
        testbench_body=tb_body,
        hints=hints,
    )


def make_comb2_problem(
    make_fn: Callable[..., Dict[str, Any]],
    pid: str,
    title: str,
    track_id: str,
    difficulty: str,
    tags: List[str],
    in1_type: str,
    in1_name: str,
    in2_type: str,
    in2_name: str,
    out_type: str,
    method_name: str,
    module_name: str,
    ifc_name: str,
    ref_body: str,
    stimuli: List[Tuple[str, str]],
    description: str,
    bsv_vs_verilog: str,
    diagram: str,
    hints: List[str],
    extra_typedefs: str = "",
    starter_body: str = "",
) -> Dict[str, Any]:
    """Build a 2-input combinational/type/datapath/protocol BSV curriculum problem."""
    ifc_def = ""
    if extra_typedefs.strip():
        ifc_def += extra_typedefs.strip() + "\n\n"
    ifc_def += (
        f"interface {ifc_name};\n"
        f"    method {out_type} {method_name}({in1_type} {in1_name}, {in2_type} {in2_name});\n"
        f"endinterface"
    )

    if not starter_body:
        starter_body = "        return ?;"

    snippet_template = (
        f"    // Implement {method_name}({in1_type} {in1_name}, {in2_type} {in2_name}) -> {out_type}\n"
        f"    // === YOUR CODE HERE ===\n"
        f"    method {out_type} {method_name}({in1_type} {in1_name}, {in2_type} {in2_name});\n"
        f"{starter_body}\n"
        f"    endmethod"
    )

    reference_snippet = (
        f"    method {out_type} {method_name}({in1_type} {in1_name}, {in2_type} {in2_name});\n"
        f"{ref_body}\n"
        f"    endmethod"
    )

    n = len(stimuli)
    arr1 = ", ".join(s[0] for s in stimuli)
    arr2 = ", ".join(s[1] for s in stimuli)
    tb_body = (
        f"    rule test;\n"
        f"        {in1_type} v1[{n}] = {{{arr1}}};\n"
        f"        {in2_type} v2[{n}] = {{{arr2}}};\n"
        f"        {in1_type} a = v1[cycle];\n"
        f"        {in2_type} b = v2[cycle];\n"
        f"        {out_type} r = ref_dut.{method_name}(a, b);\n"
        f"        {out_type} u = user_dut.{method_name}(a, b);\n"
        f"        Bool ok = (pack(r) == pack(u));\n"
        f"        $display(\"@WAVE cycle=%0d|in={in1_name}:0x%0h,{in2_name}:0x%0h|ref=out:0x%0h|user=out:0x%0h|match=%0d|note={pid}\", cycle, pack(a), pack(b), pack(r), pack(u), ok ? 1 : 0);\n"
        f"        let np = passed_cnt + (ok ? 1 : 0);\n"
        f"        passed_cnt <= np;\n"
        f"        if (cycle == {n - 1}) begin\n"
        f"            $display(\"@SUMMARY total={n} passed=%0d\", np);\n"
        f"            $finish(0);\n"
        f"        end\n"
        f"        cycle <= cycle + 1;\n"
        f"    endrule"
    )

    return make_fn(
        pid=pid,
        number=0,
        title=title,
        track_id=track_id,
        track_title="",
        difficulty=difficulty,
        tags=tags,
        description=description,
        bsv_vs_verilog=bsv_vs_verilog,
        diagram=diagram,
        interface_name=ifc_name,
        module_name=module_name,
        interface_def=ifc_def,
        snippet_template=snippet_template,
        reference_snippet=reference_snippet,
        testbench_body=tb_body,
        hints=hints,
    )


def make_seq_step_problem(
    make_fn: Callable[..., Dict[str, Any]],
    pid: str,
    title: str,
    track_id: str,
    difficulty: str,
    tags: List[str],
    in_type: str,
    in_name: str,
    out_type: str,
    step_method: str,
    read_method: str,
    module_name: str,
    ifc_name: str,
    state_decls: str,
    step_body: str,
    read_body: str,
    stimuli: List[str],
    description: str,
    bsv_vs_verilog: str,
    diagram: str,
    hints: List[str],
    extra_typedefs: str = "",
    extra_rules: str = "",
    starter_state: str = "",
) -> Dict[str, Any]:
    """Build a sequential/FSM/CDC/verification/architecture problem with step(in) Action and read() Value methods."""
    ifc_def = ""
    if extra_typedefs.strip():
        ifc_def += extra_typedefs.strip() + "\n\n"
    ifc_def += (
        f"interface {ifc_name};\n"
        f"    method Action {step_method}({in_type} {in_name});\n"
        f"    method {out_type} {read_method}();\n"
        f"endinterface"
    )

    st_init = starter_state if starter_state else state_decls
    snippet_template = (
        f"{st_init}\n\n"
        f"    // Implement {step_method}({in_type} {in_name}) and {read_method}()\n"
        f"    // === YOUR CODE HERE ===\n"
        f"    method Action {step_method}({in_type} {in_name});\n"
        f"    endmethod\n\n"
        f"    method {out_type} {read_method}();\n"
        f"        return ?;\n"
        f"    endmethod"
    )

    rules_block = (extra_rules + "\n\n") if extra_rules.strip() else ""
    reference_snippet = (
        f"{state_decls}\n\n"
        f"{rules_block}"
        f"    method Action {step_method}({in_type} {in_name});\n"
        f"{step_body}\n"
        f"    endmethod\n\n"
        f"    method {out_type} {read_method}();\n"
        f"{read_body}\n"
        f"    endmethod"
    )

    n = len(stimuli)
    arr_items = ", ".join(stimuli)
    tb_body = (
        f"    rule test;\n"
        f"        {in_type} vec[{n}] = {{{arr_items}}};\n"
        f"        {in_type} x = vec[cycle];\n"
        f"        {out_type} r = ref_dut.{read_method}();\n"
        f"        {out_type} u = user_dut.{read_method}();\n"
        f"        ref_dut.{step_method}(x);\n"
        f"        user_dut.{step_method}(x);\n"
        f"        Bool ok = (pack(r) == pack(u));\n"
        f"        $display(\"@WAVE cycle=%0d|in={in_name}:0x%0h|ref=out:0x%0h|user=out:0x%0h|match=%0d|note={pid}\", cycle, pack(x), pack(r), pack(u), ok ? 1 : 0);\n"
        f"        let np = passed_cnt + (ok ? 1 : 0);\n"
        f"        passed_cnt <= np;\n"
        f"        if (cycle == {n - 1}) begin\n"
        f"            $display(\"@SUMMARY total={n} passed=%0d\", np);\n"
        f"            $finish(0);\n"
        f"        end\n"
        f"        cycle <= cycle + 1;\n"
        f"    endrule"
    )

    return make_fn(
        pid=pid,
        number=0,
        title=title,
        track_id=track_id,
        track_title="",
        difficulty=difficulty,
        tags=tags,
        description=description,
        bsv_vs_verilog=bsv_vs_verilog,
        diagram=diagram,
        interface_name=ifc_name,
        module_name=module_name,
        interface_def=ifc_def,
        snippet_template=snippet_template,
        reference_snippet=reference_snippet,
        testbench_body=tb_body,
        hints=hints,
    )
