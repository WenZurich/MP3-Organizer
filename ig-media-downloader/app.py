# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gallery_dl import config, job

APP = "IG Media Downloader"
VIDEO_EXTS = {"mp4", "mov", "webm", "m4v", "mkv", "avi"}
IMAGE_EXTS = {"jpg", "jpeg", "png", "webp", "gif", "avif", "heic"}


def data_dir():
    p = Path(os.environ.get("APPDATA", Path.home())) / "IG-Media-Downloader"
    p.mkdir(parents=True, exist_ok=True)
    return p


SETTINGS = data_dir() / "settings.json"


def load_settings():
    d = {"folder": str(Path.home() / "Downloads" / "Instagram"), "cookie": "Chrome", "cookie_file": ""}
    try:
        if SETTINGS.exists():
            d.update(json.loads(SETTINGS.read_text(encoding="utf-8")))
    except Exception:
        pass
    return d


def save_settings(d):
    try:
        SETTINGS.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def valid_url(raw):
    raw = raw.strip()
    if not raw:
        raise ValueError("請貼上 Instagram 連結")
    if not re.match(r"^https?://", raw, re.I):
        raw = "https://" + raw
    host = urlparse(raw).netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    if host != "instagram.com" and not host.endswith(".instagram.com"):
        raise ValueError("目前只接受 instagram.com 連結")
    return raw


