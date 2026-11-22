from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/workspace/.tools/cft/chrome-linux64/chrome',args=['--no-sandbox','--disable-dev-shm-usage'])
    ctx=b.new_context(viewport={'width':1000,'height':1200})
    pg=ctx.new_page(); pg.goto('https://trippick.pages.dev/sos?country=TH', wait_until='networkidle', timeout=60000)
    pg.wait_for_timeout(900)
    print('screen panels visible:', pg.evaluate("() => [...document.querySelectorAll('.sos-panel')].filter(p=>p.offsetParent!==null).length"))
    pg.emulate_media(media='print'); pg.wait_for_timeout(400)
    info = pg.evaluate("""() => {
      const panels=[...document.querySelectorAll('.sos-panel')];
      const vis=panels.filter(p=>p.offsetParent!==null).length;
      return {panels: panels.length, visible: vis,
              headerHidden: getComputedStyle(document.querySelector('.site-head')).display==='none',
              printBtnHidden: getComputedStyle(document.querySelector('.sos-save')).display==='none',
              shareHidden: getComputedStyle(document.querySelector('.share-row')).display==='none'};
    }""")
    print('print media:', info)
    pg.screenshot(path='sos_print_1280.png', full_page=False)
    b.close()
