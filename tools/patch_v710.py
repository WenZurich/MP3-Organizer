from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'mp3_organizer_v7_0_1.py'
out = ROOT / 'mp3_organizer_v7_1_0.py'
s = src.read_text(encoding='utf-8')

def rep(old, new, n=1):
    global s
    if old not in s:
        raise SystemExit('MISSING:\n' + old[:300])
    s = s.replace(old, new, n)

rep('MP3 Organizer v7.0.0', 'MP3 Organizer v7.1.0', 1)
rep('- v7.0.0: Rebuilt UI in PySide6 with true rounded cards/controls, persistent Light/Dark/System themes, and live Traditional Chinese / Simplified Chinese / English / Japanese language switching.\n',
    '- v7.0.0: Rebuilt UI in PySide6 with true rounded cards/controls, persistent Light/Dark/System themes, and live Traditional Chinese / Simplified Chinese / English / Japanese language switching.\n- v7.1.0: Verifies that .mp3 files contain real MPEG Layer III audio and safely auto-converts disguised AAC/MP4, Opus/WebM and other decodable audio into standard MP3 before tags/covers are written.\n')
rep('py -m pip install mutagen pillow PySide6', 'py -m pip install mutagen pillow PySide6 imageio-ffmpeg')
rep('import ctypes\n', 'import ctypes\nimport os\nimport shutil\nimport subprocess\nimport uuid\n', 1)
rep('    from mutagen.easyid3 import EasyID3\n', '    from mutagen.easyid3 import EasyID3\n    from mutagen.mp3 import MP3, HeaderNotFoundError\n', 1)
rep('raise SystemExit("Run:\\npy -m pip install mutagen pillow PySide6")', 'raise SystemExit("Run:\\npy -m pip install mutagen pillow PySide6 imageio-ffmpeg")')
rep('APP_VERSION = "7.0.1"', 'APP_VERSION = "7.1.0"', 1)

health = r'''
# ============================================================
# Audio compatibility / health
# ============================================================

def _id3v2_payload_offset(path: Path) -> int:
    """Byte offset immediately after a leading ID3v2 tag, if present."""
    try:
        with path.open("rb") as f:
            head = f.read(10)
        if len(head) >= 10 and head[:3] == b"ID3":
            size_bytes = head[6:10]
            if all((b & 0x80) == 0 for b in size_bytes):
                size = ((size_bytes[0] & 0x7F) << 21) | ((size_bytes[1] & 0x7F) << 14) | ((size_bytes[2] & 0x7F) << 7) | (size_bytes[3] & 0x7F)
                footer = 10 if (head[5] & 0x10) else 0
                return 10 + size + footer
    except Exception:
        pass
    return 0


def sniff_audio_container(path: Path) -> str:
    """Best-effort signature check when the file cannot be parsed as MP3."""
    try:
        offset = _id3v2_payload_offset(path)
        with path.open("rb") as f:
            f.seek(offset)
            data = f.read(65536)
    except Exception:
        return "Unknown audio"

    if len(data) >= 12 and data[4:8] == b"ftyp" or b"ftyp" in data[:64]:
        return "MP4 / M4A (AAC)"
    if data.startswith(b"OggS"):
        return "Ogg / Opus or Vorbis"
    if data.startswith(b"fLaC"):
        return "FLAC"
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WAVE":
        return "WAV"
    if data.startswith(b"\x1a\x45\xdf\xa3"):
        return "WebM / Matroska"
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xF6) == 0xF0:
        return "AAC (ADTS)"
    return "Unknown / damaged audio"


def inspect_audio_health(path: Path):
    """Verify that a .mp3 really contains MPEG Layer III audio."""
    try:
        audio = MP3(path)
        length = float(getattr(audio.info, "length", 0.0) or 0.0)
        bitrate = int(getattr(audio.info, "bitrate", 0) or 0)
        sample_rate = int(getattr(audio.info, "sample_rate", 0) or 0)
        if length <= 0:
            raise HeaderNotFoundError("MP3 duration is zero")
        detail = "MP3"
        if sample_rate:
            detail += f" · {sample_rate/1000:g} kHz"
        if bitrate:
            detail += f" · {round(bitrate/1000)} kbps"
        return {"state":"compatible", "format":"MP3", "detail":detail, "length":length}
    except Exception as exc:
        fmt = sniff_audio_container(path)
        return {"state":"convert", "format":fmt, "detail":f"Not a valid MP3 · {fmt}", "length":0.0, "error":str(exc)}


def get_ffmpeg_exe() -> str:
    """Use the FFmpeg executable bundled with the official Windows build."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).is_file():
            return exe
    except Exception:
        pass
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    raise RuntimeError("FFmpeg is unavailable. Reinstall the official MP3 Organizer build.")


def convert_to_compatible_mp3(path: Path):
    """
    Decode a disguised/non-MP3 file and atomically replace it with standard MP3.
    The original file stays untouched unless the new MP3 passes verification.
    """
    ffmpeg = get_ffmpeg_exe()
    tmp = path.with_name(f".{path.stem}.mp3organizer-{uuid.uuid4().hex}.mp3")
    startupinfo = None
    creationflags = 0
    if sys.platform == "win32":
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        except Exception:
            startupinfo = None
            creationflags = 0
    cmd = [
        ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(path), "-map", "0:a:0", "-vn", "-map_metadata", "-1",
        "-c:a", "libmp3lame", "-q:a", "2", "-id3v2_version", "3", str(tmp),
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, errors="replace", startupinfo=startupinfo,
                              creationflags=creationflags)
        if proc.returncode != 0 or not tmp.is_file() or tmp.stat().st_size < 1024:
            detail = (proc.stderr or "FFmpeg conversion failed").strip()
            raise RuntimeError(detail[-900:])
        check = MP3(tmp)
        length = float(getattr(check.info, "length", 0.0) or 0.0)
        if length <= 0:
            raise RuntimeError("Converted file did not contain valid MP3 audio.")
        os.replace(tmp, path)
        return length
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass

'''
rep('# ============================================================\n# File / cover planning\n# ============================================================\n', health + '# ============================================================\n# File / cover planning\n# ============================================================\n', 1)

