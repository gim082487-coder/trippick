/* 트립픽 v35 — 제휴 클릭 추적(GA4 연동) + 「한 번에 예약·준비 묶음」 CTA
   ------------------------------------------------------------------
   content/v35.js → 빌드가 assets/tp-v35.js 로 복사합니다(캐시 버전 ?v=35).

   1) 제휴 클릭 추적
      · kr.trip.com(트립닷컴) · link.coupang.com · naver.me · klook.com 클릭을 문서 캡처 단계에서 잡아
        localStorage 'tp_clicks_v1' 에 페이지·섹션·제휴사·상품명·도시·trip_sub3·시각을 남깁니다
        (최근 40건 + 제휴사/페이지/일자 카운터). 서버로 보내는 값은 없습니다.
      · window.tpTrack.read() 로 조회, window.tpTrack.reset() 으로 초기화, window.tpTrack.record(url, label) 로
        다른 스크립트(계산기 등)가 직접 한 건을 남길 수 있습니다. v34 의 저장 키·구조는 그대로입니다.

   2) GA4 는 data/analytics.json 의 ga4.measurementId 한 곳으로 켭니다.
      · 그 값이 채워지면 build.py·build_pages.py 가 전 페이지 <head> 에 gtag.js 로더와 config 를 넣습니다.
      · 이 스크립트는 window.gtag 이 있으면 같은 클릭을 'affiliate_click' 이벤트로 한 번만 보냅니다
        (gtag 이 없고 GTM dataLayer 만 있으면 dataLayer 로 한 번만 보냅니다 — v34 는 둘 다에 보내
        GTM+GA4 를 같이 쓰는 사이트에서 이벤트가 두 번 잡혔습니다).
      · 이벤트 파라미터: partner · page_path · section · link_label · city · link_url

   3) 묶음 CTA: <div data-tp-bundle="planner|checklist|kit|exchange"> 자리에
      도시에 맞는 항공·숙소·투어·공항픽업·eSIM·필수품 바로가기를 그립니다.
*/
(function () {
  'use strict';

  /* ======================= 1. 제휴 클릭 추적 ======================= */
  var CLICK_KEY = 'tp_clicks_v1';
  var MAX_RECENT = 40;
  var PARTNERS = [
    ['kr.trip.com', 'trip'], ['trip.com', 'trip'],
    ['link.coupang.com', 'coupang'], ['coupang.com', 'coupang'],
    ['naver.me', 'naver'], ['brand.naver.com', 'naver'], ['m.travel.naver.com', 'naver'],
    ['shopping.naver.com', 'naver'], ['smartstore.naver.com', 'naver'],
    ['affiliate.klook.com', 'klook'], ['klook.com', 'klook']
  ];

  function partnerOf(host) {
    for (var i = 0; i < PARTNERS.length; i++) {
      var d = PARTNERS[i][0];
      if (host === d || host.slice(-(d.length + 1)) === '.' + d) return PARTNERS[i][1];
    }
    return '';
  }

  function loadClicks() {
    try {
      var v = JSON.parse(localStorage.getItem(CLICK_KEY) || 'null');
      if (v && typeof v === 'object') {
        v.byPartner = v.byPartner || {};
        v.byPage = v.byPage || {};
        v.byDay = v.byDay || {};
        v.recent = v.recent || [];
        v.total = v.total || 0;
        return v;
      }
    } catch (e) {}
    return { v: 1, total: 0, byPartner: {}, byPage: {}, byDay: {}, recent: [] };
  }

  function saveClicks(d) {
    try { localStorage.setItem(CLICK_KEY, JSON.stringify(d)); } catch (e) {}
  }

  function sectionOf(a) {
    var n = a;
    while (n && n !== document.body) {
      if (n.getAttribute && n.getAttribute('data-tp-bundle')) {
        return 'bundle:' + n.getAttribute('data-tp-bundle') +
          (n.getAttribute('data-tp-city') ? ':' + n.getAttribute('data-tp-city') : '');
      }
      if (n.id) return n.id;
      if (n.className && typeof n.className === 'string') {
        var m = /(?:^|\s)(gacts|gnext|sc-links|tc-acts|esim-cmp|adslot)(?:\s|$)/.exec(n.className);
        if (m) return m[1];
      }
      n = n.parentElement;
    }
    return '';
  }

  function dayKey(ts) {
    var d = new Date(ts);
    var m = d.getMonth() + 1, day = d.getDate();
    return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day;
  }

  function bundleCityOf(a) {
    var n = a.parentElement;
    while (n && n !== document.body) {
      if (n.getAttribute && n.getAttribute('data-tp-city')) return n.getAttribute('data-tp-city');
      n = n.parentElement;
    }
    return '';
  }

  /* GA4 / GTM — 둘 다 있으면 gtag 한 번만 쓴다(중복 집계 방지) */
  function sendEvent(rec) {
    var payload = {
      partner: rec.partner, page_path: rec.page, section: rec.section,
      link_label: rec.label, city: rec.city || '(none)', link_url: rec.href
    };
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'affiliate_click', payload);
        return 'ga4';
      }
      if (Array.isArray(window.dataLayer)) {
        window.dataLayer.push({
          event: 'affiliate_click', affiliate_partner: rec.partner, affiliate_page: rec.page,
          affiliate_section: rec.section, affiliate_label: rec.label,
          affiliate_city: rec.city || '', affiliate_url: rec.href
        });
        return 'gtm';
      }
    } catch (e) {}
    return '';
  }

  function recordClick(a, url) {
    var host = '';
    try { host = new URL(url, location.href).hostname.replace(/^www\./, ''); } catch (e) {}
    var partner = partnerOf(host);
    if (!partner) return null;
    var label = (a.getAttribute('data-tp-label') || a.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 70);
    var ts = Date.now();
    var rec = {
      page: location.pathname || '/',
      section: sectionOf(a),
      partner: partner,
      label: label,
      city: a.getAttribute('data-tp-city') || bundleCityOf(a),
      kind: a.getAttribute('data-tp-kind') || '',
      href: url.slice(0, 300),
      ts: ts
    };
    var q = /[?&]trip_sub3=([^&]+)/.exec(url);
    if (q) rec.sub3 = q[1];
    rec.sent = sendEvent(rec);

    var d = loadClicks();
    d.total += 1;
    d.byPartner[partner] = (d.byPartner[partner] || 0) + 1;
    d.byPage[rec.page] = (d.byPage[rec.page] || 0) + 1;
    var k = dayKey(ts);
    d.byDay[k] = (d.byDay[k] || 0) + 1;
    d.recent.unshift(rec);
    if (d.recent.length > MAX_RECENT) d.recent.length = MAX_RECENT;
    d.last = rec;
    saveClicks(d);
    return rec;
  }

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (!/^https?:/i.test(href)) return;
    recordClick(a, href);
  }, true);

  /* 다른 스크립트(계산기·비교표 등)가 직접 부를 수 있는 창구 */
  window.tpTrack = {
    record: function (url, label, kind) {
      return recordClick({ getAttribute: function () { return null; }, textContent: label || '' }, url);
    },
    read: loadClicks,
    reset: function () { try { localStorage.removeItem(CLICK_KEY); } catch (e) {} },
    /* GA4 설정이 켜졌는지 화면에서 바로 확인할 때 쓴다 */
    isGa4: function () { return typeof window.gtag === 'function'; }
  };

  /* ======================= 2. 묶음 CTA ======================= */
  var dataEl = document.getElementById('tpBundles');
  if (!dataEl) return;
  var BD;
  try { BD = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var CITIES = BD.cities || {};
  var ALIAS = BD.alias || {};
  var KIND = {
    flight: { k: '항공권', note: '최저가 검색' },
    hotel: { k: '숙소', note: '이 달 요금' },
    ticket: { k: '투어·패스', note: '입장권·액티비티' },
    transfer: { k: '공항픽업', note: '공항→숙소' },
    stays: { k: '찐숙소', note: '평점·1박 최저가' },
    esim: { k: 'eSIM·유심', note: '도착 전 설치' },
    goods: { k: '여행 필수품', note: '쿠팡' }
  };
  var MODE_KEYS = {
    planner: ['flight', 'stays', 'ticket', 'goods'],
    checklist: ['flight', 'hotel', 'esim', 'goods'],
    exchange: ['ticket', 'stays', 'transfer']
  };
  var CITY_KEY = 'trippick.bundle.city.v1';

  function cityOf(id) {
    if (!id) return null;
    var key = ALIAS[id] || id;
    var c = CITIES[key];
    if (!c) return null;
    return { id: key, name: c.name, items: c.items || {} };
  }

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function pick(city, keys) {
    var out = keys.filter(function (k) { return !!city.items[k]; });
    /* 링크가 없는 칸은 숙소·공항픽업·eSIM으로 채우되, '필수품'은 맨 뒤에 둔다 */
    var fill = ['hotel', 'transfer', 'esim', 'stays', 'flight', 'ticket'];
    var guard = 0;
    while (out.length < keys.length && guard < 8) {
      guard += 1;
      var next = '';
      for (var j = 0; j < fill.length; j++) {
        if (city.items[fill[j]] && out.indexOf(fill[j]) < 0) { next = fill[j]; break; }
      }
      if (!next) break;
      var at = out.indexOf('goods');
      if (at >= 0) out.splice(at, 0, next); else out.push(next);
    }
    return out.map(function (k) { return [k, city.items[k]]; });
  }

  function card(kind, it) {
    var meta = KIND[kind] || { k: kind, note: '' };
    var ext = it.external === false ? '' : ' target="_blank" rel="noopener sponsored"';
    return '<a class="tp-b-card tp-b-' + kind + '" href="' + esc(it.url) + '"' + ext +
      ' data-tp-kind="' + kind + '" data-tp-label="' + esc(meta.k + ' ' + it.label) + '">' +
      '<span class="tp-b-k">' + esc(meta.k) + '</span>' +
      '<b>' + esc(it.label) + '</b>' +
      '<span class="tp-b-n">' + esc(it.note || meta.note) + '</span>' +
      '<span class="tp-b-go">열기</span></a>';
  }

  function render(host, city, keys, sub) {
    if (!city) { host.hidden = true; host.innerHTML = ''; return; }
    var items = pick(city, keys);
    if (items.length < 2) { host.hidden = true; host.innerHTML = ''; return; }
    host.setAttribute('data-tp-city', city.id);
    var head = '<div class="tp-b-head"><b>' + esc(city.name) + ' 한 번에 예약·준비</b>' +
      '<span>' + esc(sub || '항공·숙소·투어·필수품을 이 순서로') + '</span></div>';
    var grid = '<div class="tp-b-grid">' + items.map(function (p) { return card(p[0], p[1]); }).join('') + '</div>';
    host.innerHTML = head + grid +
      '<p class="tp-b-note">제휴 링크입니다. 예약·구매가 이루어지면 트립픽이 수수료를 받지만 결제 금액은 같습니다. 가격은 2026.11.21 확인 기준입니다.</p>';
    host.hidden = false;
  }

  /* ---- 홈 예산 계산기: 고른 조합의 도시에 맞춰 다시 그린다 ---- */
  var plannerHost = document.querySelector('[data-tp-bundle="planner"]');
  var plannerBody = document.getElementById('plBody');
  window.tpBundle = {
    setCity: function (id, name) {
      var city = cityOf(id);
      if (!city && name) {
        /* 별칭에 없는 도시는 이름으로 다시 찾는다(예: '오사카·교토') */
        Object.keys(CITIES).some(function (key) {
          if (CITIES[key].name.indexOf(name.split('·')[0]) === 0) {
            city = { id: key, name: CITIES[key].name, items: CITIES[key].items };
            return true;
          }
          return false;
        });
      }
      if (plannerHost) render(plannerHost, city, MODE_KEYS.planner, '항공·숙소·투어·필수품을 이 순서로');
    }
  };

  /* 계산기가 이미 그려 둔 첫 조합부터 묶음을 채운다(계산기 스크립트가 먼저 실행된다) */
  if (plannerHost && plannerBody) {
    var syncPlanner = function () {
      var cid = plannerBody.getAttribute('data-tp-city');
      if (!cid) return;
      var c = cityOf(cid);
      if (c) render(plannerHost, c, MODE_KEYS.planner, '항공·숙소·투어·필수품을 이 순서로');
    };
    syncPlanner();
    if ('MutationObserver' in window) {
      new MutationObserver(syncPlanner).observe(plannerBody, { attributes: true, attributeFilter: ['data-tp-city'] });
    }
  }

  /* ---- /checklist: 도시 칩 + 4개 묶음 ---- */
  document.querySelectorAll('[data-tp-bundle="checklist"]').forEach(function (host) {
    var chips = (host.getAttribute('data-tp-chips') || 'osaka,tokyo,fukuoka,danang,bangkok,taipei,paris,london,rome,barcelona').split(',');
    var bar = document.createElement('div');
    bar.className = 'tp-b-chips';
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', '준비할 도시 선택');
    chips.forEach(function (cid) {
      var c = CITIES[cid];
      if (!c) return;
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'tp-b-chip';
      b.textContent = c.name.split('·')[0];
      b.setAttribute('data-tp-chip', cid);
      b.setAttribute('aria-pressed', 'false');
      bar.appendChild(b);
    });
    var body = document.createElement('div');
    body.className = 'tp-b-body';
    host.appendChild(bar);
    host.appendChild(body);
    var saved = '';
    try { saved = localStorage.getItem(CITY_KEY) || ''; } catch (e) {}
    var start = CITIES[saved] ? saved : 'osaka';
    function choose(cid, remember) {
      Array.prototype.forEach.call(bar.children, function (b) {
        var on = b.getAttribute('data-tp-chip') === cid;
        b.classList.toggle('on', on);
        b.setAttribute('aria-pressed', String(on));
      });
      render(body, cityOf(cid), MODE_KEYS.checklist, '항공·숙소·eSIM·필수품을 이 순서로');
      if (remember) { try { localStorage.setItem(CITY_KEY, cid); } catch (e) {} }
    }
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('[data-tp-chip]');
      if (b) choose(b.getAttribute('data-tp-chip'), true);
    });
    choose(start, false);
    host.hidden = false;
  });

  /* ---- /passes 등: 도시 고정 묶음 ---- */
  document.querySelectorAll('[data-tp-bundle="kit"]').forEach(function (host) {
    var keys = (host.getAttribute('data-tp-keys') || 'ticket,stays,transfer').split(',');
    render(host, cityOf(host.getAttribute('data-tp-city')), keys, '패스·찐숙소·공항픽업을 이어서');
  });

  /* ---- /exchange: 고른 통화의 나라 도시로 ---- */
  var fxHost = document.querySelector('[data-tp-bundle="exchange"]');
  if (fxHost) {
    var map = BD.currencyCity || {};
    // v45: /exchange?city=tokyo 로 들어오면 통화가 같아도(JPY) 도쿄 상품으로 묶는다
    var qCity = '';
    try { qCity = (new URLSearchParams(location.search).get('city') || '').toLowerCase(); } catch (e) {}
    function fxCity() {
      var sel = document.getElementById('fxCur');
      var code = sel ? sel.value : 'JPY';
      var cid = (qCity && cityOf(qCity)) ? qCity : (map[code] || 'osaka');
      var c = cityOf(cid);
      if (c) c.code = code;
      return c;
    }
    function drawFx() {
      var c = fxCity();
      if (!c) { fxHost.hidden = true; return; }
      render(fxHost, c, MODE_KEYS.exchange, (c.code || '') + ' 결제 전에 투어·찐숙소·공항픽업을 이어서');
    }
    var sel = document.getElementById('fxCur');
    if (sel) sel.addEventListener('change', drawFx);
    drawFx();
  }
})();
