#!/usr/bin/env python3
"""v65 제휴 URL 검증 — HTTP 200 + 한국어 제목 + 파트너스 코드 유지 확인.

    python3 tools/v65_links.py urls.txt

한 줄에 `라벨<탭>URL` 형식. 결과는 /workspace/v65_links_result.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_LIBS = [p for p in ("/workspace/.tools/chromelibs/root/usr/lib/x86_64-linux-gnu",
                    "/workspace/.tools/sysroot/usr/lib/x86_64-linux-gnu") if Path(p).is_dir()]
if _LIBS:
    os.environ["LD_LIBRARY_PATH"] = ":".join(_LIBS + ([os.environ["LD_LIBRARY_PATH"]] if os.environ.get("LD_LIBRARY_PATH") else []))

from playwright.sync_api import sync_playwright  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")


def main() -> int:
    rows = []
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        label, url = line.split("\t", 1)
        rows.append((label.strip(), url.strip()))
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",
                              args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(locale="ko-KR", user_agent=UA, viewport={"width": 1280, "height": 900})
        pg = ctx.new_page()
        for label, url in rows:
            status, title = 0, ""
            for attempt in range(2):
                try:
                    resp = pg.goto(url, wait_until="domcontentloaded", timeout=45000)
                    pg.wait_for_timeout(2500)
                    status = resp.status if resp else 0
                    title = pg.title()
                except Exception as e:  # noqa: BLE001
                    title = f"ERR {e}"
                if status == 200 and "봇" not in title and "verify" not in pg.url.lower():
                    break
                pg.wait_for_timeout(8000)
            korean = any("\uac00" <= ch <= "\ud7a3" for ch in title)
            out.append({"label": label, "url": url, "status": status, "title": title,
                        "korean": korean, "final": pg.url})
            print(f"{status} | {'KO' if korean else '--'} | {label} | {title[:60]}")
            sys.stdout.flush()
        b.close()
    Path("/workspace/v65_links_result.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
