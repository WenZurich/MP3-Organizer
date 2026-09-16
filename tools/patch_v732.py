from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'mp3_organizer_v7_3_1.py'
out = ROOT / 'mp3_organizer_v7_3_2.py'
s = src.read_text(encoding='utf-8')


def rep(old, new, n=1):
    global s
    if old not in s:
        raise SystemExit('MISSING: ' + old[:260])
    s = s.replace(old, new, n)

rep('MP3 Organizer v7.3.1', 'MP3 Organizer v7.3.2', 1)
rep('APP_VERSION = "7.3.1"', 'APP_VERSION = "7.3.2"', 1)
rep(
    '- v7.3.1: Rebuilds sidebar field geometry for Windows HiDPI/text scaling: inputs no longer clip vertically, long paths open from the beginning, and album-art actions use a separate row instead of squeezing the path field.\n',
    '- v7.3.1: Rebuilds sidebar field geometry for Windows HiDPI/text scaling: inputs no longer clip vertically, long paths open from the beginning, and album-art actions use a separate row instead of squeezing the path field.\n'
    '- v7.3.2: Fixes the remaining sidebar compression bug. The settings column is now a proper scroll area with minimum-size cards, wrapped descriptions reserve their real text height, and album controls can no longer overlap at Windows 125/150/200% scaling.\n',
    1,
)

rep(
    '        Qt, Signal, QThread, QSettings, QSize, QRectF, Property,\n',
    '        Qt, Signal, QThread, QSettings, QSize, QRect, QRectF, Property,\n',
    1,
)
rep(
    '        QSizePolicy, QGraphicsDropShadowEffect, QCheckBox,\n',
    '        QSizePolicy, QGraphicsDropShadowEffect, QCheckBox, QScrollArea, QLayout,\n',
    1,
)

old = '''        sidebar = QWidget()\n        sidebar.setFixedWidth(420)\n        side = QVBoxLayout(sidebar)\n        side.setContentsMargins(0, 0, 0, 0)\n        side.setSpacing(12)\n        main.addWidget(sidebar)\n\n        workspace = QWidget()\n'''
new = '''        self.sidebar_scroll = QScrollArea()\n        self.sidebar_scroll.setObjectName("sidebarScroll")\n        self.sidebar_scroll.setWidgetResizable(True)\n        self.sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)\n        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)\n        self.sidebar_scroll.setFrameShape(QFrame.Shape.NoFrame)\n        self.sidebar_scroll.setFixedWidth(444)\n        self.sidebar_content = QWidget()\n        self.sidebar_content.setObjectName("sidebarContent")\n        self.sidebar_content.setMinimumWidth(420)\n        side = QVBoxLayout(self.sidebar_content)\n        side.setContentsMargins(0, 0, 8, 2)\n        side.setSpacing(12)\n        side.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)\n        self.sidebar_scroll.setWidget(self.sidebar_content)\n        main.addWidget(self.sidebar_scroll)\n\n        workspace = QWidget()\n'''
rep(old, new, 1)

rep('        side.addWidget(options)\n        side.addStretch(1)\n', '        side.addWidget(options)\n        side.addSpacing(2)\n', 1)

rep(
    '        al = QVBoxLayout(album_card); al.setContentsMargins(20,19,20,19); al.setSpacing(11)\n',
    '        al = QVBoxLayout(album_card); al.setContentsMargins(20,19,20,21); al.setSpacing(14)\n',
    1,
)
rep(
    '        ol = QVBoxLayout(options); ol.setContentsMargins(20,19,20,19); ol.setSpacing(9)\n',
    '        ol = QVBoxLayout(options); ol.setContentsMargins(20,19,20,21); ol.setSpacing(11)\n',
    1,
)

rep(
    '    def _desc_label(self):\n        x = QLabel(); x.setObjectName("muted"); x.setWordWrap(True); return x\n',
    '''    def _desc_label(self):\n        x = QLabel(); x.setObjectName("muted"); x.setWordWrap(True)\n        x.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)\n        x.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)\n        return x\n\n    def _refresh_sidebar_text_geometry(self):\n        if not hasattr(self, "sidebar_content"):\n            return\n        content_w = self.sidebar_content.width() or 420\n        text_w = max(260, content_w - 48)\n        for key in ("sources_desc", "album_desc", "album_art_desc", "options_desc", "workflow_hint"):\n            label = self.labels.get(key)\n            if label is None:\n                continue\n            rect = label.fontMetrics().boundingRect(\n                QRect(0, 0, text_w, 10000),\n                Qt.TextFlag.TextWordWrap | Qt.TextFlag.AlignLeft,\n                label.text(),\n            )\n            label.setMinimumHeight(max(24, rect.height() + 6))\n            label.updateGeometry()\n        self.sidebar_content.updateGeometry()\n''',
    1,
)

rep(
    '        app.setStyleSheet(qss)\n        # Update card shadows for the active theme.\n',
    '        app.setStyleSheet(qss)\n        QTimer.singleShot(0, self._refresh_sidebar_text_geometry)\n        # Update card shadows for the active theme.\n',
    1,
)
rep(
    '        self._update_cover_display()\n\n    def _set_headers(self):\n',
    '        self._update_cover_display()\n        QTimer.singleShot(0, self._refresh_sidebar_text_geometry)\n\n    def _set_headers(self):\n',
    1,
)

rep(
    '        QWidget#root {{ background: {c[\'bg\']}; color: {c[\'text\']}; }}\n',
    '''        QWidget#root {{ background: {c['bg']}; color: {c['text']}; }}\n        QScrollArea#sidebarScroll {{ background: transparent; border: none; }}\n        QWidget#sidebarContent {{ background: transparent; }}\n''',
    1,
)
rep(
    '        QScrollBar:vertical {{ background: transparent; width: 9px; margin: 4px 2px; }}\n',
    '        QScrollBar:vertical {{ background: transparent; width: 7px; margin: 5px 1px; }}\n',
    1,
)

out.write_text(s, encoding='utf-8', newline='\n')
print(out, out.stat().st_size)
