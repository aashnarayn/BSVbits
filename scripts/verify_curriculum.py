#!/usr/bin/env python3
"""
Verify all 32 stored BSVbits Curriculum problems and all 10 CP Generator families
using the real Bluespec SystemVerilog compiler (`bsc`) and Bluesim co-simulator.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.curriculum import CURRICULUM_PROBLEMS
from backend.cp_generator import (
    _gen_prio_encoder,
    _gen_modulo_counter,
    _gen_regslice_transform,
    _gen_pattern_fsm,
    _gen_gray_codec,
    _gen_barrel_rotator,
    _gen_saturating_alu,
    _gen_pwm_timer,
    _gen_arbiter_perm,
    _gen_mac_engine,
)
from backend.evaluator import evaluate_submission
import random


def main() -> int:
    print(f"=== Verifying {len(CURRICULUM_PROBLEMS)} Stored Curriculum Problems with bsc ===")
    failures = []
    for p in CURRICULUM_PROBLEMS:
        res = evaluate_submission(p, p["reference_snippet"], mode="snippet")
        status = "PASS" if (res.compiled and res.passed) else "FAIL"
        print(
            f"[{status}] #{p['number']:02d} {p['id']:30s} | "
            f"tests={res.passed_tests}/{res.total_tests} | "
            f"regs={res.metrics.reg_count} rules={res.metrics.rule_count} | "
            f"{res.execution_time_ms}ms"
        )
        if not (res.compiled and res.passed):
            failures.append((p["id"], res.compiler_output, res.sim_output))

    print("\n=== Verifying All 10 Dynamic CP Generator Families with bsc ===")
    cp_gens = [
        ("prio_encoder", _gen_prio_encoder),
        ("modulo_counter", _gen_modulo_counter),
        ("regslice_transform", _gen_regslice_transform),
        ("pattern_fsm", _gen_pattern_fsm),
        ("gray_codec", _gen_gray_codec),
        ("barrel_rotator", _gen_barrel_rotator),
        ("saturating_alu", _gen_saturating_alu),
        ("pwm_timer", _gen_pwm_timer),
        ("arbiter_perm", _gen_arbiter_perm),
        ("mac_engine", _gen_mac_engine),
    ]
    for name, fn in cp_gens:
        rng = random.Random(42)
        p = fn(rng, 1042, "Medium")
        res = evaluate_submission(p, p["reference_snippet"], mode="snippet")
        status = "PASS" if (res.compiled and res.passed) else "FAIL"
        print(
            f"[{status}] CP:{name:20s} ({p['id']}) | "
            f"tests={res.passed_tests}/{res.total_tests} | "
            f"{res.execution_time_ms}ms"
        )
        if not (res.compiled and res.passed):
            failures.append((f"CP:{name}", res.compiler_output, res.sim_output))

    if failures:
        print(f"\nFound {len(failures)} failure(s):")
        for pid, comp_out, sim_out in failures:
            print(f"\n--- {pid} ---")
            print("COMPILER:", comp_out)
            print("SIM:", sim_out)
        return 1

    print("\n100% OF CURRICULUM & CP GENERATOR PROBLEMS COMPILED AND PASSED BLUESIM CO-SIMULATION!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
