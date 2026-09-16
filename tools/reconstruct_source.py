from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "src_payload_v7"
OUT = ROOT / "mp3_organizer_v7_0_0.py"
EXPECTED_SHA256 = "e723acd53bedb8c9b07f070bff62c63c8adda9e91656fd16e78662561ea0cce4"

payload = "".join(
    p.read_text(encoding="ascii").strip()
    for p in sorted(PARTS.glob("part_*.b85"))
)

if not payload:
    raise SystemExit("No v7 source payload parts found.")

raw = gzip.decompress(base64.b85decode(payload.encode("ascii")))
sha = hashlib.sha256(raw).hexdigest()
if sha != EXPECTED_SHA256:
    raise SystemExit(f"Source checksum mismatch: {sha}")

OUT.write_bytes(raw)
print(f"Reconstructed {OUT.name} ({len(raw)} bytes, sha256={sha})")