class ProgressDownloadJob(job.DownloadJob):
    callback = None
    total_hint = 0
    def __init__(self, url, parent=None):
        super().__init__(url, parent)
        self.n = 0
    def handle_url(self, url, kwdict):
        self.n += 1
        if self.callback:
            self.callback(self.n, max(self.total_hint, self.n), kwdict)
        return super().handle_url(url, kwdict)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.title("IG Media Downloader 1.0")
        self.geometry("900x680")
        self.minsize(780, 600)
        self.media_urls = []
        self.media_meta = []
        self.current_url = ""
        self.busy = False
        self._style()
        self._ui()

    def _style(self):
        s = ttk.Style(self)
        if "vista" in s.theme_names():
            s.theme_use("vista")
        s.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
        s.configure("Sub.TLabel", font=("Segoe UI", 10))
        s.configure("TButton", font=("Segoe UI", 10), padding=8)
        s.configure("TLabel", font=("Segoe UI", 10))

    def _ui(self):
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(7, weight=1)

        ttk.Label(root, text="Instagram 媒體下載器", style="Title.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(root, text="整頁解析完成後，一次下載該 URL 中全部可存取的照片與影片", style="Sub.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(2,18))

        ttk.Label(root, text="Instagram URL").grid(row=2, column=0, columnspan=4, sticky="w")
        self.url = ttk.Entry(root)
        self.url.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5,14), ipady=7)
        ttk.Button(root, text="貼上", command=self.paste).grid(row=3, column=2, padx=(8,4), pady=(5,14))
        self.analyze_btn = ttk.Button(root, text="解析整頁", command=self.analyze)
        self.analyze_btn.grid(row=3, column=3, padx=(4,0), pady=(5,14))
        self.url.bind("<Return>", lambda e: self.analyze())

        ttk.Label(root, text="下載到").grid(row=4, column=0, sticky="w")
        self.folder = ttk.Entry(root)
        self.folder.insert(0, self.settings["folder"])
        self.folder.grid(row=4, column=1, sticky="ew", padx=(8,8), ipady=5)
        ttk.Button(root, text="選擇資料夾", command=self.choose_folder).grid(row=4, column=2, sticky="ew")

        ttk.Label(root, text="登入 Cookie").grid(row=5, column=0, sticky="w", pady=(10,12))
        self.cookie = ttk.Combobox(root, values=["不使用", "Chrome", "Edge", "Firefox", "cookies.txt"], state="readonly", width=18)
        self.cookie.set(self.settings.get("cookie", "Chrome"))
        self.cookie.grid(row=5, column=1, sticky="w", padx=(8,8), pady=(10,12))
        self.cookie.bind("<<ComboboxSelected>>", lambda e: self.cookie_changed())
        self.cookie_file_btn = ttk.Button(root, text="選擇 cookies.txt", command=self.choose_cookie_file)
        self.cookie_file_btn.grid(row=5, column=2, sticky="ew", pady=(10,12))
        self.cookie_changed()

        self.summary = ttk.Label(root, text="尚未解析", font=("Segoe UI", 13, "bold"))
        self.summary.grid(row=6, column=0, columnspan=2, sticky="w", pady=(2,5))
        self.progress = ttk.Progressbar(root, mode="determinate", maximum=100)
        self.progress.grid(row=6, column=2, columnspan=2, sticky="ew", padx=(8,0))

        self.results = tk.Text(root, wrap="none", font=("Consolas", 10), relief="solid", borderwidth=1)
        self.results.grid(row=7, column=0, columnspan=4, sticky="nsew", pady=(5,12))
        self.results.insert("1.0", "解析後會在這裡列出抓到的全部媒體。\n")
        self.results.configure(state="disabled")

        self.status = ttk.Label(root, text="僅下載你有權保存的公開內容或已授權內容；遇到 Instagram 驗證請回瀏覽器自行完成。")
        self.status.grid(row=8, column=0, columnspan=2, sticky="w")
        ttk.Button(root, text="開啟資料夾", command=self.open_folder).grid(row=8, column=2, padx=(8,4))
        self.download_btn = ttk.Button(root, text="全部下載", command=self.download, state="disabled")
        self.download_btn.grid(row=8, column=3, padx=(4,0))

    def set_text(self, text):
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", text)
        self.results.configure(state="disabled")

    def paste(self):
        try: t = self.clipboard_get().strip()
        except Exception: return
        self.url.delete(0, "end"); self.url.insert(0, t)

    def choose_folder(self):
        p = filedialog.askdirectory(initialdir=self.folder.get() or str(Path.home()))
        if p:
            self.folder.delete(0, "end"); self.folder.insert(0, p)
            self.settings["folder"] = p; save_settings(self.settings)

    def choose_cookie_file(self):
        p = filedialog.askopenfilename(filetypes=[("cookies.txt", "*.txt"), ("All files", "*.*")])
        if p:
            self.settings["cookie_file"] = p; save_settings(self.settings)
            messagebox.showinfo(APP, "已選擇 cookies.txt")

    def cookie_changed(self):
        self.settings["cookie"] = self.cookie.get(); save_settings(self.settings)
        self.cookie_file_btn.configure(state="normal" if self.cookie.get() == "cookies.txt" else "disabled")

    def configure_dl(self):
        out = Path(self.folder.get().strip()).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        config.set((), "base-directory", str(out))
        config.set((), "directory", ())
        config.set((), "path-restrict", "windows")
        config.set((), "retries", 3)
        mode = self.cookie.get()
        if mode == "不使用":
            config.set((), "cookies", None)
        elif mode == "cookies.txt":
            p = self.settings.get("cookie_file", "")
            if not p or not Path(p).exists():
                raise ValueError("請先選擇有效的 cookies.txt")
            config.set((), "cookies", p)
        else:
            config.set((), "cookies", [mode.lower()])
        self.settings["folder"] = str(out); self.settings["cookie"] = mode; save_settings(self.settings)
        return out

    def set_busy(self, yes):
        self.busy = yes
        self.analyze_btn.configure(state="disabled" if yes else "normal")
        self.download_btn.configure(state="disabled" if yes or not self.media_urls else "normal")

    def analyze(self):
        if self.busy: return
        try:
            u = valid_url(self.url.get()); self.configure_dl()
        except Exception as e:
            messagebox.showerror(APP, str(e)); return
        self.current_url = u; self.media_urls = []; self.media_meta = []
        self.summary.configure(text="正在解析整頁…"); self.status.configure(text="先完整解析頁面，不會只抓第一張。")
        self.progress["value"] = 0; self.set_text("正在解析 Instagram 頁面…\n"); self.set_busy(True)
        threading.Thread(target=self._analyze_worker, args=(u,), daemon=True).start()

    def _analyze_worker(self, u):
        try:
            j = job.DataJob(u, file=None, resolve=True); j.run()
            if j.exception: raise j.exception
            seen = set(); pairs = []
            for i, media in enumerate(j.data_urls):
                if media in seen: continue
                seen.add(media); pairs.append((media, j.data_meta[i] if i < len(j.data_meta) else {}))
            if not pairs:
                raise RuntimeError("沒有解析到可下載媒體。若需要登入，請選擇你已登入 Instagram 的瀏覽器 Cookie。")
            self.media_urls = [x[0] for x in pairs]; self.media_meta = [x[1] for x in pairs]
            imgs = vids = other = 0; lines = []
            for n, (media, meta) in enumerate(pairs, 1):
                ext = str(meta.get("extension") or Path(urlparse(media).path).suffix.lstrip(".")).lower()
                if ext in VIDEO_EXTS: kind="影片"; vids += 1
                elif ext in IMAGE_EXTS: kind="照片"; imgs += 1
                else: kind="媒體"; other += 1
                ident = meta.get("shortcode") or meta.get("post_shortcode") or meta.get("id") or ""
                lines.append(f"{n:03d}  {kind}{('.'+ext) if ext else ''}{('  '+str(ident)) if ident else ''}")
            detail = f"照片 {imgs} · 影片 {vids}" + (f" · 其他 {other}" if other else "")
            self.after(0, lambda: self._analyze_done(len(pairs), detail, "\n".join(lines)))
        except Exception as e:
            self.after(0, lambda: self.fail("解析失敗", e))

    def _analyze_done(self, total, detail, text):
        self.summary.configure(text=f"已解析 {total} 個媒體")
        self.status.configure(text=detail + " · 可以按『全部下載』")
        self.progress["value"] = 100; self.set_text(text + "\n"); self.set_busy(False)

    def download(self):
        if self.busy or not self.media_urls: return
        try:
            self.configure_dl(); u = valid_url(self.current_url or self.url.get())
        except Exception as e:
            messagebox.showerror(APP, str(e)); return
        self.set_busy(True); self.progress["value"] = 0
        total = len(self.media_urls); self.summary.configure(text=f"準備下載 {total} 個媒體")
        threading.Thread(target=self._download_worker, args=(u,total), daemon=True).start()

    def _download_worker(self, u, total):
        try:
            ProgressDownloadJob.total_hint = total; ProgressDownloadJob.callback = self.on_progress
            j = ProgressDownloadJob(u); status = j.run()
            if status: raise RuntimeError(f"下載器回傳狀態碼 {status}。部分檔案可能已完成。")
            self.after(0, lambda: self.done(total))
        except Exception as e:
            self.after(0, lambda: self.fail("下載失敗", e))
        finally:
            ProgressDownloadJob.callback = None

    def on_progress(self, n, total, meta):
        self.after(0, lambda: (self.progress.configure(value=min(100, n*100/max(total,1))), self.summary.configure(text=f"正在下載 {n} / {total}")))

    def done(self, total):
        self.progress["value"] = 100; self.summary.configure(text="下載完成")
        self.status.configure(text=f"已處理 {total} 個媒體 · {self.folder.get()}"); self.set_busy(False)
        messagebox.showinfo(APP, "全部下載完成")

    def fail(self, title, e):
        text = str(e).strip() or e.__class__.__name__
        if any(x in text.lower() for x in ["cookie","login","401","403"]):
            text += "\n\n請先在瀏覽器正常登入 Instagram。若出現 CAPTCHA / 驗證，請在官方網站自行完成後再試。"
        self.summary.configure(text=title); self.status.configure(text=text.splitlines()[0][:150]); self.set_text(title+"\n\n"+text+"\n")
        self.progress["value"] = 0; self.set_busy(False); messagebox.showerror(APP, text)

    def open_folder(self):
        p = Path(self.folder.get().strip()).expanduser(); p.mkdir(parents=True, exist_ok=True)
        if hasattr(os, "startfile"): os.startfile(p)
        elif sys.platform == "darwin": subprocess.Popen(["open", str(p)])
        else: subprocess.Popen(["xdg-open", str(p)])


if __name__ == "__main__":
    App().mainloop()
