#!/usr/bin/env python3
"""v53 스크린샷 — 신규 가이드 3편(1280·390)·/passes 홍콩·/stays 홍콩·마카오."""
from __future__ import annotations
import functools, http.server, socketserver, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = "/workspace/trippick_repo/deploy_site"
OUT = Path("/workspace/trippick_repo/v53_shots"); OUT.mkdir(exist_ok=True)
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
class Q(socketserver.TCPServer):
    allow_reuse_address = True
srv = Q(("127.0.0.1", 8094), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

GUIDES = ["chiang-mai-3n4d-course", "bali-ubud-seminyak-3n4d-course", "shanghai-2n3d-3n4d-course"]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, tag in ((1280, "pc"), (390, "mo")):
        ctx = b.new_context(viewport={"width": w, "height": 900 if w > 500 else 844}, device_scale_factor=1)
        pg = ctx.new_page()
        for slug in GUIDES:
            pg.goto(f"http://127.0.0.1:8094/guides/{slug}.html", wait_until="load")
            pg.wait_for_timeout(600)
            pg.screenshot(path=str(OUT / f"{tag}_{slug}_top.png"))
            pg.evaluate("()=>window.scrollTo(0, document.body.scrollHeight*0.42)")
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(OUT / f"{tag}_{slug}_mid.png"))
        pg.goto("http://127.0.0.1:8094/passes.html", wait_until="load")
        pg.wait_for_timeout(700)
        pg.click('.pk-tab[data-city="hongkong"]'); pg.wait_for_timeout(600)
        pg.screenshot(path=str(OUT / f"{tag}_passes_hongkong.png"))
        pg.goto("http://127.0.0.1:8094/stays.html#hongkong", wait_until="load")
        pg.wait_for_timeout(1200)
        pg.evaluate("()=>{const a=document.getElementById('hongkong'); if(a) a.scrollIntoView();}")
        pg.wait_for_timeout(800)
        pg.screenshot(path=str(OUT / f"{tag}_stays_hongkong.png"))
        ctx.close()
    b.close()
srv.shutdown()
print("saved", len(list(OUT.glob('*.png'))), "shots →", OUT)