rep('''            identified = smart_identify(p)\n            plan.append({\n                "old": p,\n                "artist": identified["artist"],\n                "title": identified["title"],\n                "album": self.cfg.get("album", ""),\n                "score": identified["score"],\n                "source": identified["source"],\n                "review": identified["review"],\n                "apply_status": "pending",\n                "cover": None,\n            })''',
'''            identified = smart_identify(p)\n            health = inspect_audio_health(p)\n            plan.append({\n                "old": p,\n                "artist": identified["artist"],\n                "title": identified["title"],\n                "album": self.cfg.get("album", ""),\n                "score": identified["score"],\n                "source": identified["source"],\n                "review": identified["review"],\n                "apply_status": "pending",\n                "cover": None,\n                "audio_state": health["state"],\n                "audio_format": health["format"],\n                "audio_detail": health["detail"],\n                "audio_error": health.get("error", ""),\n            })''')

rep('''            row_errors = []\n            cover_bytes = None''',
'''            row_errors = []\n            converted = False\n            if row.get("audio_state") == "convert":\n                try:\n                    convert_to_compatible_mp3(p)\n                    converted = True\n                    row["audio_state"] = "compatible"\n                    row["audio_format"] = "MP3"\n                    row["audio_detail"] = "Converted to standard MP3"\n                except Exception as e:\n                    row_errors.append(f"Audio conversion: {e}")\n\n            cover_bytes = None''')

rep('''            repaired = False\n            repair_reason = ""\n            if self.cfg.get("write_artist_title") or self.cfg.get("write_album") or cover_bytes is not None:\n                try:''',
'''            repaired = False\n            repair_reason = ""\n            if not row_errors and (self.cfg.get("write_artist_title") or self.cfg.get("write_album") or cover_bytes is not None):\n                try:''')

