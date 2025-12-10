from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple in-memory store for demo purposes.
bloom_store = set()


def insert(value: str) -> bool:
    """Insert a value into the in-memory store."""
    bloom_store.add(str(value))
    return True


def lookup(value: str) -> bool:
    """Return True if the value is present."""
    return str(value) in bloom_store


@app.route("/insert", methods=["POST"])
def insert_route():
    payload = request.get_json(force=True, silent=True) or {}
    value = (payload.get("value") or "").strip()
    if not value:
        return jsonify({"ok": False, "message": "Value is required."}), 400

    insert(value)
    return jsonify({"ok": True, "message": f'"{value}" inserted.'}), 201


@app.route("/lookup", methods=["POST"])
def lookup_route():
    payload = request.get_json(force=True, silent=True) or {}
    value = (payload.get("value") or "").strip()
    if not value:
        return jsonify({"ok": False, "message": "Value is required."}), 400

    exists = lookup(value)
    message = f'"{value}" is probably in the set.' if exists else f'"{value}" is probably not in the set.'
    return jsonify({"ok": True, "exists": exists, "message": message})


@app.route("/store", methods=["GET"])
def store_route():
    """Return the current contents of the in-memory bloom_store."""
    return jsonify({"ok": True, "values": sorted(bloom_store)})



if __name__ == "__main__":
    # Hosts on all interfaces for local testing; adjust as needed.
    context = (
        "/home/ubuntu/bloom-filter-session/certs/fullchain.pem",
        "/home/ubuntu/bloom-filter-session/certs/privkey.pem",
    )
    app.run(host="0.0.0.0", port=5000, ssl_context=context)
