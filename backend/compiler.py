"""
Bluespec SystemVerilog (bsc) Compiler, Bluesim Co-Simulator, Schedule Analyzer & VCD Parser.
Supports HDLBits-style part-by-part snippet injection as well as full-module compilation.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
BSV_LIB_DIR = REPO_ROOT / "bsv_lib"


BSC_ERROR_EXPLANATIONS: Dict[str, str] = {
    "S0015": (
        "Syntax Error: Check for missing semicolons `;`, unmatched `begin`/`end`, `module`/`endmodule`, "
        "`rule`/`endrule`, `method`/`endmethod`, or using Verilog keywords not valid in BSV."
    ),
    "T0004": (
        "Unbound Identifier: A variable, method, rule, or type name is used before being declared. "
        "Remember that in BSV, type names and enum tags MUST start with an UPPERCASE letter, while variables, "
        "functions, modules, and methods MUST start with a lowercase letter."
    ),
    "T0007": (
        "Unbound Type Constructor: Check that your type name starts with a capital letter (e.g. `Bit#(8)`, `Bool`, `Int#(16)`, `UInt#(8)`) "
        "and that any required package (`import Vector::*;`, `import FIFOF::*;`) is imported."
    ),
    "T0020": (
        "Type Mismatch: The expression type does not match what BSV expects. Common causes:\n"
        "• Using `=` instead of `<=` to write a `Reg`, or using `<=` on a local variable (`Bit#(n) x = ...`).\n"
        "• Forgetting `return` in a value `method` or `function`.\n"
        "• Mixing `Bit#(n)`, `UInt#(n)`, and `Int#(n)` without `pack()` / `unpack()`.\n"
        "• Calling an `ActionValue` method with `=` instead of `<-`."
    ),
    "T0031": (
        "Missing Typeclass Proviso (`Bits` or `Eq`): When defining a `typedef struct` or `typedef enum` that will be stored "
        "in a `Reg`, `FIFO`, or compared with `==`, add `deriving (Bits, Eq);` at the end of the `typedef`."
    ),
    "T0032": (
        "Proviso Not Satisfied: A generic type or numeric width requires a typeclass instance (like `Bits#(t, sz)` or `Arith#(t)`)."
    ),
    "T0080": (
        "Type Width Mismatch: Two `Bit#(n)` expressions have different bit widths. Use `zeroExtend()`, `signExtend()`, "
        "`truncate()`, or explicit bit slicing `x[hi:lo]`."
    ),
    "T0127": (
        "Invalid Left-Hand Side of `<=`: The `<=` operator in BSV is syntactic sugar for calling the `_write` Action method "
        "of a `Reg` interface. For combinational variables or wires inside a rule/method, use `=`."
    ),
    "G0002": (
        "Multiple Writes / Double Action Error: A single rule or method is attempting to write to the same register or call "
        "the same single-ported Action method twice in the same clock cycle."
    ),
    "G0004": (
        "Rule Never Fires: A rule's guard (explicit or implicit) is permanently false (`0`), so it can never fire."
    ),
    "G0005": (
        "Rule Conflict / Urgency Warning: Two rules can be enabled in the same clock cycle and access shared state in a conflicting way. "
        "BSV automatically picks one to be more urgent, or you can resolve it using `(* descending_urgency = \"r1, r2\" *)`, "
        "`(* mutually_exclusive = \"r1, r2\" *)`, or an `Ehr`."
    ),
    "G0010": (
        "Action Shadowing Warning: One rule blocks another rule whenever both guards are true. Check if their guards should be mutually exclusive."
    ),
    "G0021": (
        "Uninitialized Interface Method: Your module didn't define one or more methods required by its interface. "
        "Make sure every `method` declared in the `interface` is implemented inside your `module`."
    ),
    "G0117": (
        "Rule Cannot Fire Between Methods: A rule and an interface method have a scheduling cycle across a synthesis boundary."
    ),
}


def find_bsc() -> Tuple[str, str]:
    """Locate the bsc binary and BLUESPECDIR library directory."""
    candidates = [
        Path("/home/antigravity/.local/bsc"),
        REPO_ROOT / "tools" / "bsc",
        Path.home() / ".local" / "bsc",
        Path("/opt/bsc"),
        Path("/usr/local/bsc"),
    ]
    for base in candidates:
        bsc_bin = base / "bin" / "bsc"
        lib_dir = base / "lib"
        if bsc_bin.is_file() and os.access(bsc_bin, os.X_OK):
            return str(bsc_bin), str(lib_dir)

    which_bsc = shutil.which("bsc")
    if which_bsc:
        bsc_path = Path(which_bsc).resolve()
        lib_dir = bsc_path.parent.parent / "lib"
        return str(bsc_path), str(lib_dir)

    raise RuntimeError(
        "Bluespec compiler (bsc) not found. Run `./scripts/setup_bsc.sh` to install it automatically."
    )


def get_bsc_env() -> Dict[str, str]:
    """Return environment dictionary with PATH and BLUESPECDIR configured for bsc."""
    bsc_bin, lib_dir = find_bsc()
    bin_dir = str(Path(bsc_bin).parent)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    env["BLUESPECDIR"] = lib_dir
    return env


def ensure_bsv_lib_compiled() -> None:
    """Ensure bsv_lib/Ehr.bsv is compiled so `-p +:bsv_lib` works immediately."""
    bo_file = BSV_LIB_DIR / "Ehr.bo"
    bsv_file = BSV_LIB_DIR / "Ehr.bsv"
    if bsv_file.exists() and (not bo_file.exists() or bsv_file.stat().st_mtime > bo_file.stat().st_mtime):
        bsc_bin, _ = find_bsc()
        env = get_bsc_env()
        subprocess.run(
            [bsc_bin, "-sim", "-bdir", str(BSV_LIB_DIR), "-u", str(bsv_file)],
            env=env,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )


@dataclass
class CompilerDiagnostic:
    severity: str  # "error" | "warning"
    code: str
    file: str
    line: int
    column: int
    message: str
    friendly_hint: str = ""


@dataclass
class WaveCycle:
    cycle: int
    signals: Dict[str, str]
    ref_outputs: Dict[str, str]
    user_outputs: Dict[str, str]
    match: bool
    note: str = ""


@dataclass
class ScheduleInfo:
    rules: List[Dict[str, str]] = field(default_factory=list)
    methods: List[Dict[str, str]] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    conflict_matrix: str = ""
    raw_schedule: str = ""


@dataclass
class HardwareMetrics:
    reg_count: int = 0
    wire_count: int = 0
    rule_count: int = 0
    method_count: int = 0
    can_fire_signals: List[str] = field(default_factory=list)
    verilog_lines: int = 0


@dataclass
class EvaluationResult:
    compiled: bool
    passed: bool
    total_tests: int
    passed_tests: int
    first_mismatch_cycle: Optional[int]
    diagnostics: List[CompilerDiagnostic]
    compiler_output: str
    sim_output: str
    waveform: List[WaveCycle]
    vcd_content: str
    schedule: ScheduleInfo
    verilog_code: str
    metrics: HardwareMetrics
    wrapped_user_bsv: str
    execution_time_ms: int
    ai_review: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_user_solution_bsv(
    problem: Dict[str, Any],
    user_code: str,
    mode: str = "snippet",
) -> Tuple[str, int]:
    """
    Construct a complete `package UserSolution; ... endpackage` BSV file from either:
      - a part-by-part code snippet (`mode == "snippet"`), OR
      - a full module / package submission (`mode == "full"`).
     Also normalizes common user variations (e.g. if the user included `module ... endmodule`
    inside snippet mode or used a different module name) so valid solutions are never rejected
    for trivial wrapper differences.

    Returns (full_bsv_source, line_offset_before_user_code).
    """
    imports = problem.get("package_imports", "import Vector::*; import FIFOF::*; import Ehr::*;")
    interface_name = problem["interface_name"]
    module_name = problem["module_name"]
    harness_wrapper = problem.get("harness_wrapper", "")

    cleaned = user_code.strip("\r\n")

    # Detect if user provided `package ... endpackage`
    if re.search(r"^\s*package\s+\w+\s*;", cleaned, re.MULTILINE):
        # Replace package name with UserSolution
        normalized = re.sub(
            r"^\s*package\s+\w+\s*;",
            "package UserSolution;\nimport ProblemTypes::*;",
            cleaned,
            count=1,
            flags=re.MULTILINE,
        )
        normalized = re.sub(r"endpackage\s*(:\s*\w+)?", "endpackage: UserSolution", normalized)
        # Ensure module name matches expected `module_name` if there is a single module
        normalized = _normalize_module_name(normalized, module_name)
        return normalized, 0

    # Detect if user wrote `module ... endmodule` (either in full mode or accidentally in snippet mode)
    has_module_decl = bool(re.search(r"\bmodule\s+\w+", cleaned))
    if mode == "full" or has_module_decl:
        if has_module_decl:
            normalized_mod = _normalize_module_name(cleaned, module_name)
            header_lines = [
                "package UserSolution;",
                "import ProblemTypes::*;",
                imports,
                "",
            ]
            line_offset = len(header_lines)
            full_src = "\n".join(header_lines) + "\n" + normalized_mod + "\n\nendpackage: UserSolution\n"
            return full_src, line_offset

    # Snippet mode: inject into `harness_wrapper` if provided, or inside `module <module_name>(<interface_name>);`
    if harness_wrapper and "{{USER_SNIPPET}}" in harness_wrapper:
        prefix = harness_wrapper.split("{{USER_SNIPPET}}")[0]
        line_offset = prefix.count("\n")
        full_src = harness_wrapper.replace("{{USER_SNIPPET}}", cleaned)
        return full_src, line_offset

    header_lines = [
        "package UserSolution;",
        "import ProblemTypes::*;",
        imports,
        "",
        f"module {module_name}({interface_name});",
    ]
    line_offset = len(header_lines)
    footer_lines = [
        "endmodule",
        "",
        "endpackage: UserSolution",
    ]
    full_src = "\n".join(header_lines) + "\n" + cleaned + "\n" + "\n".join(footer_lines) + "\n"
    return full_src, line_offset


def _normalize_module_name(bsv_code: str, expected_module_name: str) -> str:
    """
    If the user named their main module something slightly different (e.g. `mkMyCounter` instead of `mkCounterUp`),
    normalize the last (or only) module definition to `expected_module_name` so the testbench can instantiate it.
    """
    matches = list(re.finditer(r"\bmodule\s+(\w+)\b", bsv_code))
    if not matches:
        return bsv_code
    names = [m.group(1) for m in matches]
    if expected_module_name in names:
        return bsv_code
    # Replace the last module's name with expected_module_name
    last_match = matches[-1]
    old_name = last_match.group(1)
    start, end = last_match.span(1)
    updated = bsv_code[:start] + expected_module_name + bsv_code[end:]
    updated = re.sub(rf"\bendmodule\s*:\s*{re.escape(old_name)}\b", f"endmodule: {expected_module_name}", updated)
    return updated


def parse_bsc_diagnostics(raw_output: str, line_offset: int = 0) -> List[CompilerDiagnostic]:
    """Parse bsc stderr/stdout for Error and Warning blocks and attach beginner-friendly hints."""
    diagnostics: List[CompilerDiagnostic] = []
    pattern = re.compile(
        r'(Error|Warning):\s*"([^"]+)",\s*line\s*(\d+),\s*column\s*(\d+):\s*\(([A-Z]\d+)\)\s*\n((?:  .*\n?)+)',
        re.MULTILINE,
    )
    for match in pattern.finditer(raw_output):
        sev_raw, filepath, line_str, col_str, code, msg_block = match.groups()
        severity = "error" if sev_raw == "Error" else "warning"
        filename = Path(filepath).name
        raw_line = int(line_str)
        adj_line = max(1, raw_line - line_offset) if filename == "UserSolution.bsv" else raw_line
        col = int(col_str)
        msg = " ".join(l.strip() for l in msg_block.strip().splitlines())
        friendly = BSC_ERROR_EXPLANATIONS.get(code, "")
        if not friendly:
            if code.startswith("T"):
                friendly = "Typechecking error: Verify bit-widths, `Reg` `<=` vs `=` assignments, and `Method` return types."
            elif code.startswith("G"):
                friendly = "Hardware elaboration / rule scheduling message from BSC."
            elif code.startswith("S"):
                friendly = "BSV syntax issue: Check semicolons, `begin`/`end` blocks, and method/rule declarations."

        diagnostics.append(
            CompilerDiagnostic(
                severity=severity,
                code=code,
                file=filename,
                line=adj_line,
                column=col,
                message=msg,
                friendly_hint=friendly,
            )
        )
    return diagnostics


def parse_schedule_file(sched_text: str) -> ScheduleInfo:
    """Parse a BSC `.sched` dump into structured rules, methods, conflict matrix, and execution order."""
    info = ScheduleInfo(raw_schedule=sched_text)
    if not sched_text.strip():
        return info

    # Extract conflict matrix if present
    if "Method conflict matrix:" in sched_text:
        parts = sched_text.split("Method conflict matrix:", 1)[1]
        end_idx = parts.find("Rule schedule")
        if end_idx != -1:
            info.conflict_matrix = parts[:end_idx].strip()
        else:
            info.conflict_matrix = parts.strip()

    # Extract rules & methods
    rule_blocks = re.split(r"\n(?=(?:Rule|Method):\s+)", sched_text)
    for block in rule_blocks:
        m_rule = re.match(r"Rule:\s+(\S+)\s*\nPredicate:\s*(.*?)\nBlocking rules:\s*(.*?)(?:\n|$)", block, re.DOTALL)
        if m_rule:
            info.rules.append({
                "name": m_rule.group(1).strip(),
                "predicate": " ".join(m_rule.group(2).split()),
                "blocking_rules": m_rule.group(3).strip(),
            })
            continue
        m_meth = re.match(r"Method:\s+(\S+)\s*\nReady signal:\s*(.*?)\n(.*?)(?:\n\n|\Z)", block, re.DOTALL)
        if m_meth:
            info.methods.append({
                "name": m_meth.group(1).strip(),
                "ready": " ".join(m_meth.group(2).split()),
                "details": " ".join(m_meth.group(3).split()),
            })

    m_order = re.search(r"Logical execution order:\s*(.+)", sched_text)
    if m_order:
        info.execution_order = [x.strip() for x in m_order.group(1).split(",") if x.strip()]

    return info


def extract_hardware_metrics(verilog_code: str, sched_info: ScheduleInfo) -> HardwareMetrics:
    """Analyze generated BSC Verilog and Schedule to extract hardware complexity metrics."""
    metrics = HardwareMetrics()
    metrics.rule_count = len(sched_info.rules)
    metrics.method_count = len(sched_info.methods)
    if not verilog_code.strip():
        return metrics

    lines = verilog_code.splitlines()
    metrics.verilog_lines = len(lines)
    # Count registers (`reg [...]`) excluding CLK/RST
    reg_matches = re.findall(r"^\s*reg\s+(?:\[\d+:\d+\]\s+)?(\w+)\s*;", verilog_code, re.MULTILINE)
    metrics.reg_count = len([r for r in reg_matches if not r.startswith("TASK_")])
    wire_matches = re.findall(r"^\s*wire\s+(?:\[\d+:\d+\]\s+)?(\w+)\s*;", verilog_code, re.MULTILINE)
    metrics.wire_count = len(wire_matches)
    can_fires = re.findall(r"\b(CAN_FIRE_\w+)\b", verilog_code)
    metrics.can_fire_signals = sorted(set(can_fires))
    return metrics


def parse_sim_waveforms(sim_stdout: str) -> Tuple[List[WaveCycle], int, int, Optional[int]]:
    """
    Parse structured `@WAVE` lines emitted by BSVbits testbenches:
    Format:
      @WAVE cycle=0|in=a:5,b:3|ref=out:8|user=out:8|match=1|note=Add test
    Also supports `@SUMMARY total=16 passed=16`.
    """
    waveform: List[WaveCycle] = []
    total_tests = 0
    passed_tests = 0
    first_mismatch: Optional[int] = None

    for raw_line in sim_stdout.splitlines():
        line = raw_line.strip()
        if line.startswith("@WAVE "):
            payload = line[len("@WAVE "):]
            fields: Dict[str, str] = {}
            for part in payload.split("|"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    fields[k.strip()] = v.strip()

            cycle = int(fields.get("cycle", len(waveform)))
            sig_map = _parse_kv_pairs(fields.get("in", ""))
            ref_map = _parse_kv_pairs(fields.get("ref", ""))
            user_map = _parse_kv_pairs(fields.get("user", ""))
            match_flag = fields.get("match", "1") == "1"
            note = fields.get("note", "")

            total_tests += 1
            if match_flag:
                passed_tests += 1
            elif first_mismatch is None:
                first_mismatch = cycle

            waveform.append(
                WaveCycle(
                    cycle=cycle,
                    signals=sig_map,
                    ref_outputs=ref_map,
                    user_outputs=user_map,
                    match=match_flag,
                    note=note,
                )
            )
        elif line.startswith("@SUMMARY "):
            m_tot = re.search(r"total=(\d+)", line)
            m_pass = re.search(r"passed=(\d+)", line)
            if m_tot and m_pass:
                total_tests = max(total_tests, int(m_tot.group(1)))
                passed_tests = int(m_pass.group(1))

    return waveform, total_tests, passed_tests, first_mismatch


def _parse_kv_pairs(s: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not s:
        return out
    for item in s.split(","):
        if ":" in item:
            k, v = item.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def evaluate_submission_with_bsc(
    problem: Dict[str, Any],
    user_code: str,
    mode: str = "snippet",
) -> EvaluationResult:
    """
    Full HDLBits-style BSV compilation, Golden Reference co-simulation, VCD generation,
    schedule extraction, and Verilog RTL synthesis.
    """
    t0 = time.time()
    ensure_bsv_lib_compiled()
    bsc_bin, _ = find_bsc()
    env = get_bsc_env()

    wrapped_user_bsv, line_offset = build_user_solution_bsv(problem, user_code, mode=mode)

    with tempfile.TemporaryDirectory(prefix="bsvbits_eval_") as tmpdir:
        tmp = Path(tmpdir)
        # 1. Write ProblemTypes.bsv (shared interfaces & typedefs)
        problem_types_bsv = (
            "package ProblemTypes;\n"
            + problem.get("package_imports", "import Vector::*; import FIFOF::*; import Ehr::*;")
            + "\n\n"
            + problem["interface_def"]
            + "\n\nendpackage: ProblemTypes\n"
        )
        (tmp / "ProblemTypes.bsv").write_text(problem_types_bsv, encoding="utf-8")

        # 2. Write RefSolution.bsv (Golden Reference Solution)
        (tmp / "RefSolution.bsv").write_text(problem["reference_bsv"], encoding="utf-8")

        # 3. Write UserSolution.bsv (User's Solution)
        (tmp / "UserSolution.bsv").write_text(wrapped_user_bsv, encoding="utf-8")

        # 4. Write Testbench.bsv (Co-Simulation Harness comparing RefSolution vs UserSolution)
        (tmp / "Testbench.bsv").write_text(problem["testbench_bsv"], encoding="utf-8")

        bsv_path_flag = f"+:{BSV_LIB_DIR}:{tmp}"

        # Compile UserSolution first with `-show-schedule` so we get clean diagnostics & schedule for user module
        user_compile_cmd = [
            bsc_bin,
            "-sim",
            "-show-schedule",
            "-p",
            bPath := bsv_path_flag,
            "-bdir",
            str(tmp),
            "-simdir",
            str(tmp),
            "-info-dir",
            str(tmp),
            "-u",
            str(tmp / "UserSolution.bsv"),
        ]
        proc_user = subprocess.run(
            user_compile_cmd,
            env=env,
            cwd=str(tmp),
            capture_output=True,
            text=True,
            timeout=25,
        )
        compiler_log = (proc_user.stdout or "") + "\n" + (proc_user.stderr or "")
        diagnostics = parse_bsc_diagnostics(compiler_log, line_offset=line_offset)

        if proc_user.returncode != 0:
            elapsed = int((time.time() - t0) * 1000)
            return EvaluationResult(
                compiled=False,
                passed=False,
                total_tests=0,
                passed_tests=0,
                first_mismatch_cycle=None,
                diagnostics=diagnostics,
                compiler_output=compiler_log.strip(),
                sim_output="",
                waveform=[],
                vcd_content="",
                schedule=ScheduleInfo(),
                verilog_code="",
                metrics=HardwareMetrics(),
                wrapped_user_bsv=wrapped_user_bsv,
                execution_time_ms=elapsed,
            )

        # Compile Testbench (which pulls in RefSolution & UserSolution)
        tb_compile_cmd = [
            bsc_bin,
            "-sim",
            "-show-schedule",
            "-suppress-warnings",
            "T0157:S0073",
            "-p",
            bPath,
            "-bdir",
            str(tmp),
            "-simdir",
            str(tmp),
            "-info-dir",
            str(tmp),
            "-g",
            "mkTestbench",
            "-u",
            str(tmp / "Testbench.bsv"),
        ]
        proc_tb = subprocess.run(
            tb_compile_cmd,
            env=env,
            cwd=str(tmp),
            capture_output=True,
            text=True,
            timeout=25,
        )
        tb_log = (proc_tb.stdout or "") + "\n" + (proc_tb.stderr or "")
        compiler_log = (compiler_log + "\n" + tb_log).strip()
        diagnostics.extend(parse_bsc_diagnostics(tb_log, line_offset=line_offset))

        if proc_tb.returncode != 0:
            elapsed = int((time.time() - t0) * 1000)
            return EvaluationResult(
                compiled=False,
                passed=False,
                total_tests=0,
                passed_tests=0,
                first_mismatch_cycle=None,
                diagnostics=diagnostics,
                compiler_output=compiler_log,
                sim_output="",
                waveform=[],
                vcd_content="",
                schedule=ScheduleInfo(),
                verilog_code="",
                metrics=HardwareMetrics(),
                wrapped_user_bsv=wrapped_user_bsv,
                execution_time_ms=elapsed,
            )

        # Link simulation binary
        sim_exe = tmp / "sim_out"
        link_cmd = [
            bsc_bin,
            "-sim",
            "-bdir",
            str(tmp),
            "-simdir",
            str(tmp),
            "-e",
            "mkTestbench",
            "-o",
            str(sim_exe),
        ]
        proc_link = subprocess.run(
            link_cmd,
            env=env,
            cwd=str(tmp),
            capture_output=True,
            text=True,
            timeout=25,
        )
        if proc_link.returncode != 0:
            compiler_log += "\n" + (proc_link.stdout or "") + "\n" + (proc_link.stderr or "")
            elapsed = int((time.time() - t0) * 1000)
            return EvaluationResult(
                compiled=False,
                passed=False,
                total_tests=0,
                passed_tests=0,
                first_mismatch_cycle=None,
                diagnostics=diagnostics,
                compiler_output=compiler_log,
                sim_output="",
                waveform=[],
                vcd_content="",
                schedule=ScheduleInfo(),
                verilog_code="",
                metrics=HardwareMetrics(),
                wrapped_user_bsv=wrapped_user_bsv,
                execution_time_ms=elapsed,
            )

        # Run Bluesim with VCD waveform dump
        vcd_file = tmp / "dump.vcd"
        proc_sim = subprocess.run(
            [str(sim_exe), "-V", str(vcd_file)],
            env=env,
            cwd=str(tmp),
            capture_output=True,
            text=True,
            timeout=15,
        )
        sim_output = ((proc_sim.stdout or "") + "\n" + (proc_sim.stderr or "")).strip()
        vcd_content = vcd_file.read_text(encoding="utf-8", errors="replace") if vcd_file.exists() else ""

        waveform, total_tests, passed_tests, first_mismatch = parse_sim_waveforms(sim_output)
        passed = (total_tests > 0 and passed_tests == total_tests and first_mismatch is None)

        # Also synthesize standalone User module to Verilog & Schedule to inspect RTL & Schedule!
        synth_wrapper = (
            "package UserSynth;\n"
            "import ProblemTypes::*;\n"
            "import UserSolution::*;\n\n"
            "(* synthesize *)\n"
            f"module mkUserSynth({problem['interface_name']});\n"
            f"    let _m <- {problem['module_name']}();\n"
            "    return _m;\n"
            "endmodule\n"
            "endpackage: UserSynth\n"
        )
        (tmp / "UserSynth.bsv").write_text(synth_wrapper, encoding="utf-8")
        proc_v = subprocess.run(
            [
                bsc_bin,
                "-verilog",
                "-show-schedule",
                "-p",
                bPath,
                "-vdir",
                str(tmp),
                "-bdir",
                str(tmp),
                "-info-dir",
                str(tmp),
                "-g",
                "mkUserSynth",
                "-u",
                str(tmp / "UserSynth.bsv"),
            ],
            env=env,
            cwd=str(tmp),
            capture_output=True,
            text=True,
            timeout=20,
        )
        sched_file = tmp / "mkUserSynth.sched"
        if not sched_file.exists():
            sched_file = tmp / "mkTestbench.sched"
        sched_text = sched_file.read_text(encoding="utf-8", errors="replace") if sched_file.exists() else ""
        schedule_info = parse_schedule_file(sched_text)

        v_file = tmp / "mkUserSynth.v"
        verilog_code = v_file.read_text(encoding="utf-8", errors="replace") if v_file.exists() else ""
        metrics = extract_hardware_metrics(verilog_code, schedule_info)

        # Check if user had any schedule warnings during UserSynth compilation
        if proc_v.returncode == 0 and (proc_v.stderr or proc_v.stdout):
            synth_diags = parse_bsc_diagnostics((proc_v.stdout or "") + "\n" + (proc_v.stderr or ""), line_offset=line_offset)
            for d in synth_diags:
                if d.code not in {x.code for x in diagnostics}:
                    diagnostics.append(d)

        elapsed = int((time.time() - t0) * 1000)
        return EvaluationResult(
            compiled=True,
            passed=passed,
            total_tests=total_tests,
            passed_tests=passed_tests,
            first_mismatch_cycle=first_mismatch,
            diagnostics=diagnostics,
            compiler_output=compiler_log,
            sim_output=sim_output,
            waveform=waveform,
            vcd_content=vcd_content,
            schedule=schedule_info,
            verilog_code=verilog_code,
            metrics=metrics,
            wrapped_user_bsv=wrapped_user_bsv,
            execution_time_ms=elapsed,
        )
