#!/usr/bin/env python3
"""v53 라이브 스크린샷 — 신규 가이드·/passes 홍콩·/stays 홍콩(1280·390) + 넘침·오류·깨진 이미지 확인."""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path("/workspace/trippick_repo/v53_shots"); OUT.mkdir(exist_ok=True)
B = "https://trippick.pages.dev"
TARGETS = [("/guides/chiang-mai-3n4d-course", "live_chiangmai"),
           ("/guides/shanghai-2n3d-3n4d-course", "live_shanghai"),
           ("/stays#hongkong", "live_stays_hongkong")]
fails = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844})
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        for path, name in TARGETS:
            pg.goto(B + path, wait_until="load", timeout=60000)
            pg.wait_for_timeout(1500)
            sw = pg.evaluate("()=>document.documentElement.scrollWidth")
            iw = pg.evaluate("()=>innerWidth")
            broken = pg.evaluate("()=>[...document.images].filter(i=>i.complete && i.naturalWidth===0).length")
            print(f"{tag} {path} overflow={sw-iw} broken={broken}")
            if sw > iw + 2: fails.append(f"{tag} {path} 가로 넘침 {sw-iw}px")
            if broken: fails.append(f"{tag} {path} 깨진 이미지 {broken}")
            pg.screenshot(path=str(OUT / f"{tag}_{name}.png"))
        pg.goto(B + "/passes", wait_until="load", timeout=60000)
        pg.wait_for_timeout(1200)
        pg.click('.pk-tab[data-city="hongkong"]'); pg.wait_for_timeout(700)
        best = pg.inner_text("#pkHkBest")
        print(f"{tag} /passes 홍콩 best={best}")
        pg.screenshot(path=str(OUT / f"{tag}_live_passes_hongkong.png"))
        if tag == "pc" and "홍콩달러" not in best: fails.append("라이브 /passes 홍콩 계산 미작동")
        if errs: fails.append(f"{tag} JS 오류 {errs[:2]}")
        ctx.close()
    b.close()
print("[LIVE]", "PASS" if not fails else "FAIL " + "; ".join(fails))
