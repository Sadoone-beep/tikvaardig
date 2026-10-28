"""Session history in a JSON file."""

from __future__ import annotations

import json
import os
from datetime import datetime


def data_dir() -> str:
    base = os.environ.get("TIKVAARDIG_DATA_DIR") or os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Tikvaardig")
    os.makedirs(base, exist_ok=True)
    return base


OLD_FILE = "geschiedenis.json"
OLD_MODES = {"30 seconden": "30 seconds", "60 seconden": "60 seconds", "Hele tekst": "Full text"}


def path() -> str:
    return os.path.join(data_dir(), "history.json")


def _migrate() -> None:
    """Rename the history file from the Dutch-only days, once."""
    old = os.path.join(data_dir(), OLD_FILE)
    if os.path.exists(old) and not os.path.exists(path()):
        try:
            os.replace(old, path())
        except OSError:
            pass


def load() -> list[dict]:
    _migrate()
    try:
        with open(path(), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    for it in data:
        if isinstance(it, dict) and it.get("mode") in OLD_MODES:
            it["mode"] = OLD_MODES[it["mode"]]
    return data


def add(mode: str, lang: str, wpm: float, accuracy: float, seconds: float, chars: int,
        when: datetime | None = None) -> dict:
    entry = {
        "when": (when or datetime.now()).strftime("%Y-%m-%d %H:%M"),
        "mode": mode, "lang": lang,
        "wpm": round(wpm, 1), "accuracy": round(accuracy, 1),
        "seconds": round(seconds, 1), "chars": chars,
    }
    items = load()
    items.append(entry)
    items = items[-500:]
    tmp = path() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path())
    return entry


def best(items: list[dict] | None = None, mode: str | None = None) -> dict | None:
    items = load() if items is None else items
    if mode:
        items = [i for i in items if i.get("mode") == mode]
    return max(items, key=lambda i: i.get("wpm", 0)) if items else None


def summary(items: list[dict] | None = None) -> dict:
    items = load() if items is None else items
    if not items:
        return {"count": 0, "avg_wpm": 0.0, "best_wpm": 0.0, "avg_accuracy": 0.0}
    return {
        "count": len(items),
        "avg_wpm": round(sum(i["wpm"] for i in items) / len(items), 1),
        "best_wpm": max(i["wpm"] for i in items),
        "avg_accuracy": round(sum(i["accuracy"] for i in items) / len(items), 1),
    }
