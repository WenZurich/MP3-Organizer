from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'mp3_organizer_v7_1_1.py'
out = ROOT / 'mp3_organizer_v7_2_0.py'
s = src.read_text(encoding='utf-8')


def rep(old, new, n=1):
    global s
    if old not in s:
        raise SystemExit('MISSING:\n' + old[:500])
    s = s.replace(old, new, n)


rep('MP3 Organizer v7.1.1', 'MP3 Organizer v7.2.0', 1)
rep('- v7.1.0: Verifies that .mp3 files contain real MPEG Layer III audio and safely auto-converts disguised AAC/MP4, Opus/WebM and other decodable audio into standard MP3 before tags/covers are written.\n',
    '- v7.1.0: Verifies that .mp3 files contain real MPEG Layer III audio and safely auto-converts disguised AAC/MP4, Opus/WebM and other decodable audio into standard MP3 before tags/covers are written.\n- v7.2.0: Adds a fixed album-cover mode. Pick one JPG/PNG and the same front cover is embedded into every track so mobile players keep a stable album thumbnail when new songs are added.\n')
rep('APP_VERSION = "7.1.1"', 'APP_VERSION = "7.2.0"', 1)

# Cover-mode translations and generic cover wording.
for old, new in [
    ('"sources_desc": "選擇音樂與隨機封面來源。所有分析都在本機完成。",', '"sources_desc": "選擇音樂與封面來源。所有分析都在本機完成。",'),
    ('"cover_folder": "封面圖片資料夾",', '"cover_mode": "封面模式", "cover_mode_random": "每首隨機封面", "cover_mode_fixed": "固定整張專輯封面", "cover_folder": "封面圖片資料夾", "fixed_cover_file": "固定專輯封面", "fixed": "固定",'),
    ('"write_cover": "寫入隨機封面",', '"write_cover": "寫入封面",'),
    ('"cover_desc": "點選歌曲即可檢查它被分配到的封面。",', '"cover_desc": "點選歌曲即可檢查將寫入的封面。固定模式會讓整張專輯永遠使用同一張圖。",'),
    ('"col_album": "專輯", "col_confidence": "信心", "col_audio": "音訊相容性", "col_source": "判斷來源", "col_status": "狀態", "col_cover": "隨機封面",', '"col_album": "專輯", "col_confidence": "信心", "col_audio": "音訊相容性", "col_source": "判斷來源", "col_status": "狀態", "col_cover": "封面",'),
    ('"cover_folder_error": "你已開啟隨機封面，請先選擇有效的圖片資料夾。",', '"cover_folder_error": "你已開啟每首隨機封面，請先選擇有效的圖片資料夾。", "fixed_cover_error": "你已開啟固定整張專輯封面，請先選擇有效的 JPG / JPEG / PNG 圖片。",'),

    ('"sources": "音乐来源", "sources_desc": "选择音乐与随机封面来源。所有分析都在本机完成。",', '"sources": "音乐来源", "sources_desc": "选择音乐与封面来源。所有分析都在本机完成。",'),
    ('"cover_folder": "封面图片文件夹",', '"cover_mode": "封面模式", "cover_mode_random": "每首随机封面", "cover_mode_fixed": "固定整张专辑封面", "cover_folder": "封面图片文件夹", "fixed_cover_file": "固定专辑封面", "fixed": "固定",'),
    ('"write_cover": "写入随机封面",', '"write_cover": "写入封面",'),
    ('"cover": "封面", "selected_track": "当前歌曲", "cover_desc": "点选歌曲即可检查分配到的封面。",', '"cover": "封面", "selected_track": "当前歌曲", "cover_desc": "点选歌曲即可检查将写入的封面。固定模式会让整张专辑始终使用同一张图。",'),
    ('"col_old": "原文件名", "col_new": "新文件名", "col_artist": "歌手", "col_title": "歌名", "col_album": "专辑", "col_confidence": "信心", "col_audio": "音频兼容性", "col_source": "判断来源", "col_status": "状态", "col_cover": "随机封面",', '"col_old": "原文件名", "col_new": "新文件名", "col_artist": "歌手", "col_title": "歌名", "col_album": "专辑", "col_confidence": "信心", "col_audio": "音频兼容性", "col_source": "判断来源", "col_status": "状态", "col_cover": "封面",'),
    ('"cover_folder_error": "已开启随机封面，请先选择有效的图片文件夹。",', '"cover_folder_error": "已开启每首随机封面，请先选择有效的图片文件夹。", "fixed_cover_error": "已开启固定整张专辑封面，请先选择有效的 JPG / JPEG / PNG 图片。",'),

    ('"sources": "Music sources", "sources_desc": "Choose your music and random cover folders. All analysis stays on this computer.",', '"sources": "Music sources", "sources_desc": "Choose your music and cover source. All analysis stays on this computer.",'),
    ('"cover_folder": "Cover image folder",', '"cover_mode": "Cover mode", "cover_mode_random": "Random per track", "cover_mode_fixed": "Fixed album cover", "cover_folder": "Cover image folder", "fixed_cover_file": "Fixed album cover", "fixed": "Fixed",'),
    ('"write_cover": "Write random covers",', '"write_cover": "Write cover art",'),
    ('"cover": "Cover", "selected_track": "Selected track", "cover_desc": "Select a song to inspect its assigned cover.",', '"cover": "Cover", "selected_track": "Selected track", "cover_desc": "Select a song to inspect the cover that will be written. Fixed mode embeds the same image into every track.",'),
    ('"col_old": "Original", "col_new": "New filename", "col_artist": "Artist", "col_title": "Title", "col_album": "Album", "col_confidence": "Confidence", "col_audio": "Audio compatibility", "col_source": "Source", "col_status": "Status", "col_cover": "Random cover",', '"col_old": "Original", "col_new": "New filename", "col_artist": "Artist", "col_title": "Title", "col_album": "Album", "col_confidence": "Confidence", "col_audio": "Audio compatibility", "col_source": "Source", "col_status": "Status", "col_cover": "Cover",'),
    ('"cover_folder_error": "Random covers are enabled. Choose a valid image folder first.",', '"cover_folder_error": "Random-per-track covers are enabled. Choose a valid image folder first.", "fixed_cover_error": "Fixed album cover is enabled. Choose a valid JPG / JPEG / PNG image first.",'),

    ('"sources": "音楽ソース", "sources_desc": "MP3 とランダムジャケットのフォルダーを選択します。解析はすべてこのPC上で行います。",', '"sources": "音楽ソース", "sources_desc": "MP3 とジャケットのソースを選択します。解析はすべてこのPC上で行います。",'),
    ('"cover_folder": "ジャケット画像フォルダー",', '"cover_mode": "ジャケットモード", "cover_mode_random": "曲ごとにランダム", "cover_mode_fixed": "アルバム全体で固定", "cover_folder": "ジャケット画像フォルダー", "fixed_cover_file": "固定アルバムジャケット", "fixed": "固定",'),
    ('"write_cover": "ランダムジャケットを書き込む",', '"write_cover": "ジャケットを書き込む",'),
    ('"cover": "ジャケット", "selected_track": "選択中の曲", "cover_desc": "曲を選ぶと割り当てられたジャケットを確認できます。",', '"cover": "ジャケット", "selected_track": "選択中の曲", "cover_desc": "曲を選ぶと書き込まれるジャケットを確認できます。固定モードでは全曲に同じ画像を書き込みます。",'),
    ('"col_album": "アルバム", "col_confidence": "信頼度", "col_audio": "音声互換性", "col_source": "判定元", "col_status": "状態", "col_cover": "ランダムジャケット",', '"col_album": "アルバム", "col_confidence": "信頼度", "col_audio": "音声互換性", "col_source": "判定元", "col_status": "状態", "col_cover": "ジャケット",'),
    ('"cover_folder_error": "ランダムジャケットが有効です。有効な画像フォルダーを選んでください。",', '"cover_folder_error": "曲ごとのランダムジャケットが有効です。有効な画像フォルダーを選んでください。", "fixed_cover_error": "固定アルバムジャケットが有効です。有効な JPG / JPEG / PNG 画像を選んでください。",'),
]:
    rep(old, new)

