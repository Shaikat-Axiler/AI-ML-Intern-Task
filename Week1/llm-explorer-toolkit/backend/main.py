"""
LLM Explorer Toolkit - FastAPI Backend
Handles model comparisons, prompt strategies, favorites, and ratings.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .models import ModelManager
from .storage import StorageManager

app = FastAPI(title="LLM Explorer Toolkit", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model_manager = ModelManager()
storage = StorageManager()

# ── Request / Response Schemas ──────────────────────────────────────────────

class CompareRequest(BaseModel):
    prompt: str
    model_a: str
    model_b: str
    technique: str          # zero_shot | one_shot | few_shot | chain_of_thought | role_play
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 512

class RatingRequest(BaseModel):
    session_id: str
    model: str              # "a" or "b"
    rating: int             # 1-5
    comment: Optional[str] = None

class SaveFavoriteRequest(BaseModel):
    session_id: str
    title: str
    tags: list[str] = []

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/models")
async def list_models():
    """Return available models fetched live from OpenRouter."""
    return await model_manager.available_models_async()


@app.get("/api/techniques")
def list_techniques():
    """Return supported prompting techniques with descriptions."""
    return {
        "zero_shot": {
            "label": "Zero Shot",
            "description": "Direct prompt with no examples — tests raw model capability.",
            "icon": "⚡"
        },
        "one_shot": {
            "label": "One Shot",
            "description": "One example provided before the main prompt.",
            "icon": "🎯"
        },
        "few_shot": {
            "label": "Few Shot",
            "description": "Multiple examples guide the model's response format.",
            "icon": "🔢"
        },
        "chain_of_thought": {
            "label": "Chain of Thought",
            "description": "Encourages step-by-step reasoning before answering.",
            "icon": "🔗"
        },
        "role_play": {
            "label": "Role Play",
            "description": "Assigns a persona or expert role to the model.",
            "icon": "🎭"
        },
    }


@app.post("/api/compare")
async def compare(req: CompareRequest):
    """Run side-by-side comparison of two models with a given technique."""
    session_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat()

    result_a = await model_manager.generate(
        model=req.model_a,
        prompt=req.prompt,
        technique=req.technique,
        system_prompt=req.system_prompt,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )

    result_b = await model_manager.generate(
        model=req.model_b,
        prompt=req.prompt,
        technique=req.technique,
        system_prompt=req.system_prompt,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )

    session = {
        "session_id": session_id,
        "created_at": started_at,
        "prompt": req.prompt,
        "technique": req.technique,
        "temperature": req.temperature,
        "max_tokens": req.max_tokens,
        "model_a": {"name": req.model_a, **result_a},
        "model_b": {"name": req.model_b, **result_b},
        "ratings": {},
        "is_favorite": False,
        "tags": [],
        "title": None,
    }

    storage.save_session(session)
    return session


@app.post("/api/rate")
def rate_response(req: RatingRequest):
    """Save a 1-5 star rating for a model response in a session."""
    session = storage.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session["ratings"][req.model] = {
        "rating": req.rating,
        "comment": req.comment,
        "rated_at": datetime.utcnow().isoformat(),
    }
    storage.save_session(session)
    return {"status": "ok", "session_id": req.session_id}


@app.post("/api/favorites")
def save_favorite(req: SaveFavoriteRequest):
    """Mark a session as a favourite with an optional title and tags."""
    session = storage.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session["is_favorite"] = True
    session["title"] = req.title
    session["tags"] = req.tags
    storage.save_session(session)
    return {"status": "ok"}


@app.delete("/api/favorites/{session_id}")
def remove_favorite(session_id: str):
    """Remove a session from favourites."""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session["is_favorite"] = False
    storage.save_session(session)
    return {"status": "ok"}


@app.get("/api/favorites")
def list_favorites():
    """Return all saved favourite sessions."""
    return storage.list_favorites()


@app.get("/api/sessions")
def list_sessions(limit: int = 20):
    """Return recent sessions."""
    return storage.list_sessions(limit=limit)


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/api/stats")
def get_stats():
    """Aggregate stats: total comparisons, favourite count, ratings summary."""
    return storage.get_stats()


# ── Static files (frontend) ───────────────────────────────────────────────────

_frontend = Path(__file__).parent.parent / "frontend"
if _frontend.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend / "static")), name="static")

    @app.get("/", response_class=FileResponse)
    def serve_index():
        return str(_frontend / "index.html")
