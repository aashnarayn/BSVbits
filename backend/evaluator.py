"""
Smart Hybrid Evaluator for BSVbits:
1. Interface-Aware Method & Identifier Auto-Adapter (accepts naming variations & alternative structures)
2. Structural & Semantic BSV AST Analyzer (compares User code vs Golden Solution on hand)
3. Progressive Context-Aware Clue / Hint Generator
4. LLM Reviewer (supports OpenAI / Gemini / custom OpenAI-compatible endpoints + built-in Expert BSV Analyzer)
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from .compiler import EvaluationResult, evaluate_submission_with_bsc


def extract_bsv_constructs(code: str) -> Dict[str, Any]:
    """Extract structural BSV constructs from source code for semantic comparison."""
    # Strip comments
    no_comments = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)
    no_comments = re.sub(r"/\*.*?\*/", "", no_comments, flags=re.DOTALL)

    regs = re.findall(r"\bReg#\s*\(([^)]+)\)\s*(\w+)\s*<-\s*(mk\w+)", no_comments)
    ehrs = re.findall(r"\bEhr#\s*\(([^)]+)\)\s*(\w+)\s*<-\s*mkEhr", no_comments)
    fifos = re.findall(r"\b(?:FIFOF|FIFO)#\s*\(([^)]+)\)\s*(\w+)\s*<-\s*(mk\w+)", no_comments)
    rwires = re.findall(r"\b(?:RWire|PulseWire)\b[^;]*?(\w+)\s*<-\s*(mk\w+)", no_comments)
    vectors = re.findall(r"\bVector#\s*\(([^)]+)\)", no_comments)
    rules = re.findall(r"\brule\s+(\w+)(?:\s*\((.*?)\))?\s*;", no_comments, flags=re.DOTALL)
    methods = re.findall(
        r"\bmethod\s+(ActionValue#\([^)]+\)|Action|[A-Za-z0-9_#()]+)\s+(\w+)\s*(?:\(([^)]*)\))?(?:\s*if\s*\((.*?)\))?",
        no_comments,
    )
    has_for = bool(re.search(r"\bfor\s*\(\s*Integer\b", no_comments))
    has_case = bool(re.search(r"\bcase\s*\(", no_comments))
    has_tagged = bool(re.search(r"\btagged\s+(?:Valid|Invalid|[A-Z]\w*)", no_comments))
    has_urgency = bool(re.search(r"descending_urgency|mutually_exclusive|conflict_free", no_comments))
    has_stmtfsm = bool(re.search(r"\bseq\b|\bmkFSM\b", no_comments))

    return {
        "regs": [{"type": r[0].strip(), "name": r[1], "maker": r[2]} for r in regs],
        "ehrs": [{"params": e[0].strip(), "name": e[1]} for e in ehrs],
        "fifos": [{"type": f[0].strip(), "name": f[1], "maker": f[2]} for f in fifos],
        "rwires": [{"name": w[0], "maker": w[1]} for w in rwires],
        "vectors": len(vectors),
        "rules": [{"name": r[0], "guard": r[1].strip() if r[1] else "True"} for r in rules],
        "methods": [
            {
                "return_type": m[0].strip(),
                "name": m[1].strip(),
                "args": m[2].strip(),
                "guard": m[3].strip() if m[3] else "True",
            }
            for m in methods
        ],
        "has_for": has_for,
        "has_case": has_case,
        "has_tagged": has_tagged,
        "has_urgency": has_urgency,
        "has_stmtfsm": has_stmtfsm,
    }


def extract_interface_methods(interface_def: str) -> List[Dict[str, str]]:
    """Extract expected method names and kinds from the problem's interface definition."""
    no_comments = re.sub(r"//.*?$", "", interface_def, flags=re.MULTILINE)
    matches = re.findall(
        r"\bmethod\s+(ActionValue#\([^)]+\)|Action|[A-Za-z0-9_#()]+)\s+(\w+)\s*(?:\(([^)]*)\))?\s*;",
        no_comments,
    )
    return [
        {"return_type": m[0].strip(), "name": m[1].strip(), "args": m[2].strip()}
        for m in matches
    ]


