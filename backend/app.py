"""
FastAPI Backend for BSVbits:
  - Serves the interactive Web IDE (Monaco VS Code editor + Waveform Viewer + Schedule & RTL Inspector)
  - Provides REST endpoints for Mode 1 (HDLBits Guided Progression) and Mode 2 (Dynamic CP Arena)
  - Background watcher that detects edits to `workspace/current_problem.bsv` in VS Code and automatically evaluates or syncs!
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .compiler import find_bsc
from .cp_generator import CP_CATEGORIES
from .curriculum import CURRICULUM_BY_ID, CURRICULUM_PROBLEMS, CURRICULUM_TRACKS
from .evaluator import evaluate_submission, generate_contextual_hint
from .state import BSVBitsState, VSCODE_BSV_FILE

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"

app = FastAPI(
    title="BSVbits — Bluespec SystemVerilog Learning & Competitive Hardware Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

state = BSVBitsState()


class SubmitRequest(BaseModel):
    problem_id: str
    code: str
    editor_mode: str = "snippet"  # "snippet" | "full"
    llm_api_key: Optional[str] = None
    llm_api_base: Optional[str] = None
    llm_model: Optional[str] = None


class SelectProblemRequest(BaseModel):
    problem_id: str
    mode_type: str = "curriculum"
    editor_mode: Optional[str] = None


class GenerateCpRequest(BaseModel):
    difficulty: str = "Medium"
    category: str = "all"
    seed: Optional[int] = None


class HintRequest(BaseModel):
    problem_id: str
    code: str
    hint_level: int = 0


class SyncVsCodeRequest(BaseModel):
    problem_id: str
    code: str
    editor_mode: str = "snippet"


@app.on_event("startup")
async def start_vscode_watcher() -> None:
    """Background loop that watches `workspace/current_problem.bsv` for external VS Code saves."""
    asyncio.create_task(_vscode_file_watcher_loop())


async def _vscode_file_watcher_loop() -> None:
    while True:
        await asyncio.sleep(1.5)
        try:
            if VSCODE_BSV_FILE.exists():
                mtime = VSCODE_BSV_FILE.stat().st_mtime
                last_mtime = float(state.data.get("last_vscode_mtime", 0.0))
                if mtime > last_mtime + 0.05:
                    state.data["last_vscode_mtime"] = mtime
                    new_code = state.read_from_vscode_workspace()
                    if new_code is not None:
                        prob = state.get_active_problem()
                        mode = state.data.get("editor_mode", "snippet")
                        state.set_user_code(prob["id"], new_code, mode)
        except Exception:
            pass


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    try:
        bsc_bin, lib_dir = find_bsc()
        bsc_ready = True
    except Exception as e:
        bsc_bin, lib_dir = str(e), ""
        bsc_ready = False

    active_prob = state.get_active_problem()
    editor_mode = state.data.get("editor_mode", "snippet")
    return {
        "bsc_ready": bsc_ready,
        "bsc_path": bsc_bin,
        "bluespecdir": lib_dir,
        "active_mode": state.data.get("active_mode", "curriculum"),
        "editor_mode": editor_mode,
        "active_problem": _serialize_problem_for_client(active_prob, editor_mode),
        "solved_curriculum": state.data.get("solved_curriculum", []),
        "total_curriculum": len(CURRICULUM_PROBLEMS),
        "cp_rating": state.data.get("cp_rating", 1200),
        "cp_streak": state.data.get("cp_streak", 0),
        "cp_solved_count": state.data.get("cp_solved_count", 0),
        "submissions": state.data.get("submissions", [])[:20],
        "vscode_workspace_file": str(VSCODE_BSV_FILE),
        "last_eval_result": state.data.get("last_eval_result"),
    }


@app.get("/api/curriculum")
def get_curriculum() -> Dict[str, Any]:
    solved = set(state.data.get("solved_curriculum", []))
    tracks_out = []
    for t in CURRICULUM_TRACKS:
        t_probs = [p for p in CURRICULUM_PROBLEMS if p["track_id"] == t["id"]]
        tracks_out.append({
            "id": t["id"],
            "title": t["title"],
            "subtitle": t["subtitle"],
            "problems": [
                {
                    "id": p["id"],
                    "number": p["number"],
                    "title": p["title"],
                    "difficulty": p["difficulty"],
                    "tags": p["tags"],
                    "solved": p["id"] in solved,
                }
                for p in t_probs
            ],
        })
    return {
        "tracks": tracks_out,
        "solved_count": len(solved),
        "total_count": len(CURRICULUM_PROBLEMS),
        "cp_categories": CP_CATEGORIES,
    }


@app.get("/api/problem/{problem_id}")
def get_problem(problem_id: str, editor_mode: Optional[str] = None) -> Dict[str, Any]:
    prob = state.get_problem_by_id(problem_id)
    mode = editor_mode or state.data.get("editor_mode", "snippet")
    return _serialize_problem_for_client(prob, mode)


@app.post("/api/select")
def select_problem(req: SelectProblemRequest) -> Dict[str, Any]:
    prob = state.select_problem(req.problem_id, mode_type=req.mode_type, editor_mode=req.editor_mode)
    mode = state.data.get("editor_mode", "snippet")
    return {
        "active_mode": state.data.get("active_mode"),
        "editor_mode": mode,
        "problem": _serialize_problem_for_client(prob, mode),
        "vscode_file": str(VSCODE_BSV_FILE),
    }


@app.post("/api/cp/generate")
def generate_cp(req: GenerateCpRequest) -> Dict[str, Any]:
    prob = state.generate_new_cp(difficulty=req.difficulty, category=req.category, seed=req.seed)
    mode = state.data.get("editor_mode", "snippet")
    return {
        "active_mode": "cp",
        "editor_mode": mode,
        "problem": _serialize_problem_for_client(prob, mode),
        "cp_rating": state.data.get("cp_rating", 1200),
        "cp_streak": state.data.get("cp_streak", 0),
    }


@app.post("/api/submit")
def submit_solution(req: SubmitRequest) -> Dict[str, Any]:
    prob = state.get_problem_by_id(req.problem_id)
    llm_cfg = {
        "api_key": req.llm_api_key or "",
        "api_base": req.llm_api_base or "",
        "model": req.llm_model or "",
    }
    eval_res = evaluate_submission(prob, req.code, mode=req.editor_mode, llm_config=llm_cfg)
    eval_dict = eval_res.to_dict()
    state.record_evaluation(prob, req.code, req.editor_mode, eval_dict)
    # Also keep VS Code workspace file synced with the submitted code
    state.sync_to_vscode_workspace()
    return {
        "evaluation": eval_dict,
        "solved_curriculum": state.data.get("solved_curriculum", []),
        "cp_rating": state.data.get("cp_rating", 1200),
        "cp_streak": state.data.get("cp_streak", 0),
        "cp_solved_count": state.data.get("cp_solved_count", 0),
        "submissions": state.data.get("submissions", [])[:20],
    }


@app.post("/api/hint")
def get_hint(req: HintRequest) -> Dict[str, Any]:
    prob = state.get_problem_by_id(req.problem_id)
    return generate_contextual_hint(prob, req.code, hint_level=req.hint_level)


@app.get("/api/solution/{problem_id}")
def get_golden_solution(problem_id: str) -> Dict[str, Any]:
    prob = state.get_problem_by_id(problem_id)
    return {
        "problem_id": prob["id"],
        "title": prob["title"],
        "reference_snippet": prob["reference_snippet"],
        "reference_full": (
            f"module {prob['module_name']}({prob['interface_name']});\n"
            f"{prob['reference_snippet']}\n"
            f"endmodule"
        ),
        "reference_bsv": prob["reference_bsv"],
    }


@app.post("/api/vscode/sync")
def sync_vscode(req: SyncVsCodeRequest) -> Dict[str, Any]:
    prob = state.get_problem_by_id(req.problem_id)
    state.set_user_code(prob["id"], req.code, req.editor_mode)
    state.data["editor_mode"] = req.editor_mode
    state.sync_to_vscode_workspace()
    return {
        "synced": True,
        "vscode_file": str(VSCODE_BSV_FILE),
        "code": state.get_user_code(prob, req.editor_mode),
    }


@app.get("/api/vscode/pull")
def pull_from_vscode() -> Dict[str, Any]:
    prob = state.get_active_problem()
    mode = state.data.get("editor_mode", "snippet")
    code = state.read_from_vscode_workspace()
    if code is not None:
        state.set_user_code(prob["id"], code, mode)
    return {
        "problem_id": prob["id"],
        "editor_mode": mode,
        "code": state.get_user_code(prob, mode),
        "last_eval_result": state.data.get("last_eval_result"),
    }


def _serialize_problem_for_client(prob: Dict[str, Any], editor_mode: str = "snippet") -> Dict[str, Any]:
    solved = set(state.data.get("solved_curriculum", []))
    return {
        "id": prob["id"],
        "number": prob.get("number", 1),
        "title": prob["title"],
        "track_id": prob.get("track_id", ""),
        "track_title": prob.get("track_title", ""),
        "difficulty": prob.get("difficulty", "Easy"),
        "tags": prob.get("tags", []),
        "description": prob.get("description", ""),
        "bsv_vs_verilog": prob.get("bsv_vs_verilog", ""),
        "diagram": prob.get("diagram", ""),
        "interface_name": prob["interface_name"],
        "module_name": prob["module_name"],
        "interface_def": prob["interface_def"],
        "snippet_template": prob["snippet_template"],
        "full_template": prob["full_template"],
        "user_code_snippet": state.get_user_code(prob, "snippet"),
        "user_code_full": state.get_user_code(prob, "full"),
        "active_code": state.get_user_code(prob, editor_mode),
        "hints_count": len(prob.get("hints", [])),
        "mode_type": prob.get("mode_type", "curriculum"),
        "solved": prob["id"] in solved,
        "time_limit_sec": prob.get("time_limit_sec", 300),
        "points": prob.get("points", 100),
        "seed": prob.get("seed"),
    }


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> Any:
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>BSVbits Backend Running</h1>")
