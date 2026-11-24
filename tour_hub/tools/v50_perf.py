#!/usr/bin/env python3
"""v50 성능 실측 — 모바일 390 · CPU 4x · Slow4G(1.6Mbps/750ms RTT).

v49_perf.py 와 같은 스로틀을 쓰되, 실제 서비스(Cloudflare Pages·brotli)에 가깝게
텍스트 자원을 gzip 으로 내려 준다. LCP 요소(태그·클래스·텍스트)도 함께 남긴다.

사용: python3 tools/v50_perf.py <root> [paths] [--nogzip]
예)  python3 tools/v50_perf.py ../../deploy_site "/,/stays,/guides/"
"""
from __future__ import annotations

import gzip
import json
import mimetypes
import os
import sys
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

PORT = 8831
GZIP = "--nogzip" not in sys.argv
TEXTY = ("text/", "application/json", "application/javascript", "application/xml", "image/svg")

INIT = """
window.__fcp=0; window.__lcp=0; window.__lt=[]; window.__cls=0; window.__lcpe='';
new PerformanceObserver(l=>{for(const e of l.getEntries()) if(e.name==='first-contentful-paint') window.__fcp=e.startTime;}).observe({type:'paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()){ if(e.startTime>=window.__lcp){ window.__lcp=e.startTime; var el=e.element; window.__lcpe = el ? (el.tagName.toLowerCase()+(el.className? '.'+String(el.className).split(' ').slice(0,2).join('.'):'')+' | '+(el.textContent||'').trim().slice(0,40)) : ''; } }}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()) window.__lt.push(e.duration);}).observe({type:'longtask',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value;}).observe({type:'layout-shift',buffered:true});
"""


class H(BaseHTTPRequestHandler):
    root = "."

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0].split("#")[0]
        rel = path.lstrip("/")
        f = Path(self.root) / rel
        if f.is_dir():
            f = f / "index.html"
        if not f.exists() and not rel.startswith(("assets/", "images/")):
            cand = Path(self.root) / (rel.rstrip("/") + ".html")
            if cand.is_file():
                f = cand
        if not f.is_file():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"not found")
            return
        data = f.read_bytes()
        ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
        headers = [("Content-Type", ctype if "text" in ctype or "json" in ctype else ctype)]
        body = data
        if GZIP and any(ctype.startswith(t) for t in TEXTY) and len(data) > 512:
            body = gzip.compress(data, 6)
            headers.append(("Content-Encoding", "gzip"))
        headers.append(("Cache-Control", "no-cache"))
        self.send_response(200)
        for k, v in headers:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else Path(
        "/workspace/trippick_repo/deploy_site")
    paths = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2].startswith("/") else ["/", "/stays", "/guides/"]
    H.root = str(root)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{PORT}"
    out = {}
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
            pg.goto(base + path, wait_until="load", timeout=180000)
            pg.wait_for_timeout(3500)
            m = {x["name"]: x["value"] for x in cdp.send("Performance.getMetrics")["metrics"]}
            r = pg.evaluate("""()=>{const nav=performance.getEntriesByType('navigation')[0];
              const res=performance.getEntriesByType('resource');
              let xf=0,img=0,nimg=0; for(const e of res){xf+=e.transferSize||0; if(e.initiatorType==='img'||e.initiatorType==='link'&&/\\.jpg|webp/.test(e.name)){img+=e.transferSize||0;nimg++;}}
              return {fcp:Math.round(window.__fcp),lcp:Math.round(window.__lcp),lcpEl:window.__lcpe,cls:Math.round(window.__cls*1000)/1000,
                longtask:window.__lt.length, ltmax:Math.round(Math.max(0,...window.__lt)),
                dom:document.getElementsByTagName('*').length,
                navBytes:nav?nav.transferSize:0, resBytes:xf, imgBytes:img, imgN:nimg, res:res.length, url:location.pathname};}""")
            r.update({k: round(m.get(k, 0), 1) for k in
                      ("TaskDuration", "LayoutDuration", "RecalcStyleDuration", "ScriptDuration")})
            r["path"] = path
            r["root"] = str(root)
            r["gzip"] = GZIP
            out[path] = r
            print(json.dumps(r, ensure_ascii=False))
            ctx.close()
        b.close()
    srv.shutdown()
    tag = "v50_perf_nogzip.json" if not GZIP else "v50_perf.json"
    dst = Path("/workspace/trippick_repo") / tag
    if dst.exists():
        try:
            prev = json.loads(dst.read_text())
        except Exception:
            prev = {}
    else:
        prev = {}
    prev.update({f"{root.name}{k}": v for k, v in out.items()})
    dst.write_text(json.dumps(prev, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
