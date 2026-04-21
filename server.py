from flask import Flask, jsonify, Response
from collectors import collect_all
import json
import os
from datetime import datetime

app = Flask(__name__)

CACHE_FILE = "support_cache.json"
MIN_VALID_COUNT = 10


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {"count": 0, "items": [], "updated_at": ""}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"count": 0, "items": [], "updated_at": ""}


def save_cache(items):
    payload = {
        "count": len(items),
        "items": items,
        "updated_at": datetime.now().isoformat(timespec="seconds")
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    return payload


def get_best_snapshot():
    snapshots = []
    errors = []

    for _ in range(3):
        try:
            items = collect_all()
            snapshots.append(items)
        except Exception as e:
            errors.append(str(e))

    if snapshots:
        best = max(snapshots, key=lambda x: len(x))
        return best, errors

    return [], errors


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/support-notices", methods=["GET"])
def support_notices():
    cached = load_cache()
    items, errors = get_best_snapshot()

    if len(items) >= MIN_VALID_COUNT:
        payload = save_cache(items)
    else:
        payload = cached
        payload["warning"] = f"live_count={len(items)} too low, fallback to cache"
        if errors:
            payload["errors"] = errors

    return Response(
        json.dumps(payload, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


@app.route("/refresh", methods=["GET"])
def refresh():
    items, errors = get_best_snapshot()
    payload = save_cache(items)
    if errors:
        payload["errors"] = errors

    return Response(
        json.dumps(payload, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)