# Preview planning: fixed mode assigns one image to every track.
rep('''        images = []
        if self.cfg.get("cover_enabled"):
            self.phase.emit("checking_covers")
            cf = Path(self.cfg["cover_folder"])
            images = list_images(cf, self.cfg.get("cover_recursive", False), self.cancel_event)
            if self.cancel_event.is_set():
                self.cancelled.emit()
                return
            if not images:
                raise RuntimeError("NO_IMAGES")
            assign_random_covers(plan, images)
''', '''        images = []
        if self.cfg.get("cover_enabled"):
            self.phase.emit("checking_covers")
            if self.cfg.get("cover_mode", "random") == "fixed":
                fixed = Path(self.cfg.get("fixed_cover", ""))
                if not fixed.is_file():
                    raise RuntimeError("FIXED_COVER_INVALID")
                try:
                    with Image.open(fixed) as im:
                        im.verify()
                except Exception:
                    raise RuntimeError("FIXED_COVER_INVALID")
                images = [fixed]
                for row in plan:
                    row["cover"] = fixed
            else:
                cf = Path(self.cfg["cover_folder"])
                images = list_images(cf, self.cfg.get("cover_recursive", False), self.cancel_event)
                if self.cancel_event.is_set():
                    self.cancelled.emit()
                    return
                if not images:
                    raise RuntimeError("NO_IMAGES")
                assign_random_covers(plan, images)
''')

