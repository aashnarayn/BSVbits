"""
SQLite3 Relational DBMS for BSVbits (`workspace/bsvbits.db`).
Provides ACID-compliant, zero-cost persistent state shared in real time between:
  1. The Web Application (`backend/app.py`)
  2. The VS Code IDE & CLI (`./bsvbits` and `workspace/current_problem.bsv`)

Tables:
  - users               : User profiles, active mode/problem, ELO rating, streaks, active session
  - curriculum_progress : Per-user solved status, best score, attempt count, and timestamps
  - saved_code          : Per-user, per-problem, per-editor-mode code snapshots
  - submissions         : Complete submission audit log with hardware metrics & AI scores
  - cp_problems         : Generated Competitive Arena & Daily problems
  - cp_sessions         : Multi-problem timed/untimed practice sets & contest sessions
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = REPO_ROOT / "workspace"
DB_PATH = WORKSPACE_DIR / "bsvbits.db"


def get_connection() -> sqlite3.Connection:
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                display_name TEXT NOT NULL DEFAULT 'Hardware Learner',
                active_mode TEXT NOT NULL DEFAULT 'curriculum',
                active_problem_id TEXT NOT NULL DEFAULT '01_wire_zero',
                editor_mode TEXT NOT NULL DEFAULT 'snippet',
                cp_rating INTEGER NOT NULL DEFAULT 1200,
                cp_streak INTEGER NOT NULL DEFAULT 0,
                cp_solved_count INTEGER NOT NULL DEFAULT 0,
                daily_streak INTEGER NOT NULL DEFAULT 0,
                last_daily_date TEXT NOT NULL DEFAULT '',
                active_session_id TEXT NOT NULL DEFAULT '',
                last_vscode_mtime REAL NOT NULL DEFAULT 0.0,
                last_eval_json TEXT NOT NULL DEFAULT '',
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS curriculum_progress (
                username TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                solved INTEGER NOT NULL DEFAULT 0,
                best_score INTEGER NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0,
                updated_at INTEGER NOT NULL,
                PRIMARY KEY (username, problem_id)
            );

            CREATE TABLE IF NOT EXISTS saved_code (
                username TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                editor_mode TEXT NOT NULL,
                code TEXT NOT NULL,
                updated_at INTEGER NOT NULL,
                PRIMARY KEY (username, problem_id, editor_mode)
            );

            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                title TEXT NOT NULL,
                mode_type TEXT NOT NULL,
                question_format TEXT NOT NULL DEFAULT 'design_from_spec',
                compiled INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                passed_tests INTEGER NOT NULL,
                total_tests INTEGER NOT NULL,
                idiomatic_score INTEGER NOT NULL,
                execution_time_ms INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cp_problems (
                problem_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                seed INTEGER NOT NULL,
                difficulty TEXT NOT NULL,
                category TEXT NOT NULL,
                question_format TEXT NOT NULL,
                is_daily INTEGER NOT NULL DEFAULT 0,
                daily_date TEXT NOT NULL DEFAULT '',
                solved INTEGER NOT NULL DEFAULT 0,
                problem_json TEXT NOT NULL,
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cp_sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                title TEXT NOT NULL,
                time_budget_sec INTEGER NOT NULL,
                difficulty TEXT NOT NULL,
                category TEXT NOT NULL,
                question_format TEXT NOT NULL,
                problem_ids_json TEXT NOT NULL,
                completed_ids_json TEXT NOT NULL,
                current_index INTEGER NOT NULL DEFAULT 0,
                started_at INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active'
            );
            """
        )
        # Ensure default user exists
        cur = conn.execute("SELECT username FROM users WHERE username = 'default'")
        if not cur.fetchone():
            conn.execute(
                "INSERT INTO users (username, display_name, created_at) VALUES (?, ?, ?)",
                ("default", "Default Engineer", int(time.time())),
            )
        conn.commit()


def ensure_user(username: str) -> Dict[str, Any]:
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO users (username, display_name, created_at) VALUES (?, ?, ?)",
                (username, username.capitalize(), int(time.time())),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row)


def list_users() -> List[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT username, display_name, cp_rating, cp_streak, cp_solved_count, daily_streak FROM users ORDER BY created_at ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def update_user_fields(username: str, **fields: Any) -> None:
    if not fields:
        return
    ensure_user(username)
    cols = ", ".join(f"{k} = ?" for k in fields.keys())
    vals = list(fields.values()) + [username]
    with get_connection() as conn:
        conn.execute(f"UPDATE users SET {cols} WHERE username = ?", vals)
        conn.commit()


def get_solved_curriculum_ids(username: str) -> List[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT problem_id FROM curriculum_progress WHERE username = ? AND solved = 1 ORDER BY updated_at ASC",
            (username,),
        ).fetchall()
        return [r["problem_id"] for r in rows]


def mark_curriculum_attempt(username: str, problem_id: str, passed: bool, score: int) -> None:
    now = int(time.time())
    with get_connection() as conn:
        row = conn.execute(
            "SELECT solved, best_score, attempts FROM curriculum_progress WHERE username = ? AND problem_id = ?",
            (username, problem_id),
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO curriculum_progress (username, problem_id, solved, best_score, attempts, updated_at) VALUES (?, ?, ?, ?, 1, ?)",
                (username, problem_id, 1 if passed else 0, score, now),
            )
        else:
            new_solved = 1 if (row["solved"] or passed) else 0
            new_best = max(int(row["best_score"]), score)
            new_att = int(row["attempts"]) + 1
            conn.execute(
                "UPDATE curriculum_progress SET solved = ?, best_score = ?, attempts = ?, updated_at = ? WHERE username = ? AND problem_id = ?",
                (new_solved, new_best, new_att, now, username, problem_id),
            )
        conn.commit()


def get_saved_code_db(username: str, problem_id: str, editor_mode: str) -> Optional[str]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT code FROM saved_code WHERE username = ? AND problem_id = ? AND editor_mode = ?",
            (username, problem_id, editor_mode),
        ).fetchone()
        return row["code"] if row else None


