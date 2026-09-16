from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'mp3_organizer_v7_2_0.py'
out = ROOT / 'mp3_organizer_v7_2_1.py'
s = src.read_text(encoding='utf-8')


def rep(old, new, n=1):
    global s
    if old not in s:
        raise SystemExit('MISSING:\n' + old[:500])
    s = s.replace(old, new, n)


rep('MP3 Organizer v7.2.0', 'MP3 Organizer v7.2.1', 1)
rep('APP_VERSION = "7.2.0"', 'APP_VERSION = "7.2.1"', 1)
rep(
    '- v7.2.0: Adds a fixed album-cover mode. Pick one JPG/PNG and the same front cover is embedded into every track so mobile players keep a stable album thumbnail when new songs are added.\n',
    '- v7.2.0: Adds a fixed album-cover mode. Pick one JPG/PNG and the same front cover is embedded into every track so mobile players keep a stable album thumbnail when new songs are added.\n'
    '- v7.2.1: Fixes disguised MP4/AAC files that Mutagen could falsely recognize as MP3 because MPEG-like bytes appeared later in the payload. Container signatures now take precedence over heuristic MP3 parsing.\n',
    1,
)

old = '''def inspect_audio_health(path: Path):
    """Verify that a .mp3 really contains MPEG Layer III audio."""
    try:
        audio = MP3(path)
'''
new = '''def inspect_audio_health(path: Path):
    """Verify that a .mp3 really contains MPEG Layer III audio.

    Important: check strong container signatures before asking Mutagen to scan
    for MPEG frames. A file such as ID3 + MP4/AAC can contain byte patterns
    later in the payload that look like MPEG sync words; Mutagen may then
    return an MP3 object even though the real container is MP4. Android players
    correctly reject those files. Strong non-MP3 signatures therefore win.
    """
    signature_format = sniff_audio_container(path)
    if signature_format in {
        "MP4 / M4A (AAC)",
        "Ogg / Opus or Vorbis",
        "FLAC",
        "WAV",
        "WebM / Matroska",
        "AAC (ADTS)",
    }:
        return {
            "state": "convert",
            "format": signature_format,
            "detail": f"Not a valid MP3 · {signature_format}",
            "length": 0.0,
            "error": "Strong non-MP3 container signature detected",
        }

    try:
        audio = MP3(path)
'''
rep(old, new, 1)

out.write_text(s, encoding='utf-8', newline='\n')
print(out, out.stat().st_size)