# UI: add an explicit cover mode selector.
rep('''        sl.addWidget(self._divider())
        cover_title = QHBoxLayout()
''', '''        sl.addWidget(self._divider())
        self.labels["cover_mode"] = self._field_label()
        sl.addWidget(self.labels["cover_mode"])
        self.cover_mode_combo = QComboBox(); self.cover_mode_combo.setObjectName("field")
        self.cover_mode_combo.addItem("", "random"); self.cover_mode_combo.addItem("", "fixed")
        self.cover_mode_combo.currentIndexChanged.connect(self._cover_mode_changed)
        sl.addWidget(self.cover_mode_combo)
        cover_title = QHBoxLayout()
''')

rep('''        self.config_widgets = [
            self.folder_edit, self.folder_btn, self.cover_edit, self.cover_btn, self.album_edit,
            *[r for r in self.switch_rows.values()], self.lang_combo, self.theme_combo,
        ]
''', '''        self.config_widgets = [
            self.folder_edit, self.folder_btn, self.cover_mode_combo, self.cover_edit, self.cover_btn, self.album_edit,
            *[r for r in self.switch_rows.values()], self.lang_combo, self.theme_combo,
        ]
''')

# Keep independent paths for random-folder mode and fixed-image mode.
rep('''    def _restore_settings(self):
        self.folder_edit.setText(self.settings.value("mp3_folder", ""))
        self.cover_edit.setText(self.settings.value("cover_folder", ""))
        self.album_edit.setText(self.settings.value("album_name", "Between Departures"))
''', '''    def _restore_settings(self):
        self.folder_edit.setText(self.settings.value("mp3_folder", ""))
        self._random_cover_path = self.settings.value("cover_folder", "")
        self._fixed_cover_path = self.settings.value("fixed_cover_file", "")
        mode = self.settings.value("cover_mode", "random")
        if mode not in {"random", "fixed"}: mode = "random"
        self.cover_mode_combo.blockSignals(True)
        idx = self.cover_mode_combo.findData(mode); self.cover_mode_combo.setCurrentIndex(max(0, idx))
        self.cover_mode_combo.blockSignals(False)
        self._cover_mode_current = mode
        self.cover_edit.setText(self._fixed_cover_path if mode == "fixed" else self._random_cover_path)
        self.album_edit.setText(self.settings.value("album_name", "Between Departures"))
''')

rep('''        for key, default in defaults.items():
            val = self.settings.value(key, default)
            if isinstance(val, str): val = val.lower() in {"1","true","yes"}
            self.switch_rows[key].setChecked(bool(val))

    def _save_settings(self):
        self.settings.setValue("language", self.lang); self.settings.setValue("theme", self.theme_pref)
        self.settings.setValue("mp3_folder", self.folder_edit.text()); self.settings.setValue("cover_folder", self.cover_edit.text()); self.settings.setValue("album_name", self.album_edit.text())
''', '''        for key, default in defaults.items():
            val = self.settings.value(key, default)
            if isinstance(val, str): val = val.lower() in {"1","true","yes"}
            self.switch_rows[key].setChecked(bool(val))
        self._sync_cover_mode_ui()

    def _save_settings(self):
        self.settings.setValue("language", self.lang); self.settings.setValue("theme", self.theme_pref)
        mode = self.cover_mode_combo.currentData() or "random"
        if mode == "fixed": self._fixed_cover_path = self.cover_edit.text().strip()
        else: self._random_cover_path = self.cover_edit.text().strip()
        self.settings.setValue("cover_mode", mode)
        self.settings.setValue("mp3_folder", self.folder_edit.text()); self.settings.setValue("cover_folder", self._random_cover_path); self.settings.setValue("fixed_cover_file", self._fixed_cover_path); self.settings.setValue("album_name", self.album_edit.text())
''')

