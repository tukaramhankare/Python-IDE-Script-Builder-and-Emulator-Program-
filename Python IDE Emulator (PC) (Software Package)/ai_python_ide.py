"""
AI Python IDE  —  Production Grade  v1.1.0
Developed by Tukaram Hankare

A full-featured AI-powered Python code editor and generator.
PyInstaller-ready | Dark Gray / White / Black themes | No API key required
"""

# ── stdlib ─────────────────────────────────────────────────────────────────────
import sys
import os
import re
import io
import json
import time
import shutil
import tempfile
import threading
import traceback
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

# ── tkinter ────────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ── PyInstaller asset helper ───────────────────────────────────────────────────
def resource_path(relative_path: str) -> str:
    """Return correct path both in dev and when frozen with PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

# ── Optional Anthropic SDK ─────────────────────────────────────────────────────
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ==============================================================================
#  CONSTANTS
# ==============================================================================
APP_NAME    = "AI Python IDE"
APP_VERSION = "1.1.0"
APP_AUTHOR  = "Tukaram Hankare"

THEMES: Dict[str, Dict[str, str]] = {
    "Dark Gray": {
        "bg":         "#1e1e1e",
        "bg2":        "#252526",
        "bg3":        "#2d2d30",
        "fg":         "#d4d4d4",
        "fg2":        "#9d9d9d",
        "accent":     "#0078d4",
        "accent2":    "#1a8cff",
        "success":    "#4ec9b0",
        "warning":    "#ddb100",
        "error":      "#f44747",
        "border":     "#3c3c3c",
        "select":     "#264f78",
        "editor_bg":  "#1e1e1e",
        "editor_fg":  "#d4d4d4",
        "lineno_bg":  "#252526",
        "lineno_fg":  "#858585",
        "cursor":     "#aeafad",
        "btn_bg":     "#3a3d41",
        "btn_fg":     "#d4d4d4",
        "btn_active": "#505050",
        "tab_bg":     "#2d2d30",
        "tab_sel":    "#1e1e1e",
        "sidebar_bg": "#252526",
        "output_bg":  "#1e1e1e",
        "output_fg":  "#d4d4d4",
        "prompt_bg":  "#1a1a2e",
        "scrollbar":  "#3c3c3c",
    },
    "White": {
        "bg":         "#f3f3f3",
        "bg2":        "#ffffff",
        "bg3":        "#e8e8e8",
        "fg":         "#1e1e1e",
        "fg2":        "#6e6e6e",
        "accent":     "#0066cc",
        "accent2":    "#004fa3",
        "success":    "#007a6e",
        "warning":    "#8a6d00",
        "error":      "#cc0000",
        "border":     "#c8c8c8",
        "select":     "#b8d6f5",
        "editor_bg":  "#ffffff",
        "editor_fg":  "#1e1e1e",
        "lineno_bg":  "#f0f0f0",
        "lineno_fg":  "#999999",
        "cursor":     "#000000",
        "btn_bg":     "#e0e0e0",
        "btn_fg":     "#1e1e1e",
        "btn_active": "#d0d0d0",
        "tab_bg":     "#e8e8e8",
        "tab_sel":    "#ffffff",
        "sidebar_bg": "#f0f0f0",
        "output_bg":  "#ffffff",
        "output_fg":  "#1e1e1e",
        "prompt_bg":  "#eef4ff",
        "scrollbar":  "#c0c0c0",
    },
    "Black": {
        "bg":         "#000000",
        "bg2":        "#0d0d0d",
        "bg3":        "#1a1a1a",
        "fg":         "#e8e8e8",
        "fg2":        "#888888",
        "accent":     "#00bfff",
        "accent2":    "#00d4ff",
        "success":    "#00ff9d",
        "warning":    "#ffcc00",
        "error":      "#ff3333",
        "border":     "#2a2a2a",
        "select":     "#003a5c",
        "editor_bg":  "#050505",
        "editor_fg":  "#e0e0e0",
        "lineno_bg":  "#0d0d0d",
        "lineno_fg":  "#505050",
        "cursor":     "#00bfff",
        "btn_bg":     "#1a1a1a",
        "btn_fg":     "#e0e0e0",
        "btn_active": "#2a2a2a",
        "tab_bg":     "#0d0d0d",
        "tab_sel":    "#050505",
        "sidebar_bg": "#0d0d0d",
        "output_bg":  "#000000",
        "output_fg":  "#e0e0e0",
        "prompt_bg":  "#000d1a",
        "scrollbar":  "#2a2a2a",
    },
}

SYNTAX_COLORS: Dict[str, Dict[str, str]] = {
    "Dark Gray": {
        "keyword":  "#569cd6",
        "string":   "#ce9178",
        "comment":  "#6a9955",
        "number":   "#b5cea8",
        "function": "#dcdcaa",
        "class_kw": "#4ec9b0",
        "builtin":  "#4ec9b0",
    },
    "White": {
        "keyword":  "#0000ff",
        "string":   "#a31515",
        "comment":  "#008000",
        "number":   "#098658",
        "function": "#795e26",
        "class_kw": "#267f99",
        "builtin":  "#267f99",
    },
    "Black": {
        "keyword":  "#00bfff",
        "string":   "#ff9966",
        "comment":  "#55aa55",
        "number":   "#99ff66",
        "function": "#ffdd44",
        "class_kw": "#00ffcc",
        "builtin":  "#00ffcc",
    },
}

PYTHON_KEYWORDS = [
    "False","None","True","and","as","assert","async","await",
    "break","class","continue","def","del","elif","else","except",
    "finally","for","from","global","if","import","in","is",
    "lambda","nonlocal","not","or","pass","raise","return",
    "try","while","with","yield",
]

PYTHON_BUILTINS = [
    "abs","all","any","bin","bool","bytearray","bytes","callable",
    "chr","compile","complex","delattr","dict","dir","divmod",
    "enumerate","eval","exec","filter","float","format","frozenset",
    "getattr","globals","hasattr","hash","help","hex","id","input",
    "int","isinstance","issubclass","iter","len","list","locals",
    "map","max","memoryview","min","next","object","oct","open",
    "ord","pow","print","property","range","repr","reversed","round",
    "set","setattr","slice","sorted","staticmethod","str","sum",
    "super","tuple","type","vars","zip",
]


# ==============================================================================
#  SYNTAX HIGHLIGHTER
# ==============================================================================
class SyntaxHighlighter:
    """Debounced syntax highlighter attached to a tk.Text widget."""

    def __init__(self, text_widget: tk.Text, theme_name: str = "Dark Gray"):
        self.text  = text_widget
        self.theme = theme_name
        self._job: Optional[str] = None
        self._configure_tags()

    def set_theme(self, theme_name: str) -> None:
        self.theme = theme_name
        self._configure_tags()
        self.highlight()

    def highlight(self, event=None) -> None:
        if self._job:
            try:
                self.text.after_cancel(self._job)
            except Exception:
                pass
        self._job = self.text.after(150, self._do_highlight)

    def _configure_tags(self) -> None:
        c = SYNTAX_COLORS.get(self.theme, SYNTAX_COLORS["Dark Gray"])
        tag_map = {
            "kw_tag":  "keyword",
            "str_tag": "string",
            "cmt_tag": "comment",
            "num_tag": "number",
            "fn_tag":  "function",
            "cls_tag": "class_kw",
            "bi_tag":  "builtin",
        }
        for tag, key in tag_map.items():
            self.text.tag_configure(tag, foreground=c[key])

    def _do_highlight(self) -> None:
        try:
            content = self.text.get("1.0", "end-1c")
        except tk.TclError:
            return

        for tag in ("kw_tag","str_tag","cmt_tag","num_tag","fn_tag","cls_tag","bi_tag"):
            self.text.tag_remove(tag, "1.0", "end")

        # Build offset->line.col index
        lines   = content.split("\n")
        offsets = []
        pos     = 0
        for ln in lines:
            offsets.append(pos)
            pos += len(ln) + 1

        def idx(char_offset: int) -> str:
            lo, hi = 0, len(offsets) - 1
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if offsets[mid] <= char_offset:
                    lo = mid
                else:
                    hi = mid - 1
            col = char_offset - offsets[lo]
            return f"{lo + 1}.{col}"

        def apply(tag: str, pattern: str, flags: int = 0) -> None:
            for m in re.finditer(pattern, content, flags):
                try:
                    self.text.tag_add(tag, idx(m.start()), idx(m.end()))
                except tk.TclError:
                    pass

        apply("bi_tag",  r"\b(?:" + "|".join(map(re.escape, PYTHON_BUILTINS)) + r")\b")
        apply("kw_tag",  r"\b(?:" + "|".join(map(re.escape, PYTHON_KEYWORDS)) + r")\b")
        apply("num_tag", r"\b\d+\.?\d*(?:[eE][+-]?\d+)?\b")
        apply("fn_tag",  r"(?<=def )\s*\w+")
        apply("cls_tag", r"(?<=class )\s*\w+")
        apply("str_tag", r'"""[\s\S]*?"""')
        apply("str_tag", r"'''[\s\S]*?'''")
        apply("str_tag", r'"(?:[^"\\]|\\.)*"')
        apply("str_tag", r"'(?:[^'\\]|\\.)*'")
        apply("cmt_tag", r"#[^\n]*")


# ==============================================================================
#  LINE NUMBER CANVAS
# ==============================================================================
class LineNumbers(tk.Canvas):
    def __init__(self, parent, text_widget: tk.Text, theme: str, **kw):
        t = THEMES.get(theme, THEMES["Dark Gray"])
        super().__init__(parent, width=52, bg=t["lineno_bg"],
                         bd=0, highlightthickness=0, **kw)
        self.text_widget = text_widget
        self.theme       = theme
        self._running    = True
        self._poll()

    def destroy(self) -> None:
        self._running = False
        super().destroy()

    def set_theme(self, theme: str) -> None:
        self.theme = theme
        t = THEMES.get(theme, THEMES["Dark Gray"])
        self.configure(bg=t["lineno_bg"])

    def _poll(self) -> None:
        if not self._running:
            return
        try:
            self._redraw()
            self.after(100, self._poll)
        except tk.TclError:
            pass

    def _redraw(self) -> None:
        self.delete("all")
        t  = THEMES.get(self.theme, THEMES["Dark Gray"])
        fg = t["lineno_fg"]
        i  = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y  = dline[1]
            ln = str(i).split(".")[0]
            self.create_text(46, y + 2, anchor="ne", text=ln,
                             fill=fg, font=("Consolas", 10))
            next_i = self.text_widget.index(f"{i}+1line")
            if self.text_widget.compare(next_i, "==", i):
                break
            i = next_i


# ==============================================================================
#  CODE EDITOR  — ROOT FIX: highlighter created BEFORE bindings
# ==============================================================================
class CodeEditor(tk.Frame):
    """
    BUG FIXED: In v1.0 _build() was called first, which tried to bind
    self.highlighter.highlight before self.highlighter was assigned,
    causing AttributeError: 'CodeEditor' object has no attribute 'highlighter'.

    Fix: build all widgets inline in __init__, assign self.highlighter,
    THEN add the KeyRelease binding.
    """

    def __init__(self, parent, theme: str = "Dark Gray", **kw):
        super().__init__(parent, **kw)
        self.theme = theme
        t = THEMES[theme]
        self.configure(bg=t["bg"])

        # 1. Build scrollbars
        self.vscroll = ttk.Scrollbar(self, orient="vertical")
        self.hscroll = ttk.Scrollbar(self, orient="horizontal")

        # 2. Build text widget  (tabs="40p" = single value, no space = no bad-distance)
        self.text = tk.Text(
            self,
            wrap="none",
            font=("Consolas", 11),
            bg=t["editor_bg"],
            fg=t["editor_fg"],
            insertbackground=t["cursor"],
            selectbackground=t["select"],
            relief="flat",
            bd=0,
            undo=True,
            maxundo=200,
            autoseparators=True,
            yscrollcommand=self._on_yscroll,
            xscrollcommand=self.hscroll.set,
            tabs="40p",
        )

        # 3. Line numbers
        self.linenos = LineNumbers(self, self.text, theme)

        # 4. Grid layout
        self.linenos.grid(row=0, column=0, sticky="ns")
        self.text.grid(   row=0, column=1, sticky="nsew")
        self.vscroll.grid(row=0, column=2, sticky="ns")
        self.hscroll.grid(row=1, column=1, sticky="ew")
        self.vscroll.configure(command=self._on_vscroll)
        self.hscroll.configure(command=self.text.xview)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # 5. Create highlighter FIRST — before any binding that references it
        self.highlighter = SyntaxHighlighter(self.text, theme)

        # 6. NOW safe to bind KeyRelease
        self.text.bind("<KeyRelease>", self.highlighter.highlight)
        self.text.bind("<Tab>",        self._on_tab)
        self.text.bind("<Return>",     self._on_return)

    # ── private ───────────────────────────────────────────────────────────────
    def _on_tab(self, event) -> str:
        self.text.insert("insert", "    ")
        return "break"

    def _on_return(self, event) -> str:
        idx     = self.text.index("insert")
        line_no = int(idx.split(".")[0])
        line    = self.text.get(f"{line_no}.0", f"{line_no}.end")
        indent  = len(line) - len(line.lstrip())
        if line.rstrip().endswith(":"):
            indent += 4
        self.text.insert("insert", "\n" + " " * indent)
        return "break"

    def _on_vscroll(self, *args) -> None:
        self.text.yview(*args)

    def _on_yscroll(self, *args) -> None:
        self.vscroll.set(*args)

    # ── public ────────────────────────────────────────────────────────────────
    def set_theme(self, theme: str) -> None:
        self.theme = theme
        t = THEMES[theme]
        self.configure(bg=t["bg"])
        self.text.configure(
            bg=t["editor_bg"], fg=t["editor_fg"],
            insertbackground=t["cursor"],
            selectbackground=t["select"],
        )
        self.linenos.set_theme(theme)
        self.highlighter.set_theme(theme)

    def get_content(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set_content(self, content: str) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.highlighter.highlight()

    def clear(self) -> None:
        self.text.delete("1.0", "end")


# ==============================================================================
#  OUTPUT PANEL
# ==============================================================================
class OutputPanel(tk.Frame):
    def __init__(self, parent, theme: str = "Dark Gray", **kw):
        super().__init__(parent, **kw)
        self.theme = theme
        self._build()

    def _build(self) -> None:
        t = THEMES[self.theme]
        self.configure(bg=t["bg2"])

        hdr = tk.Frame(self, bg=t["bg3"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="▶  OUTPUT / CONSOLE", bg=t["bg3"], fg=t["fg2"],
                 font=("Consolas", 9, "bold"), padx=10, pady=5).pack(side="left")

        self._clear_btn = tk.Button(
            hdr, text="✕ Clear", bg=t["btn_bg"], fg=t["fg2"],
            font=("Consolas", 8), relief="flat", bd=0,
            activebackground=t["btn_active"], activeforeground=t["fg"],
            cursor="hand2", command=self.clear_output, padx=6, pady=2,
        )
        self._clear_btn.pack(side="right", padx=6, pady=3)

        frame = tk.Frame(self, bg=t["output_bg"])
        frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.output = tk.Text(
            frame, font=("Consolas", 10), bg=t["output_bg"], fg=t["output_fg"],
            relief="flat", bd=0, state="disabled", wrap="word",
            insertbackground=t["cursor"],
        )
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.output.yview)
        self.output.configure(yscrollcommand=scroll.set)
        self.output.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._configure_tags()

    def _configure_tags(self) -> None:
        t = THEMES[self.theme]
        self.output.tag_configure("error",   foreground=t["error"])
        self.output.tag_configure("success", foreground=t["success"])
        self.output.tag_configure("info",    foreground=t["accent"])
        self.output.tag_configure("warn",    foreground=t["warning"])

    def set_theme(self, theme: str) -> None:
        self.theme = theme
        t = THEMES[theme]
        self.configure(bg=t["bg2"])
        self.output.configure(bg=t["output_bg"], fg=t["output_fg"],
                              insertbackground=t["cursor"])
        self._clear_btn.configure(bg=t["btn_bg"], fg=t["fg2"],
                                  activebackground=t["btn_active"])
        self._configure_tags()

    def write(self, text: str, tag: Optional[str] = None) -> None:
        self.output.configure(state="normal")
        if tag:
            self.output.insert("end", text, tag)
        else:
            self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def clear_output(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")


# ==============================================================================
#  AI PROMPT PANEL
# ==============================================================================
class AIPromptPanel(tk.Frame):
    def __init__(self, parent, theme: str = "Dark Gray",
                 on_generate: Optional[Callable] = None, **kw):
        super().__init__(parent, **kw)
        self.theme       = theme
        self.on_generate = on_generate
        self._build()

    def _build(self) -> None:
        t = THEMES[self.theme]
        self.configure(bg=t["bg2"])

        hdr = tk.Frame(self, bg=t["bg3"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="🤖  AI CODE GENERATOR", bg=t["bg3"], fg=t["fg2"],
                 font=("Consolas", 9, "bold"), padx=10, pady=5).pack(side="left")

        # Mode row
        row_mode = tk.Frame(self, bg=t["bg2"])
        row_mode.pack(fill="x", padx=8, pady=(6, 0))
        tk.Label(row_mode, text="Mode:", bg=t["bg2"], fg=t["fg2"],
                 font=("Consolas", 9), width=8, anchor="w").pack(side="left")
        self.mode_var = tk.StringVar(value="Generate New Script")
        self.mode_cb  = ttk.Combobox(
            row_mode, textvariable=self.mode_var,
            values=["Generate New Script","Improve Existing Code",
                    "Fix Bugs in Code","Explain Code","Add Comments"],
            state="readonly", width=28, font=("Consolas", 9),
        )
        self.mode_cb.pack(side="left", padx=(4, 0))

        # API key row
        row_key = tk.Frame(self, bg=t["bg2"])
        row_key.pack(fill="x", padx=8, pady=(4, 0))
        tk.Label(row_key, text="API Key:", bg=t["bg2"], fg=t["fg2"],
                 font=("Consolas", 9), width=8, anchor="w").pack(side="left")
        self.api_var    = tk.StringVar()
        self._api_entry = tk.Entry(
            row_key, textvariable=self.api_var, show="*",
            font=("Consolas", 9), bg=t["bg3"], fg=t["fg"],
            insertbackground=t["cursor"], relief="flat", bd=1, width=30,
        )
        self._api_entry.pack(side="left", padx=(4, 0), ipady=3)

        # Prompt label + text
        tk.Label(self, text="Describe what you want to build:",
                 bg=t["bg2"], fg=t["fg2"],
                 font=("Consolas", 9)).pack(anchor="w", padx=8, pady=(8, 2))

        self.prompt = tk.Text(
            self, height=5, font=("Consolas", 10),
            bg=t["prompt_bg"], fg=t["fg"],
            insertbackground=t["cursor"],
            selectbackground=t["select"],
            relief="flat", bd=1, wrap="word",
        )
        self.prompt.pack(fill="x", padx=8, pady=(0, 6))
        self.prompt.bind("<Control-Return>", lambda e: self._trigger())

        # Generate button
        self._gen_btn = tk.Button(
            self, text="⚡  GENERATE CODE",
            bg=t["accent"], fg="#ffffff",
            font=("Consolas", 10, "bold"), relief="flat", bd=0,
            activebackground=t["accent2"], activeforeground="#ffffff",
            cursor="hand2", command=self._trigger, padx=10, pady=8,
        )
        self._gen_btn.pack(fill="x", padx=8, pady=(0, 4))

        self._status_var = tk.StringVar(value="Ready — Ctrl+Enter to generate")
        tk.Label(self, textvariable=self._status_var, bg=t["bg2"], fg=t["fg2"],
                 font=("Consolas", 8), anchor="w").pack(fill="x", padx=8, pady=(0, 6))

    def _trigger(self) -> None:
        if self.on_generate:
            self.on_generate(
                self.prompt.get("1.0", "end-1c").strip(),
                self.api_var.get().strip(),
                self.mode_var.get(),
            )

    def set_status(self, msg: str) -> None:
        self._status_var.set(msg)

    def set_theme(self, theme: str) -> None:
        self.theme = theme
        t = THEMES[theme]
        self.configure(bg=t["bg2"])
        self.prompt.configure(bg=t["prompt_bg"], fg=t["fg"],
                              insertbackground=t["cursor"],
                              selectbackground=t["select"])
        self._api_entry.configure(bg=t["bg3"], fg=t["fg"],
                                  insertbackground=t["cursor"])
        self._gen_btn.configure(bg=t["accent"], activebackground=t["accent2"])


# ==============================================================================
#  FILE SIDEBAR
# ==============================================================================
class FileSidebar(tk.Frame):
    def __init__(self, parent, theme: str = "Dark Gray",
                 on_open: Optional[Callable] = None, **kw):
        super().__init__(parent, **kw)
        self.theme   = theme
        self.on_open = on_open
        self._paths: List[str] = []
        self._build()

    def _build(self) -> None:
        t = THEMES[self.theme]
        self.configure(bg=t["sidebar_bg"])

        hdr = tk.Frame(self, bg=t["bg3"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="📁  FILES", bg=t["bg3"], fg=t["fg2"],
                 font=("Consolas", 9, "bold"), padx=10, pady=5).pack(side="left")

        btn_row = tk.Frame(self, bg=t["sidebar_bg"])
        btn_row.pack(fill="x", padx=4, pady=4)
        for label, cmd in [("+ New", self._new), ("📂 Open", self._open)]:
            tk.Button(btn_row, text=label, bg=t["btn_bg"], fg=t["btn_fg"],
                      font=("Consolas", 8), relief="flat", bd=0,
                      activebackground=t["btn_active"], activeforeground=t["fg"],
                      cursor="hand2", command=cmd,
                      padx=6, pady=4).pack(side="left", padx=2)

        lb_frame = tk.Frame(self, bg=t["sidebar_bg"])
        lb_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        self._lb = tk.Listbox(lb_frame, font=("Consolas", 9),
                              bg=t["sidebar_bg"], fg=t["fg"],
                              selectbackground=t["select"],
                              relief="flat", bd=0, activestyle="none")
        sb = ttk.Scrollbar(lb_frame, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        self._lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._lb.bind("<Double-Button-1>", self._on_select)

    def _new(self)  -> None:
        if self.on_open:
            self.on_open(None, "new")

    def _open(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if path:
            self.add_file(path)
            if self.on_open:
                self.on_open(path, "open")

    def _on_select(self, event=None) -> None:
        sel = self._lb.curselection()
        if sel and self.on_open:
            idx  = sel[0]
            path = self._paths[idx] if idx < len(self._paths) else None
            if path:
                self.on_open(path, "open")

    def add_file(self, path: str) -> None:
        if path not in self._paths:
            self._paths.append(path)
            self._lb.insert("end", f"  {os.path.basename(path)}")

    def set_theme(self, theme: str) -> None:
        self.theme = theme
        t = THEMES[theme]
        self.configure(bg=t["sidebar_bg"])
        self._lb.configure(bg=t["sidebar_bg"], fg=t["fg"],
                            selectbackground=t["select"])


# ==============================================================================
#  CODE TEMPLATES  (local AI fallback — no API key needed)
# ==============================================================================
class CodeTemplates:
    @staticmethod
    def generate(prompt: str, mode: str) -> str:
        pl = prompt.lower()
        if any(w in pl for w in ["tkinter","gui","window","interface","form","widget"]):
            return CodeTemplates._tkinter(prompt)
        if any(w in pl for w in ["flask","fastapi","api","web server","route","endpoint","http"]):
            return CodeTemplates._flask(prompt)
        if any(w in pl for w in ["csv","excel","pandas","dataframe","data analysis","dataset"]):
            return CodeTemplates._data(prompt)
        if any(w in pl for w in ["class","oop","object","inherit","polymorphism"]):
            return CodeTemplates._oop(prompt)
        if any(w in pl for w in ["file","read","write","parse","json","xml","yaml"]):
            return CodeTemplates._file_io(prompt)
        if any(w in pl for w in ["thread","async","concurrent","parallel","multiprocess"]):
            return CodeTemplates._async_t(prompt)
        if any(w in pl for w in ["test","unittest","pytest","assert","mock"]):
            return CodeTemplates._test(prompt)
        if any(w in pl for w in ["sort","search","algorithm","binary","linked list","tree","graph"]):
            return CodeTemplates._algo(prompt)
        if any(w in pl for w in ["sqlite","database","sql","db","orm","table"]):
            return CodeTemplates._db(prompt)
        if any(w in pl for w in ["scrape","scraping","requests","beautifulsoup","selenium","crawl"]):
            return CodeTemplates._scraper(prompt)
        return CodeTemplates._generic(prompt)

    @staticmethod
    def _tkinter(prompt: str) -> str:
        return (
            '"""\n'
            + prompt + '\n'
            + 'Developed by Tukaram Hankare\n'
            + '"""\n'
            + 'import sys\n'
            + 'import os\n'
            + 'import tkinter as tk\n'
            + 'from tkinter import ttk, messagebox, filedialog\n\n'
            + 'def resource_path(relative_path):\n'
            + '    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))\n'
            + '    return os.path.join(base, relative_path)\n\n'
            + 'class App(tk.Tk):\n'
            + '    def __init__(self):\n'
            + '        super().__init__()\n'
            + '        self.title("' + prompt[:48] + '")\n'
            + '        self.geometry("900x600")\n'
            + '        self.minsize(640, 400)\n'
            + '        self._build()\n\n'
            + '    def _build(self):\n'
            + '        toolbar = tk.Frame(self, bg="#2d2d30", height=36)\n'
            + '        toolbar.pack(fill="x")\n'
            + '        toolbar.pack_propagate(False)\n\n'
            + '        for label, cmd in [("New", self._new), ("About", self._about)]:\n'
            + '            tk.Button(toolbar, text=label, bg="#3a3d41", fg="#d4d4d4",\n'
            + '                      font=("Segoe UI", 9), relief="flat", bd=0,\n'
            + '                      activebackground="#505050", cursor="hand2",\n'
            + '                      command=cmd, padx=10, pady=4).pack(side="left", padx=2, pady=4)\n\n'
            + '        pane = ttk.PanedWindow(self, orient="horizontal")\n'
            + '        pane.pack(fill="both", expand=True)\n\n'
            + '        left = tk.Frame(pane, bg="#252526", width=200)\n'
            + '        pane.add(left, weight=0)\n'
            + '        tk.Label(left, text="Items", bg="#252526", fg="#9d9d9d",\n'
            + '                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=6)\n'
            + '        self._lb = tk.Listbox(left, bg="#1e1e1e", fg="#d4d4d4",\n'
            + '                              selectbackground="#264f78",\n'
            + '                              relief="flat", bd=0, font=("Consolas", 10))\n'
            + '        self._lb.pack(fill="both", expand=True, padx=6, pady=(0, 6))\n\n'
            + '        right = tk.Frame(pane, bg="#1e1e1e")\n'
            + '        pane.add(right, weight=1)\n'
            + '        self._detail = tk.Text(right, bg="#1e1e1e", fg="#d4d4d4",\n'
            + '                               font=("Consolas", 10), relief="flat", bd=0,\n'
            + '                               insertbackground="#aeafad")\n'
            + '        self._detail.pack(fill="both", expand=True, padx=8, pady=8)\n\n'
            + '        inp = tk.Frame(self, bg="#2d2d30")\n'
            + '        inp.pack(fill="x", padx=8, pady=4)\n'
            + '        self._entry = tk.Entry(inp, bg="#3c3c3c", fg="#d4d4d4",\n'
            + '                               insertbackground="#aeafad",\n'
            + '                               relief="flat", bd=0, font=("Consolas", 10))\n'
            + '        self._entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 6))\n'
            + '        self._entry.bind("<Return>", lambda e: self._add())\n'
            + '        for label, cmd in [("Add", self._add), ("Remove", self._remove)]:\n'
            + '            tk.Button(inp, text=label, bg="#0078d4", fg="#ffffff",\n'
            + '                      font=("Segoe UI", 9), relief="flat", bd=0,\n'
            + '                      activebackground="#1a8cff", cursor="hand2",\n'
            + '                      command=cmd, padx=10, pady=5).pack(side="left", padx=2)\n\n'
            + '        self._status = tk.StringVar(value="Ready")\n'
            + '        bar = tk.Frame(self, bg="#007acc")\n'
            + '        bar.pack(fill="x", side="bottom")\n'
            + '        tk.Label(bar, textvariable=self._status, bg="#007acc", fg="#ffffff",\n'
            + '                 font=("Segoe UI", 8), padx=8, pady=3).pack(side="left")\n\n'
            + '    def _new(self):    self._lb.delete(0, "end"); self._status.set("New")\n'
            + '    def _about(self):  messagebox.showinfo("About", "Developed by Tukaram Hankare")\n'
            + '    def _add(self):\n'
            + '        t = self._entry.get().strip()\n'
            + '        if t: self._lb.insert("end", t); self._entry.delete(0, "end")\n'
            + '    def _remove(self):\n'
            + '        sel = self._lb.curselection()\n'
            + '        if sel: self._lb.delete(sel[0])\n\n'
            + 'if __name__ == "__main__":\n'
            + '    App().mainloop()\n'
        )

    @staticmethod
    def _flask(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'from flask import Flask, request, jsonify, abort\n'
            'import logging\n\n'
            'logging.basicConfig(level=logging.INFO)\n'
            'logger = logging.getLogger(__name__)\n'
            'app    = Flask(__name__)\n'
            '_store = {}\n\n'
            '@app.errorhandler(404)\n'
            'def not_found(e): return jsonify({"error": "Not found"}), 404\n\n'
            '@app.errorhandler(400)\n'
            'def bad_req(e):   return jsonify({"error": str(e)}), 400\n\n'
            '@app.route("/", methods=["GET"])\n'
            'def health(): return jsonify({"status": "ok"})\n\n'
            '@app.route("/api/items", methods=["GET"])\n'
            'def list_items(): return jsonify({"items": list(_store.values()), "count": len(_store)})\n\n'
            '@app.route("/api/items", methods=["POST"])\n'
            'def create_item():\n'
            '    data = request.get_json(silent=True)\n'
            '    if not data or "name" not in data: abort(400, "name required")\n'
            '    nid = max(_store.keys(), default=0) + 1\n'
            '    item = {"id": nid, "name": data["name"], "value": data.get("value", 0)}\n'
            '    _store[nid] = item\n'
            '    return jsonify(item), 201\n\n'
            '@app.route("/api/items/<int:item_id>", methods=["DELETE"])\n'
            'def delete_item(item_id):\n'
            '    if item_id not in _store: abort(404)\n'
            '    del _store[item_id]\n'
            '    return jsonify({"deleted": item_id})\n\n'
            'if __name__ == "__main__":\n'
            '    app.run(debug=True, host="0.0.0.0", port=5000)\n'
        )

    @staticmethod
    def _data(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'import csv, json, sys\n'
            'from pathlib import Path\n'
            'from typing import Any, Dict, List\n\n'
            'def read_csv(path):\n'
            '    with open(path, newline="", encoding="utf-8") as f:\n'
            '        return list(csv.DictReader(f))\n\n'
            'def write_csv(data, path):\n'
            '    if not data: return\n'
            '    Path(path).parent.mkdir(parents=True, exist_ok=True)\n'
            '    with open(path, "w", newline="", encoding="utf-8") as f:\n'
            '        w = csv.DictWriter(f, fieldnames=data[0].keys())\n'
            '        w.writeheader(); w.writerows(data)\n'
            '    print(f"Wrote {len(data)} rows -> {path}")\n\n'
            'def describe(data):\n'
            '    if not data: return {}\n'
            '    numeric = {}\n'
            '    for key in data[0]:\n'
            '        try:\n'
            '            vals = [float(r[key]) for r in data if r.get(key)]\n'
            '            numeric[key] = {"count": len(vals), "min": min(vals),\n'
            '                            "max": max(vals), "mean": sum(vals)/len(vals)}\n'
            '        except (ValueError, TypeError): pass\n'
            '    return {"rows": len(data), "columns": list(data[0].keys()), "numeric": numeric}\n\n'
            'def main():\n'
            '    sample = [\n'
            '        {"name": "Alice", "dept": "Eng",  "salary": "95000"},\n'
            '        {"name": "Bob",   "dept": "Mkt",  "salary": "72000"},\n'
            '        {"name": "Carol", "dept": "Eng",  "salary": "105000"},\n'
            '    ]\n'
            '    write_csv(sample, "output/employees.csv")\n'
            '    loaded = read_csv("output/employees.csv")\n'
            '    print(json.dumps(describe(loaded), indent=2))\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        )

    @staticmethod
    def _oop(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'from __future__ import annotations\n'
            'from dataclasses import dataclass, field\n'
            'from datetime import datetime\n'
            'from typing import Iterator, List, Optional\n\n'
            '@dataclass\n'
            'class Record:\n'
            '    id:         int\n'
            '    name:       str\n'
            '    value:      float     = 0.0\n'
            '    tags:       List[str] = field(default_factory=list)\n'
            '    created_at: datetime  = field(default_factory=datetime.now)\n\n'
            '    def __post_init__(self):\n'
            '        if not self.name.strip(): raise ValueError("name must not be empty")\n\n'
            '    def to_dict(self):\n'
            '        return {"id": self.id, "name": self.name, "value": self.value, "tags": self.tags}\n\n'
            'class Repository:\n'
            '    def __init__(self): self._store: dict = {}; self._seq = 0\n\n'
            '    def add(self, name, value=0.0, tags=None):\n'
            '        self._seq += 1\n'
            '        r = Record(id=self._seq, name=name, value=value, tags=list(tags or []))\n'
            '        self._store[self._seq] = r; return r\n\n'
            '    def get(self, rid): return self._store.get(rid)\n'
            '    def delete(self, rid): return bool(self._store.pop(rid, None))\n'
            '    def all(self): return list(self._store.values())\n'
            '    def __len__(self): return len(self._store)\n\n'
            'if __name__ == "__main__":\n'
            '    repo = Repository()\n'
            '    repo.add("Alpha", 10.5, ["urgent"])\n'
            '    repo.add("Beta",  20.0)\n'
            '    print("All:", repo.all())\n'
            '    print("Total:", len(repo))\n'
        )

    @staticmethod
    def _file_io(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'import json, shutil, sys\n'
            'from pathlib import Path\n\n'
            'def read_json(path):\n'
            '    with open(path, encoding="utf-8") as f: return json.load(f)\n\n'
            'def write_json(data, path, indent=2):\n'
            '    Path(path).parent.mkdir(parents=True, exist_ok=True)\n'
            '    with open(path, "w", encoding="utf-8") as f:\n'
            '        json.dump(data, f, indent=indent, ensure_ascii=False)\n'
            '    print(f"Written -> {path}")\n\n'
            'def read_text(path):\n'
            '    with open(path, encoding="utf-8") as f: return f.read()\n\n'
            'def write_text(text, path):\n'
            '    Path(path).parent.mkdir(parents=True, exist_ok=True)\n'
            '    with open(path, "w", encoding="utf-8") as f: f.write(text)\n\n'
            'if __name__ == "__main__":\n'
            '    payload = {"project": "Demo", "version": 1, "active": True}\n'
            '    write_json(payload, "output/config.json")\n'
            '    loaded = read_json("output/config.json")\n'
            '    print("Loaded:", loaded)\n'
            '    write_text("Hello World\\n", "output/hello.txt")\n'
            '    print("Text:", read_text("output/hello.txt"))\n'
        )

    @staticmethod
    def _async_t(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'import asyncio, time, threading\n'
            'from concurrent.futures import ThreadPoolExecutor, as_completed\n\n'
            'async def async_task(task_id, delay=0.3):\n'
            '    await asyncio.sleep(delay)\n'
            '    return {"id": task_id, "result": task_id ** 2}\n\n'
            'async def run_all(ids):\n'
            '    return await asyncio.gather(*(async_task(i) for i in ids))\n\n'
            'def cpu_task(n): return sum(i * i for i in range(n))\n\n'
            'def parallel(tasks, workers=4):\n'
            '    results = []\n'
            '    with ThreadPoolExecutor(max_workers=workers) as ex:\n'
            '        futs = {ex.submit(fn): fn for fn in tasks}\n'
            '        for fut in as_completed(futs):\n'
            '            try: results.append(fut.result())\n'
            '            except Exception as e: print(f"Error: {e}")\n'
            '    return results\n\n'
            'if __name__ == "__main__":\n'
            '    print("Async:", asyncio.run(run_all(range(1, 6))))\n'
            '    tasks = [lambda n=n: cpu_task(n * 1000) for n in range(1, 5)]\n'
            '    print("Parallel:", parallel(tasks))\n'
        )

    @staticmethod
    def _test(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'import unittest\n'
            'from unittest.mock import MagicMock, patch\n\n'
            'def add(a, b): return a + b\n'
            'def divide(a, b):\n'
            '    if b == 0: raise ZeroDivisionError("Cannot divide by zero")\n'
            '    return a / b\n\n'
            'class TestAdd(unittest.TestCase):\n'
            '    def test_integers(self): self.assertEqual(add(2, 3), 5)\n'
            '    def test_negatives(self): self.assertEqual(add(-1, -1), -2)\n'
            '    def test_floats(self): self.assertAlmostEqual(add(0.1, 0.2), 0.3, places=10)\n\n'
            'class TestDivide(unittest.TestCase):\n'
            '    def test_normal(self): self.assertEqual(divide(10, 2), 5.0)\n'
            '    def test_zero(self):\n'
            '        with self.assertRaises(ZeroDivisionError): divide(5, 0)\n\n'
            'if __name__ == "__main__":\n'
            '    unittest.main(verbosity=2)\n'
        )

    @staticmethod
    def _algo(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'import time, random\n\n'
            'def binary_search(arr, target, lo=0, hi=None):\n'
            '    if hi is None: hi = len(arr) - 1\n'
            '    while lo <= hi:\n'
            '        mid = (lo + hi) // 2\n'
            '        if arr[mid] == target: return mid\n'
            '        if arr[mid] < target:  lo = mid + 1\n'
            '        else:                  hi = mid - 1\n'
            '    return -1\n\n'
            'def merge_sort(arr):\n'
            '    if len(arr) <= 1: return arr\n'
            '    mid = len(arr) // 2\n'
            '    left, right = merge_sort(arr[:mid]), merge_sort(arr[mid:])\n'
            '    out, i, j = [], 0, 0\n'
            '    while i < len(left) and j < len(right):\n'
            '        if left[i] <= right[j]: out.append(left[i]); i += 1\n'
            '        else:                   out.append(right[j]); j += 1\n'
            '    return out + left[i:] + right[j:]\n\n'
            'def benchmark(name, fn, *args, runs=5):\n'
            '    times = []\n'
            '    for _ in range(runs):\n'
            '        t0 = time.perf_counter(); fn(*args); times.append(time.perf_counter() - t0)\n'
            '    print(f"{name:<20} avg={sum(times)/len(times)*1000:.3f}ms")\n\n'
            'if __name__ == "__main__":\n'
            '    n = 10000; data = random.sample(range(n * 10), n)\n'
            '    benchmark("sorted (builtin)", sorted, data)\n'
            '    benchmark("merge_sort",       merge_sort, data)\n'
            '    arr = sorted(data); target = arr[n // 2]\n'
            '    print(f"Found {target} at index {binary_search(arr, target)}")\n'
        )

    @staticmethod
    def _db(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'import sqlite3, os\n'
            'from contextlib import contextmanager\n\n'
            'DB_PATH = "app.db"\n\n'
            '@contextmanager\n'
            'def get_conn(path=DB_PATH):\n'
            '    conn = sqlite3.connect(path)\n'
            '    conn.row_factory = sqlite3.Row\n'
            '    conn.execute("PRAGMA foreign_keys=ON")\n'
            '    try:\n'
            '        yield conn; conn.commit()\n'
            '    except Exception:\n'
            '        conn.rollback(); raise\n'
            '    finally:\n'
            '        conn.close()\n\n'
            'def init_db():\n'
            '    with get_conn() as c:\n'
            '        c.executescript("""\n'
            '            CREATE TABLE IF NOT EXISTS users (\n'
            '                id    INTEGER PRIMARY KEY AUTOINCREMENT,\n'
            '                name  TEXT NOT NULL,\n'
            '                email TEXT UNIQUE NOT NULL\n'
            '            );\n'
            '        """)\n\n'
            'def create_user(name, email):\n'
            '    with get_conn() as c:\n'
            '        cur = c.execute("INSERT INTO users(name,email) VALUES(?,?)", (name,email))\n'
            '        return cur.lastrowid\n\n'
            'def list_users():\n'
            '    with get_conn() as c:\n'
            '        return [dict(r) for r in c.execute("SELECT * FROM users")]\n\n'
            'if __name__ == "__main__":\n'
            '    if os.path.exists(DB_PATH): os.remove(DB_PATH)\n'
            '    init_db()\n'
            '    create_user("Alice", "alice@example.com")\n'
            '    create_user("Bob",   "bob@example.com")\n'
            '    print("Users:", list_users())\n'
        )

    @staticmethod
    def _scraper(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'import sys\n'
            'from urllib.request import urlopen, Request\n'
            'from urllib.parse import urljoin\n'
            'from urllib.error import URLError, HTTPError\n'
            'from html.parser import HTMLParser\n\n'
            'HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PythonScraper/1.0)"}\n\n'
            'def fetch(url, timeout=10):\n'
            '    req = Request(url, headers=HEADERS)\n'
            '    try:\n'
            '        with urlopen(req, timeout=timeout) as r:\n'
            '            enc = r.headers.get_content_charset("utf-8")\n'
            '            return r.read().decode(enc, errors="replace")\n'
            '    except (HTTPError, URLError) as e:\n'
            '        print(f"Fetch error: {e}", file=sys.stderr); raise\n\n'
            'class LinkParser(HTMLParser):\n'
            '    def __init__(self, base):\n'
            '        super().__init__()\n'
            '        self.base = base; self.links = []; self._in_a = False; self._txt = []\n'
            '    def handle_starttag(self, tag, attrs):\n'
            '        if tag == "a":\n'
            '            self._in_a = True\n'
            '            for n, v in attrs:\n'
            '                if n == "href" and v:\n'
            '                    full = urljoin(self.base, v)\n'
            '                    if full.startswith("http"): self.links.append(full)\n'
            '    def handle_endtag(self, tag):\n'
            '        if tag == "a": self._in_a = False\n'
            '    def handle_data(self, data):\n'
            '        if self._in_a and data.strip(): self._txt.append(data.strip())\n\n'
            'if __name__ == "__main__":\n'
            '    url = "https://example.com"\n'
            '    html = fetch(url)\n'
            '    p = LinkParser(url); p.feed(html)\n'
            '    for href, txt in zip(p.links[:10], p._txt[:10]):\n'
            '        print(f"{txt!r:30} -> {href}")\n'
        )

    @staticmethod
    def _generic(prompt: str) -> str:
        return (
            '"""\n' + prompt + '\nDeveloped by Tukaram Hankare\n"""\n'
            'import sys, os, logging\n'
            'from typing import Any, Dict, List, Optional\n\n'
            'logging.basicConfig(\n'
            '    level=logging.INFO,\n'
            '    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",\n'
            ')\n'
            'logger = logging.getLogger(__name__)\n\n'
            'class Config:\n'
            '    DEBUG   = os.getenv("DEBUG", "false").lower() == "true"\n'
            '    VERSION = "1.0.0"\n'
            '    AUTHOR  = "Tukaram Hankare"\n\n'
            'class Application:\n'
            '    """' + prompt[:80] + '"""\n'
            '    def __init__(self, config=None):\n'
            '        self.config = config or Config()\n'
            '        self._data: List[Dict[str, Any]] = []\n'
            '        logger.info("Application v%s initialised", self.config.VERSION)\n\n'
            '    def run(self):\n'
            '        logger.info("Starting...")\n'
            '        try:\n'
            '            self._setup()\n'
            '            self._process()\n'
            '            self._report()\n'
            '            return 0\n'
            '        except KeyboardInterrupt:\n'
            '            logger.info("Interrupted"); return 0\n'
            '        except Exception:\n'
            '            logger.exception("Unhandled error"); return 1\n'
            '        finally:\n'
            '            logger.info("Cleanup done")\n\n'
            '    def _setup(self):   logger.info("Setup done")\n'
            '    def _process(self):\n'
            '        # TODO: replace with real logic for: ' + prompt[:60] + '\n'
            '        self._data = [{"id": i, "label": f"item_{i}", "score": round(i * 1.5, 2)}\n'
            '                      for i in range(1, 11)]\n'
            '        logger.info("Processed %d records", len(self._data))\n\n'
            '    def _report(self):\n'
            '        if not self._data: print("No data."); return\n'
            '        print("-" * 50)\n'
            '        for rec in self._data[:5]: print(f"  {rec}")\n'
            '        if len(self._data) > 5: print(f"  ...and {len(self._data)-5} more")\n\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(Application().run())\n'
        )


# ==============================================================================
#  MAIN APPLICATION WINDOW
# ==============================================================================
class AIPythonIDE(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}  v{APP_VERSION}  —  {APP_AUTHOR}")
        self.geometry("1400x860")
        self.minsize(900, 600)

        self._theme        = "Dark Gray"
        self._active_tab   = None
        self._tabs: Dict[str, dict] = {}
        self._tab_counter  = 0
        self._running_proc: Optional[subprocess.Popen] = None

        self._apply_style()
        self._build_menu()
        self._build_ui()
        self._bind_shortcuts()
        self._new_tab()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── TTK style ──────────────────────────────────────────────────────────────
    def _apply_style(self) -> None:
        t   = THEMES[self._theme]
        sty = ttk.Style(self)
        sty.theme_use("clam")
        sty.configure("TScrollbar", troughcolor=t["bg2"], background=t["scrollbar"],
                       bordercolor=t["bg2"], arrowcolor=t["fg2"], relief="flat")
        sty.configure("TCombobox",  fieldbackground=t["bg3"], background=t["bg3"],
                       foreground=t["fg"], selectbackground=t["select"],
                       selectforeground=t["fg"], bordercolor=t["border"])
        sty.configure("TNotebook",  background=t["tab_bg"], bordercolor=t["border"],
                       tabmargins=[2, 2, 2, 0])
        sty.configure("TNotebook.Tab", background=t["tab_bg"], foreground=t["fg2"],
                       padding=[12, 4], font=("Consolas", 9))
        sty.map("TNotebook.Tab",
                background=[("selected", t["tab_sel"])],
                foreground=[("selected", t["fg"])])
        sty.configure("TPanedwindow", background=t["border"])
        sty.configure("Sash", sashrelief="flat", sashpad=2)
        self.configure(bg=t["bg"])

    # ── Menu ───────────────────────────────────────────────────────────────────
    def _build_menu(self) -> None:
        t  = THEMES[self._theme]
        mb = tk.Menu(self, bg=t["bg2"], fg=t["fg"],
                     activebackground=t["accent"], activeforeground="#ffffff",
                     tearoff=0, relief="flat")
        self.configure(menu=mb)

        def sub():
            return tk.Menu(mb, tearoff=0, bg=t["bg2"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground="#ffffff")

        fm = sub()
        mb.add_cascade(label="File", menu=fm)
        fm.add_command(label="New Tab        Ctrl+N",      command=self._new_tab)
        fm.add_command(label="Open File...   Ctrl+O",      command=self._open_file)
        fm.add_command(label="Save           Ctrl+S",      command=self._save_file)
        fm.add_command(label="Save As...  Ctrl+Shift+S",   command=self._save_as)
        fm.add_separator()
        fm.add_command(label="Close Tab      Ctrl+W",      command=self._close_tab)
        fm.add_separator()
        fm.add_command(label="Exit",                       command=self._on_close)

        em = sub()
        mb.add_cascade(label="Edit", menu=em)
        em.add_command(label="Undo  Ctrl+Z",   command=self._undo)
        em.add_command(label="Redo  Ctrl+Y",   command=self._redo)
        em.add_separator()
        em.add_command(label="Cut   Ctrl+X",   command=self._cut)
        em.add_command(label="Copy  Ctrl+C",   command=self._copy)
        em.add_command(label="Paste Ctrl+V",   command=self._paste)
        em.add_separator()
        em.add_command(label="Select All  Ctrl+A",         command=self._select_all)
        em.add_separator()
        em.add_command(label="Find & Replace  Ctrl+H",     command=self._find_replace)
        em.add_command(label="Go to Line      Ctrl+G",     command=self._goto_line)

        rm = sub()
        mb.add_cascade(label="Run", menu=rm)
        rm.add_command(label="Run Script   F5",            command=self._run_script)
        rm.add_command(label="Stop         F6",            command=self._stop_script)
        rm.add_command(label="Run with Args F7",           command=self._run_with_args)
        rm.add_command(label="Run Selection F8",           command=self._run_selection)

        thm = sub()
        mb.add_cascade(label="Theme", menu=thm)
        for name in THEMES:
            thm.add_command(label=name, command=lambda n=name: self._switch_theme(n))

        tm = sub()
        mb.add_cascade(label="Tools", menu=tm)
        tm.add_command(label="Format Code (autopep8)",     command=self._format_code)
        tm.add_command(label="Lint Code   (pyflakes)",     command=self._lint_code)
        tm.add_command(label="Install Package...",         command=self._install_package)
        tm.add_separator()
        tm.add_command(label="Clear Output",               command=lambda: self._output.clear_output())

        hm = sub()
        mb.add_cascade(label="Help", menu=hm)
        hm.add_command(label="Keyboard Shortcuts",         command=self._show_shortcuts)
        hm.add_command(label="About",                      command=self._show_about)

    # ── UI layout ──────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        t = THEMES[self._theme]
        self._build_toolbar()

        self._main_pane = ttk.PanedWindow(self, orient="horizontal")
        self._main_pane.pack(fill="both", expand=True)

        self._sidebar = FileSidebar(self._main_pane, theme=self._theme,
                                    on_open=self._sidebar_open)
        self._main_pane.add(self._sidebar, weight=0)

        self._center_pane = ttk.PanedWindow(self._main_pane, orient="horizontal")
        self._main_pane.add(self._center_pane, weight=1)

        self._editor_area = tk.Frame(self._center_pane, bg=t["bg"])
        self._center_pane.add(self._editor_area, weight=3)

        self._v_pane = ttk.PanedWindow(self._editor_area, orient="vertical")
        self._v_pane.pack(fill="both", expand=True)

        self._notebook = ttk.Notebook(self._v_pane)
        self._v_pane.add(self._notebook, weight=3)
        self._notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self._output = OutputPanel(self._v_pane, theme=self._theme)
        self._v_pane.add(self._output, weight=1)

        self._right_frame = tk.Frame(self._center_pane, bg=t["bg2"])
        self._center_pane.add(self._right_frame, weight=1)

        self._ai_panel = AIPromptPanel(self._right_frame, theme=self._theme,
                                       on_generate=self._on_ai_generate)
        self._ai_panel.pack(fill="both", expand=True)

        self._build_statusbar()

    def _build_toolbar(self) -> None:
        t = THEMES[self._theme]
        self._toolbar = tk.Frame(self, bg=t["bg3"])
        self._toolbar.pack(fill="x")

        items = [
            ("📄 New",   self._new_tab),
            ("📂 Open",  self._open_file),
            ("💾 Save",  self._save_file),
            ("|", None),
            ("▶ Run",    self._run_script),
            ("■ Stop",   self._stop_script),
            ("|", None),
            ("↩ Undo",  self._undo),
            ("↪ Redo",  self._redo),
            ("|", None),
            ("🔍 Find",  self._find_replace),
            ("📦 Pkg",   self._install_package),
        ]
        for label, cmd in items:
            if label == "|":
                tk.Frame(self._toolbar, bg=t["border"], width=1).pack(
                    side="left", fill="y", padx=4, pady=6)
                continue
            tk.Button(self._toolbar, text=label, bg=t["btn_bg"], fg=t["btn_fg"],
                      font=("Consolas", 9), relief="flat", bd=0,
                      activebackground=t["btn_active"], activeforeground=t["fg"],
                      cursor="hand2", command=cmd,
                      padx=8, pady=4).pack(side="left", padx=2, pady=4)

        self._theme_label = tk.Label(self._toolbar, text=f"Theme: {self._theme}",
                                     bg=t["bg3"], fg=t["fg2"], font=("Consolas", 8))
        self._theme_label.pack(side="right", padx=10)

    def _build_statusbar(self) -> None:
        t = THEMES[self._theme]
        self._statusbar = tk.Frame(self, bg=t["bg3"])
        self._statusbar.pack(fill="x", side="bottom")
        self._status_left  = tk.StringVar(value="Ready")
        self._status_right = tk.StringVar(value=f"Python {sys.version.split()[0]}")
        tk.Label(self._statusbar, textvariable=self._status_left,
                 bg=t["bg3"], fg=t["fg2"], font=("Consolas", 8),
                 anchor="w", padx=8, pady=3).pack(side="left")
        tk.Label(self._statusbar, textvariable=self._status_right,
                 bg=t["bg3"], fg=t["accent"], font=("Consolas", 8),
                 padx=8, pady=3).pack(side="right")

    # ── Tab management ─────────────────────────────────────────────────────────
    def _new_tab(self, path: Optional[str] = None) -> str:
        t = THEMES[self._theme]
        self._tab_counter += 1
        tab_id = f"tab_{self._tab_counter}"

        frame  = tk.Frame(self._notebook, bg=t["bg"])
        editor = CodeEditor(frame, theme=self._theme)
        editor.pack(fill="both", expand=True)

        # Safe to bind now — CodeEditor.__init__ is fully complete
        editor.text.bind("<KeyRelease>",
                         lambda e, tid=tab_id: self._mark_modified(tid))

        title = os.path.basename(path) if path else "untitled.py"
        self._notebook.add(frame, text=f"  {title}  ")
        self._tabs[tab_id] = {"frame": frame, "editor": editor,
                               "path": path, "modified": False}
        self._active_tab = tab_id

        if path and os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    editor.set_content(f.read())
                editor.text.edit_reset()
            except Exception as e:
                self._output.write(f"Error opening {path}: {e}\n", "error")

        self._notebook.select(frame)
        return tab_id

    def _close_tab(self, *_) -> None:
        if not self._active_tab:
            return
        data = self._tabs.get(self._active_tab)
        if data and data["modified"]:
            ans = messagebox.askyesnocancel("Unsaved Changes",
                                            "Save before closing this tab?")
            if ans is None: return
            if ans: self._save_file()

        frame = data["frame"]
        try:
            idx = self._notebook.index(frame)
            self._notebook.forget(idx)
        except tk.TclError:
            pass
        del self._tabs[self._active_tab]
        self._active_tab = None

        if self._tabs:
            last_id = list(self._tabs.keys())[-1]
            self._active_tab = last_id
            self._notebook.select(self._tabs[last_id]["frame"])
        else:
            self._new_tab()

    def _on_tab_change(self, event=None) -> None:
        cur = self._notebook.select()
        for tid, data in self._tabs.items():
            if str(data["frame"]) == str(cur):
                self._active_tab = tid
                self._status_left.set(f"  {data['path'] or 'untitled.py'}")
                break

    def _mark_modified(self, tab_id: str) -> None:
        data = self._tabs.get(tab_id)
        if data and not data["modified"]:
            data["modified"] = True
            self._update_tab_title(tab_id)

    def _update_tab_title(self, tab_id: str) -> None:
        data = self._tabs.get(tab_id)
        if not data: return
        fname = os.path.basename(data["path"]) if data["path"] else "untitled.py"
        mark  = " ●" if data["modified"] else ""
        try:
            idx = self._notebook.index(data["frame"])
            self._notebook.tab(idx, text=f"  {fname}{mark}  ")
        except tk.TclError:
            pass

    def _active_editor(self) -> Optional[CodeEditor]:
        data = self._tabs.get(self._active_tab)
        return data["editor"] if data else None

    def _sidebar_open(self, path: Optional[str], action: str) -> None:
        if action == "new": self._new_tab()
        elif path: self._new_tab(path)

    # ── File ops ───────────────────────────────────────────────────────────────
    def _open_file(self, *_) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if path:
            self._new_tab(path)
            self._sidebar.add_file(path)

    def _save_file(self, *_) -> None:
        data = self._tabs.get(self._active_tab)
        if not data: return
        if not data["path"]: self._save_as(); return
        try:
            with open(data["path"], "w", encoding="utf-8") as f:
                f.write(data["editor"].get_content())
            data["modified"] = False
            self._update_tab_title(self._active_tab)
            self._status_left.set(f"Saved: {data['path']}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _save_as(self, *_) -> None:
        data = self._tabs.get(self._active_tab)
        if not data: return
        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if path:
            data["path"] = path
            self._save_file()
            self._sidebar.add_file(path)

    # ── Edit ──────────────────────────────────────────────────────────────────
    def _undo(self, *_) -> None:
        ed = self._active_editor()
        if ed:
            try: ed.text.edit_undo()
            except tk.TclError: pass

    def _redo(self, *_) -> None:
        ed = self._active_editor()
        if ed:
            try: ed.text.edit_redo()
            except tk.TclError: pass

    def _cut(self,  *_) -> None:
        ed = self._active_editor()
        if ed: ed.text.event_generate("<<Cut>>")

    def _copy(self, *_) -> None:
        ed = self._active_editor()
        if ed: ed.text.event_generate("<<Copy>>")

    def _paste(self,*_) -> None:
        ed = self._active_editor()
        if ed: ed.text.event_generate("<<Paste>>")

    def _select_all(self, *_) -> None:
        ed = self._active_editor()
        if ed:
            ed.text.tag_add("sel", "1.0", "end")
            ed.text.mark_set("insert", "end")

    # ── Find & Replace ─────────────────────────────────────────────────────────
    def _find_replace(self, *_) -> None:
        t   = THEMES[self._theme]
        win = tk.Toplevel(self)
        win.title("Find & Replace")
        win.geometry("480x240")
        win.configure(bg=t["bg2"])
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        def lbl(text):
            return tk.Label(win, text=text, bg=t["bg2"], fg=t["fg"],
                            font=("Consolas", 10), width=10, anchor="e")

        def ent():
            return tk.Entry(win, font=("Consolas", 10), bg=t["bg3"], fg=t["fg"],
                            insertbackground=t["cursor"], relief="flat", bd=1, width=36)

        lbl("Find:").grid(   row=0, column=0, padx=(10, 4), pady=10, sticky="e")
        find_e = ent()
        find_e.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="w")
        find_e.focus_set()

        lbl("Replace:").grid(row=1, column=0, padx=(10, 4), pady=0, sticky="e")
        repl_e = ent()
        repl_e.grid(row=1, column=1, padx=(0, 10), pady=0, sticky="w")

        case_var  = tk.BooleanVar()
        regex_var = tk.BooleanVar()
        opt = tk.Frame(win, bg=t["bg2"])
        opt.grid(row=2, column=0, columnspan=2, padx=10, pady=6, sticky="w")
        for text, var in [("Case sensitive", case_var), ("Regex", regex_var)]:
            tk.Checkbutton(opt, text=text, variable=var, bg=t["bg2"], fg=t["fg"],
                           selectcolor=t["bg3"], activebackground=t["bg2"],
                           font=("Consolas", 9)).pack(side="left", padx=8)

        def _find():
            ed = self._active_editor()
            if not ed: return
            ed.text.tag_remove("found", "1.0", "end")
            needle = find_e.get()
            if not needle: return
            content = ed.text.get("1.0", "end-1c")
            try:
                flags = 0 if case_var.get() else re.IGNORECASE
                pat   = needle if regex_var.get() else re.escape(needle)
                count = 0
                for m in re.finditer(pat, content, flags):
                    ed.text.tag_add("found", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
                    count += 1
                ed.text.tag_configure("found", background=t["warning"],
                                      foreground="#000000")
                self._output.write(f"Found {count} match(es)\n", "info")
            except re.error as err:
                self._output.write(f"Regex error: {err}\n", "error")

        def _replace_all():
            ed = self._active_editor()
            if not ed: return
            needle = find_e.get()
            repl   = repl_e.get()
            if not needle: return
            content = ed.text.get("1.0", "end-1c")
            try:
                flags = 0 if case_var.get() else re.IGNORECASE
                pat   = needle if regex_var.get() else re.escape(needle)
                new_c, n = re.subn(pat, repl, content, flags=flags)
                if n:
                    ed.set_content(new_c)
                    self._output.write(f"Replaced {n} occurrence(s)\n", "success")
                else:
                    self._output.write("No matches found\n", "warn")
            except re.error as err:
                self._output.write(f"Regex error: {err}\n", "error")

        btn_row = tk.Frame(win, bg=t["bg2"])
        btn_row.grid(row=3, column=0, columnspan=2, pady=12)
        for label, cmd in [("Find All", _find), ("Replace All", _replace_all),
                            ("Close", win.destroy)]:
            tk.Button(btn_row, text=label, bg=t["btn_bg"], fg=t["btn_fg"],
                      font=("Consolas", 9), relief="flat", bd=0,
                      activebackground=t["btn_active"], activeforeground=t["fg"],
                      cursor="hand2", command=cmd,
                      padx=12, pady=5).pack(side="left", padx=5)
        find_e.bind("<Return>", lambda e: _find())

    # ── Go to line ─────────────────────────────────────────────────────────────
    def _goto_line(self, *_) -> None:
        t   = THEMES[self._theme]
        win = tk.Toplevel(self)
        win.title("Go to Line")
        win.geometry("280x120")
        win.configure(bg=t["bg2"])
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Line number:", bg=t["bg2"], fg=t["fg"],
                 font=("Consolas", 10)).pack(pady=(16, 4))
        e = tk.Entry(win, font=("Consolas", 11), bg=t["bg3"], fg=t["fg"],
                     insertbackground=t["cursor"], relief="flat", bd=1, width=14)
        e.pack(ipady=4)
        e.focus_set()

        def _go(*_):
            ed = self._active_editor()
            if not ed: return
            try:
                ln = int(e.get())
                ed.text.see(f"{ln}.0")
                ed.text.mark_set("insert", f"{ln}.0")
                win.destroy()
            except ValueError:
                pass

        e.bind("<Return>", _go)
        tk.Button(win, text="Go", bg=t["accent"], fg="#ffffff",
                  font=("Consolas", 9), relief="flat", bd=0,
                  activebackground=t["accent2"], cursor="hand2",
                  command=_go, padx=16, pady=4).pack(pady=8)

    # ── Run / Stop ─────────────────────────────────────────────────────────────
    def _run_script(self, *_) -> None:
        self._save_file()
        data = self._tabs.get(self._active_tab)
        if data and data["path"]:
            self._execute(data["path"])
        else:
            ed = self._active_editor()
            if not ed: return
            code = ed.get_content().strip()
            if not code:
                self._output.write("Nothing to run.\n", "warn")
                return
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False,
                                             mode="w", encoding="utf-8") as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            self._execute(tmp_path, temp=True)

    def _run_selection(self, *_) -> None:
        ed = self._active_editor()
        if not ed: return
        try:
            code = ed.text.get("sel.first", "sel.last").strip()
        except tk.TclError:
            self._output.write("No selection.\n", "warn")
            return
        if not code: return
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False,
                                         mode="w", encoding="utf-8") as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        self._execute(tmp_path, temp=True, label="<selection>")

    def _run_with_args(self, *_) -> None:
        t   = THEMES[self._theme]
        win = tk.Toplevel(self)
        win.title("Run with Arguments")
        win.geometry("420x130")
        win.configure(bg=t["bg2"])
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Script arguments:", bg=t["bg2"], fg=t["fg"],
                 font=("Consolas", 10)).pack(pady=(16, 4))
        e = tk.Entry(win, font=("Consolas", 10), bg=t["bg3"], fg=t["fg"],
                     insertbackground=t["cursor"], relief="flat", bd=1, width=48)
        e.pack(ipady=4)

        def _run(*_):
            args = e.get().split()
            win.destroy()
            self._save_file()
            data = self._tabs.get(self._active_tab)
            if data and data["path"]:
                self._execute(data["path"], extra_args=args)

        e.bind("<Return>", _run)
        tk.Button(win, text="▶ Run", bg=t["accent"], fg="#ffffff",
                  font=("Consolas", 9), relief="flat", bd=0,
                  activebackground=t["accent2"], cursor="hand2",
                  command=_run, padx=14, pady=4).pack(pady=8)

    def _execute(self, path: str, temp: bool = False,
                 extra_args: Optional[List[str]] = None,
                 label: Optional[str] = None) -> None:
        self._output.clear_output()
        display = label or os.path.basename(path)
        self._output.write(f"▶  Running: {display}\n", "info")
        self._output.write("─" * 60 + "\n", "info")
        self._status_left.set(f"Running: {display}")
        cmd = [sys.executable, path] + (extra_args or [])
        cwd = os.path.dirname(path) or "."

        def _worker():
            try:
                self._running_proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8", errors="replace", cwd=cwd)
                stdout, stderr = self._running_proc.communicate()
                if stdout:
                    self.after(0, lambda: self._output.write(stdout))
                if stderr:
                    self.after(0, lambda: self._output.write(stderr, "error"))
                rc  = self._running_proc.returncode
                tag = "success" if rc == 0 else "error"
                msg = f"\n{'─'*60}\nProcess exited with code {rc}\n"
                self.after(0, lambda: self._output.write(msg, tag))
                self.after(0, lambda: self._status_left.set(f"Done (exit {rc})"))
            except Exception as exc:
                tb = traceback.format_exc()
                self.after(0, lambda: self._output.write(
                    f"Launch error: {exc}\n{tb}", "error"))
            finally:
                self._running_proc = None
                if temp:
                    try: os.unlink(path)
                    except OSError: pass

        threading.Thread(target=_worker, daemon=True).start()

    def _stop_script(self, *_) -> None:
        if self._running_proc:
            try:
                self._running_proc.terminate()
                self._output.write("\n⏹  Terminated by user.\n", "warn")
                self._status_left.set("Stopped")
            except Exception as e:
                self._output.write(f"Could not stop: {e}\n", "error")
        else:
            self._output.write("No process running.\n", "warn")

    # ── Tools ──────────────────────────────────────────────────────────────────
    def _format_code(self) -> None:
        ed = self._active_editor()
        if not ed: return
        try:
            import autopep8
            result = autopep8.fix_code(ed.get_content(),
                                        options={"max_line_length": 100})
            ed.set_content(result)
            self._output.write("✔ Formatted with autopep8\n", "success")
        except ImportError:
            self._output.write(
                "autopep8 not installed — run: pip install autopep8\n", "warn")

    def _lint_code(self) -> None:
        ed = self._active_editor()
        if not ed: return
        code = ed.get_content()
        try:
            import pyflakes.api
            buf = io.StringIO()

            class _Rep:
                def unexpectedError(self, fn, msg): buf.write(f"Error: {msg}\n")
                def syntaxError(self, fn, msg, row, col, src):
                    buf.write(f"SyntaxError line {row}: {msg}\n")
                def flake(self, msg): buf.write(str(msg) + "\n")

            pyflakes.api.check(code, "<editor>", reporter=_Rep())
            result = buf.getvalue()
            if result:
                self._output.write("⚠ Lint results:\n" + result, "warn")
            else:
                self._output.write("✔ No issues (pyflakes)\n", "success")
        except ImportError:
            self._output.write(
                "pyflakes not installed — run: pip install pyflakes\n", "warn")

    def _install_package(self) -> None:
        t   = THEMES[self._theme]
        win = tk.Toplevel(self)
        win.title("Install Package")
        win.geometry("380x140")
        win.configure(bg=t["bg2"])
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Package name(s):", bg=t["bg2"], fg=t["fg"],
                 font=("Consolas", 10)).pack(pady=(16, 6))
        e = tk.Entry(win, font=("Consolas", 11), bg=t["bg3"], fg=t["fg"],
                     insertbackground=t["cursor"], relief="flat", bd=1, width=34)
        e.pack(ipady=4)
        e.focus_set()

        def _install(*_):
            pkgs = e.get().strip().split()
            if not pkgs: return
            win.destroy()
            self._output.write(f"📦  Installing: {' '.join(pkgs)}\n", "info")

            def _worker():
                for pkg in pkgs:
                    try:
                        r = subprocess.run(
                            [sys.executable, "-m", "pip", "install", pkg],
                            capture_output=True, text=True, encoding="utf-8")
                        self.after(0, lambda o=r.stdout: self._output.write(o))
                        if r.returncode == 0:
                            self.after(0, lambda p=pkg: self._output.write(
                                f"✔ {p} installed\n", "success"))
                        else:
                            self.after(0, lambda e=r.stderr: self._output.write(e, "error"))
                    except Exception as ex:
                        self.after(0, lambda ex=ex: self._output.write(
                            f"Error: {ex}\n", "error"))

            threading.Thread(target=_worker, daemon=True).start()

        e.bind("<Return>", _install)
        tk.Button(win, text="Install", bg=t["accent"], fg="#ffffff",
                  font=("Consolas", 9), relief="flat", bd=0,
                  activebackground=t["accent2"], cursor="hand2",
                  command=_install, padx=14, pady=4).pack(pady=8)

    # ── AI code generation ─────────────────────────────────────────────────────
    def _on_ai_generate(self, prompt: str, api_key: str, mode: str) -> None:
        if not prompt:
            self._output.write("⚠ Please enter a description.\n", "warn")
            return
        self._ai_panel.set_status("⏳ Generating…")
        self._output.write(f"\n🤖  [{mode}] {prompt[:80]}\n", "info")
        self._output.write("─" * 60 + "\n")
        threading.Thread(target=self._ai_worker,
                         args=(prompt, api_key, mode), daemon=True).start()

    def _ai_worker(self, prompt: str, api_key: str, mode: str) -> None:
        try:
            if ANTHROPIC_AVAILABLE and api_key:
                code = self._call_api(prompt, api_key, mode)
            else:
                code = CodeTemplates.generate(prompt, mode)
                if not ANTHROPIC_AVAILABLE:
                    self.after(0, lambda: self._output.write(
                        "ℹ anthropic SDK not installed — using local templates.\n"
                        "  Install with: pip install anthropic\n", "warn"))
            if code:
                self.after(0, lambda: self._apply_generated(code, mode))
            else:
                self.after(0, lambda: self._output.write("No code generated.\n", "warn"))
        except Exception:
            tb = traceback.format_exc()
            self.after(0, lambda: self._output.write(f"AI error:\n{tb}", "error"))
        finally:
            self.after(0, lambda: self._ai_panel.set_status(
                "Ready — Ctrl+Enter to generate"))

    def _call_api(self, prompt: str, api_key: str, mode: str) -> str:
        sys_msgs = {
            "Generate New Script":
                "You are an expert Python developer. Generate clean, well-commented, "
                "production-ready Python code. Return ONLY the Python code with no "
                "markdown fences or explanations outside code comments. Include imports, "
                "type hints, error handling, and docstrings.",
            "Improve Existing Code":
                "Improve the provided Python code for readability and efficiency. "
                "Return ONLY the improved Python code.",
            "Fix Bugs in Code":
                "Find and fix all bugs in the provided Python code. Add brief comments "
                "explaining each fix. Return ONLY the corrected code.",
            "Explain Code":
                "Add comprehensive inline comments and docstrings explaining every part. "
                "Return ONLY the commented Python code.",
            "Add Comments":
                "Add thorough docstrings and inline comments. Return ONLY the commented code.",
        }
        client  = anthropic.Anthropic(api_key=api_key)
        sys_msg = sys_msgs.get(mode, sys_msgs["Generate New Script"])
        ed      = self._active_editor()
        ctx     = ""
        if ed and mode != "Generate New Script":
            ctx = f"\n\nCode:\n```python\n{ed.get_content()}\n```"
        msg = client.messages.create(
            model="claude-opus-4-5", max_tokens=4096,
            system=sys_msg,
            messages=[{"role": "user", "content": f"{prompt}{ctx}"}],
        )
        raw = msg.content[0].text
        m   = re.search(r"```(?:python)?\n([\s\S]*?)```", raw)
        return m.group(1).strip() if m else raw.strip()

    def _apply_generated(self, code: str, mode: str) -> None:
        if mode in ("Improve Existing Code","Fix Bugs in Code","Explain Code","Add Comments"):
            ed = self._active_editor()
            if ed:
                ed.set_content(code)
                self._mark_modified(self._active_tab)
                self._output.write(
                    f"✔ Updated current tab ({len(code.splitlines())} lines)\n", "success")
                return
        tab_id = self._new_tab()
        self._tabs[tab_id]["editor"].set_content(code)
        self._mark_modified(tab_id)
        self._output.write(
            f"✔ Generated {len(code.splitlines())} lines in new tab\n", "success")

    # ── Theme switch ───────────────────────────────────────────────────────────
    def _switch_theme(self, name: str) -> None:
        self._theme = name
        t           = THEMES[name]
        self.configure(bg=t["bg"])
        self._apply_style()

        self._toolbar.configure(bg=t["bg3"])
        self._theme_label.configure(bg=t["bg3"], fg=t["fg2"],
                                    text=f"Theme: {name}")
        for w in self._toolbar.winfo_children():
            if isinstance(w, tk.Button):
                w.configure(bg=t["btn_bg"], fg=t["btn_fg"],
                            activebackground=t["btn_active"],
                            activeforeground=t["fg"])
            elif isinstance(w, tk.Frame):
                w.configure(bg=t["border"])

        self._statusbar.configure(bg=t["bg3"])
        for w in self._statusbar.winfo_children():
            try: w.configure(bg=t["bg3"])
            except tk.TclError: pass

        for data in self._tabs.values():
            data["editor"].set_theme(name)

        self._output.set_theme(name)
        self._ai_panel.set_theme(name)
        self._sidebar.set_theme(name)
        self._editor_area.configure(bg=t["bg"])
        self._right_frame.configure(bg=t["bg2"])

    # ── Shortcuts ──────────────────────────────────────────────────────────────
    def _bind_shortcuts(self) -> None:
        self.bind("<Control-n>", lambda e: self._new_tab())
        self.bind("<Control-o>", self._open_file)
        self.bind("<Control-s>", self._save_file)
        self.bind("<Control-S>", self._save_as)
        self.bind("<Control-w>", self._close_tab)
        self.bind("<Control-z>", self._undo)
        self.bind("<Control-y>", self._redo)
        self.bind("<Control-a>", self._select_all)
        self.bind("<Control-h>", self._find_replace)
        self.bind("<Control-g>", self._goto_line)
        self.bind("<F5>",        self._run_script)
        self.bind("<F6>",        self._stop_script)
        self.bind("<F7>",        self._run_with_args)
        self.bind("<F8>",        self._run_selection)

    # ── Help dialogs ───────────────────────────────────────────────────────────
    def _show_shortcuts(self) -> None:
        t   = THEMES[self._theme]
        win = tk.Toplevel(self)
        win.title("Keyboard Shortcuts")
        win.geometry("420x420")
        win.configure(bg=t["bg2"])
        win.resizable(False, False)
        win.transient(self)

        tk.Label(win, text="Keyboard Shortcuts", bg=t["bg2"], fg=t["fg"],
                 font=("Consolas", 12, "bold")).pack(pady=(16, 8))

        pairs = [
            ("Ctrl+N",       "New Tab"),
            ("Ctrl+O",       "Open File"),
            ("Ctrl+S",       "Save"),
            ("Ctrl+Shift+S", "Save As"),
            ("Ctrl+W",       "Close Tab"),
            ("Ctrl+Z",       "Undo"),
            ("Ctrl+Y",       "Redo"),
            ("Ctrl+A",       "Select All"),
            ("Ctrl+H",       "Find & Replace"),
            ("Ctrl+G",       "Go to Line"),
            ("F5",           "Run Script"),
            ("F6",           "Stop Script"),
            ("F7",           "Run with Arguments"),
            ("F8",           "Run Selection"),
            ("Ctrl+Enter",   "Generate AI Code (AI panel)"),
        ]
        for key, desc in pairs:
            row = tk.Frame(win, bg=t["bg2"])
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=key, bg=t["bg3"], fg=t["accent"],
                     font=("Consolas", 9, "bold"),
                     width=18, anchor="w", padx=4).pack(side="left")
            tk.Label(row, text=desc, bg=t["bg2"], fg=t["fg"],
                     font=("Consolas", 9), anchor="w").pack(side="left", padx=8)

        tk.Button(win, text="Close", bg=t["btn_bg"], fg=t["btn_fg"],
                  font=("Consolas", 9), relief="flat", bd=0,
                  activebackground=t["btn_active"], cursor="hand2",
                  command=win.destroy, padx=14, pady=5).pack(pady=14)

    def _show_about(self) -> None:
        t   = THEMES[self._theme]
        win = tk.Toplevel(self)
        win.title(f"About {APP_NAME}")
        win.geometry("400x280")
        win.configure(bg=t["bg2"])
        win.resizable(False, False)
        win.transient(self)

        tk.Label(win, text="⚡", bg=t["bg2"], fg=t["accent"],
                 font=("Segoe UI Emoji", 40)).pack(pady=(20, 4))
        tk.Label(win, text=APP_NAME, bg=t["bg2"], fg=t["fg"],
                 font=("Consolas", 15, "bold")).pack()
        tk.Label(win, text=f"Version {APP_VERSION}", bg=t["bg2"], fg=t["fg2"],
                 font=("Consolas", 10)).pack(pady=(2, 0))
        tk.Label(win, text=f"Developed by {APP_AUTHOR}", bg=t["bg2"], fg=t["accent"],
                 font=("Consolas", 11)).pack(pady=(6, 0))
        tk.Label(win,
                 text="Production-grade AI-powered Python IDE\n"
                      "Syntax highlighting  ·  Multi-tab editor\n"
                      "AI code generation  ·  3 themes\n"
                      "Run · Lint · Format · Install packages",
                 bg=t["bg2"], fg=t["fg2"],
                 font=("Consolas", 9), justify="center").pack(pady=10)
        tk.Button(win, text="Close", bg=t["accent"], fg="#ffffff",
                  font=("Consolas", 9), relief="flat", bd=0,
                  activebackground=t["accent2"], cursor="hand2",
                  command=win.destroy, padx=20, pady=5).pack(pady=4)

    # ── Close ──────────────────────────────────────────────────────────────────
    def _on_close(self) -> None:
        unsaved = [d for d in self._tabs.values() if d["modified"]]
        if unsaved:
            ans = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"{len(unsaved)} tab(s) have unsaved changes.\nSave before exiting?")
            if ans is None: return
            if ans:
                for tid in list(self._tabs):
                    if self._tabs[tid]["modified"]:
                        self._active_tab = tid
                        self._save_file()

        if self._running_proc:
            try: self._running_proc.terminate()
            except OSError: pass

        self.destroy()


# ==============================================================================
#  ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    app = AIPythonIDE()
    app.mainloop()
