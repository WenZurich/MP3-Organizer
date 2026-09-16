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

SMOOTH_SCROLL_PATCH = r'''
# ============================================================
# v7.0.1 UX patch: precision / inertial-feeling table scrolling
# ============================================================
# QAbstractItemView defaults can scroll horizontally one column/item at a time.
# That feels jerky in a wide metadata table.  Configure every item view for
# pixel-accurate scrolling and add a short eased animation for discrete
# Shift+mouse-wheel horizontal scrolling. Precision touchpads keep Qt's native
# pixelDelta path, so their OS-level smooth/natural scrolling is not disturbed.
try:
    from PySide6.QtCore import QObject, QEvent, Qt, QPropertyAnimation, QEasingCurve
    from PySide6.QtWidgets import QApplication, QAbstractItemView

    class _MP3OrgSmoothScrollFilter(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._animations = {}

        @staticmethod
        def _view_for(widget):
            current = widget
            while current is not None:
                if isinstance(current, QAbstractItemView):
                    return current
                try:
                    current = current.parentWidget()
                except Exception:
                    return None
            return None

        def eventFilter(self, obj, event):
            if event.type() != QEvent.Type.Wheel:
                return False

            view = self._view_for(obj)
            if view is None:
                return False

            # Let Windows/Qt handle precision-touchpad pixel deltas natively.
            # ScrollPerPixel below makes those gestures genuinely smooth.
            pixel = event.pixelDelta()
            if not pixel.isNull():
                return False

            angle = event.angleDelta()
            shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            horizontal_delta = angle.x()
            if not horizontal_delta and shift:
                horizontal_delta = angle.y()
            if not horizontal_delta:
                return False

            bar = view.horizontalScrollBar()
            if bar is None or bar.maximum() <= bar.minimum():
                return False

            # Accumulate repeated wheel notches against the animation target,
            # instead of restarting from a stale value and feeling sticky.
            key = id(bar)
            anim = self._animations.get(key)
            if anim is not None and anim.state() == QPropertyAnimation.State.Running:
                try:
                    base = int(anim.endValue())
                except Exception:
                    base = bar.value()
            else:
                base = bar.value()

            # One wheel notch ~= 84 px: quick enough for wide tables, still precise.
            pixels = int(round((-horizontal_delta / 120.0) * 84.0))
            target = max(bar.minimum(), min(bar.maximum(), base + pixels))
            if target == bar.value() and (anim is None or anim.state() != QPropertyAnimation.State.Running):
                return True

            if anim is None:
                anim = QPropertyAnimation(bar, b"value", bar)
                anim.setDuration(150)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                self._animations[key] = anim
            else:
                anim.stop()

            anim.setStartValue(bar.value())
            anim.setEndValue(target)
            anim.start()
            event.accept()
            return True

    def _mp3org_install_smooth_scrolling(app):
        scroll_filter = _MP3OrgSmoothScrollFilter(app)
        app._mp3org_smooth_scroll_filter = scroll_filter
        app.installEventFilter(scroll_filter)

        for view in app.allWidgets():
            if not isinstance(view, QAbstractItemView):
                continue
            # Critical fix: scrollbar position maps to pixels, not columns/rows.
            view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

            hbar = view.horizontalScrollBar()
            vbar = view.verticalScrollBar()
            if hbar is not None:
                hbar.setSingleStep(14)
                hbar.setPageStep(max(160, int(view.viewport().width() * 0.62)))
                hbar.setTracking(True)
            if vbar is not None:
                vbar.setSingleStep(18)
                vbar.setTracking(True)

    _mp3org_original_qapp_exec = QApplication.exec

    def _mp3org_qapp_exec_with_smooth_scroll(*_args, **_kwargs):
        app = QApplication.instance()
        if app is not None and not hasattr(app, "_mp3org_smooth_scroll_filter"):
            _mp3org_install_smooth_scrolling(app)
        # PySide6 exposes exec as a static callable; call it without a bound self.
        return _mp3org_original_qapp_exec()

    QApplication.exec = _mp3org_qapp_exec_with_smooth_scroll
except Exception:
    # UX enhancement must never prevent the organizer from launching.
    pass
'''

marker = 'if __name__ == "__main__":'
if marker not in source:
    raise SystemExit("Could not locate application entry point for v7.0.1 UX patch.")
source = source.replace(marker, SMOOTH_SCROLL_PATCH + "\n\n" + marker, 1)

OUT.write_text(source, encoding="utf-8", newline="\n")
out_sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
print(f"Reconstructed and patched {OUT.name} ({OUT.stat().st_size} bytes, sha256={out_sha})")
