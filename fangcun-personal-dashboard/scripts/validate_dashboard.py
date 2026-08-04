#!/usr/bin/env python3
"""
个人工作台验收脚本。

  python3 validate_dashboard.py <工作台目录>

查的都是肉眼容易漏、但用户会真实踩到的问题：
占位符没替换、分区标记不闭合、绕过 Store 直接碰 localStorage、
输入框字号小于 16px（iOS 会放大整页）、图片没压缩就存、
manifest 和 html 对不上、API key 可能进了备份。
"""
import json, os, re, sys

RED, YEL, GRN, DIM, END = "\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m"
errors, warns = [], []


def err(msg, detail=""):
    errors.append((msg, detail))


def warn(msg, detail=""):
    warns.append((msg, detail))


def check_files(d):
    for f in ("index.html", "manifest.json"):
        if not os.path.exists(os.path.join(d, f)):
            err(f"缺少 {f}")
    if not os.path.exists(os.path.join(d, "icon.png")):
        warn("缺少 icon.png", "加到手机桌面后图标会是一张白纸")


def check_placeholders(d):
    for root, _, files in os.walk(d):
        if "node_modules" in root:
            continue
        for fn in files:
            if not fn.endswith((".html", ".json", ".js", ".md")):
                continue
            p = os.path.join(root, fn)
            try:
                txt = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            # 配置文件里的 {{}} 是模板正常内容，跳过
            if fn == "工作台配置.md":
                continue
            hits = set(re.findall(r"\{\{[^}]{1,40}\}\}", txt))
            if hits:
                rel = os.path.relpath(p, d)
                err(f"{rel} 里还有没替换的占位符",
                    "、".join(sorted(hits)[:6]) + ("…" if len(hits) > 6 else ""))


def check_sections(html):
    starts = re.findall(r"====\s*功能：(.+?)\s*START\s*====", html)
    ends = re.findall(r"====\s*功能：(.+?)\s*END\s*====", html)
    for name in set(starts) | set(ends):
        if starts.count(name) != ends.count(name):
            err(f"功能「{name}」的分区标记没闭合",
                f"START × {starts.count(name)}，END × {ends.count(name)}")
    if not starts:
        warn("一个功能分区标记都没有", "以后迭代时 AI 定位不到功能，改起来容易出错")
    if "功能：示例" in html:
        err("示例功能没删干净", "搜 ==== 功能：示例 ==== 把 HTML 和 JS 两段都删掉")


def check_store(html):
    # 排除 Store 内部实现（driver 里那几行是允许的）
    body = re.sub(r"const Store = \(\(\) => \{.*?\n\}\)\(\);", "", html, flags=re.S)
    bad = re.findall(r"localStorage\.(getItem|setItem|removeItem)", body)
    if bad:
        err(f"有 {len(bad)} 处直接调用 localStorage", "必须走 Store.get/set，否则以后没法平滑上云")


