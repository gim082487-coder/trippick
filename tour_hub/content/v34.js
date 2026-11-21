/* 트립픽 v34 — 제휴 클릭 추적 + 「한 번에 예약·준비 묶음」 CTA
   ------------------------------------------------------------------
   assets/tp-v34.js 로 복사됩니다(빌드가 자동 복사).
   1) 제휴 클릭 추적: kr.trip.com · link.coupang.com · naver.me · klook.com 링크 클릭을
      localStorage(tp_clicks_v1)에 페이지·섹션·제휴사·상품·시각으로 남긴다.
      window.gtag / dataLayer 가 붙으면 affiliate_click 이벤트를 자동으로 같이 보낸다.
   2) 묶음 CTA: <div data-tp-bundle="planner|checklist|kit|exchange"> 자리에
      도시에 맞는 항공·숙소·투어·공항픽업·eSIM·필수품 바로가기를 그린다.
   서버로 보내는 값은 없다. */
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
        v.recent = v.recent || [];
        v.total = v.total || 0;
        return v;
      }
    } catch (e) {}
    return { v: 1, total: 0, byPartner: {}, byPage: {}, recent: [] };
  }

  function saveClicks(d) {
    try { localStorage.setItem(CLICK_KEY, JSON.stringify(d)); } catch (e) {}
  }

  function sectionOf(a) {
    var n = a;
    while (n && n !== document.body) {
      if (n.getAttribute && n.getAttribute('data-tp-bundle')) {
        return 'bundle:' + n.getAttribute('data-tp-bundle') + (n.getAttribute('data-tp-city') ? ':' + n.getAttribute('data-tp-city') : '');
      }
      if (n.id) return n.id;
      n = n.parentElement;
    }
    return '';
  }

  function dayKey(ts) {
    var d = new Date(ts);
    var m = d.getMonth() + 1, day = d.getDate();
    return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day;
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
    var d = loadClicks();
    d.total += 1;
    d.byPartner[partner] = (d.byPartner[partner] || 0) + 1;
    d.byPage[rec.page] = (d.byPage[rec.page] || 0) + 1;
    d.byDay = d.byDay || {};
    var k = dayKey(ts);
    d.byDay[k] = (d.byDay[k] || 0) + 1;
    d.recent.unshift(rec);
    if (d.recent.length > MAX_RECENT) d.recent.length = MAX_RECENT;
    d.last = rec;
    saveClicks(d);
    /* GA4 / GTM 훅 — 스크립트가 붙어 있으면 같은 클릭을 이벤트로도 보낸다 */
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'affiliate_click', {
          partner: rec.partner, page_path: rec.page, section: rec.section,
          link_label: rec.label, city: rec.city || '(none)', link_url: rec.href
        });
      }
      if (Array.isArray(window.dataLayer)) {
        window.dataLayer.push({
          event: 'affiliate_click', affiliate_partner: rec.partner, affiliate_page: rec.page,
          affiliate_section: rec.section, affiliate_label: rec.label,
          affiliate_city: rec.city || '', affiliate_url: rec.href
        });
      }
    } catch (e) {}
    return rec;
  }

  function bundleCityOf(a) {
    var n = a.parentElement;
    while (n && n !== document.body) {
      if (n.getAttribute && n.getAttribute('data-tp-city')) return n.getAttribute('data-tp-city');
      n = n.parentElement;
    }
    return '';
  }

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (!/^https?:/i.test(href)) return;
    recordClick(a, href);
  }, true);

  /* 다른 스크립트(계산기 등)가 직접 부를 수 있는 창구 */
  window.tpTrack = {
    record: function (url, label, kind) {
      return recordClick({ getAttribute: function () { return null; }, textContent: label || '' }, url);
    },
    read: loadClicks,
    reset: function () { try { localStorage.removeItem(CLICK_KEY); } catch (e) {} }
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
          if (CITIES[key].name.indexOf(name.split('·')[0]) === 0) { city = { id: key, name: CITIES[key].name, items: CITIES[key].items }; return true; }
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
    function fxCity() {
      var sel = document.getElementById('fxCur');
      var code = sel ? sel.value : 'JPY';
      var cid = map[code] || 'osaka';
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
