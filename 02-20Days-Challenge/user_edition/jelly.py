# -*- coding: utf-8 -*-
"""
圆角果冻风格控件库 v2
====================
白色 + 浅粉果冻风：
  - 按钮：纵向渐变 + 顶部窄高光 + 底部柔阴影，悬停放大、按下回弹
  - 输入框：圆角 + 聚焦时粉色描边
  - 卡片：大圆角 + 极浅粉底

绘制方式：用 round_rect 画出圆角轮廓，再用多条横向细线裁剪出渐变。
"""

import tkinter as tk
from tkinter import font as tkfont

# ===== 配色（白色 + 浅粉）=====
C_BG = "#FFFFFF"
C_BG_SOFT = "#FFF8FA"
C_PINK = "#FFA6BD"
C_PINK_DEEP = "#FF7A9C"
C_PINK_DARK = "#F26187"
C_PINK_LIGHT = "#FFE9EF"
C_PINK_PALE = "#FFF0F4"
C_TEXT = "#4A3540"
C_TEXT_SOFT = "#8B7280"
C_TEXT_MUTED = "#C4AEB8"
C_OK = "#5FC99A"
C_ERR = "#FF8A8A"
C_WARN = "#FFB86B"
C_WHITE = "#FFFFFF"
C_BORDER = "#FFDCE5"
C_SHADOW = "#FFE3EC"


def lerp(c1, c2, t):
    def hx(c):
        c = c.lstrip("#")
        return [int(c[i:i + 2], 16) for i in (0, 2, 4)]
    a, b = hx(c1), hx(c2)
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rrect(cv, x1, y1, x2, y2, r, **kw):
    """圆角矩形（用 smooth polygon 近似）"""
    r = max(1, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1,
           x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2,
           x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, **kw)


