"""
Persistent State & Live VS Code Workspace Synchronization Manager for BSVbits.
Backed by the bundled SQLite3 Relational DBMS (`backend/db.py` -> `workspace/bsvbits.db`)
so that user progress, ELO rating, streaks, saved code, CP sessions, and daily challenges
are shared in real time between the Website and the VS Code IDE (`./bsvbits` CLI).
"""

from __future__ import annotations

import datetime
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .curriculum import CURRICULUM_BY_ID, CURRICULUM_PROBLEMS
from .cp_generator import generate_cp_problem, generate_cp_session, generate_daily_problem
from .db import (
    DB_PATH,
    create_cp_session_db,
    ensure_user,
    get_cp_problem_db,
    get_cp_session_db,
    get_daily_problem_db,
    get_saved_code_db,
    get_solved_curriculum_ids,
    init_db,
    list_recent_cp_problems_db,
    list_submissions_db,
    list_users,
    mark_cp_problem_solved_db,
    mark_curriculum_attempt,
    record_submission_db,
    save_cp_problem_db,
    set_saved_code_db,
    update_cp_session_progress_db,
    update_user_fields,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = REPO_ROOT / "workspace"
STATE_FILE = WORKSPACE_DIR / ".bsvbits_state.json"
ACTIVE_USER_FILE = WORKSPACE_DIR / ".active_user"
VSCODE_BSV_FILE = WORKSPACE_DIR / "current_problem.bsv"
VSCODE_PROBLEM_MD = WORKSPACE_DIR / "PROBLEM.md"
VSCODE_RESULT_MD = WORKSPACE_DIR / "last_result.md"


class BSVBitsState:
    def __init__(self, username: Optional[str] = None) -> None:
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        init_db()
        if username:
            self.username = username
            ACTIVE_USER_FILE.write_text(username, encoding="utf-8")
        elif ACTIVE_USER_FILE.exists():
            self.username = ACTIVE_USER_FILE.read_text(encoding="utf-8").strip() or "default"
        else:
            self.username = "default"
            ACTIVE_USER_FILE.write_text("default", encoding="utf-8")

        self.data: Dict[str, Any] = {}
        self._migrate_legacy_json_if_needed()
        self.load()
        if not self.data.get("active_cp_problem"):
            prob = generate_cp_problem(difficulty="Medium", category="all", seed=2026)
            save_cp_problem_db(self.username, prob)
            self.data["active_cp_problem"] = prob
        self.sync_to_vscode_workspace()

    def _migrate_legacy_json_if_needed(self) -> None:
        """One-time import of legacy `.bsvbits_state.json` into SQLite if SQLite is brand new."""
        if not STATE_FILE.exists():
            return
        try:
            legacy = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if legacy.get("_migrated_to_sqlite"):
                return
            ensure_user(self.username)
            for pid in legacy.get("solved_curriculum", []):
                mark_curriculum_attempt(self.username, pid, True, 95)
            for k, code in legacy.get("saved_code", {}).items():
                if ":" in k:
                    pid, emode = k.split(":", 1)
                    set_saved_code_db(self.username, pid, emode, code)
            if legacy.get("active_cp_problem"):
                save_cp_problem_db(self.username, legacy["active_cp_problem"])
            update_user_fields(
                self.username,
                active_mode=legacy.get("active_mode", "curriculum"),
                active_problem_id=legacy.get("active_problem_id", "01_wire_zero"),
                editor_mode=legacy.get("editor_mode", "snippet"),
                cp_rating=int(legacy.get("cp_rating", 1200)),
                cp_streak=int(legacy.get("cp_streak", 0)),
                cp_solved_count=int(legacy.get("cp_solved_count", 0)),
            )
            legacy["_migrated_to_sqlite"] = True
            STATE_FILE.write_text(json.dumps(legacy, indent=2), encoding="utf-8")
        except Exception:
            pass

    def switch_user(self, username: str) -> Dict[str, Any]:
        clean = "".join(c for c in username.strip() if c.isalnum() or c in ("_", "-")) or "default"
        self.username = clean
        ACTIVE_USER_FILE.write_text(clean, encoding="utf-8")
        ensure_user(clean)
        self.load()
        self.sync_to_vscode_workspace()
        return self.data

    def load(self) -> None:
        """Refresh in-memory dictionary from the SQLite3 DBMS (`workspace/bsvbits.db`)."""
        if ACTIVE_USER_FILE.exists():
            disk_user = ACTIVE_USER_FILE.read_text(encoding="utf-8").strip()
            if disk_user:
                self.username = disk_user

        u = ensure_user(self.username)
        solved_curr = get_solved_curriculum_ids(self.username)
        cp_hist = list_recent_cp_problems_db(self.username, limit=25)
        subs = list_submissions_db(self.username, limit=30)

        active_pid = u["active_problem_id"]
        active_cp = get_cp_problem_db(active_pid)
        if not active_cp and cp_hist:
            active_cp = cp_hist[0]

        last_eval = None
        if u.get("last_eval_json"):
            try:
                last_eval = json.loads(u["last_eval_json"])
            except Exception:
                last_eval = None

        active_sess = get_cp_session_db(u.get("active_session_id", ""))

        self.data = {
            "username": self.username,
            "display_name": u.get("display_name", self.username),
            "db_engine": f"SQLite3 ({DB_PATH.name})",
            "active_mode": u.get("active_mode", "curriculum"),
            "active_problem_id": active_pid,
            "editor_mode": u.get("editor_mode", "snippet"),
            "solved_curriculum": solved_curr,
            "cp_rating": int(u.get("cp_rating", 1200)),
            "cp_streak": int(u.get("cp_streak", 0)),
            "cp_solved_count": int(u.get("cp_solved_count", 0)),
            "daily_streak": int(u.get("daily_streak", 0)),
            "last_daily_date": u.get("last_daily_date", ""),
            "cp_history": cp_hist,
            "active_cp_problem": active_cp,
            "active_session": active_sess,
            "submissions": subs,
            "last_vscode_mtime": float(u.get("last_vscode_mtime", 0.0)),
            "last_eval_result": last_eval,
            "users": list_users(),
        }

    def save(self) -> None:
        """Persist current user fields to SQLite3 DBMS."""
        update_user_fields(
            self.username,
            active_mode=self.data.get("active_mode", "curriculum"),
            active_problem_id=self.data.get("active_problem_id", "01_wire_zero"),
            editor_mode=self.data.get("editor_mode", "snippet"),
            cp_rating=int(self.data.get("cp_rating", 1200)),
            cp_streak=int(self.data.get("cp_streak", 0)),
            cp_solved_count=int(self.data.get("cp_solved_count", 0)),
            daily_streak=int(self.data.get("daily_streak", 0)),
            last_daily_date=self.data.get("last_daily_date", ""),
            last_vscode_mtime=float(self.data.get("last_vscode_mtime", 0.0)),
        )

    def get_active_problem(self) -> Dict[str, Any]:
        self.load()
        if self.data.get("active_mode") == "cp":
            pid = self.data.get("active_problem_id", "")
            cp_prob = get_cp_problem_db(pid) or self.data.get("active_cp_problem")
            if cp_prob:
                return cp_prob
        pid = self.data.get("active_problem_id", "01_wire_zero")
        return CURRICULUM_BY_ID.get(pid, CURRICULUM_PROBLEMS[0])

    def get_problem_by_id(self, problem_id: str) -> Dict[str, Any]:
        if problem_id in CURRICULUM_BY_ID:
            return CURRICULUM_BY_ID[problem_id]
        cp_prob = get_cp_problem_db(problem_id)
        if cp_prob:
            return cp_prob
        if self.data.get("active_cp_problem") and self.data["active_cp_problem"].get("id") == problem_id:
            return self.data["active_cp_problem"]
        return CURRICULUM_PROBLEMS[0]

    def get_user_code(self, problem: Dict[str, Any], editor_mode: Optional[str] = None) -> str:
        mode = editor_mode or self.data.get("editor_mode", "snippet")
        pid = problem["id"]
        saved = get_saved_code_db(self.username, pid, mode)
        if saved is not None:
            return saved
        return problem["snippet_template"] if mode == "snippet" else problem["full_template"]

    def set_user_code(self, problem_id: str, code: str, editor_mode: str = "snippet") -> None:
        set_saved_code_db(self.username, problem_id, editor_mode, code)

    def select_problem(self, problem_id: str, mode_type: str = "curriculum", editor_mode: Optional[str] = None) -> Dict[str, Any]:
        fields: Dict[str, Any] = {"active_mode": mode_type, "active_problem_id": problem_id}
        if editor_mode:
            fields["editor_mode"] = editor_mode
        if mode_type == "cp":
            cp_prob = get_cp_problem_db(problem_id)
            if cp_prob:
                self.data["active_cp_problem"] = cp_prob
        update_user_fields(self.username, **fields)
        self.load()
        self.sync_to_vscode_workspace()
        return self.get_active_problem()

    def generate_new_cp(
        self,
        difficulty: str = "Medium",
        category: str = "all",
        seed: Optional[int] = None,
        question_format: str = "all",
    ) -> Dict[str, Any]:
        prob = generate_cp_problem(
            difficulty=difficulty,
            category=category,
            seed=seed,
            question_format=question_format,
        )
        save_cp_problem_db(self.username, prob)
        update_user_fields(
            self.username,
            active_mode="cp",
            active_problem_id=prob["id"],
        )
        self.load()
        self.sync_to_vscode_workspace()
        return prob

    def start_daily_challenge(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        if not date_str:
            date_str = datetime.date.today().isoformat()
        existing = get_daily_problem_db(date_str)
        if existing:
            prob = existing
        else:
            prob = generate_daily_problem(date_str)
            save_cp_problem_db(self.username, prob, is_daily=True, daily_date=date_str)
        update_user_fields(
            self.username,
            active_mode="cp",
            active_problem_id=prob["id"],
        )
        self.load()
        self.sync_to_vscode_workspace()
        return prob

    def start_cp_session(
        self,
        time_budget_min: int = 20,
        difficulty: str = "Medium",
        count: int = 0,
        category: str = "all",
        question_format: str = "all",
    ) -> Dict[str, Any]:
        pack = generate_cp_session(
            time_budget_min=time_budget_min,
            difficulty=difficulty,
            count=count,
            category=category,
            question_format=question_format,
        )
        pids = []
        for p in pack["problems"]:
            save_cp_problem_db(self.username, p)
            pids.append(p["id"])

        sess_title = f"{pack['problem_count']}-Problem {difficulty} Pack ({time_budget_min}m)"
        sess = create_cp_session_db(
            session_id=pack["session_id"],
            username=self.username,
            title=sess_title,
            time_budget_sec=pack["time_budget_sec"],
            difficulty=difficulty,
            category=category,
            question_format=question_format,
            problem_ids=pids,
        )
        first_prob = pack["problems"][0]
        update_user_fields(
            self.username,
            active_mode="cp",
            active_problem_id=first_prob["id"],
            active_session_id=pack["session_id"],
        )
        self.load()
        self.sync_to_vscode_workspace()
        return {
            "session": sess,
            "problems": pack["problems"],
            "active_problem": first_prob,
        }

    def record_evaluation(self, problem: Dict[str, Any], user_code: str, editor_mode: str, eval_dict: Dict[str, Any]) -> None:
        self.load()
        pid = problem["id"]
        self.set_user_code(pid, user_code, editor_mode)
        passed = bool(eval_dict.get("passed"))
        ai_score = int(eval_dict.get("ai_review", {}).get("idiomatic_score", 0))

        if problem.get("mode_type") == "cp":
            if passed:
                first_time = mark_cp_problem_solved_db(pid)
                if first_time:
                    delta = 25 if problem.get("difficulty") == "Easy" else (45 if problem.get("difficulty") == "Medium" else 75)
                    new_rating = int(self.data.get("cp_rating", 1200)) + delta
                    new_streak = int(self.data.get("cp_streak", 0)) + 1
                    new_solved = int(self.data.get("cp_solved_count", 0)) + 1
                    fields: Dict[str, Any] = {
                        "cp_rating": new_rating,
                        "cp_streak": new_streak,
                        "cp_solved_count": new_solved,
                    }
                    if problem.get("is_daily"):
                        today_s = problem.get("daily_date") or datetime.date.today().isoformat()
                        if self.data.get("last_daily_date") != today_s:
                            fields["daily_streak"] = int(self.data.get("daily_streak", 0)) + 1
                            fields["last_daily_date"] = today_s
                    update_user_fields(self.username, **fields)
                # Update active session if problem belongs to it
                sess = self.data.get("active_session")
                if sess and pid in sess.get("problem_ids", []):
                    update_cp_session_progress_db(sess["session_id"], pid)
            else:
                update_user_fields(self.username, cp_streak=0)
        else:
            mark_curriculum_attempt(self.username, pid, passed, ai_score)

        record_submission_db(
            username=self.username,
            problem_id=pid,
            title=problem["title"],
            mode_type=problem.get("mode_type", "curriculum"),
            question_format=problem.get("question_format", "design_from_spec"),
            compiled=bool(eval_dict.get("compiled", False)),
            passed=passed,
            passed_tests=int(eval_dict.get("passed_tests", 0)),
            total_tests=int(eval_dict.get("total_tests", 0)),
            idiomatic_score=ai_score,
            execution_time_ms=int(eval_dict.get("execution_time_ms", 0)),
        )

        last_eval_obj = {
            "problem_id": pid,
            "timestamp": int(time.time()),
            "result": eval_dict,
        }
        update_user_fields(self.username, last_eval_json=json.dumps(last_eval_obj))
        self.load()
        self.write_vscode_result_md(problem, eval_dict)

    def sync_to_vscode_workspace(self) -> None:
        """
        Stage the currently active problem into `workspace/current_problem.bsv` and `workspace/PROBLEM.md`
        so the user can edit directly inside VS Code and submit via VS Code tasks or auto-save!
        """
        prob = self.get_active_problem()
        editor_mode = self.data.get("editor_mode", "snippet")
        code = self.get_user_code(prob, editor_mode)
        q_fmt = prob.get("question_format", "design_from_spec")

        header = (
            f"// ============================================================================\n"
            f"// BSVbits Active Problem: {prob['title']} ({prob['id']})\n"
            f"// User: {self.username} (SQLite Shared State) | Mode: {prob.get('mode_type', 'curriculum').upper()} ({q_fmt})\n"
            f"// Difficulty: {prob.get('difficulty', 'Easy')} | Editor Mode: {editor_mode.upper()}\n"
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
        mtime = VSCODE_BSV_FILE.stat().st_mtime
        self.data["last_vscode_mtime"] = mtime
        update_user_fields(self.username, last_vscode_mtime=mtime)

        md_text = (
            f"# {prob['title']}\n\n"
            f"- **ID**: `{prob['id']}` | **User**: `{self.username}` (SQLite DBMS Shared State)\n"
            f"- **Track**: {prob.get('track_title', 'Competitive Arena')}\n"
            f"- **Difficulty**: **{prob.get('difficulty', 'Medium')}** | **Format**: `{q_fmt}`\n"
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
            f"**User**: `{self.username}` | **Verdict**: **{verdict}**  ",
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