def check_mobile(html):
    if "viewport" not in html:
        err("缺少 viewport meta", "手机上会以桌面宽度渲染")
    elif "width=device-width" not in html:
        err("viewport 没有 width=device-width")
    if "viewport-fit=cover" not in html:
        warn("viewport 缺 viewport-fit=cover", "全面屏上安全区不生效")

    # 输入框字号
    for m in re.finditer(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", html):
        size = float(m.group(1))
        if size >= 16:
            continue
        # 只关心可能作用在输入控件上的规则
        chunk = html[max(0, m.start() - 260):m.start()]
        rule = chunk.rsplit("}", 1)[-1]
        if re.search(r"\b(input|textarea|select)\b", rule):
            err(f"输入框 font-size 只有 {size:g}px",
                "小于 16px 时 iOS 会自动放大整个页面且退不回去")

    if "safe-area-inset-bottom" not in html:
        warn("没用 env(safe-area-inset-bottom)", "全面屏底部横条会盖住内容")


def check_images(html):
    if re.search(r"readAsDataURL", html) and "compressImage" not in html:
        err("有图片转 base64 但没走 Util.compressImage",
            "手机原图几张就撑爆 localStorage，届时所有功能一起失效")
    for m in re.finditer(r'src\s*=\s*["\']https?://([^/"\']+)', html):
        host = m.group(1)
        if "cdn" in host or "unpkg" in host or "jsdelivr" in host:
            warn(f"引用了外部 CDN：{host}", "国内访问会明显变慢，能内联就内联")


def check_secrets(html):
    if "setSecret" in html or "getSecret" in html:
        if "bysdash$secret:" not in html:
            err("用了 Secret 接口但找不到独立命名空间", "key 可能会被导出进备份文件")
        # exportAll 必须只导出普通命名空间
        m = re.search(r"exportAll\(\)\s*\{(.*?)\n\s{4}\}", html, re.S)
        if m and "SEC" in m.group(1):
            err("exportAll 里出现了 SEC", "备份文件会带上 API key，用户转发时会泄漏")
    # 硬编码 key 的粗略嗅探
    for m in re.finditer(r'["\'](sk-[A-Za-z0-9_\-]{16,})["\']', html):
        err("代码里疑似硬编码了 API key", m.group(1)[:12] + "…（必须改成让用户在设置页填）")


def check_routes(html):
    ids = re.findall(r'id\s*=\s*["\']page-([\w-]+)["\']', html)
    routes = re.findall(r"id\s*:\s*['\"]([\w-]+)['\"]", html)
    routes = [r for r in routes if r in ids or f"page-{r}" not in html]
    missing = [r for r in set(routes) if r not in ids]
    orphan = [i for i in set(ids) if i not in routes]
    if missing:
        err("routes 里有页面不存在", "、".join(missing))
    if orphan:
        warn("有页面没挂到 routes 上（侧边栏点不到）", "、".join(orphan))
    if "settings" not in ids:
        err("没有设置页", "备份功能必须有，否则用户丢数据无法恢复")
    n = len(ids)
    if n > 9:
        warn(f"侧边栏有 {n} 个功能", "超过 9 个在手机上会挤到要滚动，建议合并")


def check_manifest(d, html):
    p = os.path.join(d, "manifest.json")
    if not os.path.exists(p):
        return
    try:
        m = json.load(open(p, encoding="utf-8"))
    except json.JSONDecodeError as e:
        err("manifest.json 不是合法 JSON", str(e))
        return
    for k in ("name", "short_name", "start_url", "display", "icons"):
        if not m.get(k):
            err(f"manifest.json 缺少 {k}")
    if m.get("display") != "standalone":
        warn("manifest display 不是 standalone", "加到桌面后会带浏览器地址栏，不像 App")
    if len(m.get("short_name", "")) > 6:
        warn(f"short_name「{m['short_name']}」偏长", "桌面图标下面会显示成省略号，建议 ≤4 字")
    if 'rel="manifest"' not in html and "rel='manifest'" not in html:
        err("index.html 没有引用 manifest.json")
    if "apple-touch-icon" not in html:
        err("缺少 apple-touch-icon", "iOS 加到桌面后图标会是页面截图，很难看")
    if "apple-mobile-web-app-capable" not in html:
        warn("缺少 apple-mobile-web-app-capable", "iOS 上加桌面后不会全屏")


def check_size(d):
    p = os.path.join(d, "index.html")
    if not os.path.exists(p):
        return
    lines = sum(1 for _ in open(p, encoding="utf-8"))
    if lines > 1500:
        warn(f"index.html 已经 {lines} 行", "建议按 build-guide.md 拆分到 features/，否则后续迭代容易改错地方")


def main():
    if len(sys.argv) < 2:
        sys.exit("用法：python3 validate_dashboard.py <工作台目录>")
    d = sys.argv[1]
    if not os.path.isdir(d):
        sys.exit(f"不是目录：{d}")

    check_files(d)
    check_placeholders(d)

    p = os.path.join(d, "index.html")
    if os.path.exists(p):
        html = open(p, encoding="utf-8").read()
        for fn in (check_sections, check_store, check_mobile,
                   check_images, check_secrets, check_routes):
            fn(html)
        check_manifest(d, html)
    else:
        check_manifest(d, "")
    check_size(d)

    print()
    if errors:
        print(f"{RED}✗ {len(errors)} 个问题必须修{END}")
        for m, det in errors:
            print(f"  {RED}·{END} {m}")
            if det:
                print(f"    {DIM}{det}{END}")
    if warns:
        print(f"{YEL}! {len(warns)} 个建议{END}")
        for m, det in warns:
            print(f"  {YEL}·{END} {m}")
            if det:
                print(f"    {DIM}{det}{END}")
    if not errors and not warns:
        print(f"{GRN}✓ 全部通过{END}")
    elif not errors:
        print(f"\n{GRN}✓ 没有阻塞问题，可以交付{END}")
    print()
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
