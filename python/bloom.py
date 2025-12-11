from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import hashlib

app = Flask(__name__)
CORS(app)

# Bloom filter parameters:
# n = 50
# p = 0.1 (1 in 10)
# m = 264 (33B)
# k = 2

M_BITS = 264
K_HASHES = 2


class BloomFilter:
    def __init__(self, m_bits: int, k_hashes: int):
        self.m = m_bits
        self.k = k_hashes
        # Bit array storage.
        self._bits = bytearray((m_bits + 7) // 8)
        # Re-entrant lock to protect against concurrent access
        self._lock = threading.RLock()

    def _hashes(self, value: str):
        """
        Generate k indices in [0, m) using double hashing.
        h_i(x) = (h1 + i * h2) mod m
        """
        data = value.encode("utf-8")
        digest = hashlib.sha256(data).digest()
        # Use 16 bytes to derive two 64-bit integers
        h1 = int.from_bytes(digest[:8], byteorder="big", signed=False)
        h2 = int.from_bytes(digest[8:16], byteorder="big", signed=False) or 1  # avoid 0

        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def _set_bit(self, idx: int) -> None:
        byte_index = idx >> 3          # idx // 8
        bit_index = idx & 7            # idx % 8
        self._bits[byte_index] |= (1 << bit_index)

    def _get_bit(self, idx: int) -> bool:
        byte_index = idx >> 3
        bit_index = idx & 7
        return bool(self._bits[byte_index] & (1 << bit_index))

    def add(self, value: str) -> None:
        """Insert a value into the Bloom filter."""
        with self._lock:
            for idx in self._hashes(value):
                self._set_bit(idx)

    def might_contain(self, value: str) -> bool:
        """
        Check membership.

        Returns:
            True  -> value is *probably* in the set (or a false positive)
            False -> value is definitely not in the set
        """
        with self._lock:
            for idx in self._hashes(value):
                if not self._get_bit(idx):
                    return False
            return True

    def bit_dump(self) -> str:
        """
        Return a binary string representation of the bit array.
        Index 0 corresponds to bit index 0 in the filter, up to m-1.
        """
        with self._lock:
            bits = []
            for i in range(self.m):
                byte_index = i >> 3          # i // 8
                bit_index = i & 7            # i % 8
                bit = (self._bits[byte_index] >> bit_index) & 1
                bits.append(str(bit))
            return "".join(bits)


# Global Bloom filter instance
bloom = BloomFilter(M_BITS, K_HASHES)


def insert(value: str) -> None:
    """Insert a value into the Bloom filter."""
    bloom.add(value)


def lookup(value: str) -> bool:
    """Return True if the value is *probably* present in the Bloom filter."""
    return bloom.might_contain(value)


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
    message = (
        f'"{value}" is probably in the set.'
        if exists
        else f'"{value}" is definitely not in the set.'
    )
    return jsonify({"ok": True, "exists": exists, "message": message})


@app.route("/bits", methods=["GET"])
def bits_route():
    """Debug endpoint: dump the raw bit array as a binary string."""
    return jsonify({"ok": True, "bits": bloom.bit_dump()})


if __name__ == "__main__":
    # Hosts on all interfaces for local testing; adjust as needed.
    context = (
        "/home/ubuntu/bloom-filter-session/certs/fullchain.pem",
        "/home/ubuntu/bloom-filter-session/certs/privkey.pem",
    )
    app.run(host="0.0.0.0", port=5000, ssl_context=context, threaded=True)