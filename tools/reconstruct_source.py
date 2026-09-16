from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "src_payload"
OUT = ROOT / "mp3_organizer_v6_5_0.py"
EXPECTED_SHA256 = "dd8ab7d68b19cb9e7b9afba3824f538384f1f23fd7c987f5f4b1a100c3599ffe"

payload = "".join(
    p.read_text(encoding="ascii").strip()
    for p in sorted(PARTS.glob("part_*.b85"))
)

if not payload:
    raise SystemExit("No source payload parts found.")

raw = gzip.decompress(base64.b85decode(payload.encode("ascii")))
sha = hashlib.sha256(raw).hexdigest()
if sha != EXPECTED_SHA256:
    raise SystemExit(f"Source checksum mismatch: {sha}")

OUT.write_bytes(raw)
print(f"Reconstructed {OUT.name} ({len(raw)} bytes, sha256={sha})")
