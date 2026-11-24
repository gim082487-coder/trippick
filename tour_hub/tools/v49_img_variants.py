#!/usr/bin/env python3
"""v49 반응형 이미지 변형 생성 — 가이드 히어로·카드, 코스 커버의 WebP(480/720/960) 변형.

    python3 tools/v49_img_variants.py [--all]

- 대상: data/guides.json 의 모든 guide.image + data/courses.json 의 course.img
- 출력: 같은 폴더에 `<이름>-<폭>.webp` (예: hero_kyoto_street-720.webp)
- 이미 있고 원본보다 새로우면 건너뜀
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
WIDTHS = (480, 720, 960)


def targets() -> set[Path]:
    out: set[Path] = set()
    g = json.loads((ROOT / "data" / "guides.json").read_text(encoding="utf-8"))
    for x in g["guides"]:
        p = x.get("image")
        if p:
            out.add(ROOT / p)
    try:
        c = json.loads((ROOT / "data" / "courses.json").read_text(encoding="utf-8"))
        for course in c["courses"]:
            out.add(ROOT / course["img"])
    except Exception:
        pass
    return {p for p in out if p.exists() and p.suffix.lower() in (".jpg", ".jpeg")}


def main():
    made = skipped = 0
    total_new = 0
    for p in sorted(targets()):
        try:
            with Image.open(p) as im:
                im = im.convert("RGB")
                w, h = im.size
                for tw in WIDTHS:
                    if w <= tw:
                        continue
                    dst = p.with_name(f"{p.stem}-{tw}.webp")
                    if dst.exists() and dst.stat().st_mtime >= p.stat().st_mtime:
                        skipped += 1
                        continue
                    nh = round(h * tw / w)
                    im.resize((tw, nh), Image.LANCZOS).save(dst, "WEBP", quality=78, method=6)
                    made += 1
                    total_new += dst.stat().st_size
        except Exception as e:
            print("skip", p.name, e)
    print(f"[variants] 생성 {made} · 건너뜀 {skipped} · 신규 {total_new/1048576:.1f}MB")


if __name__ == "__main__":
    main()
