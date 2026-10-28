"""The window: text at the top, your fingers do the rest; below it the numbers and the chart."""

from __future__ import annotations

import os
import time
import tkinter as tk
from tkinter import ttk

from . import history, texts
from .engine import Session

TEXT_FONT = ("Consolas", 16)
FONT = ("Segoe UI", 10)
BIG = ("Segoe UI", 22, "bold")
MODES = {"30 seconds": 30, "60 seconds": 60, "Full text": None}


class TikvaardigApp(tk.Tk):
    def __init__(self, clock=time.monotonic):
        super().__init__()
        self.clock = clock
        self.headless = bool(os.environ.get("TIKVAARDIG_HEADLESS"))
        if self.headless:
            self.withdraw()
        self.title("Tikvaardig")
        self.minsize(760, 520)
        self.geometry("900x600")
        try:
            ttk.Style(self).theme_use("vista")
        except tk.TclError:
            pass
        self.session: Session | None = None
        self.saved = False
        self.mode = tk.StringVar(value="60 seconds")
        self.lang = tk.StringVar(value="en")
        self._build()
        self.new_session()
        self.after(200, self._tick)

    # -- layout --------------------------------------------------------------------
    def _build(self) -> None:
        bar = ttk.Frame(self, padding=(10, 8))
        bar.pack(fill="x")
        for label in MODES:
            ttk.Radiobutton(bar, text=label, value=label, variable=self.mode, command=self.new_session).pack(side="left", padx=(0, 8))
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        for code, label in (("en", "English"), ("nl", "Nederlands")):
            ttk.Radiobutton(bar, text=label, value=code, variable=self.lang, command=self.new_session).pack(side="left", padx=(0, 8))
        ttk.Button(bar, text="New text", command=self.new_session).pack(side="right")

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        typ = ttk.Frame(self.nb, padding=10)
        self.nb.add(typ, text="Typing")
        hist = ttk.Frame(self.nb, padding=10)
        self.nb.add(hist, text="History")

        self.text = tk.Text(typ, font=TEXT_FONT, wrap="word", height=7, relief="flat", bg="#fbfbf6",
                            padx=14, pady=12, cursor="arrow", spacing2=6)
        self.text.pack(fill="both", expand=True)
        self.text.tag_configure("ok", foreground="#1b5e20")
        self.text.tag_configure("bad", foreground="#ffffff", background="#c62828")
        self.text.tag_configure("cur", background="#ffe082")
        self.text.tag_configure("rest", foreground="#777")
        self.text.configure(state="disabled")

        stats = ttk.Frame(typ)
        stats.pack(fill="x", pady=(10, 0))
        self.v_wpm = tk.StringVar(value="0")
        self.v_acc = tk.StringVar(value="100%")
        self.v_time = tk.StringVar(value="")
        self.v_err = tk.StringVar(value="0")
        for i, (label, var) in enumerate((("words/min", self.v_wpm), ("accuracy", self.v_acc),
                                           ("time", self.v_time), ("errors", self.v_err))):
            cell = ttk.Frame(stats)
            cell.grid(row=0, column=i, sticky="ew", padx=6)
            ttk.Label(cell, textvariable=var, font=BIG, anchor="center").pack(fill="x")
            ttk.Label(cell, text=label, font=FONT, foreground="#666", anchor="center").pack(fill="x")
            stats.columnconfigure(i, weight=1)
        self.message = ttk.Label(typ, text="Just start typing. Backspace works. Esc = start over.",
                                 font=FONT, foreground="#666", anchor="center")
        self.message.pack(fill="x", pady=(10, 0))

        # history
        self.summary = ttk.Label(hist, text="", font=FONT)
        self.summary.pack(anchor="w")
        self.chart = tk.Canvas(hist, height=160, bg="white", highlightthickness=1, highlightbackground="#ddd")
        self.chart.pack(fill="x", pady=(6, 8))
        cols = ("when", "mode", "lang", "wpm", "accuracy")
        self.table = ttk.Treeview(hist, columns=cols, show="headings", height=8)
        for c, label, w in (("when", "When", 140), ("mode", "Mode", 110), ("lang", "Language", 70),
                            ("wpm", "Words/min", 100), ("accuracy", "Accuracy", 100)):
            self.table.heading(c, text=label)
            self.table.column(c, width=w, anchor="w" if c in ("when", "mode") else "center")
        self.table.pack(fill="both", expand=True)
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refresh_history())

        self.bind("<Key>", self.on_key)
        self.bind("<Escape>", lambda e: self.new_session())

    # -- session ---------------------------------------------------------------------
    def new_session(self) -> None:
        duration = MODES[self.mode.get()]
        min_chars = 700 if duration == 60 else 400 if duration == 30 else 250
        text = texts.make_text(self.lang.get(), min_chars)
        self.session = Session(text, duration)
        self.saved = False
        self._render()
        self._update_stats()
        self.message.configure(text="Just start typing. Backspace works. Esc = start over.")
        if not self.headless:
            self.nb.select(0)
            self.focus_set()

    def on_key(self, event) -> None:
        if self.session is None or self.nb.index(self.nb.select()) != 0:
            return
        if event.keysym == "BackSpace":
            self.session.backspace()
        elif event.keysym == "Escape":
            return
        elif event.char and (event.char.isprintable()) and len(event.char) == 1:
            self.session.key(event.char, self.clock())
        else:
            return
        self._render()
        self._update_stats()

    def _tick(self) -> None:
        if self.session is not None and self.session.running:
            self.session.tick(self.clock())
            self._update_stats()
        self.after(200, self._tick)

    def _render(self) -> None:
        s = self.session
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        for i, ch in enumerate(s.text):
            if i < len(s.state):
                tag = "ok" if s.state[i] else "bad"
            elif i == s.pos:
                tag = "cur"
            else:
                tag = "rest"
            self.text.insert("end", ch, tag)
        self.text.configure(state="disabled")
        if s.pos < len(s.text):
            self.text.see(f"1.0+{s.pos}c")

    def _update_stats(self) -> None:
        s = self.session
        st = s.stats(self.clock())
        self.v_wpm.set(f"{st.wpm:.0f}")
        self.v_acc.set(f"{st.accuracy:.0f}%")
        self.v_err.set(str(st.errors))
        left = s.time_left(self.clock())
        self.v_time.set(f"{left:.0f}s" if left is not None else f"{st.elapsed:.0f}s")
        if st.finished and not self.saved:
            self.saved = True
            entry = history.add(self.mode.get(), self.lang.get(), st.wpm, st.accuracy, st.elapsed, st.correct)
            best = history.best(mode=self.mode.get())
            record = best is not None and best["wpm"] <= entry["wpm"] and best["when"] == entry["when"]
            self.message.configure(text=(f"Done: {st.wpm:.0f} words per minute, {st.accuracy:.0f}% accuracy."
                                         + ("  New record!" if record else "") + "  Esc or 'New text' to go again."))

    # -- history -----------------------------------------------------------------------------
    def refresh_history(self) -> None:
        items = history.load()
        sm = history.summary(items)
        self.summary.configure(text=f"{sm['count']} sessions · average {sm['avg_wpm']} wpm · "
                                    f"best {sm['best_wpm']} wpm · accuracy {sm['avg_accuracy']}%")
        self.table.delete(*self.table.get_children())
        for it in reversed(items[-50:]):
            self.table.insert("", "end", values=(it["when"], it["mode"], it["lang"], it["wpm"], f"{it['accuracy']}%"))
        self._draw_chart(items[-30:])

    def _draw_chart(self, items: list[dict]) -> None:
        c = self.chart
        c.delete("all")
        if not items:
            c.create_text(10, 20, anchor="w", text="No sessions yet.", fill="#888", font=FONT)
            return
        w = max(int(c.winfo_width()), 300)
        h = 160
        top = max(it["wpm"] for it in items) or 1
        best = max(items, key=lambda i: i["wpm"])
        n = len(items)
        slot = (w - 40) / n
        for i, it in enumerate(items):
            x0 = 30 + i * slot + 2
            x1 = x0 + max(slot - 4, 2)
            bh = (h - 30) * it["wpm"] / top
            color = "#f9a825" if it is best else "#4caf50" if it["accuracy"] >= 95 else "#90a4ae"
            c.create_rectangle(x0, h - 10 - bh, x1, h - 10, fill=color, width=0)
        for frac in (0.5, 1.0):
            y = h - 10 - (h - 30) * frac
            c.create_line(30, y, w - 10, y, fill="#eee")
            c.create_text(4, y, anchor="w", text=f"{top * frac:.0f}", fill="#888", font=("Segoe UI", 8))


def main() -> int:
    app = TikvaardigApp()
    app.mainloop()
    return 0
