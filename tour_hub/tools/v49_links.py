#!/usr/bin/env python3
"""v49 내부 링크 고립 해소 — in-degree 1~2 인 가이드를 관련 허브·가이드에서 자연 연결.

    python3 tools/v49_links.py          # 미리보기
    python3 tools/v49_links.py --apply  # data/guides.json · data/city_hubs.json 갱신(.bak-v49 백업)
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# 고립 가이드 -> 이 글이 실제로 도움이 되는 허브(도시 페이지)
HUB_LINKS = {
    "danang-vs-nhatrang-comparison": ["danang", "nhatrang"],
    "osaka-vs-fukuoka-comparison": ["osaka", "fukuoka"],
    "taipei-3n4d-course-budget": ["taipei"],
    "japan-ryokan-onsen-etiquette-budget": ["fukuoka", "osaka"],
}

# 고립 가이드 -> 함께 읽으면 자연스러운 가이드(역방향 related 삽입)
RELATED_BACK = {
    "danang-vs-nhatrang-comparison": ["danang-hoian-3n5d", "nhatrang-3n4d-food-resort", "danang-hoian-rainy"],
    "europe-train-eurail-vs-point": ["paris-london-5n7d", "italy-9d-packages", "spain-barcelona-madrid"],
    "osaka-vs-fukuoka-comparison": ["osaka-kyoto-3n4d", "fukuoka-yufuin", "osaka-3d-package"],
    "incheon-airport-parking-bus": ["incheon-airport-smartpass-lounge", "airport-arrival-city-transfer-guide"],
    "japan-ryokan-onsen-etiquette-budget": ["fukuoka-yufuin", "sapporo-hokkaido-3n4d-winter"],
    "taipei-3n4d-course-budget": ["taipei-yehliu", "taipei-food-route"],
}


def main():
    apply = "--apply" in sys.argv
    gp, hp = DATA / "guides.json", DATA / "city_hubs.json"
    gspec = json.loads(gp.read_text(encoding="utf-8"))
    hspec = json.loads(hp.read_text(encoding="utf-8"))
    guides = {g["slug"]: g for g in gspec["guides"]}
    hubs = {c["slug"]: c for c in hspec["cities"]}
    changes = []

    for target, partners in RELATED_BACK.items():
        if target not in guides:
            print("!! 없는 가이드", target)
            continue
        for p in partners:
            g = guides.get(p)
            if not g:
                print("!! 없는 파트너", p)
                continue
            rel = g.setdefault("related", [])
            if target in rel:
                continue
            pos = 1 if len(rel) >= 1 else 0
            rel.insert(pos, target)
            changes.append(f"guides.json: {p} related ← {target} (pos {pos})")

    for target, hub_slugs in HUB_LINKS.items():
        for hs in hub_slugs:
            c = hubs.get(hs)
            if not c:
                print("!! 없는 허브", hs)
                continue
            lst = c.setdefault("guides", [])
            if target in lst:
                continue
            pos = min(3, len(lst))
            lst.insert(pos, target)
            changes.append(f"city_hubs.json: {hs} ← {target} (pos {pos})")

    for ch in changes:
        print(" ", ch)
    print(f"[{'APPLY' if apply else 'DRY'}] 변경 {len(changes)}건")
    if apply and changes:
        for p in (gp, hp):
            bak = p.with_suffix(p.suffix + ".bak-v49")
            if not bak.exists():
                shutil.copy2(p, bak)
        gp.write_text(json.dumps(gspec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        hp.write_text(json.dumps(hspec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("저장 완료")


if __name__ == "__main__":
    main()
