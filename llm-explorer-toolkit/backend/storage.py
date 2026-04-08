"""
Storage Manager
Persists sessions, ratings, and favourites as JSON files on disk.
Easily swappable for SQLite or Postgres in production.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


DATA_DIR = Path(__file__).parent.parent / "data"
SESSIONS_DIR = DATA_DIR / "sessions"


class StorageManager:

    def __init__(self):
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Sessions ──────────────────────────────────────────────────────────────

    def _session_path(self, session_id: str) -> Path:
        return SESSIONS_DIR / f"{session_id}.json"

    def save_session(self, session: dict) -> None:
        path = self._session_path(session["session_id"])
        path.write_text(json.dumps(session, indent=2, ensure_ascii=False), encoding='utf-8')

    def get_session(self, session_id: str) -> Optional[dict]:
        path = self._session_path(session_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding='utf-8'))

    def list_sessions(self, limit: int = 20) -> list[dict]:
        sessions = []
        for p in sorted(SESSIONS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                s = json.loads(p.read_text(encoding='utf-8'))
                sessions.append(self._summary(s))
            except Exception:
                pass
            if len(sessions) >= limit:
                break
        return sessions

    def list_favorites(self) -> list[dict]:
        favs = []
        for p in sorted(SESSIONS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                s = json.loads(p.read_text(encoding='utf-8'))
                if s.get("is_favorite"):
                    favs.append(s)
            except Exception:
                pass
        return favs

    def get_stats(self) -> dict:
        total = 0
        favorites = 0
        rated = 0
        ratings: list[int] = []
        model_counts: dict[str, int] = {}
        technique_counts: dict[str, int] = {}

        for p in SESSIONS_DIR.glob("*.json"):
            try:
                s = json.loads(p.read_text(encoding='utf-8'))
                total += 1
                if s.get("is_favorite"):
                    favorites += 1
                if s.get("ratings"):
                    rated += 1
                    for r in s["ratings"].values():
                        ratings.append(r["rating"])

                for side in ("model_a", "model_b"):
                    name = s.get(side, {}).get("name")
                    if name:
                        model_counts[name] = model_counts.get(name, 0) + 1

                tech = s.get("technique")
                if tech:
                    technique_counts[tech] = technique_counts.get(tech, 0) + 1
            except Exception:
                pass

        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
        return {
            "total_comparisons": total,
            "total_favorites": favorites,
            "total_rated": rated,
            "average_rating": avg_rating,
            "model_usage": model_counts,
            "technique_usage": technique_counts,
        }

    @staticmethod
    def _summary(s: dict) -> dict:
        """Return a lightweight session summary for list views."""
        return {
            "session_id": s.get("session_id"),
            "created_at": s.get("created_at"),
            "prompt": (s.get("prompt") or "")[:120],
            "technique": s.get("technique"),
            "model_a": s.get("model_a", {}).get("name"),
            "model_b": s.get("model_b", {}).get("name"),
            "is_favorite": s.get("is_favorite", False),
            "title": s.get("title"),
            "tags": s.get("tags", []),
            "ratings": s.get("ratings", {}),
        }