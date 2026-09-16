from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'mp3_organizer_v7_2_1.py'
out = ROOT / 'mp3_organizer_v7_3_0.py'
s = src.read_text(encoding='utf-8')


def rep(old, new, n=1):
    global s
    if old not in s:
        raise SystemExit('MISSING: ' + old[:180])
    s = s.replace(old, new, n)


def span(start, end, new):
    global s
    a = s.find(start)
    if a < 0:
        raise SystemExit('MISSING START: ' + start[:120])
    b = s.find(end, a)
    if b < 0:
        raise SystemExit('MISSING END: ' + end[:120])
    if new.endswith(end):
        new = new[:-len(end)]
    s = s[:a] + new + s[b:]


rep('MP3 Organizer v7.2.1', 'MP3 Organizer v7.3.0', 1)
rep('APP_VERSION = "7.2.1"', 'APP_VERSION = "7.3.0"', 1)
rep(
    '- v7.2.1: Fixes disguised MP4/AAC files that Mutagen could falsely recognize as MP3 because MPEG-like bytes appeared later in the payload. Container signatures now take precedence over heuristic MP3 parsing, and leading ID3 is stripped before decoding disguised containers.\n',
    '- v7.2.1: Fixes disguised MP4/AAC files that Mutagen could falsely recognize as MP3 because MPEG-like bytes appeared later in the payload. Container signatures now take precedence over heuristic MP3 parsing, and leading ID3 is stripped before decoding disguised containers.\n'
    '- v7.3.0: Separates per-track embedded artwork from album-level artwork. Songs keep different covers while a selected image becomes albumart.jpg beside the album. The sidebar cover controls were rebuilt for Windows HiDPI.\n',
)

# External album artwork helper: creates albumart.jpg atomically and never touches APIC.
needle = '        return out.getvalue(), "image/jpeg"\n\n\n\n\n\n# ============================================================\n# Audio compatibility / health\n'
helper = '''        return out.getvalue(), "image/jpeg"\n\n\ndef write_albumart_file(image_path: Path, folder: Path, max_side=1600, quality=94):\n    image_path = Path(image_path)\n    folder = Path(folder)\n    if not image_path.is_file():\n        raise RuntimeError("Album artwork source does not exist")\n    folder.mkdir(parents=True, exist_ok=True)\n    target = folder / "albumart.jpg"\n    tmp = folder / f".albumart.{uuid.uuid4().hex}.tmp.jpg"\n    try:\n        with Image.open(image_path) as img:\n            img.load()\n            img = ImageOps.exif_transpose(img)\n            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):\n                rgba = img.convert("RGBA")\n                bg = Image.new("RGB", rgba.size, (255, 255, 255))\n                bg.paste(rgba, mask=rgba.getchannel("A"))\n                img = bg\n            else:\n                img = img.convert("RGB")\n            img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)\n            img.save(tmp, "JPEG", quality=quality, optimize=True, progressive=False)\n        os.replace(tmp, target)\n        with Image.open(target) as check:\n            check.verify()\n        return target\n    finally:\n        try:\n            if tmp.exists(): tmp.unlink()\n        except Exception:\n            pass\n\n\n# ============================================================\n# Audio compatibility / health\n'''
rep(needle, helper)

