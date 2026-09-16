from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "src_payload_v7"
OUT = ROOT / "mp3_organizer_v7_0_1.py"
EXPECTED_BASE_SHA256 = "e723acd53bedb8c9b07f070bff62c63c8adda9e91656fd16e78662561ea0cce4"

payload = "".join(
    p.read_text(encoding="ascii").strip()
    for p in sorted(PARTS.glob("part_*.b85"))
)

if not payload:
    raise SystemExit("No v7 source payload parts found.")

raw = gzip.decompress(base64.b85decode(payload.encode("ascii")))
sha = hashlib.sha256(raw).hexdigest()
if sha != EXPECTED_BASE_SHA256:
    raise SystemExit(f"Base source checksum mismatch: {sha}")

source = raw.decode("utf-8")
source = source.replace('APP_VERSION = "7.0.0"', 'APP_VERSION = "7.0.1"', 1)

smooth_table = r'''class SmoothTableWidget(QTableWidget):
    """Wide metadata table tuned for trackpads and smooth horizontal movement."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The important UX fix: map scrollbar values to pixels, not whole columns.
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.horizontalScrollBar().setSingleStep(12)
        self.verticalScrollBar().setSingleStep(16)
        self.horizontalScrollBar().setTracking(True)
        self.verticalScrollBar().setTracking(True)

        # Discrete Shift+mouse-wheel movement gets a short eased glide. Precision
        # touchpads keep Qt/Windows' native pixelDelta path for natural scrolling.
        self._h_anim = QPropertyAnimation(self.horizontalScrollBar(), b"value", self)
        self._h_anim.setDuration(145)
        self._h_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def wheelEvent(self, event):
        pixel = event.pixelDelta()
        if not pixel.isNull():
            return super().wheelEvent(event)

        angle = event.angleDelta()
        delta = angle.x()
        if not delta and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            delta = angle.y()
        if not delta:
            return super().wheelEvent(event)

        bar = self.horizontalScrollBar()
        if bar.maximum() <= bar.minimum():
            return super().wheelEvent(event)

        if self._h_anim.state() == QPropertyAnimation.State.Running:
            try:
                base = int(self._h_anim.endValue())
            except Exception:
                base = bar.value()
            self._h_anim.stop()
        else:
            base = bar.value()

        movement = int(round((-delta / 120.0) * 84.0))
        target = max(bar.minimum(), min(bar.maximum(), base + movement))
        self._h_anim.setStartValue(bar.value())
        self._h_anim.setEndValue(target)
        self._h_anim.start()
        event.accept()


'''

main_window_anchor = "class MainWindow(QMainWindow):\n"
if main_window_anchor not in source:
    raise SystemExit("Could not locate MainWindow anchor for v7.0.1 patch.")
source = source.replace(main_window_anchor, smooth_table + main_window_anchor, 1)

old_constructor = "self.table = QTableWidget(0, 9)"
if old_constructor not in source:
    raise SystemExit("Could not locate preview table constructor for v7.0.1 patch.")
source = source.replace(old_constructor, "self.table = SmoothTableWidget(0, 9)", 1)

old_scroll_qss = """QScrollBar:vertical {{ background: transparent; width: 12px; margin: 3px; }}
        QScrollBar::handle:vertical {{ background: {c['muted2']}; border-radius: 4px; min-height: 28px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 3px; }}
        QScrollBar::handle:horizontal {{ background: {c['muted2']}; border-radius: 4px; min-width: 28px; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}"""
new_scroll_qss = """QScrollBar:vertical {{ background: transparent; width: 9px; margin: 4px 2px; }}
        QScrollBar::handle:vertical {{ background: {c['muted2']}; border-radius: 3px; min-height: 44px; }}
        QScrollBar::handle:vertical:hover {{ background: {c['muted']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        QScrollBar:horizontal {{ background: transparent; height: 9px; margin: 2px 8px 3px 8px; }}
        QScrollBar::handle:horizontal {{ background: {c['muted2']}; border-radius: 3px; min-width: 56px; }}
        QScrollBar::handle:horizontal:hover {{ background: {c['muted']}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}"""
if old_scroll_qss not in source:
    raise SystemExit("Could not locate scrollbar style block for v7.0.1 patch.")
source = source.replace(old_scroll_qss, new_scroll_qss, 1)

OUT.write_text(source, encoding="utf-8", newline="\n")
out_sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
print(f"Reconstructed and patched {OUT.name} ({OUT.stat().st_size} bytes, sha256={out_sha})")
