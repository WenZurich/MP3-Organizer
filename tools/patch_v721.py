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
    '- v7.2.1: Fixes disguised MP4/AAC files that Mutagen could falsely recognize as MP3 because MPEG-like bytes appeared later in the payload. Container signatures now take precedence over heuristic MP3 parsing, and leading ID3 is stripped before decoding disguised containers.\n',
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

# If the organizer previously wrote an ID3v2 tag in front of a disguised
# MP4/AAC/WebM/etc file, feeding the hybrid directly to FFmpeg can fail because
# the foreign container's internal byte offsets no longer line up. Decode from
# a temporary copy that starts at the real container payload instead.
old_convert = '''    cmd = [
        ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(path), "-map", "0:a:0", "-vn", "-map_metadata", "-1",
        "-c:a", "libmp3lame", "-q:a", "2", "-id3v2_version", "3", str(tmp),
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, errors="replace", startupinfo=startupinfo,
                              creationflags=creationflags)
'''
new_convert = '''    decode_path = path
    stripped_input = None
    signature_format = sniff_audio_container(path)
    id3_offset = _id3v2_payload_offset(path)
    if id3_offset > 0 and signature_format in {
        "MP4 / M4A (AAC)", "Ogg / Opus or Vorbis", "FLAC", "WAV",
        "WebM / Matroska", "AAC (ADTS)",
    }:
        suffix_map = {
            "MP4 / M4A (AAC)": ".m4a",
            "Ogg / Opus or Vorbis": ".ogg",
            "FLAC": ".flac",
            "WAV": ".wav",
            "WebM / Matroska": ".webm",
            "AAC (ADTS)": ".aac",
        }
        stripped_input = path.with_name(
            f".{path.stem}.mp3organizer-input-{uuid.uuid4().hex}{suffix_map.get(signature_format, '.bin')}"
        )
        with path.open("rb") as src, stripped_input.open("wb") as dst:
            src.seek(id3_offset)
            shutil.copyfileobj(src, dst, length=1024 * 1024)
        decode_path = stripped_input

    cmd = [
        ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(decode_path), "-map", "0:a:0", "-vn", "-map_metadata", "-1",
        "-c:a", "libmp3lame", "-q:a", "2", "-id3v2_version", "3", str(tmp),
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, errors="replace", startupinfo=startupinfo,
                              creationflags=creationflags)
'''
rep(old_convert, new_convert, 1)

old_finally = '''    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
'''
new_finally = '''    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
        try:
            if stripped_input is not None and stripped_input.exists():
                stripped_input.unlink()
        except Exception:
            pass
'''
rep(old_finally, new_finally, 1)

out.write_text(s, encoding='utf-8', newline='\n')
print(out, out.stat().st_size)
