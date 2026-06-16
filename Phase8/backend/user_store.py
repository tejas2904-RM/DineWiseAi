from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

_USERS_FILE = DATA_DIR / "users.json"
_HISTORY_FILE = DATA_DIR / "history.json"
_FAVORITES_FILE = DATA_DIR / "favorites.json"

_lock = threading.Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(path: Path, data: Dict[str, Any]) -> None:
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Users -------------------------------------------------------------------

def get_user(user_id: str) -> Dict[str, Any]:
    users = _load(_USERS_FILE)
    if user_id not in users:
        users[user_id] = {
            "userId": user_id,
            "name": "",
            "email": None,
            "createdAt": _utc_now(),
        }
        _save(_USERS_FILE, users)
    return users[user_id]


def update_user(user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    users = _load(_USERS_FILE)
    user = users.get(user_id) or {
        "userId": user_id,
        "name": "",
        "email": None,
        "createdAt": _utc_now(),
    }
    if name is not None:
        user["name"] = name
    if email is not None:
        user["email"] = email
    users[user_id] = user
    _save(_USERS_FILE, users)
    return user


# History -----------------------------------------------------------------

def add_history(entry: Dict[str, Any]) -> None:
    history = _load(_HISTORY_FILE)
    user_id = entry.get("userId", "anonymous")
    if user_id not in history:
        history[user_id] = []
    history[user_id].insert(0, entry)
    history[user_id] = history[user_id][:50]
    _save(_HISTORY_FILE, history)


def get_history(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    history = _load(_HISTORY_FILE)
    return history.get(user_id, [])[:limit]


# Favorites ---------------------------------------------------------------

def add_favorite(user_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
    favorites = _load(_FAVORITES_FILE)
    if user_id not in favorites:
        favorites[user_id] = []
    existing_ids = {f["restaurantId"] for f in favorites[user_id]}
    if item["restaurantId"] in existing_ids:
        return item
    item["addedAt"] = _utc_now()
    favorites[user_id].insert(0, item)
    _save(_FAVORITES_FILE, favorites)
    return item


def list_favorites(user_id: str) -> List[Dict[str, Any]]:
    favorites = _load(_FAVORITES_FILE)
    return favorites.get(user_id, [])


def remove_favorite(user_id: str, restaurant_id: str) -> bool:
    favorites = _load(_FAVORITES_FILE)
    if user_id not in favorites:
        return False
    before = len(favorites[user_id])
    favorites[user_id] = [f for f in favorites[user_id] if f["restaurantId"] != restaurant_id]
    if len(favorites[user_id]) < before:
        _save(_FAVORITES_FILE, favorites)
        return True
    return False