rep('''    def _system_theme_changed(self, *_):
''', '''    def _cover_mode_changed(self, index):
        if getattr(self, "_updating_cover_mode", False): return
        new_mode = self.cover_mode_combo.itemData(index) or "random"
        old_mode = getattr(self, "_cover_mode_current", None)
        current = self.cover_edit.text().strip()
        if old_mode == "fixed": self._fixed_cover_path = current
        elif old_mode == "random": self._random_cover_path = current
        self._cover_mode_current = new_mode
        self.cover_edit.setText(self._fixed_cover_path if new_mode == "fixed" else self._random_cover_path)
        self.settings.setValue("cover_mode", new_mode)
        self._sync_cover_mode_ui()

    def _sync_cover_mode_ui(self):
        if not hasattr(self, "cover_mode_combo"): return
        mode = self.cover_mode_combo.currentData() or getattr(self, "_cover_mode_current", "random") or "random"
        if "cover_folder" in self.labels:
            self.labels["cover_folder"].setText(self.tr("fixed_cover_file" if mode == "fixed" else "cover_folder"))
        if hasattr(self, "random_chip"):
            self.random_chip.setText(self.tr("fixed" if mode == "fixed" else "random").upper())
        row = self.switch_rows.get("include_cover_sub")
        if row is not None:
            row.setVisible(mode == "random")
        self.cover_edit.setToolTip(self.tr("fixed_cover_file" if mode == "fixed" else "cover_folder"))

    def _system_theme_changed(self, *_):
''')

rep('''        self.local_chip.setText(self.tr("local")); self.random_chip.setText(self.tr("random").upper()); self.compilation_chip.setText(self.tr("compilation").upper()); self.selected_chip.setText(self.tr("selected_track").upper())
''', '''        self.local_chip.setText(self.tr("local")); self.compilation_chip.setText(self.tr("compilation").upper()); self.selected_chip.setText(self.tr("selected_track").upper())
''')

rep('''        self._updating_combos = True
        self.lang_combo.blockSignals(True); self.lang_combo.clear()
''', '''        self._updating_cover_mode = True
        current_cover_mode = self.cover_mode_combo.currentData() or "random"
        self.cover_mode_combo.blockSignals(True); self.cover_mode_combo.clear()
        self.cover_mode_combo.addItem(self.tr("cover_mode_random"), "random"); self.cover_mode_combo.addItem(self.tr("cover_mode_fixed"), "fixed")
        idx = self.cover_mode_combo.findData(current_cover_mode); self.cover_mode_combo.setCurrentIndex(max(0,idx)); self.cover_mode_combo.blockSignals(False)
        self._cover_mode_current = current_cover_mode
        self._updating_cover_mode = False
        self._sync_cover_mode_ui()
        self._updating_combos = True
        self.lang_combo.blockSignals(True); self.lang_combo.clear()
''')

# Browse either a directory or one image depending on mode.
rep('''    def pick_cover_folder(self):
        if self.busy: return
        p = QFileDialog.getExistingDirectory(self, self.tr("cover_folder"), self.cover_edit.text() or str(Path.home()))
        if p: self.cover_edit.setText(p); self.settings.setValue("cover_folder", p); self.switch_rows["write_cover"].setChecked(True)
''', '''    def pick_cover_folder(self):
        if self.busy: return
        mode = self.cover_mode_combo.currentData() or "random"
        if mode == "fixed":
            start = self.cover_edit.text().strip() or str(Path.home())
            p, _ = QFileDialog.getOpenFileName(self, self.tr("fixed_cover_file"), start, "Images (*.jpg *.jpeg *.png)")
            if p:
                self._fixed_cover_path = p; self.cover_edit.setText(p); self.settings.setValue("fixed_cover_file", p); self.switch_rows["write_cover"].setChecked(True)
                self._show_cover(Path(p))
        else:
            p = QFileDialog.getExistingDirectory(self, self.tr("cover_folder"), self.cover_edit.text() or str(Path.home()))
            if p:
                self._random_cover_path = p; self.cover_edit.setText(p); self.settings.setValue("cover_folder", p); self.switch_rows["write_cover"].setChecked(True)
''')