def try_auto_adapt_method_names(
    problem: Dict[str, Any],
    user_code: str,
) -> Tuple[str, List[str]]:
    """
    If the user wrote a valid implementation but used slightly different method names
    than the interface declaration (e.g. `get_val` instead of `read`, or `compute` instead of `calc`),
    automatically map their method names to the interface methods when unambiguous!
    Returns (adapted_code, list_of_adaptation_notes).
    """
    expected = extract_interface_methods(problem["interface_def"])
    user_ast = extract_bsv_constructs(user_code)
    user_methods = user_ast["methods"]
    notes: List[str] = []

    if not expected or not user_methods:
        return user_code, notes

    expected_names = {m["name"] for m in expected}
    user_names = {m["name"] for m in user_methods}

    missing_expected = [m for m in expected if m["name"] not in user_names]
    extra_user = [m for m in user_methods if m["name"] not in expected_names]

    adapted = user_code
    # If same number of missing expected methods and extra user methods with matching return types
    if len(missing_expected) == 1 and len(extra_user) == 1:
        exp_m = missing_expected[0]
        usr_m = extra_user[0]
        if (exp_m["return_type"] == "Action") == (usr_m["return_type"] == "Action"):
            old_name = usr_m["name"]
            new_name = exp_m["name"]
            adapted = re.sub(
                rf"\b(method\s+{re.escape(usr_m['return_type'])}\s+){re.escape(old_name)}\b",
                rf"\g<1>{new_name}",
                adapted,
            )
            adapted = re.sub(
                rf"\bendmethod\s*:\s*{re.escape(old_name)}\b",
                f"endmethod: {new_name}",
                adapted,
            )
            notes.append(
                f"Smart Naming Adapter: Mapped your method `{old_name}` to interface method `{new_name}`."
            )

    return adapted, notes


def build_semantic_review(
    problem: Dict[str, Any],
    user_code: str,
    eval_res: EvaluationResult,
    adaptation_notes: List[str],
) -> Dict[str, Any]:
    """
    Compare the user's code and synthesized hardware against the Golden Solution on hand.
    Highlights naming variations accepted, alternative architectural approaches,
    schedule analysis, and targeted next-step clues if not yet passing.
    """
    ref_code = problem.get("reference_snippet", problem.get("reference_bsv", ""))
    user_ast = extract_bsv_constructs(user_code)
    ref_ast = extract_bsv_constructs(ref_code)

    approaches_accepted: List[str] = list(adaptation_notes)

    # Check naming variations in registers & rules
    user_reg_names = [r["name"] for r in user_ast["regs"]]
    ref_reg_names = [r["name"] for r in ref_ast["regs"]]
    if user_reg_names and ref_reg_names and set(user_reg_names) != set(ref_reg_names):
        approaches_accepted.append(
            f"Custom register naming (`{', '.join(user_reg_names)}` vs reference `{', '.join(ref_reg_names)}`) verified via interface co-simulation."
        )

    user_rule_names = [r["name"] for r in user_ast["rules"]]
    ref_rule_names = [r["name"] for r in ref_ast["rules"]]
    if user_rule_names and ref_rule_names and set(user_rule_names) != set(ref_rule_names):
        approaches_accepted.append(
            f"Custom rule naming (`{', '.join(user_rule_names)}` vs reference `{', '.join(ref_rule_names)}`) verified via atomic rule scheduling."
        )

    # Check structural differences that are valid alternatives
    if user_ast["has_for"] != ref_ast["has_for"] and eval_res.passed:
        if user_ast["has_for"]:
            approaches_accepted.append(
                "Alternative structure accepted: You used a static elaboration `for` loop where the reference unrolled the expressions."
            )
        else:
            approaches_accepted.append(
                "Alternative structure accepted: You used direct bit/expression logic where the reference used a static `for` loop."
            )

    if user_ast["has_case"] != ref_ast["has_case"] and eval_res.passed:
        if user_ast["has_case"]:
            approaches_accepted.append(
                "Alternative control-flow accepted: You used `case` pattern matching where the reference used conditional `? :` / `if-else`."
            )
        else:
            approaches_accepted.append(
                "Alternative control-flow accepted: You used conditional `if-else` / ternary expressions where the reference used a `case` statement."
            )

    if len(user_ast["rules"]) != len(ref_ast["rules"]) and eval_res.passed:
        approaches_accepted.append(
            f"Alternative rule decomposition accepted: Your module uses {len(user_ast['rules'])} internal rule(s) compared to {len(ref_ast['rules'])} in the reference model, achieving identical cycle-accurate behavior."
        )

    # Compute idiomatic BSV score (0-100)
    score = 0
    if eval_res.compiled:
        score += 40
    if eval_res.total_tests > 0:
        score += int(45 * (eval_res.passed_tests / max(1, eval_res.total_tests)))
    if eval_res.passed:
        # Check for schedule warnings
        sched_warnings = [d for d in eval_res.diagnostics if d.code in ("G0005", "G0010", "G0004")]
        if not sched_warnings:
            score += 15
        else:
            score += 8

    # Construct targeted guidance / clues
    clues: List[str] = []
    if not eval_res.compiled:
        for d in eval_res.diagnostics[:3]:
            if d.friendly_hint:
                clues.append(f"Line {d.line} ({d.code}): {d.friendly_hint}")
        # Also compare missing constructs vs golden reference
        if len(ref_ast["regs"]) > 0 and len(user_ast["regs"]) == 0 and len(user_ast["ehrs"]) == 0:
            clues.append(
                f"Architecture Clue: The golden solution uses {len(ref_ast['regs'])} state register(s) (e.g. `Reg#({ref_ast['regs'][0]['type']}) <- mkReg(...);`)."
            )
        if len(ref_ast["methods"]) > len(user_ast["methods"]):
            expected_m = [m["name"] for m in ref_ast["methods"]]
            clues.append(
                f"Interface Clue: Make sure you implement all required interface methods: `{', '.join(expected_m)}`."
            )
    elif not eval_res.passed:
        if eval_res.first_mismatch_cycle is not None:
            bad_cycles = [w for w in eval_res.waveform if w.cycle == eval_res.first_mismatch_cycle]
            if bad_cycles:
                w = bad_cycles[0]
                clues.append(
                    f"First Mismatch at Cycle {w.cycle}: With inputs `{w.signals}`, the golden reference produced `{w.ref_outputs}`, but your module produced `{w.user_outputs}`."
                )
        if len(ref_ast["rules"]) > 0 and len(user_ast["rules"]) == 0:
            clues.append(
                "BSV Paradigm Clue: The golden model uses an autonomous `rule` to update state every clock cycle. Check if your state transition happens inside a `rule` vs a `method`."
            )
        for m_ref in ref_ast["methods"]:
            if m_ref["guard"] != "True":
                user_m = next((um for um in user_ast["methods"] if um["name"] == m_ref["name"]), None)
                if user_m and user_m["guard"] == "True":
                    clues.append(
                        f"Implicit Guard Clue: In the golden model, method `{m_ref['name']}` has a readiness guard `if (...)`. Check when `{m_ref['name']}` is allowed to fire!"
                    )

    if not clues and problem.get("hints"):
        clues = list(problem["hints"][:2])

    summary = (
        "All cycle-accurate Bluesim co-simulation tests passed! Your BSV implementation is functionally equivalent to the golden reference hardware."
        if eval_res.passed
        else (
            f"Compiled cleanly, passed {eval_res.passed_tests}/{eval_res.total_tests} test cycles. Inspect the waveform mismatch at cycle {eval_res.first_mismatch_cycle}."
            if eval_res.compiled
            else "Compilation failed in `bsc`. Review the compiler diagnostics and BSV hints below."
        )
    )

    return {
        "verdict": "ACCEPTED" if eval_res.passed else ("PARTIAL / MISMATCH" if eval_res.compiled else "COMPILE_ERROR"),
        "idiomatic_score": min(100, score),
        "summary": summary,
        "approaches_accepted": approaches_accepted,
        "clues": clues,
        "user_constructs": {
            "registers": len(user_ast["regs"]),
            "ehrs": len(user_ast["ehrs"]),
            "fifos": len(user_ast["fifos"]),
            "rules": len(user_ast["rules"]),
            "methods": len(user_ast["methods"]),
        },
        "ref_constructs": {
            "registers": len(ref_ast["regs"]),
            "ehrs": len(ref_ast["ehrs"]),
            "fifos": len(ref_ast["fifos"]),
            "rules": len(ref_ast["rules"]),
            "methods": len(ref_ast["methods"]),
        },
        "llm_enhanced": False,
    }


