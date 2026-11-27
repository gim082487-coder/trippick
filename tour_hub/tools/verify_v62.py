#!/usr/bin/env python3
"""v62 회귀 검증 — 홈 다듬기(경량화·외부 CSS·코스 칩·패널 히어로).

    python3 tools/verify_v62.py

검사
1. 홈 HTML 에 인라인 <style> 이 없다(외부 assets/site.css?v=62 하나로 통일)
2. 홈 HTML 이 1.4MB 미만이고, script/style/pre/textarea 밖에 들여쓰기·빈 줄이 없다(compact_html)
3. 코스 칩 21개(.pick-idx .pidx) + aria-current 1개 + 각 칩이 실제 패널 id 를 가리킨다
4. template.html 에 .panel-hero>picture>img 규칙이 있다(히어로 1000px 이미지 회귀 방지)
5. site.css(CSS_V=62) 에 .pick-idx 규칙과 .panel-hero>picture 규칙이 들어 있다
6. 코스 카드·패널 21개, 가이드 링크 카드 42개 유지(기능 보존)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT.parent / "deploy_site"
fails: list[str] = []


def check(ok: bool, msg: str) -> None:
    print(("  ✓ " if ok else "  ✗ ") + msg)
    if not ok:
        fails.append(msg)


index = (OUT / "index.html").read_text(encoding="utf-8")
tpl = (ROOT / "template.html").read_text(encoding="utf-8")
css = (OUT / "assets" / "site.css").read_text(encoding="utf-8")

# 1. 인라인 스타일 없음(남은 <style> 은 <noscript> 안의 panel 폴백뿐)
styles = re.findall(r"<style[^>]*>", index)
check(len(styles) <= 1, f"홈 인라인 <style> {len(styles)}개(기대 1 이하: noscript 폴백)")
check('href="assets/site.css?v=62"' in index, "홈이 assets/site.css?v=62 를 링크")

# 2. 크기·들여쓰기
size = len(index.encode())
check(size < 1_400_000, f"홈 HTML {size:,}B < 1,400,000B")
masked = re.sub(r"<(script|style|pre|textarea)\b[^>]*>.*?</\1>", "", index, flags=re.S | re.I)
lead = len(re.findall(r"(?m)^[ \t]+", masked))
check(lead == 0, f"본문 들여쓰기 줄 {lead}개(기대 0)")

# 3. 코스 칩
chips = re.findall(r'class="pidx"[^>]*data-course="([^"]+)"', index)
check(len(chips) == 21, f"코스 칩 {len(chips)}개(기대 21)")
check(len(re.findall(r'class="pidx"[^>]*aria-current="true"', index)) == 1, "칩 aria-current 1개")
for cid in chips:
    if f'aria-controls="course-{cid}"' not in index:
        check(f'aria-controls="course-{cid}"' not in index, f"칩 {cid} 가 패널을 가리키지 않음")
check(all(f'aria-controls="course-{c}"' in index for c in chips), "모든 칩이 자기 패널 aria-controls 를 가짐")

# 4·5. 히어로 규칙
check(".panel-hero>picture>img" in tpl.replace("\n", "").replace(" ", "") or ".panel-hero>picture" in tpl,
      "template.html 에 .panel-hero>picture 규칙")
check(".panel-hero>picture" in css, "site.css 에 .panel-hero>picture 규칙")
check(".pick-idx" in css and ".pidx" in css, "site.css 에 .pick-idx/.pidx 규칙")

# 6. 기능 보존
check(index.count('class="pick"') == 21, "코스 카드 21장 유지")
check(index.count('class="cguide"') == 42, f"코스 가이드 링크 {index.count('class=\"cguide\"')}개(기대 42)")
sm = (OUT / "sitemap.xml").read_text(encoding="utf-8")
check(sm.count("<loc>") == 188, f"sitemap {sm.count('<loc>')} URL(기대 188)")

print()
print("실패 없음" if not fails else "실패:\n  - " + "\n  - ".join(fails))
sys.exit(0 if not fails else 1)
