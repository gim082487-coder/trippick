#!/usr/bin/env python3
"""v49 진단용 실측 — 로컬 deploy_site 를 http 로 띄워 DOM·전송량·LCP/CLS·모바일 터치/넘침 측정."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent / "deploy_site"
PORT = 8811

JS_INIT = """
window.__lcp = 0; window.__cls = 0;
try {
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = Math.max(window.__lcp, e.startTime); })
    .observe({type:'largest-contentful-paint', buffered:true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
    .observe({type:'layout-shift', buffered:true});
} catch (e) {}
"""

JS_REPORT = """
() => {
  const res = performance.getEntriesByType('resource');
  let xfer = 0, dec = 0, n = 0;
  for (const r of res) { xfer += r.transferSize || 0; n++; dec += r.decodedBodySize || 0; }
  const nav = performance.getEntriesByType('navigation')[0];
  const imgs = [...document.images];
  const vh = innerHeight;
  const above = imgs.filter(i => { const r = i.getBoundingClientRect(); return r.top < vh && r.bottom > 0; });
  const small = [...document.querySelectorAll('a,button,[role=button],input,select')].filter(el => {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return false;
    const s = getComputedStyle(el);
    if (s.visibility === 'hidden' || s.display === 'none') return false;
    return (r.width < 44 || r.height < 44);
  }).length;
  const interactive = [...document.querySelectorAll('a,button,[role=button],input,select')].filter(el => {
    const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0;
  }).length;
  return {
    dom: document.getElementsByTagName('*').length,
    html_bytes: nav ? nav.transferSize : 0,
    res_count: n, res_xfer: xfer, res_decoded: dec,
    lcp: window.__lcp, cls: window.__cls,
    doc_h: document.documentElement.scrollHeight,
    overflow: document.documentElement.scrollWidth - innerWidth,
    imgs: imgs.length,
    img_broken: imgs.filter(i => i.complete && i.naturalWidth === 0).length,
    img_no_dim: imgs.filter(i => !i.getAttribute('width') || !i.getAttribute('height')).length,
    img_above_lazy: above.filter(i => i.getAttribute('loading') === 'lazy').length,
    img_above: above.length,
    img_decoding_async: imgs.filter(i => i.getAttribute('decoding') === 'async').length,
    small_targets: small, interactive: interactive,
    h1: document.querySelectorAll('h1').length,
  };
}
"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_head(self):
        p = self.translate_path(self.path)
        if not os.path.exists(p) and not self.path.startswith(('/assets', '/images')):
            cand = p.rstrip('/') + '.html'
            if os.path.isfile(cand):
                self.path = self.path.rstrip('/') + '.html'
        return super().send_head()


def serve():
    handler = partial(Quiet, directory=str(ROOT))
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


def main():
    pages = sys.argv[1].split(",") if len(sys.argv) > 1 else ["/", "/stays", "/guides/", "/exchange", "/passes"]
    widths = [int(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["390", "1280"])]
    srv = serve()
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in widths:
            ctx = b.new_context(viewport={"width": w, "height": 844 if w < 500 else 900},
                                user_agent="Mozilla/5.0 (Linux; Android 14; SM-S911N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Mobile Safari/537.36" if w < 500 else None,
                                device_scale_factor=1, is_mobile=w < 500, has_touch=w < 500)
            pg = ctx.new_page()
            pg.add_init_script(JS_INIT)
            for path in pages:
                url = f"http://127.0.0.1:{PORT}{path}"
                try:
                    pg.goto(url, wait_until="load", timeout=45000)
                    pg.wait_for_timeout(1200)
                    r = pg.evaluate(JS_REPORT)
                except Exception as e:
                    r = {"error": str(e)[:200]}
                r["path"] = path
                r["width"] = w
                out[f"{w}{path}"] = r
                print(json.dumps(r, ensure_ascii=False))
            ctx.close()
        b.close()
    srv.shutdown()
    Path("/workspace/trippick_repo/v49_measure.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
