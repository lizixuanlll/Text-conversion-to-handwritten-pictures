#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手写体图片生成器 - 将文本转换为逼真的手写作业图片"""

import os
import sys
import random
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).parent
FONT_DIR = SCRIPT_DIR / "font"
DESKTOP = Path.home() / "Desktop"

IMG_WIDTH = 1998
IMG_HEIGHT = 2585
MARGIN_LEFT = 100
MARGIN_RIGHT = 50
MARGIN_TOP = 210
MARGIN_BOTTOM = 100
DEFAULT_FONT_SIZE = 60


def create_background(line_spacing, margin_top=None):
    mt = margin_top if margin_top is not None else MARGIN_TOP
    bg = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), "white")
    draw = ImageDraw.Draw(bg)
    for y in range(mt, IMG_HEIGHT - MARGIN_BOTTOM, line_spacing):
        draw.line([(50, y), (IMG_WIDTH - 50, y)], fill=(255, 100, 100), width=3)
    return bg


def wrap_text_pixel(text, font, indent_px):
    """像素级换行：用给定字体测量宽度，每行填到接近右边界"""
    usable_w = int((IMG_WIDTH - MARGIN_LEFT - MARGIN_RIGHT) * 0.92)  # 8%安全余量，因为渲染时混合字体会更宽
    all_lines = []

    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            all_lines.append("")
            continue

        current_line = ""
        x = indent_px  # 首行缩进

        for char in paragraph:
            bbox = font.getbbox(char)
            char_w = (bbox[2] - bbox[0]) if bbox else DEFAULT_FONT_SIZE
            spacing = random.randint(1, 2)

            if x + char_w + spacing > usable_w and current_line:
                all_lines.append(current_line)
                current_line = char
                x = char_w + spacing
            else:
                current_line += char
                x += char_w + spacing

        if current_line:
            all_lines.append(current_line)

    return all_lines


def get_font_for_char(fonts, main_name, char):
    if random.random() < 0.6:
        return fonts[main_name], main_name
    others = {k: v for k, v in fonts.items() if k != main_name}
    if others:
        name = random.choice(list(others.keys()))
        return others[name], name
    return fonts[main_name], main_name


def render_page(lines, page_num, fonts, main_name, output_dir,
                font_size, line_spacing, margin_top):
    """渲染一页，直接画出预拆好的行"""
    import random as rnd
    bg = create_background(line_spacing, margin_top)
    draw = ImageDraw.Draw(bg)

    y_offsets = {
        "MengMeiZiTi-1": 0,
        "千图纤墨体": int(-8 * font_size / DEFAULT_FONT_SIZE),
        "李国夫手写体": 0,
        "pigtruman手写体": int(2 * font_size / DEFAULT_FONT_SIZE),
        "白路俏丽手写体": int(1 * font_size / DEFAULT_FONT_SIZE),
        "ChenJingDeZiWanZhengBan-1": 0,
        "LikeJianJianTi-Regular": 0,
        "白路彤彤手写体": 0,
    }

    indent = int(font_size * 0.85)

    for i, line in enumerate(lines):
        y = margin_top + i * line_spacing
        if not line:
            continue

        is_first = (i == 0) or (i > 0 and not lines[i - 1])
        x = MARGIN_LEFT + (indent if is_first else 0)

        for char in line:
            font_obj, font_name = get_font_for_char(fonts, main_name, char)
            y_off = y_offsets.get(font_name, 0)

            sv = rnd.randint(-2, 2)
            if sv != 0:
                try:
                    varied_font = ImageFont.truetype(
                        str(FONT_DIR / f"{font_name}.ttf"), size=font_size + sv)
                except Exception:
                    varied_font = font_obj
            else:
                varied_font = font_obj

            draw.text(
                (x + rnd.randint(-1, 1), y + rnd.randint(-1, 1) + y_off),
                char, font=varied_font, fill=(30, 30, 30))

            bbox = draw.textbbox((0, 0), char, font=varied_font)
            char_w = bbox[2] - bbox[0]
            x += char_w + rnd.randint(1, 3)

    output_path = output_dir / f"result_{page_num}.jpg"
    bg.save(output_path, quality=95)
    return output_path