# Preview validates the correct source and passes mode into the worker.
rep('''        if self.switch_rows["write_cover"].isChecked():
            c = Path(self.cover_edit.text().strip())
            if not c.is_dir():
                QMessageBox.critical(self, self.tr("err"), self.tr("cover_folder_error")); return
''', '''        cover_mode = self.cover_mode_combo.currentData() or "random"
        if self.switch_rows["write_cover"].isChecked():
            c = Path(self.cover_edit.text().strip())
            if cover_mode == "fixed":
                if not c.is_file() or c.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    QMessageBox.critical(self, self.tr("err"), self.tr("fixed_cover_error")); return
                try:
                    with Image.open(c) as im: im.verify()
                except Exception:
                    QMessageBox.critical(self, self.tr("err"), self.tr("fixed_cover_error")); return
            elif not c.is_dir():
                QMessageBox.critical(self, self.tr("err"), self.tr("cover_folder_error")); return
''', 1)

rep('''        cfg={"album":self.album_edit.text().strip() if self.switch_rows["unify_album"].isChecked() else "", "cover_enabled":self.switch_rows["write_cover"].isChecked(), "cover_folder":self.cover_edit.text().strip(), "cover_recursive":self.switch_rows["include_cover_sub"].isChecked()}
''', '''        cfg={"album":self.album_edit.text().strip() if self.switch_rows["unify_album"].isChecked() else "", "cover_enabled":self.switch_rows["write_cover"].isChecked(), "cover_mode":cover_mode, "cover_folder":self.cover_edit.text().strip() if cover_mode=="random" else self._random_cover_path, "fixed_cover":self.cover_edit.text().strip() if cover_mode=="fixed" else self._fixed_cover_path, "cover_recursive":self.switch_rows["include_cover_sub"].isChecked()}
''')

# Apply fixed mode authoritatively, even if the mode changed after Preview.
rep('''        for r in self.plan: r["album"]=album_name if self.switch_rows["unify_album"].isChecked() else ""
        self._save_settings(); self.progress.setValue(0); self.progress_label.setText(f"0 / {len(self.plan)}"); self.status_label.setText(self.tr("applying_all",n=len(self.plan))); self.detail_label.setText(self.tr("do_not_close")); self._set_busy(True,"apply")
''', '''        cover_mode = self.cover_mode_combo.currentData() or "random"
        fixed_cover = None
        if self.switch_rows["write_cover"].isChecked() and cover_mode == "fixed":
            fixed_cover = Path(self.cover_edit.text().strip())
            if not fixed_cover.is_file() or fixed_cover.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                QMessageBox.critical(self, self.tr("err"), self.tr("fixed_cover_error")); return
            try:
                with Image.open(fixed_cover) as im: im.verify()
            except Exception:
                QMessageBox.critical(self, self.tr("err"), self.tr("fixed_cover_error")); return
        for r in self.plan:
            r["album"]=album_name if self.switch_rows["unify_album"].isChecked() else ""
            if fixed_cover is not None: r["cover"] = fixed_cover
        self._save_settings(); self.progress.setValue(0); self.progress_label.setText(f"0 / {len(self.plan)}"); self.status_label.setText(self.tr("applying_all",n=len(self.plan))); self.detail_label.setText(self.tr("do_not_close")); self._set_busy(True,"apply")
''')

rep('''        if text=="NO_IMAGES": text=self.tr("no_images")
''', '''        if text=="NO_IMAGES": text=self.tr("no_images")
        if text=="FIXED_COVER_INVALID": text=self.tr("fixed_cover_error")
''')

out.write_text(s, encoding='utf-8', newline='\n')
print(out, out.stat().st_size)
