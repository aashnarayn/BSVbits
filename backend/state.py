"""
Persistent State & Live VS Code Workspace Synchronization Manager for BSVbits.
Manages:
  1. Solved problems, submission history, and saved user code per problem
  2. Competitive Programming (CP) rating (ELO), streak, speedrun timer, and active generated CP problem
  3. Live VS Code synchronization via `workspace/current_problem.bsv`, `workspace/PROBLEM.md`, and `workspace/last_result.md`
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .curriculum import CURRICULUM_BY_ID, CURRICULUM_PROBLEMS
from .cp_generator import generate_cp_problem

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = REPO_ROOT / "workspace"
STATE_FILE = WORKSPACE_DIR / ".bsvbits_state.json"
VSCODE_BSV_FILE = WORKSPACE_DIR / "current_problem.bsv"
VSCODE_PROBLEM_MD = WORKSPACE_DIR / "PROBLEM.md"
VSCODE_RESULT_MD = WORKSPACE_DIR / "last_result.md"


class BSVBitsState:
    def __init__(self) -> None:
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = {
            "active_mode": "curriculum",  # "curriculum" | "cp"
            "active_problem_id": "01_wire_zero",
            "editor_mode": "snippet",  # "snippet" | "full"
            "solved_curriculum": [],
            "saved_code": {},
            "cp_rating": 1200,
            "cp_streak": 0,
            "cp_solved_count": 0,
            "cp_history": [],
            "active_cp_problem": None,
            "submissions": [],
            "last_vscode_mtime": 0.0,
            "last_eval_result": None,
        }
        self.load()
        if not self.data.get("active_cp_problem"):
            self.data["active_cp_problem"] = generate_cp_problem(difficulty="Medium", category="all", seed=2026)
            self.save()
        self.sync_to_vscode_workspace()

    def load(self) -> None:
        if STATE_FILE.exists():
            try:
                loaded = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                self.data.update(loaded)
            except Exception:
                pass

    def save(self) -> None:
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def get_active_problem(self) -> Dict[str, Any]:
        if self.data.get("active_mode") == "cp" and self.data.get("active_cp_problem"):
            return self.data["active_cp_problem"]
        pid = self.data.get("active_problem_id", "01_wire_zero")
        return CURRICULUM_BY_ID.get(pid, CURRICULUM_PROBLEMS[0])

    def get_problem_by_id(self, problem_id: str) -> Dict[str, Any]:
        if problem_id in CURRICULUM_BY_ID:
            return CURRICULUM_BY_ID[problem_id]
        cp_prob = self.data.get("active_cp_problem")
        if cp_prob and cp_prob.get("id") == problem_id:
            return cp_prob
        for item in self.data.get("cp_history", []):
            if item.get("id") == problem_id:
                return item
        return CURRICULUM_PROBLEMS[0]

    def get_user_code(self, problem: Dict[str, Any], editor_mode: Optional[str] = None) -> str:
        mode = editor_mode or self.data.get("editor_mode", "snippet")
        pid = problem["id"]
        saved_key = f"{pid}:{mode}"
        if saved_key in self.data["saved_code"]:
            return self.data["saved_code"][saved_key]
        return problem["snippet_template"] if mode == "snippet" else problem["full_template"]

    def set_user_code(self, problem_id: str, code: str, editor_mode: str = "snippet") -> None:
        saved_key = f"{problem_id}:{editor_mode}"
        self.data["saved_code"][saved_key] = code
        self.save()

    def select_problem(self, problem_id: str, mode_type: str = "curriculum", editor_mode: Optional[str] = None) -> Dict[str, Any]:
        self.data["active_mode"] = mode_type
        if mode_type == "curriculum" and problem_id in CURRICULUM_BY_ID:
            self.data["active_problem_id"] = problem_id
        if editor_mode:
            self.data["editor_mode"] = editor_mode
        self.save()
        self.sync_to_vscode_workspace()
        return self.get_active_problem()

    def generate_new_cp(self, difficulty: str = "Medium", category: str = "all", seed: Optional[int] = None) -> Dict[str, Any]:
        prob = generate_cp_problem(difficulty=difficulty, category=category, seed=seed)
        self.data["active_mode"] = "cp"
        self.data["active_cp_problem"] = prob
        self.data["active_problem_id"] = prob["id"]
        # Keep recent CP problems in history
        hist = [p for p in self.data.get("cp_history", []) if p.get("id") != prob["id"]]
        hist.insert(0, prob)
        self.data["cp_history"] = hist[:20]
        self.save()
        self.sync_to_vscode_workspace()
        return prob

    def record_evaluation(self, problem: Dict[str, Any], user_code: str, editor_mode: str, eval_dict: Dict[str, Any]) -> None:
        pid = problem["id"]
        self.set_user_code(pid, user_code, editor_mode)
        passed = bool(eval_dict.get("passed"))

        if problem.get("mode_type") == "cp":
            if passed:
                already_solved = any(
                    s.get("problem_id") == pid and s.get("passed")
                    for s in self.data.get("submissions", [])
                )
                if not already_solved:
                    delta = 25 if problem.get("difficulty") == "Easy" else (45 if problem.get("difficulty") == "Medium" else 75)
                    self.data["cp_rating"] = int(self.data.get("cp_rating", 1200)) + delta
                    self.data["cp_streak"] = int(self.data.get("cp_streak", 0)) + 1
                    self.data["cp_solved_count"] = int(self.data.get("cp_solved_count", 0)) + 1
            else:
                self.data["cp_streak"] = 0
        else:
            if passed and pid not in self.data["solved_curriculum"]:
                self.data["solved_curriculum"].append(pid)

        sub_entry = {
            "timestamp": int(time.time()),
            "problem_id": pid,
            "title": problem["title"],
            "mode_type": problem.get("mode_type", "curriculum"),
            "compiled": eval_dict.get("compiled", False),
            "passed": passed,
            "passed_tests": eval_dict.get("passed_tests", 0),
            "total_tests": eval_dict.get("total_tests", 0),
            "idiomatic_score": eval_dict.get("ai_review", {}).get("idiomatic_score", 0),
            "execution_time_ms": eval_dict.get("execution_time_ms", 0),
        }
        self.data["submissions"].insert(0, sub_entry)
        self.data["submissions"] = self.data["submissions"][:50]
        self.data["last_eval_result"] = {
            "problem_id": pid,
            "timestamp": int(time.time()),
            "result": eval_dict,
        }
        self.save()
        self.write_vscode_result_md(problem, eval_dict)

    def sync_to_vscode_workspace(self) -> None:
        """
        Stage the currently active problem into `workspace/current_problem.bsv` and `workspace/PROBLEM.md`
        so the user can edit directly inside VS Code and submit via VS Code tasks or auto-save!
        """
        prob = self.get_active_problem()
        editor_mode = self.data.get("editor_mode", "snippet")
        code = self.get_user_code(prob, editor_mode)

        header = (
            f"// ============================================================================\n"
            f"// BSVbits Active Problem: {prob['title']} ({prob['id']})\n"
            f"// Mode: {prob.get('mode_type', 'curriculum').upper()} | Difficulty: {prob.get('difficulty', 'Easy')} | Editor Mode: {editor_mode.upper()}\n"
            f"// ----------------------------------------------------------------------------\n"
            f"// Interface Contract (Automatically imported via ProblemTypes):\n"
        )
        for line in prob["interface_def"].splitlines():
            header += f"//   {line}\n"
        header += (
            f"// ----------------------------------------------------------------------------\n"
            f"// Save this file in VS Code or run `./bsvbits submit` (Ctrl+Shift+B in VS Code)\n"
            f"// to compile with `bsc`, co-simulate against the Golden Model, and view waveforms!\n"
            f"// ============================================================================\n\n"
        )

        full_file_text = header + code.strip("\n") + "\n"
        VSCODE_BSV_FILE.write_text(full_file_text, encoding="utf-8")
        self.data["last_vscode_mtime"] = VSCODE_BSV_FILE.stat().st_mtime

        md_text = (
            f"# {prob['title']}\n\n"
            f"- **ID**: `{prob['id']}`\n"
            f"- **Track**: {prob.get('track_title', 'Competitive Arena')}\n"
            f"- **Difficulty**: **{prob.get('difficulty', 'Medium')}**\n"
            f"- **Tags**: {', '.join(f'`{t}`' for t in prob.get('tags', []))}\n\n"
            f"## Hardware Diagram\n```text\n{prob.get('diagram', '')}\n```\n\n"
            f"## Problem Description\n{prob.get('description', '')}\n\n"
            f"## BSV vs. Verilog Insight\n> {prob.get('bsv_vs_verilog', '')}\n\n"
            f"## Interface Definition\n```bsv\n{prob.get('interface_def', '')}\n```\n\n"
            f"## Progressive Hints\n"
            + "\n".join(f"{i+1}. {h}" for i, h in enumerate(prob.get("hints", [])))
            + "\n"
        )
        VSCODE_PROBLEM_MD.write_text(md_text, encoding="utf-8")

    def read_from_vscode_workspace(self) -> Optional[str]:
        """Extract user code from `workspace/current_problem.bsv` (stripping the BSVbits banner header)."""
        if not VSCODE_BSV_FILE.exists():
            return None
        raw = VSCODE_BSV_FILE.read_text(encoding="utf-8")
        lines = raw.splitlines()
        idx = 0
        while idx < len(lines) and lines[idx].startswith("//"):
            idx += 1
        while idx < len(lines) and not lines[idx].strip():
            idx += 1
        return "\n".join(lines[idx:])

    def write_vscode_result_md(self, problem: Dict[str, Any], eval_dict: Dict[str, Any]) -> None:
        """Write a rich Markdown report to `workspace/last_result.md` after every submission."""
        verdict = "ACCEPTED (PASSED ALL TESTS)" if eval_dict.get("passed") else (
            "SIMULATION MISMATCH" if eval_dict.get("compiled") else "BSC COMPILATION ERROR"
        )
        ai = eval_dict.get("ai_review", {})
        lines = [
            f"# BSVbits Evaluation Report — {problem['title']}",
            f"**Verdict**: **{verdict}**  ",
            f"**Tests Passed**: `{eval_dict.get('passed_tests', 0)} / {eval_dict.get('total_tests', 0)}` | "
            f"**Idiomatic BSV Score**: `{ai.get('idiomatic_score', 0)}/100` | "
            f"**BSC Time**: `{eval_dict.get('execution_time_ms', 0)} ms`",
            "",
            "## Smart Evaluator & AI Review",
            f"{ai.get('summary', '')}",
            "",
        ]
        if ai.get("approaches_accepted"):
            lines.append("### Accepted Variations & Approaches")
            for a in ai["approaches_accepted"]:
                lines.append(f"- {a}")
            lines.append("")
        if ai.get("clues"):
            lines.append("### Actionable Clues & Guidance")
            for c in ai["clues"]:
                lines.append(f"- {c}")
            lines.append("")
        if eval_dict.get("diagnostics"):
            lines.append("## BSC Compiler Diagnostics")
            for d in eval_dict["diagnostics"]:
                lines.append(f"- **[{d['severity'].upper()} {d['code']}] Line {d['line']}**: {d['message']}")
                if d.get("friendly_hint"):
                    lines.append(f"  - *BSV Tip*: {d['friendly_hint']}")
            lines.append("")
        if eval_dict.get("waveform"):
            lines.append("## Cycle-by-Cycle Co-Simulation Waveform Table")
            lines.append("| Cycle | Inputs | Golden Ref Output | Your Output | Status |")
            lines.append("|---|---|---|---|---|")
            for w in eval_dict["waveform"]:
                in_str = ", ".join(f"{k}={v}" for k, v in w["signals"].items())
                ref_str = ", ".join(f"{k}={v}" for k, v in w["ref_outputs"].items())
                usr_str = ", ".join(f"{k}={v}" for k, v in w["user_outputs"].items())
                st = "OK" if w["match"] else "**MISMATCH**"
                lines.append(f"| `{w['cycle']}` | `{in_str}` | `{ref_str}` | `{usr_str}` | {st} |")
            lines.append("")

        VSCODE_RESULT_MD.write_text("\n".join(lines), encoding="utf-8")