def set_saved_code_db(username: str, problem_id: str, editor_mode: str, code: str) -> None:
    now = int(time.time())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO saved_code (username, problem_id, editor_mode, code, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username, problem_id, editor_mode)
            DO UPDATE SET code = excluded.code, updated_at = excluded.updated_at
            """,
            (username, problem_id, editor_mode, code, now),
        )
        conn.commit()


def save_cp_problem_db(username: str, prob: Dict[str, Any], is_daily: bool = False, daily_date: str = "") -> None:
    now = int(time.time())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO cp_problems (problem_id, username, seed, difficulty, category, question_format, is_daily, daily_date, solved, problem_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            ON CONFLICT(problem_id) DO UPDATE SET problem_json = excluded.problem_json
            """,
            (
                prob["id"],
                username,
                int(prob.get("seed") or 0),
                prob.get("difficulty", "Medium"),
                prob.get("cp_category", "all"),
                prob.get("question_format", "design_from_spec"),
                1 if is_daily else 0,
                daily_date,
                json.dumps(prob),
                now,
            ),
        )
        conn.commit()


def get_cp_problem_db(problem_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT problem_json, solved FROM cp_problems WHERE problem_id = ?", (problem_id,)).fetchone()
        if not row:
            return None
        d = json.loads(row["problem_json"])
        d["solved"] = bool(row["solved"])
        return d


def get_daily_problem_db(daily_date: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT problem_json, solved FROM cp_problems WHERE is_daily = 1 AND daily_date = ? LIMIT 1",
            (daily_date,),
        ).fetchone()
        if not row:
            return None
        d = json.loads(row["problem_json"])
        d["solved"] = bool(row["solved"])
        return d


def mark_cp_problem_solved_db(problem_id: str) -> bool:
    """Mark CP problem solved and return True if this was the FIRST time it was solved."""
    with get_connection() as conn:
        row = conn.execute("SELECT solved FROM cp_problems WHERE problem_id = ?", (problem_id,)).fetchone()
        if not row:
            return False
        already = bool(row["solved"])
        if not already:
            conn.execute("UPDATE cp_problems SET solved = 1 WHERE problem_id = ?", (problem_id,))
            conn.commit()
        return not already


def list_recent_cp_problems_db(username: str, limit: int = 25) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT problem_json, solved, is_daily, daily_date FROM cp_problems WHERE username = ? ORDER BY created_at DESC LIMIT ?",
            (username, limit),
        ).fetchall()
        out = []
        for r in rows:
            p = json.loads(r["problem_json"])
            p["solved"] = bool(r["solved"])
            p["is_daily"] = bool(r["is_daily"])
            p["daily_date"] = r["daily_date"]
            out.append(p)
        return out


def create_cp_session_db(
    session_id: str,
    username: str,
    title: str,
    time_budget_sec: int,
    difficulty: str,
    category: str,
    question_format: str,
    problem_ids: List[str],
) -> Dict[str, Any]:
    now = int(time.time())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO cp_sessions
            (session_id, username, title, time_budget_sec, difficulty, category, question_format, problem_ids_json, completed_ids_json, current_index, started_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, '[]', 0, ?, 'active')
            """,
            (
                session_id,
                username,
                title,
                time_budget_sec,
                difficulty,
                category,
                question_format,
                json.dumps(problem_ids),
                now,
            ),
        )
        conn.commit()
    return get_cp_session_db(session_id) or {}


def get_cp_session_db(session_id: str) -> Optional[Dict[str, Any]]:
    if not session_id:
        return None
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM cp_sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["problem_ids"] = json.loads(d.pop("problem_ids_json", "[]"))
        d["completed_ids"] = json.loads(d.pop("completed_ids_json", "[]"))
        return d


def update_cp_session_progress_db(session_id: str, problem_id: str, current_index: Optional[int] = None) -> None:
    sess = get_cp_session_db(session_id)
    if not sess:
        return
    comp = list(sess["completed_ids"])
    if problem_id not in comp and problem_id in sess["problem_ids"]:
        comp.append(problem_id)
    idx = current_index if current_index is not None else sess["current_index"]
    status = "completed" if len(comp) >= len(sess["problem_ids"]) else sess["status"]
    with get_connection() as conn:
        conn.execute(
            "UPDATE cp_sessions SET completed_ids_json = ?, current_index = ?, status = ? WHERE session_id = ?",
            (json.dumps(comp), idx, status, session_id),
        )
        conn.commit()


def record_submission_db(
    username: str,
    problem_id: str,
    title: str,
    mode_type: str,
    question_format: str,
    compiled: bool,
    passed: bool,
    passed_tests: int,
    total_tests: int,
    idiomatic_score: int,
    execution_time_ms: int,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO submissions
            (username, problem_id, title, mode_type, question_format, compiled, passed, passed_tests, total_tests, idiomatic_score, execution_time_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                problem_id,
                title,
                mode_type,
                question_format,
                1 if compiled else 0,
                1 if passed else 0,
                passed_tests,
                total_tests,
                idiomatic_score,
                execution_time_ms,
                int(time.time()),
            ),
        )
        conn.commit()


def list_submissions_db(username: str, limit: int = 25) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM submissions WHERE username = ? ORDER BY id DESC LIMIT ?",
            (username, limit),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["compiled"] = bool(d["compiled"])
            d["passed"] = bool(d["passed"])
            d["timestamp"] = d["created_at"]
            out.append(d)
        return out
