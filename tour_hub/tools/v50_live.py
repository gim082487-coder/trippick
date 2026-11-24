#!/usr/bin/env python3
"""v50 라이브 실측 + 스크린샷 — 390·Slow4G·CPU 4x 로 LCP·전송량을 재고,
1280/390 화면을 v50_shots/ 에 저장한다.

    python3 tools/v50_live.py
"""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://trippick.pages.dev"
OUT = Path(__file__).resolve().parent.parent.parent / "v50_shots"
OUT.mkdir(exist_ok=True)

INIT = """
window.__fcp=0; window.__lcp=0; window.__lt=[]; window.__cls=0; window.__lcpe='';
new PerformanceObserver(l=>{for(const e of l.getEntries()) if(e.name==='first-contentful-paint') window.__fcp=e.startTime;}).observe({type:'paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()){ if(e.startTime>=window.__lcp){ window.__lcp=e.startTime; var el=e.element; window.__lcpe = el ? (el.tagName.toLowerCase()+(el.className? '.'+String(el.className).split(' ').slice(0,2).join('.'):'')+' | '+(el.textContent||'').trim().slice(0,36)) : ''; } }}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()) window.__lt.push(e.duration);}).observe({type:'longtask',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value;}).observe({type:'layout-shift',buffered:true});
"""

METRIC_PATHS = ["/", "/stays", "/guides/"]
SHOTS = [
    ("/", 1280, "v50-home-1280"),
    ("/", 390, "v50-home-390"),
    ("/stays", 1280, "v50-stays-1280"),
    ("/stays", 390, "v50-stays-390"),
    ("/guides/travel-medication-rules-guide", 1280, "v50-guide-medication-1280"),
    ("/guides/travel-medication-rules-guide", 390, "v50-guide-medication-390"),
    ("/guides/europe-ees-etias-guide", 1280, "v50-guide-ees-1280"),
    ("/guides/airport-lounge-card-guide", 390, "v50-guide-lounge-390"),
    ("/guides/airport-lounge-card-guide", 1280, "v50-guide-lounge-1280"),
    ("/guides/europe-ees-etias-guide", 390, "v50-guide-ees-390"),
]


def main():
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for path in METRIC_PATHS:
            ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True,
                                device_scale_factor=2)
            pg = ctx.new_page()
            pg.add_init_script(INIT)
            cdp = ctx.new_cdp_session(pg)
            cdp.send("Network.enable")
            cdp.send("Network.emulateNetworkConditions", {
                "offline": False, "latency": 750,
                "downloadThroughput": int(1.6 * 1024 * 1024 / 8), "uploadThroughput": int(750 * 1024 / 8)})
            cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
            pg.goto(BASE + path, wait_until="load", timeout=180000)
            pg.wait_for_timeout(3500)
            r = pg.evaluate("""()=>{const nav=performance.getEntriesByType('navigation')[0];
              const res=performance.getEntriesByType('resource');
              let xf=0,img=0; for(const e of res){xf+=e.transferSize||0; if(e.initiatorType==='img') img+=e.transferSize||0;}
              return {fcp:Math.round(window.__fcp),lcp:Math.round(window.__lcp),lcpEl:window.__lcpe,
                cls:Math.round(window.__cls*1000)/1000,ltmax:Math.round(Math.max(0,...window.__lt)),
                dom:document.getElementsByTagName('*').length,
                html:nav?nav.transferSize:0,res:xf,img:img,req:res.length};}""")
            r["path"] = path
            res[path] = r
            print(json.dumps(r, ensure_ascii=False))
            ctx.close()

        for path, w, name in SHOTS:
            ctx = b.new_context(viewport={"width": w, "height": 900 if w > 600 else 844},
                                is_mobile=w < 600, has_touch=w < 600, device_scale_factor=2 if w < 600 else 1)
            pg = ctx.new_page()
            pg.goto(BASE + path, wait_until="load", timeout=120000)
            pg.wait_for_timeout(1200)
            pg.screenshot(path=str(OUT / f"{name}.png"))
            # 넘침·오류 확인
            over = pg.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
            print(f"  shot {name}.png  넘침 {over}px")
            ctx.close()
        b.close()
    (Path(__file__).resolve().parent.parent.parent / "v50_live_perf.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