def calc_layout(text, page_count):
    """二分查找最佳字号以塞进指定页数"""
    if page_count <= 0:
        return DEFAULT_FONT_SIZE, 90, MARGIN_TOP

    indent = int(DEFAULT_FONT_SIZE * 0.85)
    lo, hi = 18, 75
    best = lo

    for _ in range(20):
        mid = (lo + hi) // 2
        line_h = int(mid * 1.45)
        lpp = max(1, (IMG_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM) // line_h)

        try:
            font = ImageFont.truetype(str(next(FONT_DIR.glob("*.ttf"))), size=mid)
            lines = wrap_text_pixel(text, font, indent * mid // DEFAULT_FONT_SIZE)
            if len(lines) <= page_count * lpp:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        except Exception:
            hi = mid - 1

    line_h = int(best * 1.45)
    lpp = max(1, (IMG_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM) // line_h)
    print(f"自适应字号: {best}px, 每页约 {lpp} 行")
    return best, line_h, MARGIN_TOP


def generate(text, output_dir, main_font="李国夫手写体", page_count=0):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    text = text.strip()
    if not text:
        print("错误：没有有效文本内容")
        return 0

    font_size, line_spacing, margin_top = calc_layout(text, page_count)
    lpp = max(1, (IMG_HEIGHT - margin_top - MARGIN_BOTTOM) // line_spacing)

    # 加载字体
    fonts = {}
    for f in FONT_DIR.glob("*.ttf"):
        try:
            fonts[f.stem] = ImageFont.truetype(str(f), size=font_size)
        except Exception:
            pass
    main_name = main_font if main_font in fonts else list(fonts.keys())[0]
    print(f"字号 {font_size}px, 主字体: {main_name}")

    # 用主字体进行像素级换行
    indent_px = int(font_size * 0.85)
    wrap_font = fonts.get(main_name, list(fonts.values())[0])
    all_lines = wrap_text_pixel(text, wrap_font, indent_px)
    print(f"共 {len(all_lines)} 行, 每页 {lpp} 行")

    # 分页
    pages = []
    for start in range(0, len(all_lines), lpp):
        pages.append(all_lines[start : start + lpp])
    while page_count > 0 and len(pages) < page_count:
        pages.append([])

    for i, page_lines in enumerate(pages):
        if page_count > 0 and i >= page_count:
            break
        path = render_page(page_lines, i + 1, fonts, main_name, output_dir,
                          font_size, line_spacing, margin_top)
        print(f"第 {i+1}/{len(pages)} 页: {path}")

    print(f"完成！共 {len(pages)} 页，保存在 {output_dir}")
    if sys.platform == "win32":
        os.startfile(str(output_dir))
    return len(pages)


def run_gui():
    import tkinter as tk
    from tkinter import messagebox, ttk

    root = tk.Tk()
    root.title("手写体图片生成器")
    root.geometry("700x580")
    root.configure(bg="#f5f5f5")

    top = tk.Frame(root, bg="#f5f5f5")
    top.pack(pady=(15, 0), padx=20, fill="x")

    tk.Label(top, text="主字体:", bg="#f5f5f5", font=("Microsoft YaHei", 11)).pack(side="left")

    font_dir = FONT_DIR
    font_names = [f.stem for f in font_dir.glob("*.ttf")] if font_dir.exists() else []
    font_var = tk.StringVar(value="李国夫手写体" if "李国夫手写体" in font_names else (font_names[0] if font_names else ""))
    ttk.Combobox(top, textvariable=font_var, values=font_names, state="readonly",
                 width=18, font=("Microsoft YaHei", 11)).pack(side="left", padx=(10, 30))

    tk.Label(top, text="页数:", bg="#f5f5f5", font=("Microsoft YaHei", 11)).pack(side="left")
    page_var = tk.StringVar(value="自动")
    ttk.Combobox(top, textvariable=page_var,
                 values=["自动"] + [str(i) for i in range(1, 21)],
                 state="readonly", width=6, font=("Microsoft YaHei", 11)).pack(side="left", padx=10)
    tk.Label(top, text='选数字=自适应字号塞进指定页',
             bg="#f5f5f5", fg="#999", font=("Microsoft YaHei", 9)).pack(side="left")

    tk.Label(root, text="在下方粘贴文字（段落之间空一行）：",
             bg="#f5f5f5", font=("Microsoft YaHei", 11), anchor="w").pack(
        pady=(15, 5), padx=20, fill="x")
    text_area = tk.Text(root, font=("Microsoft YaHei", 13), wrap="word",
                        relief="solid", borderwidth=1)
    text_area.pack(padx=20, fill="both", expand=True)

    status = tk.Label(root, text="", bg="#f5f5f5", fg="#666", font=("Microsoft YaHei", 10))
    status.pack(pady=(5, 0))

    def do_generate():
        content = text_area.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("提示", "请先粘贴文字内容")
            return
        status.config(text="正在计算最佳字号...")
        root.update()
        try:
            pages = 0 if page_var.get() == "自动" else int(page_var.get())
            n = generate(content, DESKTOP / "手写作业", font_var.get(), pages)
            status.config(text=f"已生成 {n} 页，保存在桌面「手写作业」文件夹")
            messagebox.showinfo("完成", f"已生成 {n} 页\n保存在桌面「手写作业」文件夹")
        except Exception as e:
            status.config(text="")
            messagebox.showerror("错误", str(e))

    tk.Button(root, text="生成手写图片", command=do_generate, bg="#4a90d9", fg="white",
              font=("Microsoft YaHei", 13, "bold"), padx=30, pady=8,
              relief="flat", cursor="hand2").pack(pady=(10, 20))
    root.bind("<Control-Return>", lambda e: do_generate())
    tk.Label(root, text="Ctrl+Enter 快速生成",
             bg="#f5f5f5", fg="#999", font=("Microsoft YaHei", 9)).pack(pady=(0, 5))
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="手写体图片生成器")
    parser.add_argument("input", nargs="?", help="输入文本文件路径")
    parser.add_argument("--text", "-t", help="直接输入文本")
    parser.add_argument("--output", "-o", default="", help="输出目录（默认桌面/手写作业）")
    parser.add_argument("--main-font", default="李国夫手写体", help="主手写字体名称")
    parser.add_argument("--pages", "-p", type=int, default=0,
                        help="指定总页数（0=自动，>0=自适应字号）")

    args = parser.parse_args()
    if args.text or args.input:
        if args.text:
            text = args.text
        else:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"错误：文件不存在 - {input_path}")
                sys.exit(1)
            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()
        output_dir = Path(args.output) if args.output else (DESKTOP / "手写作业")
        generate(text, output_dir, args.main_font, args.pages)
    else:
        run_gui()


if __name__ == "__main__":
    main()
