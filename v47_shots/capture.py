import os, json
os.environ['LD_LIBRARY_PATH'] = '/workspace/.tools/chromelibs/root/usr/lib/x86_64-linux-gnu:/workspace/.tools/chromelibs/root/lib/x86_64-linux-gnu'
from playwright.sync_api import sync_playwright

SHOTS = '/workspace/trippick_repo/v47_shots'
B = 'https://trippick.pages.dev'
TRIP = '{"s":"osaka","n":"오사카","date":"2026-12-05","at":1700000000000}'
report, fails = [], []


def ok(c, m):
    if not c:
        fails.append(m)


PAGES = [('/', 'home'), ('/stays', 'stays'), ('/guides/guam-vs-saipan-comparison', 'guide_guam_vs_saipan'),
         ('/exchange', 'exchange'), ('/sos', 'sos')]

with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/workspace/.tools/cft/chrome-linux64/chrome', args=['--no-sandbox'])
    for w, h, tag in ((1280, 900, '1280'), (390, 844, '390')):
        ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=(w < 500), has_touch=(w < 500),
                             device_scale_factor=1, locale='ko-KR')
        for path, name in PAGES:
            pg = ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
            pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
            pg.goto(B + path, wait_until='load')
            pg.wait_for_timeout(1500)
            info = pg.evaluate("""() => ({
              title: document.title,
              h1: (document.querySelector('h1') || {}).innerText || '',
              sw: document.documentElement.scrollWidth, iw: window.innerWidth,
              font: getComputedStyle(document.body).fontFamily.split(',')[0],
              pretendard: document.fonts.check('700 16px "Pretendard Variable"'),
              broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).length,
              adsense: !!document.querySelector('script[src*="pagead2"]'),
              policyLinks: ['about','privacy','terms','contact'].filter(t => document.querySelector(`a[href$="${t}"],a[href$="${t}.html"]`)).length
            })""")
            ok(info['sw'] <= info['iw'] + 1, f'{tag} {path}: 가로 넘침 {info["sw"]}>{info["iw"]}')
            ok(not info['broken'], f'{tag} {path}: 깨진 이미지 {info["broken"]}')
            ok(info['pretendard'], f'{tag} {path}: Pretendard 미적용')
            ok(not errs, f'{tag} {path}: JS 오류 {errs[:2]}')
            pg.screenshot(path=f'{SHOTS}/{name}_{tag}.png')
            report.append({'page': name, 'viewport': tag, **info, 'errors': errs[:3]})
            pg.close()
        ctx.close()

    # 재방문(D-Day 저장) — 하단 D-Day 필
    for w, h, tag in ((1280, 900, '1280'), (390, 844, '390')):
        ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=(w < 500), has_touch=(w < 500),
                             device_scale_factor=1, locale='ko-KR')
        ctx.add_init_script("try{localStorage.setItem('trippick.trip.v1', %s);}catch(e){}" % json.dumps(TRIP))
        for path, name in (('/stays', 'dday_strip_stays'), ('/checklist', 'dday_checklist')):
            pg = ctx.new_page()
            pg.goto(B + path, wait_until='load')
            pg.wait_for_timeout(1500)
            info = pg.evaluate("""() => { const s = document.querySelector('.tp-strip');
              return {strip: !!s, stripRect: s ? [Math.round(s.getBoundingClientRect().x), Math.round(s.getBoundingClientRect().y),
                      Math.round(s.getBoundingClientRect().width), Math.round(s.getBoundingClientRect().height)] : null,
                      saved: !!document.querySelector('[data-tp-trip-saved]:not([hidden])'),
                      dday: (document.querySelector('[data-tp-trip-saved] .tp-day') || {}).textContent || null}; }""")
            pg.screenshot(path=f'{SHOTS}/{name}_{tag}.png')
            report.append({'page': name, 'viewport': tag, **info})
            pg.close()
        ctx.close()
    br.close()

json.dump({'report': report, 'fails': fails}, open(f'{SHOTS}/capture_report.json', 'w'), ensure_ascii=False, indent=1)
print('fails:', len(fails))
for f in fails[:10]:
    print('  ', f)
print('shots:', len([f for f in os.listdir(SHOTS) if f.endswith('.png')]))