# Override old fixed-cover wording without rewriting the large language table.
lang_patch = '''\n# v7.3.0 wording: track artwork and album artwork are independent.\nT["zh_TW"].update({\n    "sources_desc":"選擇 MP3 與每首歌曲的封面來源。所有分析都在本機完成。",\n    "cover_folder":"歌曲封面圖片資料夾", "cover_desc":"點選歌曲即可檢查該歌曲自己的內嵌封面。專輯封面不會覆蓋這裡。",\n    "cover_folder_error":"你已開啟歌曲封面，請先選擇有效的圖片資料夾。",\n    "album_art_file":"專輯封面", "album_art_desc":"只建立 albumart.jpg，不覆蓋任何歌曲自己的內嵌封面。Gramophone 會用它固定專輯縮圖。",\n    "album_art_clear":"清除", "album_art_error":"請選擇有效的 JPG / JPEG / PNG 專輯封面圖片。",\n})\nT["zh_CN"].update({\n    "sources_desc":"选择 MP3 与每首歌曲的封面来源。所有分析都在本机完成。",\n    "cover_folder":"歌曲封面图片文件夹", "cover_desc":"点选歌曲即可检查该歌曲自己的内嵌封面。专辑封面不会覆盖这里。",\n    "cover_folder_error":"已开启歌曲封面，请先选择有效的图片文件夹。",\n    "album_art_file":"专辑封面", "album_art_desc":"只创建 albumart.jpg，不覆盖任何歌曲自己的内嵌封面。Gramophone 会用它固定专辑缩略图。",\n    "album_art_clear":"清除", "album_art_error":"请选择有效的 JPG / JPEG / PNG 专辑封面图片。",\n})\nT["en"].update({\n    "sources_desc":"Choose the MP3 folder and per-track artwork source. All analysis stays on this computer.",\n    "cover_folder":"Track artwork folder", "cover_desc":"Select a song to inspect that track's own embedded artwork. Album artwork never replaces it.",\n    "cover_folder_error":"Track artwork is enabled. Choose a valid image folder first.",\n    "album_art_file":"Album artwork", "album_art_desc":"Creates albumart.jpg only. It never replaces embedded artwork inside individual tracks. Gramophone uses it for a stable album tile.",\n    "album_art_clear":"Clear", "album_art_error":"Choose a valid JPG / JPEG / PNG album artwork image.",\n})\nT["ja"].update({\n    "sources_desc":"MP3 と各曲のジャケット画像ソースを選択します。解析はすべてこのPC上で行います。",\n    "cover_folder":"曲ごとのジャケット画像フォルダー", "cover_desc":"曲を選ぶと、その曲自身に埋め込まれるジャケットを確認できます。アルバムジャケットは上書きしません。",\n    "cover_folder_error":"曲ごとのジャケットが有効です。有効な画像フォルダーを選んでください。",\n    "album_art_file":"アルバムジャケット", "album_art_desc":"albumart.jpg だけを作成し、各曲に埋め込まれたジャケットは変更しません。Gramophone のアルバム画像を固定できます。",\n    "album_art_clear":"クリア", "album_art_error":"有効な JPG / JPEG / PNG のアルバムジャケットを選択してください。",\n})\n\n'''
rep('\nclass ToggleSwitch(QCheckBox):\n', lang_patch + 'class ToggleSwitch(QCheckBox):\n')

# Make switch rows line up cleanly at 125/150/200% Windows scaling.
rep('''        lay = QHBoxLayout(self)\n        lay.setContentsMargins(0, 4, 0, 4)\n        lay.setSpacing(12)\n        self.label = QLabel(text)\n        self.label.setObjectName("switchText")\n        self.label.setWordWrap(True)\n        lay.addWidget(self.label, 1)\n''', '''        self.setMinimumHeight(34)\n        lay = QHBoxLayout(self)\n        lay.setContentsMargins(0, 5, 0, 5)\n        lay.setSpacing(12)\n        self.label = QLabel(text)\n        self.label.setObjectName("switchText")\n        self.label.setWordWrap(True)\n        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)\n        lay.addWidget(self.label, 1)\n''')
rep('        sidebar.setFixedWidth(365)\n', '        sidebar.setFixedWidth(405)\n')
rep('self.folder_btn = QPushButton(); self.folder_btn.setObjectName("secondaryButton"); self.folder_btn.clicked.connect(self.pick_folder)', 'self.folder_btn = QPushButton(); self.folder_btn.setObjectName("secondaryButton"); self.folder_btn.setMinimumWidth(78); self.folder_btn.clicked.connect(self.pick_folder)')

