#!/usr/bin/env python3
"""v49 홈·숙소 페이지 섹션별 DOM 노드/이미지 무게 분해."""
from __future__ import annotations

import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent / "deploy_site"
PORT = 8812


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


JS = """
() => {
  const out = [];
  const walk = (root, depth) => {
    for (const el of root.children) {
      if (['SCRIPT','STYLE','LINK','NOSCRIPT'].includes(el.tagName)) continue;
      const n = el.getElementsByTagName('*').length + 1;
      const id = el.id ? '#' + el.id : '';
      const cls = (el.className && typeof el.className === 'string') ? '.' + el.className.split(' ').slice(0,2).join('.') : '';
      if (depth < 2 && n > 300) {
        out.push({depth, tag: el.tagName, id, cls, nodes: n,
                  h: Math.round(el.getBoundingClientRect().height),
                  imgs: el.getElementsByTagName('img').length});
      }
      if (depth < 2) walk(el, depth + 1);
    }
  };
  walk(document.body, 0);
  const imgs = [...document.images].map(i => ({src: i.currentSrc || i.src, nw: i.naturalWidth, nh: i.naturalHeight,
    cw: Math.round(i.getBoundingClientRect().width), ch: Math.round(i.getBoundingClientRect().height)}));
  return {total: document.getElementsByTagName('*').length, sections: out, imgs};
}
"""


def main():
    handler = partial(Quiet, directory=str(ROOT))
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for path in ("/", "/stays"):
            pg = b.new_page(viewport={"width": 1280, "height": 900})
            pg.goto(f"http://127.0.0.1:{PORT}{path}", wait_until="load", timeout=60000)
            pg.wait_for_timeout(1500)
            r = pg.evaluate(JS)
            print(f"\n== {path} total {r['total']} ==")
            for s in sorted(r["sections"], key=lambda x: -x["nodes"]):
                print(f"  {s['nodes']:6d} nodes  h={s['h']:6d}  imgs={s['imgs']:3d}  {s['tag']}{s['id']}{s['cls']}")
            # image weight by directory
            from collections import defaultdict
            agg = defaultdict(lambda: [0, 0, 0])
            for i in r["imgs"]:
                u = i["src"].replace("http://127.0.0.1:%d/" % PORT, "")
                d = "/".join(u.split("/")[:2])
                a = agg[d]; a[0] += 1
                if i["cw"]:
                    a[1] = max(a[1], i["nw"])
            for d, a in sorted(agg.items(), key=lambda x: -x[1][0]):
                print(f"  img dir {d}: {a[0]}장 max natural width {a[1]}")
            pg.close()
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
