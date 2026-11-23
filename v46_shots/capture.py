import os, json
os.environ['LD_LIBRARY_PATH'] = '/workspace/.tools/chromelibs/root/usr/lib/x86_64-linux-gnu:/workspace/.tools/chromelibs/root/lib/x86_64-linux-gnu'
from playwright.sync_api import sync_playwright

SHOTS = '/workspace/trippick_repo/v46_shots'
B = 'https://trippick.pages.dev'
report, fails = [], []


def ok(c, m):
    if not c:
        fails.append(m)


with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/workspace/.tools/cft/chrome-linux64/chrome', args=['--no-sandbox'])

    # 1) 가이드 — 데스크톱 1280 / 모바일 390
    for w, h, tag in ((1280, 900, '1280'), (390, 844, '390')):
        ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=(w < 500), has_touch=(w < 500),
                             device_scale_factor=1, locale='ko-KR')
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
        pg.goto(B + '/guides/guam-vs-saipan-comparison', wait_until='load')
        pg.wait_for_timeout(1200)
        info = pg.evaluate("""() => ({
          title: document.title,
          h1: (document.querySelector('h1') || {}).innerText,
          tables: document.querySelectorAll('table').length,
          rows: document.querySelectorAll('tbody tr').length,
          cmp: document.querySelectorAll('.gvp, .vs-cols, .cmp-card').length,
          gtools: !!document.querySelector('.gtools'),
          sponsors: [...document.querySelectorAll('a[rel]')].filter(a => (a.getAttribute('rel')||'').includes('sponsored')).length,
          faq: document.querySelectorAll('details.fq').length,
          bm: !!document.querySelector('[data-bm]'),
          sw: document.documentElement.scrollWidth, iw: window.innerWidth,
          imgs: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src).slice(0, 5),
          hero: (document.querySelector('.ghero-img, .hero-img, .guide-hero img, .hero img') || {}).src || null
        })""")
        ok(info['sw'] <= info['iw'] + 1, f'{tag}: 가로 넘침 {info["sw"]}>{info["iw"]}')
        ok(not info['imgs'], f'{tag}: 깨진 이미지 {info["imgs"]}')
        ok(info['faq'] == 5, f'{tag}: FAQ {info["faq"]}')
        ok(info['sponsors'] >= 5, f'{tag}: 제휴 링크 {info["sponsors"]}')
        ok(not errs, f'{tag}: JS 오류 {errs[:3]}')
        pg.screenshot(path=f'{SHOTS}/guam_vs_saipan_{tag}_hero.png')
        pg.screenshot(path=f'{SHOTS}/guam_vs_saipan_{tag}_full.png', full_page=True)
        report.append({'guide': tag, **info, 'errors': errs[:5]})
        ctx.close()

    # 2) /stays 괌·사이판 필터
    for w, h in ((1280, 900), (390, 844)):
        ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=(w < 500), has_touch=(w < 500), locale='ko-KR')
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        for rid, label in (('guam', '괌'), ('saipan', '사이판')):
            pg.goto(f'{B}/stays?region={rid}', wait_until='load')
            pg.wait_for_timeout(900)
            info = pg.evaluate("""() => {
              const cards = [...document.querySelectorAll('[data-region]')].filter(e => e.className.includes('scard') || e.tagName === 'ARTICLE' || e.getAttribute('data-type'));
              const vis = cards.filter(e => e.offsetParent !== null);
              const hidden = cards.filter(e => e.offsetParent === null);
              return {url: location.href, total: cards.length, visible: vis.length, hidden: hidden.length,
                      names: vis.map(e => (e.querySelector('b, h3, .scard-name') || {}).innerText || '').slice(0, 6),
                      regions: vis.map(e => e.getAttribute('data-region')).slice(0, 6),
                      sw: document.documentElement.scrollWidth, iw: window.innerWidth,
                      active: (document.querySelector('[data-region].on, .chip.on, [aria-selected="true"]') || {}).innerText || null,
                      chip: (() => { const c = document.querySelector('.sf-regionchips .gf-chip.on'); if (!c) return null;
                        const b = c.parentElement.getBoundingClientRect(), r = c.getBoundingClientRect();
                        return {text: c.innerText, inView: r.left < b.right - 1 && r.right > b.left + 1, box: [Math.round(b.left), Math.round(b.right)], chip: [Math.round(r.left), Math.round(r.right)]}; })()}
            }""")
            ok(info['visible'] == 3, f'stays {rid} {w}: visible {info["visible"]} / total {info["total"]}')
            ok(all(r == rid for r in info['regions']), f'stays {rid} {w}: 다른 지역 카드 노출 {info["regions"]}')
            ok(info['sw'] <= info['iw'] + 1, f'stays {rid} {w}: 가로 넘침 {info["sw"]}>{info["iw"]}')
            if w == 1280:
                ok(info['chip'] and info['chip']['inView'], f'stays {rid} {w}: 선택 칩이 스크롤 밖 {info["chip"]}')
            pg.screenshot(path=f'{SHOTS}/stays_{rid}_{w}.png')
            report.append({'stays': rid, 'w': w, **info})
        ok(not errs, f'stays {w}: JS 오류 {errs[:3]}')
        ctx.close()

    br.close()

open(f'{SHOTS}/capture_report.json', 'w', encoding='utf-8').write(json.dumps({'report': report, 'fails': fails}, ensure_ascii=False, indent=1))
for r in report:
    print(json.dumps(r, ensure_ascii=False)[:600])
print('FAILS:', fails if fails else 'none')
