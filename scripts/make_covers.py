#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封面圖瘦身腳本
==============
將 assets/img/src/*.png（AI 生圖原檔，1536x1024）處理成網站用嘅封面：
  1. 裁走右下角「AI生成 WORKBUDDY」水印
  2. 縮到 800px 闊
  3. 存成 JPEG（quality 82, progressive, optimize）

輸出：assets/img/<name>.jpg

用法：
    python3 scripts/make_covers.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "assets" / "img" / "src"
OUT = REPO / "assets" / "img"

TARGET_W = 800
# 水印喺最底部約 8%，裁走 10% 確保乾淨
CROP_BOTTOM = 0.10
QUALITY = 82


def main() -> int:
    if not SRC.exists():
        print(f"❌ 搵唔到 {SRC}")
        return 1

    files = sorted(SRC.glob("*.png"))
    if not files:
        print(f"❌ {SRC} 冇 PNG")
        return 1

    print(f"處理 {len(files)} 張封面…\n")
    total = 0
    rows = []

    for f in files:
        with Image.open(f) as im:
            im = im.convert("RGB")
            w, h = im.size
            # 裁走底部水印
            im = im.crop((0, 0, w, int(h * (1 - CROP_BOTTOM))))
            w2, h2 = im.size
            # 等比縮到 TARGET_W
            nh = round(h2 * TARGET_W / w2)
            im = im.resize((TARGET_W, nh), Image.LANCZOS)

            dest = OUT / (f.stem + ".jpg")
            im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            kb = dest.stat().st_size / 1024
            total += dest.stat().st_size
            rows.append((f.stem, f"{w}x{h}", f"{TARGET_W}x{nh}", f"{kb:.1f} KB"))

    print(f"{'檔名':34s} {'原尺寸':12s} {'輸出':12s} {'大小':>9s}")
    print("-" * 72)
    for r in rows:
        print(f"{r[0]:34s} {r[1]:12s} {r[2]:12s} {r[3]:>9s}")
    print("-" * 72)
    print(f"共 {len(rows)} 張，合計 {total/1024:.0f} KB（{total/1024/1024:.2f} MB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