rep('''            if row_errors:\n                error_text = "; ".join(row_errors)\n                errors.append(f"{p.name}: {error_text}")\n                status = "problem"\n            elif repaired:\n                status = "repaired"\n                error_text = repair_reason\n            else:\n                status = "ok"\n                error_text = ""\n            row_results.append({"status":status, "error":error_text, "repaired":repaired})''',
'''            if row_errors:\n                error_text = "; ".join(row_errors)\n                errors.append(f"{p.name}: {error_text}")\n                status = "problem"\n            elif converted and repaired:\n                status = "converted_repaired"\n                error_text = repair_reason\n            elif converted:\n                status = "converted"\n                error_text = ""\n            elif repaired:\n                status = "repaired"\n                error_text = repair_reason\n            else:\n                status = "ok"\n                error_text = ""\n            row_results.append({"status":status, "error":error_text, "repaired":repaired, "converted":converted})''')

rep('w.writerow(["old", "new", "artist", "title", "album", "confidence", "source", "cover", "status", "error"])',
    'w.writerow(["old", "new", "artist", "title", "album", "confidence", "audio", "source", "cover", "status", "error"])')
rep('''                    round(r["score"], 4), r["source"], str(r["cover"]) if r.get("cover") else "",\n                    rr.get("status", ""), rr.get("error", ""),''',
'''                    round(r["score"], 4), r.get("audio_detail", ""), r["source"], str(r["cover"]) if r.get("cover") else "",\n                    rr.get("status", ""), rr.get("error", ""),''')

for old, new in [
('"col_album": "專輯", "col_confidence": "信心", "col_source": "判斷來源", "col_status": "狀態", "col_cover": "隨機封面",', '"col_album": "專輯", "col_confidence": "信心", "col_audio": "音訊相容性", "col_source": "判斷來源", "col_status": "狀態", "col_cover": "隨機封面",'),
('"status_pending": "待套用", "status_ok": "✓ 已套用", "status_repaired": "✓ 已套用（ID3 已修復）", "status_problem": "⚠ 有問題",', '"status_pending": "待套用", "status_ok": "✓ 已套用", "status_repaired": "✓ 已套用（ID3 已修復）", "status_converted": "✓ 已轉為標準 MP3", "status_converted_repaired": "✓ 已轉 MP3 + 修復 ID3", "status_problem": "⚠ 有問題", "audio_ok": "✓ 標準 MP3", "audio_convert": "⚠ 將自動轉換：{fmt}",'),
('"col_album": "专辑", "col_confidence": "信心", "col_source": "判断来源", "col_status": "状态", "col_cover": "随机封面",', '"col_album": "专辑", "col_confidence": "信心", "col_audio": "音频兼容性", "col_source": "判断来源", "col_status": "状态", "col_cover": "随机封面",'),
('"status_pending": "待应用", "status_ok": "✓ 已应用", "status_repaired": "✓ 已应用（ID3 已修复）", "status_problem": "⚠ 有问题",', '"status_pending": "待应用", "status_ok": "✓ 已应用", "status_repaired": "✓ 已应用（ID3 已修复）", "status_converted": "✓ 已转为标准 MP3", "status_converted_repaired": "✓ 已转 MP3 + 修复 ID3", "status_problem": "⚠ 有问题", "audio_ok": "✓ 标准 MP3", "audio_convert": "⚠ 将自动转换：{fmt}",'),
('"col_album": "Album", "col_confidence": "Confidence", "col_source": "Source", "col_status": "Status", "col_cover": "Random cover",', '"col_album": "Album", "col_confidence": "Confidence", "col_audio": "Audio compatibility", "col_source": "Source", "col_status": "Status", "col_cover": "Random cover",'),
('"status_pending": "Pending", "status_ok": "✓ Applied", "status_repaired": "✓ Applied (ID3 repaired)", "status_problem": "⚠ Issue",', '"status_pending": "Pending", "status_ok": "✓ Applied", "status_repaired": "✓ Applied (ID3 repaired)", "status_converted": "✓ Converted to standard MP3", "status_converted_repaired": "✓ Converted + ID3 repaired", "status_problem": "⚠ Issue", "audio_ok": "✓ Standard MP3", "audio_convert": "⚠ Will convert: {fmt}",'),
('"col_album": "アルバム", "col_confidence": "信頼度", "col_source": "判定元", "col_status": "状態", "col_cover": "ランダムジャケット",', '"col_album": "アルバム", "col_confidence": "信頼度", "col_audio": "音声互換性", "col_source": "判定元", "col_status": "状態", "col_cover": "ランダムジャケット",'),
('"status_pending": "適用待ち", "status_ok": "✓ 適用済み", "status_repaired": "✓ 適用済み（ID3 修復）", "status_problem": "⚠ 問題あり",', '"status_pending": "適用待ち", "status_ok": "✓ 適用済み", "status_repaired": "✓ 適用済み（ID3 修復）", "status_converted": "✓ 標準 MP3 に変換済み", "status_converted_repaired": "✓ MP3 変換 + ID3 修復", "status_problem": "⚠ 問題あり", "audio_ok": "✓ 標準 MP3", "audio_convert": "⚠ 自動変換：{fmt}",'),
]:
    rep(old, new)

