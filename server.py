from flask import Flask, jsonify, Response
from collectors import collect_all
import json
import os
from datetime import datetime

app = Flask(__name__)

CACHE_FILE = "support_cache.json"
MIN_VALID_COUNT = 10  # 이 개수보다 적으면 비정상 응답으로 보고 캐시 유지


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
    """
    수집 결과가 흔들릴 수 있으므로 3번 시도해서
    가장 많이 나온 결과를 사용
    """
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

    # 정상적으로 충분히 많이 잡히면 캐시 갱신
    if len(items) >= MIN_VALID_COUNT:
        payload = save_cache(items)
    else:
        # 비정상적으로 적게 잡히면 이전 캐시 유지
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