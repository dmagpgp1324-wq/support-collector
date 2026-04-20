from flask import Flask, jsonify
from collectors import collect_all

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

@app.route("/support-notices", methods=["GET"])
def support_notices():
    items = collect_all()
    return jsonify({
        "count": len(items),
        "items": items
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)