rep('黃色列代表資訊不足；點「信心」可集中檢查。雙擊歌手 / 歌名可手動修正。','黃色列代表命名資訊不足；點「信心」可集中檢查。音訊相容性也會驗證，假 MP3 會在套用時安全轉為標準 MP3。')
rep('黄色行代表信息不足；点“信心”可集中检查。双击歌手 / 歌名可手动修正。','黄色行代表命名信息不足；点“信心”可集中检查。音频兼容性也会验证，伪 MP3 会在应用时安全转为标准 MP3。')
rep('Yellow rows need review. Click Confidence to group them; double-click Artist / Title to edit.','Yellow rows need naming review. Audio compatibility is verified too; disguised MP3 files are safely converted to standard MP3 during Apply.')
rep('黄色行は要確認です。「信頼度」をクリックしてまとめ、Artist / Title をダブルクリックして修正できます。','黄色行は命名の要確認です。音声互換性も検証し、偽装 MP3 は適用時に安全な標準 MP3 へ変換します。')

rep('self.table = SmoothTableWidget(0, 9)', 'self.table = SmoothTableWidget(0, 10)')
rep('widths = [285,285,170,220,190,92,205,155,165]', 'widths = [285,285,170,220,190,92,205,205,155,165]')
rep('keys = ["col_old","col_new","col_artist","col_title","col_album","col_confidence","col_source","col_status","col_cover"]', 'keys = ["col_old","col_new","col_artist","col_title","col_album","col_confidence","col_audio","col_source","col_status","col_cover"]')
rep('status_key={"pending":"status_pending","ok":"status_ok","repaired":"status_repaired","problem":"status_problem","待套用":"status_pending"}', 'status_key={"pending":"status_pending","ok":"status_ok","repaired":"status_repaired","converted":"status_converted","converted_repaired":"status_converted_repaired","problem":"status_problem","待套用":"status_pending"}')
rep('''            values=[r["old"].name,r["new"].name,r.get("artist",""),r.get("title",""),r.get("album",""),f"{round(r.get('score',0)*100)}%",src,stat,r["cover"].name if r.get("cover") else ""]''', '''            audio_text = self.tr("audio_ok") if r.get("audio_state")=="compatible" else self.tr("audio_convert",fmt=r.get("audio_format","Unknown"))\n            values=[r["old"].name,r["new"].name,r.get("artist",""),r.get("title",""),r.get("album",""),f"{round(r.get('score',0)*100)}%",audio_text,src,stat,r["cover"].name if r.get("cover") else ""]''')
rep('''            if r.get("apply_status")=="problem":\n                self.table.item(row_no,7).setForeground(QColor(c["danger"]))\n            elif r.get("apply_status") in {"ok","repaired"}:\n                self.table.item(row_no,7).setForeground(QColor(c["success"]))''', '''            if r.get("audio_state")=="convert":\n                self.table.item(row_no,6).setForeground(QColor(c["warning"]))\n            else:\n                self.table.item(row_no,6).setForeground(QColor(c["success"]))\n            if r.get("apply_status")=="problem":\n                self.table.item(row_no,8).setForeground(QColor(c["danger"]))\n            elif r.get("apply_status") in {"ok","repaired","converted","converted_repaired"}:\n                self.table.item(row_no,8).setForeground(QColor(c["success"]))''')

out.write_text(s, encoding='utf-8', newline='\n')
print(out, out.stat().st_size)