# Sources card: remove the bad mode dropdown; this area only controls per-track artwork.
span(
    '        self.switch_rows["include_mp3_sub"] = SwitchRow(checked=False)\n',
    '        # Album card\n',
'''        self.switch_rows["include_mp3_sub"] = SwitchRow(checked=False)\n        sl.addWidget(self.switch_rows["include_mp3_sub"])\n        sl.addWidget(self._divider())\n        cover_title = QHBoxLayout(); cover_title.setSpacing(8)\n        self.labels["cover_folder"] = self._field_label()\n        cover_title.addWidget(self.labels["cover_folder"]); cover_title.addStretch(1)\n        self.random_chip = QLabel(); self.random_chip.setObjectName("accentChip"); cover_title.addWidget(self.random_chip)\n        sl.addLayout(cover_title)\n        coverrow = QHBoxLayout(); coverrow.setSpacing(8)\n        self.cover_edit = QLineEdit(); self.cover_edit.setObjectName("field")\n        self.cover_btn = QPushButton(); self.cover_btn.setObjectName("secondaryButton"); self.cover_btn.setMinimumWidth(78); self.cover_btn.clicked.connect(self.pick_cover_folder)\n        coverrow.addWidget(self.cover_edit, 1); coverrow.addWidget(self.cover_btn)\n        sl.addLayout(coverrow)\n        self.switch_rows["include_cover_sub"] = SwitchRow(checked=False)\n        sl.addWidget(self.switch_rows["include_cover_sub"])\n        side.addWidget(sources)\n\n        # Album card\n''')

# Album card gets its own albumart.jpg selector, visually separate from song covers.
span(
    '        # Album card\n',
    '        # Options card\n',
'''        # Album card\n        album_card = self._card()\n        al = QVBoxLayout(album_card); al.setContentsMargins(18,17,18,17); al.setSpacing(10)\n        album_head = QHBoxLayout()\n        self.labels["album"] = self._section_label(); album_head.addWidget(self.labels["album"]); album_head.addStretch(1)\n        self.compilation_chip = QLabel(); self.compilation_chip.setObjectName("successChip"); album_head.addWidget(self.compilation_chip)\n        al.addLayout(album_head)\n        self.labels["album_desc"] = self._desc_label(); al.addWidget(self.labels["album_desc"])\n        self.labels["album_name"] = self._field_label(); al.addWidget(self.labels["album_name"])\n        self.album_edit = QLineEdit(); self.album_edit.setObjectName("field"); al.addWidget(self.album_edit)\n        self.switch_rows["unify_album"] = SwitchRow(checked=True); al.addWidget(self.switch_rows["unify_album"])\n        al.addWidget(self._divider())\n        art_head = QHBoxLayout(); art_head.setSpacing(8)\n        self.labels["album_art_file"] = self._field_label(); art_head.addWidget(self.labels["album_art_file"]); art_head.addStretch(1)\n        self.album_art_chip = QLabel("ALBUMART.JPG"); self.album_art_chip.setObjectName("successChip"); art_head.addWidget(self.album_art_chip)\n        al.addLayout(art_head)\n        art_row = QHBoxLayout(); art_row.setSpacing(8)\n        self.album_art_edit = QLineEdit(); self.album_art_edit.setObjectName("field"); self.album_art_edit.setReadOnly(True)\n        self.album_art_btn = QPushButton(); self.album_art_btn.setObjectName("secondaryButton"); self.album_art_btn.setMinimumWidth(78); self.album_art_btn.clicked.connect(self.pick_album_art)\n        self.album_art_clear_btn = QPushButton(); self.album_art_clear_btn.setObjectName("secondaryButton"); self.album_art_clear_btn.setMinimumWidth(62); self.album_art_clear_btn.clicked.connect(self.clear_album_art)\n        art_row.addWidget(self.album_art_edit, 1); art_row.addWidget(self.album_art_btn); art_row.addWidget(self.album_art_clear_btn)\n        al.addLayout(art_row)\n        self.labels["album_art_desc"] = self._desc_label(); self.labels["album_art_desc"].setWordWrap(True); al.addWidget(self.labels["album_art_desc"])\n        side.addWidget(album_card)\n\n        # Options card\n''')

rep('''        self.config_widgets = [\n            self.folder_edit, self.folder_btn, self.cover_mode_combo, self.cover_edit, self.cover_btn, self.album_edit,\n            *[r for r in self.switch_rows.values()], self.lang_combo, self.theme_combo,\n        ]\n''', '''        self.config_widgets = [\n            self.folder_edit, self.folder_btn, self.cover_edit, self.cover_btn, self.album_edit,\n            self.album_art_edit, self.album_art_btn, self.album_art_clear_btn,\n            *[r for r in self.switch_rows.values()], self.lang_combo, self.theme_combo,\n        ]\n''')

