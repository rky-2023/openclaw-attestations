#!/usr/bin/env python3
"""Standalone verifier for openclaw daily attestations.

Usage:
    python3 verify.py YYYY/MM/DD.json

Checks:
  - Merkle root recomputed from leaf_hashes matches the stored merkle_root
  - Document is structurally complete

No external dependencies — standard library only.
Exit 0 on success, 1 on failure.
"""

import hashlib
import json
import sys


def _merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        return b"\x00" * 32
    layer = [hashlib.sha256(leaf).digest() for leaf in leaves]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [
            hashlib.sha256(layer[i] + layer[i + 1]).digest()
            for i in range(0, len(layer), 2)
        ]
    return layer[0]


def verify(path: str) -> bool:
    with open(path) as f:
        doc = json.load(f)

    required = {"version", "date", "entry_count", "merkle_root", "leaf_hashes", "generated_at"}
    missing = required - doc.keys()
    if missing:
        print(f"FAIL  missing fields: {missing}")
        return False

    # Recompute Merkle root from leaf_hashes
    leaf_bytes = []
    for h in doc["leaf_hashes"]:
        if not h.startswith("sha256:"):
            print(f"FAIL  bad leaf hash format: {h[:30]}")
            return False
        leaf_bytes.append(bytes.fromhex(h[len("sha256:"):]))

    computed_root = _merkle_root(leaf_bytes)
    stored_root_hex = doc["merkle_root"].removeprefix("sha256:")
    computed_hex = computed_root.hex()

    if computed_hex != stored_root_hex:
        print(f"FAIL  Merkle root mismatch")
        print(f"      stored:   {stored_root_hex}")
        print(f"      computed: {computed_hex}")
        return False

    print(f"PASS  date={doc['date']}  entries={doc['entry_count']}  merkle_root=sha256:{computed_hex[:16]}...")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} YYYY/MM/DD.json", file=sys.stderr)
        sys.exit(2)
    sys.exit(0 if verify(sys.argv[1]) else 1)
