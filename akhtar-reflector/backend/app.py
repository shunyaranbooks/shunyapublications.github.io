from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict, Any

from reflector_core import recursion, memory, behavior, rds, safety
from reflector_core import config as cfg
from backend.responders.llm_local_stub import LocalStubResponder

app = FastAPI(title="Akhtar Reflector API")
SESSIONS: Dict[str, Dict[str, Any]] = {}

# responder plug-in (defaults to local stub)
responder = LocalStubResponder()

class Turn(BaseModel):
    session_id: str
    text: str
    depth: int = 3
    mem: bool = True
    pause: bool = True
    safety: bool = True

@app.post("/api/session/new")
def new_session():
    sid = str(uuid4())
    SESSIONS[sid] = dict(
        history=[],
        state=recursion.init_state(),
        metrics=rds.init_metrics(window=cfg.WINDOW),
        config=dict(tau=cfg.TAU, alpha=cfg.ALPHA)
    )
    return {"id": sid}

@app.get("/api/session/{sid}")
def dump_session(sid: str):
    return dict(session_id=sid, **SESSIONS[sid])

@app.post("/api/respond")
def respond(turn: Turn):
    s = SESSIONS[turn.session_id]
    user = (turn.text or "").strip()

    # Update memory
    if turn.mem:
        s["state"] = memory.update(s["state"], user)

    # Build recursive model
    model = recursion.model_of_other(s["state"], user, depth=turn.depth)

    # Safety
    guard = safety.guard(s["state"], user, depth=turn.depth, enable=turn.safety)

    # Reply
    reply, pause_ms = behavior.generate_reply(
        responder=responder, user=user, model=model,
        mem=turn.mem, intentional_pause=turn.pause, guard=guard
    )

    # Metrics
    metrics = rds.update_metrics(
        s["metrics"], user, reply, model,
        tau=s["config"]["tau"], alpha=s["config"]["alpha"]
    )

    # Append history
    s["history"].append(dict(user=user, reply=reply, pause_ms=pause_ms, guard=guard, model=model, metrics=metrics))
    return {"reply": reply, "pause_ms": pause_ms}

@app.get("/api/metrics/{sid}")
def metrics(sid: str):
    return SESSIONS[sid]["metrics"]