# Preview always uses different per-track covers; album art never enters row["cover"].
span(
    '        images = []\n        if self.cfg.get("cover_enabled"):\n',
    '        self.finished_data.emit({\n            "kind": "preview",\n',
'''        images = []\n        if self.cfg.get("cover_enabled"):\n            self.phase.emit("checking_covers")\n            cf = Path(self.cfg["cover_folder"])\n            images = list_images(cf, self.cfg.get("cover_recursive", False), self.cancel_event)\n            if self.cancel_event.is_set():\n                self.cancelled.emit()\n                return\n            if not images:\n                raise RuntimeError("NO_IMAGES")\n            assign_random_covers(plan, images)\n\n        self.finished_data.emit({\n            "kind": "preview",\n''')

# Worker writes albumart.jpg after MP3 work/renaming, independently of embedded covers.
rep('''        log = Path(self.cfg["folder"]) / f"mp3_organizer_v{APP_VERSION.replace('.', '_')}_log.csv"\n''', '''        album_art_written = ""\n        if self.cfg.get("album_art_file"):\n            try:\n                album_art_written = str(write_albumart_file(Path(self.cfg["album_art_file"]), Path(self.cfg["folder"])))\n            except Exception as e:\n                errors.append(f"Album artwork: {e}")\n\n        log = Path(self.cfg["folder"]) / f"mp3_organizer_v{APP_VERSION.replace('.', '_')}_log.csv"\n''', 1)
rep('''            "rename_error":rename_error,\n''', '''            "rename_error":rename_error, "album_art_written":album_art_written,\n''', 1)

# Persistent settings: independent paths, no mode state.
span(
    '    def _restore_settings(self):\n',
    '    def _system_theme_changed(self, *_):\n',
'''    def _restore_settings(self):\n        self.folder_edit.setText(self.settings.value("mp3_folder", ""))\n        self.cover_edit.setText(self.settings.value("cover_folder", ""))\n        self.album_art_edit.setText(self.settings.value("album_art_file", ""))\n        self.album_edit.setText(self.settings.value("album_name", "Between Departures"))\n        defaults = {"include_mp3_sub":False, "include_cover_sub":False, "unify_album":True, "rename":True, "write_tags":True, "write_cover":True}\n        for key, default in defaults.items():\n            val = self.settings.value(key, default)\n            if isinstance(val, str): val = val.lower() in {"1","true","yes"}\n            self.switch_rows[key].setChecked(bool(val))\n\n    def _save_settings(self):\n        self.settings.setValue("language", self.lang); self.settings.setValue("theme", self.theme_pref)\n        self.settings.setValue("mp3_folder", self.folder_edit.text()); self.settings.setValue("cover_folder", self.cover_edit.text())\n        self.settings.setValue("album_art_file", self.album_art_edit.text()); self.settings.setValue("album_name", self.album_edit.text())\n        for key,row in self.switch_rows.items(): self.settings.setValue(key, row.isChecked())\n        self.settings.sync()\n\n    def _system_theme_changed(self, *_):\n''')

# Translation refresh: no cover-mode combo; add album art buttons.
span(
    '        self.folder_btn.setText(self.tr("browse")); self.cover_btn.setText(self.tr("browse")); self.preview_btn.setText(self.tr("preview")); self.apply_btn.setText(self.tr("apply")); self.stop_btn.setText(self.tr("stop"))\n',
    '        self._updating_combos = True\n',
'''        self.folder_btn.setText(self.tr("browse")); self.cover_btn.setText(self.tr("browse")); self.album_art_btn.setText(self.tr("browse")); self.album_art_clear_btn.setText(self.tr("album_art_clear"))\n        self.preview_btn.setText(self.tr("preview")); self.apply_btn.setText(self.tr("apply")); self.stop_btn.setText(self.tr("stop")); self.random_chip.setText(self.tr("random").upper())\n        self._updating_combos = True\n''')

