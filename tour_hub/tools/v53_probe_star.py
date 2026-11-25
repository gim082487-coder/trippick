import sys, json
from playwright.sync_api import sync_playwright
url=sys.argv[1]
JS="""() => {
  const out=[];
  document.querySelectorAll('a[href*="hotelId="]').forEach(a=>{
    let n=a, card=null;
    for(let i=0;i<12&&n;i++){n=n.parentElement; if(!n)break; const t=n.innerText||''; if((t.includes('리뷰'))&&t.length<1500){card=n;break;}}
    if(!card) return;
    const stars=[...card.querySelectorAll('[class*="star"],[aria-label*="성급"],[title*="성급"]')].map(e=>e.getAttribute('aria-label')||e.getAttribute('title')||e.className).slice(0,6);
    out.push({href:a.getAttribute('href'), stars, html: card.innerHTML.slice(0,600)});
  });
  return out;
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx=b.new_context(viewport={"width":1280,"height":1400},locale="ko-KR",user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    pg=ctx.new_page(); pg.goto(url,wait_until="domcontentloaded",timeout=60000); pg.wait_for_timeout(6000)
    rows=pg.evaluate(JS)
    for r in rows[:2]:
        print(r['stars'])
        print(r['html'][:500])
        print('---')
    b.close()