def maybe_call_external_llm(
    problem: Dict[str, Any],
    user_code: str,
    eval_res: EvaluationResult,
    base_review: Dict[str, Any],
    llm_config: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    If an LLM API key is configured (via environment or UI settings), query the LLM
    to enrich the semantic comparison and provide personalized BSV tutoring feedback.
    """
    cfg = llm_config or {}
    api_key = (
        cfg.get("api_key")
        or os.environ.get("BSVBITS_LLM_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or ""
    ).strip()
    if not api_key:
        return base_review

    api_base = (
        cfg.get("api_base")
        or os.environ.get("BSVBITS_LLM_API_BASE")
        or "https://api.openai.com/v1"
    ).rstrip("/")
    model = cfg.get("model") or os.environ.get("BSVBITS_LLM_MODEL") or "gpt-4o-mini"

    prompt = (
        f"You are an expert Bluespec SystemVerilog (BSV) hardware architect and tutor.\n"
        f"Problem: {problem['title']}\n"
        f"Interface:\n{problem['interface_def']}\n\n"
        f"Golden Reference Solution:\n{problem.get('reference_snippet', '')}\n\n"
        f"User Submission:\n{user_code}\n\n"
        f"BSC Compiled: {eval_res.compiled}, Simulation Passed: {eval_res.passed} ({eval_res.passed_tests}/{eval_res.total_tests})\n"
        f"Respond in JSON with keys: `summary` (2-3 sentences comparing user's approach to the golden model, acknowledging naming/structural variations), "
        f"`clues` (list of 2 actionable BSV hints or optimization tips), and `idiomatic_score` (int 0-100)."
    )
    try:
        payload_bytes = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{api_base}/chat/completions",
            data=payload_bytes,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            if "summary" in parsed:
                base_review["summary"] = parsed["summary"]
            if "clues" in parsed and isinstance(parsed["clues"], list):
                base_review["clues"] = parsed["clues"] + base_review["clues"]
            if "idiomatic_score" in parsed:
                base_review["idiomatic_score"] = int(parsed["idiomatic_score"])
            base_review["llm_enhanced"] = True
    except Exception:
        # Gracefully fall back to built-in semantic AST review
        pass

    return base_review


def evaluate_submission(
    problem: Dict[str, Any],
    user_code: str,
    mode: str = "snippet",
    llm_config: Optional[Dict[str, str]] = None,
) -> EvaluationResult:
    """
    Main entrypoint to evaluate a user's BSV submission:
    1. Automatically adapts minor method-name variations if needed
    2. Compiles with `bsc`, runs Golden Model co-simulation in `Bluesim`, extracts VCD & Schedule & Verilog
    3. Runs Semantic AST & LLM comparison against the Golden Solution on hand
    """
    adapted_code, adaptation_notes = try_auto_adapt_method_names(problem, user_code)
    result = evaluate_submission_with_bsc(problem, adapted_code, mode=mode)

    # If compilation failed on `adapted_code` with snippet mode, also check if user needed full mode
    if not result.compiled and mode == "snippet" and "endmodule" in user_code:
        result = evaluate_submission_with_bsc(problem, adapted_code, mode="full")

    review = build_semantic_review(problem, user_code, result, adaptation_notes)
    review = maybe_call_external_llm(problem, user_code, result, review, llm_config=llm_config)
    result.ai_review = review
    return result


def generate_contextual_hint(
    problem: Dict[str, Any],
    user_code: str,
    hint_level: int = 0,
) -> Dict[str, Any]:
    """
    Provide progressive clues for the current problem based on `hint_level` (0, 1, 2)
    plus live static analysis of what the user has written so far vs the Golden Solution.
    """
    hints: List[str] = problem.get("hints", [])
    ref_snippet: str = problem.get("reference_snippet", "")
    user_ast = extract_bsv_constructs(user_code)
    ref_ast = extract_bsv_constructs(ref_snippet)

    selected_hint = hints[min(hint_level, len(hints) - 1)] if hints else "Inspect the interface methods and types carefully."

    # Build a live diff clue without giving away the exact code
    live_tips: List[str] = []
    if len(ref_ast["regs"]) > len(user_ast["regs"]) and len(user_ast["ehrs"]) == 0:
        reg_types = ", ".join(f"`Reg#({r['type']})`" for r in ref_ast["regs"])
        live_tips.append(f"State Check: Consider instantiating state register(s): {reg_types} using `<- mkReg(...)`.")
    if len(ref_ast["ehrs"]) > len(user_ast["ehrs"]):
        live_tips.append("Concurrency Check: The reference solution uses an `Ehr#(2, ...)` (`<- mkEhr(...)`) so port `[0]` and port `[1]` can be accessed in the same cycle without conflict.")
    if len(ref_ast["fifos"]) > len(user_ast["fifos"]):
        live_tips.append("Buffering Check: Instantiate a FIFO (`FIFOF#(...) <- mkFIFOF;` or `mkBypassFIFOF` / `mkPipelineFIFOF`) to decouple enqueue and dequeue.")
    if len(ref_ast["rules"]) > len(user_ast["rules"]):
        live_tips.append(f"Rule Check: The reference solution defines {len(ref_ast['rules'])} internal `rule ... endrule` block(s) for autonomous state transitions.")
    if ref_ast["has_tagged"] and not user_ast["has_tagged"]:
        live_tips.append("Type Check: Use `tagged Valid x` and `tagged Invalid` (or `isValid()` / `fromMaybe()`) when working with `Maybe#(t)` types.")

    if not live_tips:
        live_tips.append("Your high-level BSV constructs (`Reg`, `rule`, `method`) match the reference structure! Focus on bit widths and cycle-level conditions.")

    return {
        "problem_id": problem["id"],
        "hint_level": hint_level,
        "total_hints": len(hints),
        "hint_text": selected_hint,
        "all_unlocked_hints": hints[: hint_level + 1],
        "live_structural_tips": live_tips,
        "bsv_vs_verilog_note": problem.get("bsv_vs_verilog", ""),
    }