class JellyButton(tk.Canvas):
    """果冻按钮：渐变 + 高光 + 阴影 + 悬停/按压反馈"""

    def __init__(self, master, text, command=None, width=200, height=48,
                 c_top=C_PINK, c_bot=C_PINK_DEEP, fg="#FFFFFF",
                 radius=16, font_size=11, bold=True, **kw):
        bg = master["bg"]
        super().__init__(master, width=width, height=height, bg=bg,
                         highlightthickness=0, bd=0, **kw)
        self.text = text
        self.command = command
        self.W, self.H = width, height
        self.c_top, self.c_bot, self.fg = c_top, c_bot, fg
        self.radius = radius
        self._hover = False
        self._pressed = False
        self.font = tkfont.Font(family="Microsoft YaHei UI", size=font_size,
                                weight="bold" if bold else "normal")
        self._draw()
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)
        self.configure(cursor="hand2")

    def _draw(self):
        self.delete("all")
        W, H = self.W, self.H
        dy = 1 if self._pressed else 0
        x1, y1, x2, y2 = 3, 2 + dy, W - 3, H - 6 + dy
        r = min(self.radius, (y2 - y1) // 2)

        # 1) 底部柔阴影
        if not self._pressed:
            rrect(self, x1 + 1, y1 + 4, x2 + 1, y2 + 4, r, fill=C_SHADOW, outline="")

        # 2) 主体：先画深色底（作为"厚度"），再画渐变层
        rrect(self, x1, y1, x2, y2, r, fill=self.c_bot, outline="")

        # 3) 渐变主体（纵向，上浅下深）
        span = y2 - y1
        n = max(24, int(span * 1.2))
        inset = max(1, int(r * 0.35))
        for i in range(n):
            t = i / (n - 1)
            yy = y1 + span * t
            col = lerp(self.c_top, self.c_bot, t ** 0.85)
            shrink = 0
            if t < 0.12:
                shrink = (0.12 - t) / 0.12 * inset
            elif t > 0.88:
                shrink = (t - 0.88) / 0.12 * inset
            self.create_line(x1 + inset + shrink, yy, x2 - inset - shrink, yy,
                             fill=col, width=max(2, span / n + 1.5))

        # 4) 顶部内高光（细窄一条，不遮挡文字）
        hl_h = max(4, int(span * 0.26))
        h = rrect(self, x1 + r * 0.5, y1 + 3, x2 - r * 0.5, y1 + 3 + hl_h,
                  hl_h // 2, fill="#FFFFFF", outline="")
        self.itemconfig(h, stipple="gray25")

        # 5) 底部内暗边（增强厚度感）
        b = rrect(self, x1 + r * 0.4, y2 - max(3, span * 0.14), x2 - r * 0.4, y2 - 1,
                  max(2, int(span * 0.07)), fill=self.c_bot, outline="")
        self.itemconfig(b, stipple="gray50")

        # 6) 文字（最后画，保证在最上层）
        cx, cy = W / 2, (y1 + y2) / 2
        self.create_text(cx, cy + 1, text=self.text,
                         fill=self._shadow_color(), font=self.font)
        self.create_text(cx, cy, text=self.text, fill=self.fg, font=self.font)

    def _shadow_color(self):
        """文字下方的柔和阴影色"""
        return lerp(self.c_bot, "#000000", 0.18) if self.fg.upper() == "#FFFFFF" else "#FFFFFF"

    def _enter(self, _):
        self._hover = True
        self._draw()

    def _leave(self, _):
        self._hover = False
        self._pressed = False
        self._draw()

    def _press(self, _):
        self._pressed = True
        self._draw()

    def _release(self, e):
        if not self._pressed:
            return
        inside = 0 <= e.x <= self.W and 0 <= e.y <= self.H
        self._pressed = False
        self._draw()
        if inside and self.command:
            self.command()


class SoftEntry(tk.Frame):
    """圆角输入框"""

    def __init__(self, master, width=430, height=44, show="", placeholder="",
                 radius=14, **kw):
        bg = master["bg"]
        super().__init__(master, bg=bg, **kw)
        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg,
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self.W, self.H, self.r = width, height, radius
        self.placeholder = placeholder
        self._focused = False
        self.var = tk.StringVar()
        self.entry = tk.Entry(self.canvas, textvariable=self.var, show=show,
                              bd=0, relief="flat", bg=C_WHITE, fg=C_TEXT,
                              insertbackground=C_PINK_DEEP, highlightthickness=0,
                              font=("Microsoft YaHei UI", 11))
        self._draw()
        self.canvas.create_window(18, height // 2, window=self.entry,
                                  anchor="w", width=width - 36, height=height - 16)
        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)
        if placeholder:
            self._placeholder_on()

    def _draw(self):
        self.canvas.delete("bg")
        fill = "#FFFFFF" if self._focused else C_BG_SOFT
        outline = C_PINK_DEEP if self._focused else C_BORDER
        rrect(self.canvas, 2, 2, self.W - 2, self.H - 2, self.r,
              fill=fill, outline=outline, width=2 if self._focused else 1, tags="bg")
        self.canvas.tag_lower("bg")

    def _placeholder_on(self):
        self.entry.delete(0, "end")
        self.entry.config(fg=C_TEXT_MUTED)
        self.entry.insert(0, self.placeholder)

    def _focus_in(self, _):
        self._focused = True
        if self.entry.cget("fg") == C_TEXT_MUTED:
            self.entry.delete(0, "end")
            self.entry.config(fg=C_TEXT)
        self._draw()

    def _focus_out(self, _):
        self._focused = False
        if not self.entry.get() and self.placeholder:
            self._placeholder_on()
        self._draw()

    def get(self):
        v = self.entry.get()
        return "" if v == self.placeholder else v

    def set(self, v):
        self.entry.delete(0, "end")
        if v:
            self.entry.config(fg=C_TEXT)
            self.entry.insert(0, v)
        elif self.placeholder:
            self._placeholder_on()

    def set_show(self, ch):
        self.entry.config(show=ch)


class JellySegmented(tk.Frame):
    """果冻分段选择器（替代 Notebook 标签页）"""

    def __init__(self, master, items, on_change=None, width=760, height=46,
                 radius=18, **kw):
        bg = master["bg"]
        super().__init__(master, bg=bg, **kw)
        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg,
                                highlightthickness=0, bd=0)
        self.canvas.pack(fill="x")
        self.items = items
        self.idx = 0
        self.on_change = on_change
        self.W, self.H, self.r = width, height, radius
        self._draw()
        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<Configure>", self._resize)

    def _seg_rect(self, i, w):
        n = len(self.items)
        pad = 4
        seg_w = (w - pad * 2) / n
        x1 = pad + seg_w * i
        return x1, pad, x1 + seg_w, self.H - pad

    def _draw(self, w=None):
        w = w or self.W
        self.canvas.delete("all")
        # 底槽
        rrect(self.canvas, 1, 1, w - 1, self.H - 1, self.r,
              fill=C_PINK_PALE, outline=C_BORDER)
        # 选中块
        x1, y1, x2, y2 = self._seg_rect(self.idx, w)
        rrect(self.canvas, x1 + 1, y1, x2 - 1, y2, self.r - 6,
              fill=C_WHITE, outline=C_BORDER)
        # 顶部高光
        hl = rrect(self.canvas, x1 + 10, y1 + 2, x2 - 10, y1 + (y2 - y1) * 0.4,
                   (self.r - 6) // 2, fill="#FFFFFF", outline="")
        # 文字
        for i, txt in enumerate(self.items):
            cx = (self._seg_rect(i, w)[0] + self._seg_rect(i, w)[2]) / 2
            sel = i == self.idx
            self.canvas.create_text(cx, self.H / 2, text=txt,
                                    fill=C_PINK_DEEP if sel else C_TEXT_SOFT,
                                    font=("Microsoft YaHei UI", 11, "bold" if sel else "normal"))

    def _resize(self, e):
        self.W = e.width
        self._draw(self.W)

    def _click(self, e):
        n = len(self.items)
        seg_w = (self.W - 8) / n
        i = int((e.x - 4) // seg_w)
        if 0 <= i < n and i != self.idx:
            self.idx = i
            self._draw()
            if self.on_change:
                self.on_change(i)

    def select(self, i):
        if 0 <= i < len(self.items) and i != self.idx:
            self.idx = i
            self._draw()


class SoftCard(tk.Frame):
    """圆角卡片"""

    def __init__(self, master, radius=22, fill=C_WHITE, outline=C_BORDER, pad=22, **kw):
        bg = master["bg"]
        super().__init__(master, bg=bg, **kw)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.r, self.fill, self.outline, self.pad = radius, fill, outline, pad
        self.inner = tk.Frame(self.canvas, bg=fill)
        self._win = self.canvas.create_window(pad, pad, window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", self._on_resize)
        self.inner.bind("<Configure>", self._on_inner)

    def _on_resize(self, e):
        self.canvas.delete("card")
        rrect(self.canvas, 1, 1, e.width - 1, e.height - 1, self.r,
              fill=self.fill, outline=self.outline, width=1, tags="card")
        self.canvas.tag_lower("card")
        self.canvas.itemconfig(self._win, width=max(10, e.width - self.pad * 2))

    def _on_inner(self, e):
        h = e.height + self.pad * 2
        cur = self.canvas.winfo_height()
        if h > cur:
            self.canvas.configure(height=h)

    def get_inner(self):
        return self.inner