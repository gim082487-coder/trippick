import sys, json
from playwright.sync_api import sync_playwright
url=sys.argv[1]
JS="""() => {
  const out=[];
  const seen=new Set();
  document.querySelectorAll('a[href*="hotelId="]').forEach(a=>{
    const m=(a.getAttribute('href')||'').match(/hotelId=(\\d+)/); if(!m) return;
    const id=m[1]; if(seen.has(id)) return;
    let n=a, card=null;
    for(let i=0;i<12&&n;i++){n=n.parentElement; if(!n)break; const t=n.innerText||''; if(t.includes('리뷰')&&t.length<1500){card=n;break;}}
    if(!card) return;
    seen.add(id);
    const stars=card.querySelectorAll('.ic_star.star-icon').length;
    const addrLines=(card.innerText||'').split('\\n').filter(x=>x.includes('에서 가까움')||x.includes('지도'));
    out.push({id, stars, loc:(addrLines[0]||'').slice(0,60)});
  });
  return out;
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/workspace/.tools/cft/chrome-linux64/chrome",args=["--no-sandbox","--disable-dev-shm-usage"])
    ctx=b.new_context(viewport={"width":1280,"height":1400},locale="ko-KR",user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    pg=ctx.new_page(); pg.goto(url,wait_until="domcontentloaded",timeout=60000); pg.wait_for_timeout(6000)
    for _ in range(int(sys.argv[2]) if len(sys.argv)>2 else 0):
        pg.mouse.wheel(0,2400); pg.wait_for_timeout(1600)
    print(json.dumps(pg.evaluate(JS), ensure_ascii=False))
    b.close()
