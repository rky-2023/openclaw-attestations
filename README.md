# openclaw-attestations

Daily Merkle root attestations for the openclaw audit ledger.

## What is this?

Every day at 03:00 UTC, the openclaw system:

1. Reads all audit envelope records from its Postgres projection for the previous day
2. Computes a binary SHA-256 Merkle root over the raw envelope bytes
3. Commits a signed attestation document to this repository

This makes the audit ledger **externally tamper-evident**: any deletion or
modification of historical audit records would produce a different Merkle root
and contradict the public record here.

## File layout

```
YYYY/
  MM/
    DD.json    ← one attestation per day
verify.py      ← standalone verifier (no dependencies)
```

## Attestation document schema (v1)

```json
{
  "version": "1",
  "date": "YYYY-MM-DD",
  "entry_count": 42,
  "first_ulid": "01J...",
  "last_ulid":  "01J...",
  "merkle_root": "sha256:<64-hex-chars>",
  "leaf_hashes": ["sha256:<64-hex-chars>", ...],
  "generated_at": "2026-05-26T03:00:00+00:00",
  "sig_attestation": "hmac-sha256:<hex>"
}
```

- **leaf_hashes**: SHA-256 of each raw audit envelope JSON, in ULID (chronological) order
- **merkle_root**: binary Merkle tree root over the leaf hashes
- **sig_attestation**: HMAC-SHA256 of the canonical document (key is process-local; Vault transit signing in Phase 3)

## Verification

```bash
python3 verify.py 2026/05/25.json
```

 has no dependencies beyond the Python standard library. It checks:

- Merkle root recomputed from leaf_hashes matches 
- Document structure is complete and well-formed

## About openclaw

openclaw is a self-hosted personal agent fabric. Source: [rky-2023/oc-ash](https://github.com/rky-2023/oc-ash)
