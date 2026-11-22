from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/workspace/.tools/cft/chrome-linux64/chrome',args=['--no-sandbox','--disable-dev-shm-usage'])
    for url in ['https://trippick.pages.dev/exchange?cur=JPY&city=tokyo','https://trippick.pages.dev/exchange?cur=VND&city=danang']:
        ctx=b.new_context(viewport={'width':1280,'height':900}); pg=ctx.new_page()
        pg.goto(url, wait_until='networkidle', timeout=60000); pg.wait_for_timeout(1200)
        txt=pg.evaluate("() => {const h=document.querySelector('[data-tp-bundle=\"exchange\"]'); return h? h.innerText.slice(0,160): 'none'}")
        print(url, '->', txt.replace('\n',' | '))
        ctx.close()
    b.close()
