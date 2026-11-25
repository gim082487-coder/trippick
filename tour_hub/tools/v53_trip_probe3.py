#!/usr/bin/env python3
import json, sys, re
from playwright.sync_api import sync_playwright
URL = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome", args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width":1280,"height":1600}, locale="ko-KR",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    pg = ctx.new_page(); pg.goto(URL, wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(8000)
    txt = pg.inner_text("body")
    open("/workspace/.tmp_body.txt","w").write(txt)
    lines=[l.strip() for l in txt.split("\n") if l.strip()]
    for i,l in enumerate(lines):
        if "원" in l and len(l)<40:
            print(i, l)