# Cover pickers are independent.
span(
    '    def pick_cover_folder(self):\n',
    '    def _set_busy(self, busy, kind=None):\n',
'''    def pick_cover_folder(self):\n        if self.busy: return\n        p = QFileDialog.getExistingDirectory(self, self.tr("cover_folder"), self.cover_edit.text() or str(Path.home()))\n        if p:\n            self.cover_edit.setText(p); self.settings.setValue("cover_folder", p); self.switch_rows["write_cover"].setChecked(True)\n\n    def pick_album_art(self):\n        if self.busy: return\n        start = self.album_art_edit.text().strip() or self.folder_edit.text().strip() or str(Path.home())\n        p, _ = QFileDialog.getOpenFileName(self, self.tr("album_art_file"), start, "Images (*.jpg *.jpeg *.png)")\n        if p:\n            try:\n                with Image.open(p) as im: im.verify()\n            except Exception:\n                QMessageBox.critical(self, self.tr("err"), self.tr("album_art_error")); return\n            self.album_art_edit.setText(p); self.settings.setValue("album_art_file", p)\n\n    def clear_album_art(self):\n        if self.busy: return\n        self.album_art_edit.clear(); self.settings.remove("album_art_file")\n\n    def _set_busy(self, busy, kind=None):\n''')

# Preview validation/config.
span(
    '        cover_mode = self.cover_mode_combo.currentData() or "random"\n',
    '        self.worker=TaskThread("preview", files=files, cfg=cfg, cancel_event=self.cancel_event, parent=self)\n',
'''        if self.switch_rows["write_cover"].isChecked():\n            if not Path(self.cover_edit.text().strip()).is_dir():\n                QMessageBox.critical(self, self.tr("err"), self.tr("cover_folder_error")); return\n        self._save_settings(); self.cancel_event.clear(); self.progress.setValue(0); self.progress_label.setText(f"0 / {len(files)}")\n        self.status_label.setText(self.tr("analyzing_all", n=len(files))); self.detail_label.setText(self.tr("background_ok")); self._set_busy(True,"preview")\n        cfg={"album":self.album_edit.text().strip() if self.switch_rows["unify_album"].isChecked() else "", "cover_enabled":self.switch_rows["write_cover"].isChecked(), "cover_folder":self.cover_edit.text().strip(), "cover_recursive":self.switch_rows["include_cover_sub"].isChecked()}\n        self.worker=TaskThread("preview", files=files, cfg=cfg, cancel_event=self.cancel_event, parent=self)\n''')

# Apply validation/config: album art is an external image, never row["cover"].
span(
    '        cover_mode = self.cover_mode_combo.currentData() or "random"\n',
    '        self.worker=TaskThread("apply",plan=[dict(r) for r in self.plan],cfg=cfg,parent=self)\n',
'''        album_art_file = self.album_art_edit.text().strip()\n        if album_art_file:\n            art = Path(album_art_file)\n            if not art.is_file() or art.suffix.lower() not in {".jpg", ".jpeg", ".png"}:\n                QMessageBox.critical(self, self.tr("err"), self.tr("album_art_error")); return\n            try:\n                with Image.open(art) as im: im.verify()\n            except Exception:\n                QMessageBox.critical(self, self.tr("err"), self.tr("album_art_error")); return\n        for r in self.plan:\n            r["album"] = album_name if self.switch_rows["unify_album"].isChecked() else ""\n        self._save_settings(); self.progress.setValue(0); self.progress_label.setText(f"0 / {len(self.plan)}"); self.status_label.setText(self.tr("applying_all",n=len(self.plan))); self.detail_label.setText(self.tr("do_not_close")); self._set_busy(True,"apply")\n        cfg={"album_name":album_name,"write_artist_title":self.switch_rows["write_tags"].isChecked(),"write_album":self.switch_rows["unify_album"].isChecked(),"cover":self.switch_rows["write_cover"].isChecked(),"rename":self.switch_rows["rename"].isChecked(),"folder":self.folder_edit.text().strip(),"album_art_file":album_art_file}\n        self.worker=TaskThread("apply",plan=[dict(r) for r in self.plan],cfg=cfg,parent=self)\n''')

rep('        if text=="FIXED_COVER_INVALID": text=self.tr("fixed_cover_error")\n', '')

out.write_text(s, encoding='utf-8', newline='\n')
print(out, out.stat().st_size)
