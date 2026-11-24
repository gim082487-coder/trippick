#!/usr/bin/env python3
"""v49 이미지 최적화 — 120KB 초과 JPEG/PNG 를 화질 손실 최소로 다시 인코딩.

    python3 tools/v49_img_opt.py            # 미리보기(변경 없음)
    python3 tools/v49_img_opt.py --apply    # 실제 적용 (원본은 git 에 남아 있음)

규칙
- JPEG: 최대 폭 1600px(비율 유지, 업스케일 없음), quality 82, progressive, optimize
- PNG : optimize + palette(알파 유지) 로 재저장, 20% 이상 줄 때만 반영
- images/og(공유 카드)·assets/ess(쿠팡 썸네일) 는 제외하지 않되 og 는 quality 86
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images"
MIN = 120 * 1024
MAXW = 1600


def optim_jpeg(p: Path, apply: bool) -> tuple[int, int]:
    before = p.stat().st_size
    with Image.open(p) as im:
        im = im.convert("RGB")
        w, h = im.size
        if w > MAXW:
            im = im.resize((MAXW, round(h * MAXW / w)), Image.LANCZOS)
        q = 86 if "og" in p.parts else 82
        tmp = p.with_suffix(".opt.jpg")
        im.save(tmp, "JPEG", quality=q, optimize=True, progressive=True)
    after = tmp.stat().st_size
    if after < before * 0.92:
        if apply:
            tmp.replace(p)
        else:
            tmp.unlink()
        return before, after
    tmp.unlink()
    return before, before


def optim_png(p: Path, apply: bool) -> tuple[int, int]:
    before = p.stat().st_size
    with Image.open(p) as im:
        im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
        tmp = p.with_suffix(".opt.png")
        im.save(tmp, "PNG", optimize=True)
    after = tmp.stat().st_size
    if after < before * 0.8:
        if apply:
            tmp.replace(p)
        else:
            tmp.unlink()
        return before, after
    tmp.unlink()
    return before, before


def main():
    apply = "--apply" in sys.argv
    tb = ta = 0
    n = 0
    rows = []
    for p in sorted(SRC.rglob("*")):
        if not p.is_file():
            continue
        suf = p.suffix.lower()
        if suf not in (".jpg", ".jpeg", ".png"):
            continue
        if p.stat().st_size < MIN:
            continue
        try:
            b, a = optim_jpeg(p, apply) if suf in (".jpg", ".jpeg") else optim_png(p, apply)
        except Exception as e:
            print("skip", p, e)
            continue
        tb += b
        ta += a
        n += 1
        if a < b:
            rows.append((b - a, b, a, str(p.relative_to(SRC))))
    rows.sort(reverse=True)
    for d, b, a, rel in rows[:20]:
        print(f"  -{d//1024:5d}KB  {b//1024:5d}->{a//1024:5d}KB  {rel}")
    print(f"\n[{'APPLY' if apply else 'DRY'}] 대상 {n}개 · {tb/1048576:.1f}MB -> {ta/1048576:.1f}MB "
          f"(-{(tb-ta)/1048576:.1f}MB, -{0 if not tb else round((tb-ta)*100/tb)}%)")


if __name__ == "__main__":
    main()
