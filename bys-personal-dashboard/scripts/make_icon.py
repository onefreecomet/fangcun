#!/usr/bin/env python3
"""
生成个人工作台的桌面图标（512x512 PNG）。

三种用法：
  # A. 纯色 + 文字（默认）
  python3 make_icon.py --out icon.png --bg "#7d9471" --text "熊"

  # B. 从用户自己的图裁切
  python3 make_icon.py --out icon.png --from photo.jpg

  # C. 从图取色 + 文字
  python3 make_icon.py --out icon.png --from photo.jpg --text "熊" --blur

图标在桌面上只有指甲盖大，所以文字建议 1-2 个字，最多 3 个。
"""
import argparse, glob, os, sys, tempfile

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    sys.exit("需要 Pillow：Windows 用 `pip install Pillow`；"
             "Linux/mac 用 `pip3 install Pillow --break-system-packages`")

SIZE = 512

# 按优先级找一个能渲染中文的字体
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]


def find_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    for pat in ("/usr/share/fonts/**/*CJK*.tt*", "/usr/share/fonts/**/*.ttf"):
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    return None


def pick_text_color(bg):
    """按背景亮度决定文字用白还是深色，保证能看清。"""
    r, g, b = bg[:3]
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return (255, 255, 255, 255) if lum < 0.6 else (28, 28, 30, 255)


def hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        sys.exit(f"色值格式不对：{h}（应该像 #7d9471）")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def dominant_color(img):
    small = img.convert("RGB").resize((1, 1), Image.LANCZOS)
    return small.getpixel((0, 0)) + (255,)


def crop_square(img):
    w, h = img.size
    s = min(w, h)
    return img.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="输出路径，比如 icon.png")
    ap.add_argument("--bg", help="背景色，比如 #7d9471")
    ap.add_argument("--text", help="图标上的字，1-2 个字最好")
    ap.add_argument("--from", dest="src", help="从这张图生成")
    ap.add_argument("--blur", action="store_true", help="配 --from 用，把图模糊成背景再压字")
    a = ap.parse_args()

    if not a.src and not a.bg:
        sys.exit("至少要给 --bg 或 --from 之一")

    if a.src:
        if not os.path.exists(a.src):
            sys.exit(f"找不到文件：{a.src}")
        base = crop_square(Image.open(a.src).convert("RGBA")).resize((SIZE, SIZE), Image.LANCZOS)
        bg_color = hex2rgb(a.bg) if a.bg else dominant_color(base)
        if a.blur or a.text:
            base = base.filter(ImageFilter.GaussianBlur(SIZE // 24))
            veil = Image.new("RGBA", (SIZE, SIZE), bg_color[:3] + (110,))
            base = Image.alpha_composite(base, veil)
        img = base
    else:
        bg_color = hex2rgb(a.bg)
        img = Image.new("RGBA", (SIZE, SIZE), bg_color)

    if a.text:
        text = a.text.strip()[:3]
        font_path = find_font()
        if not font_path:
            sys.exit("系统里找不到可用字体，改用 --from 提供一张图，或装一下 fonts-noto-cjk")

        draw = ImageDraw.Draw(img)
        # 字数越多字号越小。整体留出边距，因为 iOS/安卓会把图标裁成圆角或圆形，
        # 贴边的字会被切掉，主体要控制在中心 ~75% 的安全区内。
        size = {1: 250, 2: 175, 3: 118}[len(text)]
        try:
            font = ImageFont.truetype(font_path, size)
        except OSError:
            font = ImageFont.truetype(font_path, size, index=0)

        box = draw.textbbox((0, 0), text, font=font)
        x = (SIZE - (box[2] - box[0])) // 2 - box[0]
        y = (SIZE - (box[3] - box[1])) // 2 - box[1]
        draw.text((x, y), text, font=font, fill=pick_text_color(bg_color))

    img.convert("RGB").save(a.out, "PNG", optimize=True)

    # 缩到 60px 存一份用来肉眼确认小尺寸下认不认得出。
    # 故意写到系统临时目录：--out 通常指向工作台目录，而那个文件夹会被整个拖去公网部署，
    # 多一个预览文件就是多一个被公开的垃圾。
    preview = os.path.join(tempfile.gettempdir(),
                           os.path.basename(os.path.splitext(a.out)[0]) + "_60px预览.png")
    img.convert("RGB").resize((60, 60), Image.LANCZOS).save(preview, "PNG")

    print(f"✅ 已生成 {a.out}（512×512）")
    print(f"   小尺寸预览：{preview} —— 看一眼，认不出主体就换个做法")


if __name__ == "__main__":
    main()
