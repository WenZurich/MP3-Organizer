from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'mp3_organizer_v7_3_0.py'
out = ROOT / 'mp3_organizer_v7_3_1.py'
s = src.read_text(encoding='utf-8')


def rep(old, new, n=1):
    global s
    if old not in s:
        raise SystemExit('MISSING: ' + old[:240])
    s = s.replace(old, new, n)


rep('MP3 Organizer v7.3.0', 'MP3 Organizer v7.3.1', 1)
rep('APP_VERSION = "7.3.0"', 'APP_VERSION = "7.3.1"', 1)
rep(
    '- v7.3.0: Separates per-track embedded artwork from album-level artwork. Songs keep different covers while a selected image becomes albumart.jpg beside the album. The sidebar cover controls were rebuilt for Windows HiDPI.\n',
    '- v7.3.0: Separates per-track embedded artwork from album-level artwork. Songs keep different covers while a selected image becomes albumart.jpg beside the album. The sidebar cover controls were rebuilt for Windows HiDPI.\n'
    '- v7.3.1: Rebuilds sidebar field geometry for Windows HiDPI/text scaling: inputs no longer clip vertically, long paths open from the beginning, and album-art actions use a separate row instead of squeezing the path field.\n',
    1,
)

# Give the sidebar a touch more room without starving the preview workspace.
rep('        sidebar.setFixedWidth(405)\n', '        sidebar.setFixedWidth(420)\n', 1)

# Album artwork: full-width path on its own row, actions below. This avoids the
# three-control squeeze visible at 125/150/200% Windows scaling.
old = '''        art_row = QHBoxLayout(); art_row.setSpacing(8)\n        self.album_art_edit = QLineEdit(); self.album_art_edit.setObjectName("field"); self.album_art_edit.setReadOnly(True)\n        self.album_art_btn = QPushButton(); self.album_art_btn.setObjectName("secondaryButton"); self.album_art_btn.setMinimumWidth(78); self.album_art_btn.clicked.connect(self.pick_album_art)\n        self.album_art_clear_btn = QPushButton(); self.album_art_clear_btn.setObjectName("secondaryButton"); self.album_art_clear_btn.setMinimumWidth(62); self.album_art_clear_btn.clicked.connect(self.clear_album_art)\n        art_row.addWidget(self.album_art_edit, 1); art_row.addWidget(self.album_art_btn); art_row.addWidget(self.album_art_clear_btn)\n        al.addLayout(art_row)\n'''
new = '''        self.album_art_edit = QLineEdit(); self.album_art_edit.setObjectName("field"); self.album_art_edit.setReadOnly(True)\n        al.addWidget(self.album_art_edit)\n        art_actions = QHBoxLayout(); art_actions.setSpacing(8); art_actions.addStretch(1)\n        self.album_art_btn = QPushButton(); self.album_art_btn.setObjectName("secondaryButton"); self.album_art_btn.setMinimumWidth(92); self.album_art_btn.clicked.connect(self.pick_album_art)\n        self.album_art_clear_btn = QPushButton(); self.album_art_clear_btn.setObjectName("secondaryButton"); self.album_art_clear_btn.setMinimumWidth(78); self.album_art_clear_btn.clicked.connect(self.clear_album_art)\n        art_actions.addWidget(self.album_art_btn); art_actions.addWidget(self.album_art_clear_btn)\n        al.addLayout(art_actions)\n'''
rep(old, new, 1)

# Use robust control heights instead of vertical stylesheet padding. Qt's
# padding + point fonts can clip line-edit text under Windows text scaling.
rep(
    '''        QLineEdit#field {{ background: {c['field']}; color: {c['text']}; border: 1px solid {c['border']}; border-radius: 12px; padding: 9px 11px; selection-background-color: {c['accent']}; }}\n''',
    '''        QLineEdit#field {{ background: {c['field']}; color: {c['text']}; border: 1px solid {c['border']}; border-radius: 13px; padding: 0px 13px; min-height: 42px; selection-background-color: {c['accent']}; }}\n''',
    1,
)
rep(
    '''        QPushButton {{ border-radius: 12px; padding: 9px 16px; font-weight: 650; min-height: 20px; }}\n''',
    '''        QPushButton {{ border-radius: 13px; padding: 0px 16px; font-weight: 650; min-height: 42px; }}\n''',
    1,
)
rep(
    '''        QComboBox#pillCombo {{ background: {c['surface']}; color: {c['text2']}; border: 1px solid {c['border']}; border-radius: 12px; padding: 8px 28px 8px 12px; min-height: 20px; }}\n''',
    '''        QComboBox#pillCombo {{ background: {c['surface']}; color: {c['text2']}; border: 1px solid {c['border']}; border-radius: 13px; padding: 0px 30px 0px 12px; min-height: 42px; }}\n''',
    1,
)

# Make the two source browse buttons the same comfortable size.
rep('self.folder_btn.setMinimumWidth(78)', 'self.folder_btn.setMinimumWidth(92)', 1)
rep('self.cover_btn.setMinimumWidth(78)', 'self.cover_btn.setMinimumWidth(92)', 1)

# Long saved paths should open at the start rather than auto-scrolling to the end.
rep(
    '''        self.album_edit.setText(self.settings.value("album_name", "Between Departures"))\n        defaults = {"include_mp3_sub":False, "include_cover_sub":False, "unify_album":True, "rename":True, "write_tags":True, "write_cover":True}\n''',
    '''        self.album_edit.setText(self.settings.value("album_name", "Between Departures"))\n        for edit in (self.folder_edit, self.cover_edit, self.album_art_edit, self.album_edit):\n            edit.setCursorPosition(0)\n        defaults = {"include_mp3_sub":False, "include_cover_sub":False, "unify_album":True, "rename":True, "write_tags":True, "write_cover":True}\n''',
    1,
)
rep(
    '''        if p: self.folder_edit.setText(p); self.settings.setValue("mp3_folder", p)\n''',
    '''        if p:\n            self.folder_edit.setText(p); self.folder_edit.setCursorPosition(0); self.settings.setValue("mp3_folder", p)\n''',
    1,
)
rep(
    '''            self.cover_edit.setText(p); self.settings.setValue("cover_folder", p); self.switch_rows["write_cover"].setChecked(True)\n''',
    '''            self.cover_edit.setText(p); self.cover_edit.setCursorPosition(0); self.settings.setValue("cover_folder", p); self.switch_rows["write_cover"].setChecked(True)\n''',
    1,
)
rep(
    '''            self.album_art_edit.setText(p); self.settings.setValue("album_art_file", p)\n''',
    '''            self.album_art_edit.setText(p); self.album_art_edit.setCursorPosition(0); self.album_art_edit.setToolTip(p); self.settings.setValue("album_art_file", p)\n''',
    1,
)

# Slightly roomier cards and rows, particularly for Traditional Chinese text.
rep('sl.setContentsMargins(18, 17, 18, 17)\n        sl.setSpacing(9)', 'sl.setContentsMargins(20, 19, 20, 19)\n        sl.setSpacing(10)', 1)
rep('al = QVBoxLayout(album_card); al.setContentsMargins(18,17,18,17); al.setSpacing(10)', 'al = QVBoxLayout(album_card); al.setContentsMargins(20,19,20,19); al.setSpacing(11)', 1)
rep('ol = QVBoxLayout(options); ol.setContentsMargins(18,17,18,17); ol.setSpacing(8)', 'ol = QVBoxLayout(options); ol.setContentsMargins(20,19,20,19); ol.setSpacing(9)', 1)

out.write_text(s, encoding='utf-8', newline='\n')
print(out, out.stat().st_size)
