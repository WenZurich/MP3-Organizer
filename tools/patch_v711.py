from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'mp3_organizer_v7_1_0.py'
out = ROOT / 'mp3_organizer_v7_1_1.py'
s = src.read_text(encoding='utf-8')


def rep(old, new, n=1):
    global s
    if old not in s:
        raise SystemExit('MISSING:\n' + old[:500])
    s = s.replace(old, new, n)


rep('MP3 Organizer v7.1.0', 'MP3 Organizer v7.1.1', 1)
rep('APP_VERSION = "7.1.0"', 'APP_VERSION = "7.1.1"', 1)

# v7.1.0 trusted the preview-time audio_state during Apply. If that cached
# state was stale/missing, a disguised AAC/MP4 file could still receive new
# ID3 tags and a cover without ever being converted. v7.1.1 re-probes the
# actual bytes immediately before every Apply, converts when needed, and then
# verifies the resulting file again before any tags/covers are written.

anchor = '''def convert_to_compatible_mp3(path: Path):
'''
if anchor not in s:
    raise SystemExit('Could not locate convert_to_compatible_mp3')

# Insert a single authoritative helper just before file/cover planning.
planning_anchor = '# ============================================================\n# File / cover planning\n# ============================================================\n'
helper = r'''

def ensure_compatible_mp3(path: Path):
    """Re-probe the current file bytes and guarantee a real MPEG Layer III file.

    Returns (converted: bool, health: dict). This intentionally ignores any
    preview-time cached state so Apply is safe even when the file changed after
    preview or an older/stale plan is still in memory.
    """
    before = inspect_audio_health(path)
    if before.get("state") == "compatible":
        return False, before

    convert_to_compatible_mp3(path)
    after = inspect_audio_health(path)
    if after.get("state") != "compatible":
        raise RuntimeError(
            "Post-conversion verification failed: "
            + str(after.get("detail") or after.get("error") or after)
        )
    return True, after

'''
rep(planning_anchor, helper + planning_anchor, 1)

old_apply_start = '''            row_errors = []
            converted = False
            if row.get("audio_state") == "convert":
                try:
                    convert_to_compatible_mp3(p)
                    converted = True
                    row["audio_state"] = "compatible"
                    row["audio_format"] = "MP3"
                    row["audio_detail"] = "Converted to standard MP3"
                except Exception as e:
                    row_errors.append(f"Audio conversion: {e}")

            cover_bytes = None'''

new_apply_start = '''            row_errors = []
            converted = False
            try:
                # Never trust only the preview-time state. Inspect the actual
                # file again at the exact moment Apply begins for this track.
                converted, current_health = ensure_compatible_mp3(p)
                row["audio_state"] = current_health.get("state", "compatible")
                row["audio_format"] = current_health.get("format", "MP3")
                row["audio_detail"] = (
                    "Converted to standard MP3" if converted
                    else current_health.get("detail", "MP3")
                )
                row["audio_error"] = ""
            except Exception as e:
                row_errors.append(f"Audio compatibility: {e}")

            cover_bytes = None'''
rep(old_apply_start, new_apply_start, 1)

# Verify one final time after ID3 / APIC writes. A successful Apply must never
# report OK if the resulting bytes still are not a valid MP3.
status_anchor = '''            if row_errors:
                error_text = "; ".join(row_errors)
'''
final_verify = '''            if not row_errors:
                try:
                    final_health = inspect_audio_health(p)
                    if final_health.get("state") != "compatible":
                        raise RuntimeError(final_health.get("detail", "Not a valid MP3"))
                    row["audio_state"] = "compatible"
                    row["audio_format"] = "MP3"
                    if not converted:
                        row["audio_detail"] = final_health.get("detail", "MP3")
                except Exception as e:
                    row_errors.append(f"Post-apply MP3 verification: {e}")

            if row_errors:
                error_text = "; ".join(row_errors)
'''
rep(status_anchor, final_verify, 1)

old_result = '''            row_results.append({"status":status, "error":error_text, "repaired":repaired, "converted":converted})'''
new_result = '''            row_results.append({
                "status": status,
                "error": error_text,
                "repaired": repaired,
                "converted": converted,
                "audio_state": row.get("audio_state", ""),
                "audio_format": row.get("audio_format", ""),
                "audio_detail": row.get("audio_detail", ""),
            })'''
rep(old_result, new_result, 1)

old_done = '''            for i,rr in enumerate(d.get("row_results",[])):
                if i<len(self.plan): self.plan[i]["apply_status"]=rr.get("status","pending")'''
new_done = '''            for i,rr in enumerate(d.get("row_results",[])):
                if i < len(self.plan):
                    self.plan[i]["apply_status"] = rr.get("status", "pending")
                    if rr.get("audio_state"):
                        self.plan[i]["audio_state"] = rr.get("audio_state")
                    if rr.get("audio_format"):
                        self.plan[i]["audio_format"] = rr.get("audio_format")
                    if rr.get("audio_detail"):
                        self.plan[i]["audio_detail"] = rr.get("audio_detail")'''
rep(old_done, new_done, 1)

out.write_text(s, encoding='utf-8', newline='\n')
print(out, out.stat().st_size)
