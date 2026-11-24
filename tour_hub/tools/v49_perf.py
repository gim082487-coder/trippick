#!/usr/bin/env python3
"""v49 성능 실측 — 모바일 390 · CPU 4x · Slow4G(1.6Mbps/750ms RTT)에서 FCP/LCP/작업시간/전송량."""
from __future__ import annotations

import json
import os
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent / "deploy_site"
PORT = 8816


class Q(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_head(self):
        p = self.translate_path(self.path)
        if not os.path.exists(p) and not self.path.startswith(('/assets', '/images')):
            c = p.rstrip('/') + '.html'
            if os.path.isfile(c):
                self.path = self.path.rstrip('/') + '.html'
        return super().send_head()


INIT = """
window.__fcp=0; window.__lcp=0; window.__lt=[]; window.__cls=0;
new PerformanceObserver(l=>{for(const e of l.getEntries()) if(e.name==='first-contentful-paint') window.__fcp=e.startTime;}).observe({type:'paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()) window.__lcp=Math.max(window.__lcp,e.startTime);}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()) window.__lt.push(e.duration);}).observe({type:'longtask',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value;}).observe({type:'layout-shift',buffered:true});
"""


def main():
    paths = sys.argv[1].split(",") if len(sys.argv) > 1 else ["/", "/stays", "/guides/"]
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Q, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{PORT}"
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for path in paths:
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
            cdp.send("Performance.enable")
            pg.goto(base + path, wait_until="load", timeout=120000)
            pg.wait_for_timeout(3000)
            m = {x["name"]: x["value"] for x in cdp.send("Performance.getMetrics")["metrics"]}
            r = pg.evaluate("""()=>{const nav=performance.getEntriesByType('navigation')[0];
              const res=performance.getEntriesByType('resource');
              let xf=0,img=0,nimg=0; for(const e of res){xf+=e.transferSize||0; if(e.initiatorType==='img'||e.initiatorType==='link'&&/\\.jpg|webp/.test(e.name)){img+=e.transferSize||0;nimg++;}}
              return {fcp:Math.round(window.__fcp),lcp:Math.round(window.__lcp),cls:Math.round(window.__cls*1000)/1000,
                longtask:window.__lt.length, ltmax:Math.round(Math.max(0,...window.__lt)),
                dom:document.getElementsByTagName('*').length,
                navBytes:nav?nav.transferSize:0, resBytes:xf, imgBytes:img, imgN:nimg, res:res.length};}""")
            r.update({k: round(m.get(k, 0), 1) for k in
                      ("TaskDuration", "LayoutDuration", "RecalcStyleDuration", "ScriptDuration")})
            r["path"] = path
            res[path] = r
            print(json.dumps(r, ensure_ascii=False))
            ctx.close()
        b.close()
    srv.shutdown()
    out = Path("/workspace/trippick_repo/v49_perf.json")
    prev = json.loads(out.read_text()) if out.exists() and len(sys.argv) > 2 and sys.argv[2] == "merge" else {}
    prev.update(res)
    out.write_text(json.dumps(prev, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
