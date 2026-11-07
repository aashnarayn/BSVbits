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
from backend.cp_generator_extra import EXTRA_CP_GENERATORS
from backend.cp_generator_bank import BANK_CP_GENERATORS
from backend.evaluator import evaluate_submission
import random


def main() -> int:
    only_filter = sys.argv[1] if len(sys.argv) > 1 else ""
    failures = []

    if only_filter != "--cp-only":
        print(f"=== Verifying {len(CURRICULUM_PROBLEMS)} Stored Curriculum Problems with bsc ===")
        for p in CURRICULUM_PROBLEMS:
            if only_filter and only_filter not in p["id"]:
                continue
            res = evaluate_submission(p, p["reference_snippet"], mode="snippet")
            status = "PASS" if (res.compiled and res.passed) else "FAIL"
            print(
                f"[{status}] #{p['number']:03d} {p['id']:32s} | "
                f"tests={res.passed_tests}/{res.total_tests} | "
                f"regs={res.metrics.reg_count} rules={res.metrics.rule_count} | "
                f"{res.execution_time_ms}ms"
            )
            if not (res.compiled and res.passed):
                failures.append((p["id"], res.compiler_output, res.sim_output))

    if not only_filter or only_filter == "--cp-only":
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
            *list(EXTRA_CP_GENERATORS.items()),
            *list(BANK_CP_GENERATORS.items()),
        ]
        print(f"\n=== Verifying All {len(cp_gens)} Dynamic CP Generator Families with bsc ===")
        for name, fn in cp_gens:
            rng = random.Random(42)
            p = fn(rng, 1042, "Medium")
            res = evaluate_submission(p, p["reference_snippet"], mode="snippet")
            status = "PASS" if (res.compiled and res.passed) else "FAIL"
            print(
                f"[{status}] CP:{name:24s} ({p['id']}) | "
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

