# -*- coding: utf-8 -*-
"""把 viewer.html 打包成「离线单文件版」——给没有 Python / 不想装东西的人用。

做的事：
  1. lib/katex/katex.min.css 内联（字体文件转 base64 data URI）
  2. lib/katex/katex.min.js、auto-render.min.js 内联
  3. 输出 dist/MarkdownViewer.html（双击即用，无需 helper.py、无需联网）

用法：python build_single.py
"""
import base64
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
KATEX = os.path.join(ROOT, 'lib', 'katex')
SRC = os.path.join(ROOT, 'viewer.html')
OUT_DIR = os.path.join(ROOT, 'dist')
OUT = os.path.join(OUT_DIR, 'MarkdownViewer.html')

MIME = {'.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf'}


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def main():
    if not os.path.isfile(SRC):
        sys.exit('找不到 viewer.html')
    if not os.path.isdir(KATEX):
        sys.exit('找不到 lib/katex（KaTeX 本地文件）')

    html = read(SRC)

    # ── 1) KaTeX CSS + 字体内联 ──
    css = read(os.path.join(KATEX, 'katex.min.css'))
    fonts_dir = os.path.join(KATEX, 'fonts')
    inlined, missing = 0, 0

    def font_repl(m):
        nonlocal inlined, missing
        ref = m.group(1).strip('"\'')
        name = os.path.basename(ref)
        fp = os.path.join(fonts_dir, name)
        if not os.path.isfile(fp):
            missing += 1
            return m.group(0)
        ext = os.path.splitext(name)[1].lower()
        data = base64.b64encode(open(fp, 'rb').read()).decode()
        inlined += 1
        return 'url(data:%s;base64,%s)' % (MIME.get(ext, 'application/octet-stream'), data)

    css = re.sub(r'url\(([^)]+)\)', font_repl, css)

    # ── 2) JS 内联 ──
    katex_js = read(os.path.join(KATEX, 'katex.min.js'))
    auto_js = read(os.path.join(KATEX, 'auto-render.min.js'))
    for name, js in (('katex.min.js', katex_js), ('auto-render.min.js', auto_js)):
        if '</script' in js.lower():
            sys.exit('%s 里含 </script，不能直接内联' % name)

    # ── 3) 替换三个引用标签（精确匹配 viewer.html 里的原文）──
    css_tag_re = re.compile(r'<link rel="stylesheet" href="lib/katex/katex\.min\.css"[^>]*>')
    js_tag_re = re.compile(r'<script src="lib/katex/katex\.min\.js"[^>]*></script>')
    auto_tag_re = re.compile(r'<script src="lib/katex/auto-render\.min\.js"[^>]*></script>')

    for rx, what in ((css_tag_re, 'css'), (js_tag_re, 'katex.min.js'), (auto_tag_re, 'auto-render.min.js')):
        if not rx.search(html):
            sys.exit('viewer.html 里找不到 %s 的引用标签（格式变了？）' % what)

    html = css_tag_re.sub(lambda m: '<style>' + css + '</style>', html, count=1)
    html = js_tag_re.sub(lambda m: '<script>' + katex_js + '</script>', html, count=1)
    html = auto_tag_re.sub(lambda m: '<script>' + auto_js + '</script>', html, count=1)

    # ── 4) 输出 ──
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = os.path.getsize(OUT) / 1024
    print('输出:', OUT)
    print('内联字体: %d 个；缺失(保留原引用): %d 条' % (inlined, missing))
    print('大小: %.1f KB' % size_kb)
    # 自检：输出里不应再有 lib/katex 的相对引用
    leftover = re.findall(r'(?:src|href)="(lib/katex/[^"]+)"', html)
    print('残留相对引用:', leftover if leftover else '无 ✓')


if __name__ == '__main__':
    main()
