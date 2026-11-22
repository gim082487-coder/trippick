/* 트립픽 v42 — 통합 퀵서치(Ctrl/⌘+K) · 어디든지 파인더 · 찜 여행 견적서 · 나란히 비교
   - 모든 페이지: 헤더 돋보기 → /search_index.json(빌드 생성)에서 도시·가이드·숙소·투어·맛집 검색
   - 홈(#tpFinder): 시기·인원·예산 → 도시 3곳 추천(항공+숙소 2박+투어 1개)
   - 모든 페이지: 찜(localStorage) → 헤더 하트 → 숙소 N박·투어 N인 견적서(합산·복사)
   - #tpCompare 가 있는 페이지(홈·/stays): 최대 3개 비교 바 + 비교 모달(localStorage)
   값은 빌드가 데이터에서 만든 것만 씁니다(없는 속성을 지어내지 않음). */
(function () {
  'use strict';
  var D = document;
  var hasLS = (function () { try { localStorage.setItem('tp.v41.t', '1'); localStorage.removeItem('tp.v41.t'); return true; } catch (e) { return false; } })();

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function read(key, def) {
    if (!hasLS) return def;
    try { var v = JSON.parse(localStorage.getItem(key)); return v == null ? def : v; } catch (e) { return def; }
  }
  function write(key, val) { if (!hasLS) return; try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {} }
  function toast(msg) {
    var t = D.querySelector('[data-toast]');
    if (!t) { t = D.createElement('div'); t.className = 'toast'; t.setAttribute('data-toast', ''); t.setAttribute('role', 'status'); D.body.appendChild(t); }
    t.textContent = msg;
    t.classList.add('on');
    clearTimeout(t._tpT);
    t._tpT = setTimeout(function () { t.classList.remove('on'); }, 2200);
  }
  function won(n) { return Math.round(Number(n) || 0).toLocaleString('ko-KR'); }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  /* =========================================================
     1. 통합 퀵서치
     ========================================================= */
  var QS = { modal: null, sheet: null, input: null, list: null, tabs: null, foot: null, idx: null, loading: false, err: false, tab: 'all', cur: -1, shown: [] };

  function buildQS() {
    if (QS.modal) return;
    var d = D.createElement('div');
    d.className = 'qs-modal';
    d.id = 'qsModal';
    d.hidden = true;
    d.innerHTML = '' +
      '<div class="qs-sheet" role="dialog" aria-modal="true" aria-labelledby="qsTitle">' +
      '  <div class="qs-top">' +
      '    <svg class="qs-ic" aria-hidden="true"><use href="#i-search"/></svg>' +
      '    <h2 class="sr-only" id="qsTitle">트립픽 통합 검색</h2>' +
      '    <input class="qs-in" id="qsInput" type="search" autocomplete="off" spellcheck="false" placeholder="도시·가이드·숙소·투어·맛집을 한 번에 (예: 오사카, 온천, 유니버설)" aria-label="통합 검색어" />' +
      '    <button class="qs-esc" type="button" data-qs-close aria-label="검색 닫기">Esc</button>' +
      '  </div>' +
      '  <div class="qs-tabs" role="tablist" aria-label="종류 선택" id="qsTabs"></div>' +
      '  <div class="qs-list" id="qsList" role="listbox" aria-label="검색 결과"></div>' +
      '  <div class="qs-foot"><span id="qsFoot">도시·가이드·숙소·투어·맛집을 한 번에 찾습니다</span>' +
      '    <span class="qs-keys"><b>↑↓</b> 이동 · <b>Enter</b> 열기 · <b>Esc</b> 닫기</span></div>' +
      '</div>';
    D.body.appendChild(d);
    QS.modal = d;
    QS.sheet = d.querySelector('.qs-sheet');
    QS.input = d.querySelector('#qsInput');
    QS.list = d.querySelector('#qsList');
    QS.tabs = d.querySelector('#qsTabs');
    QS.foot = d.querySelector('#qsFoot');

    d.addEventListener('mousedown', function (e) { if (e.target === d) closeQS(); });
    d.addEventListener('click', function (e) {
      if (e.target.closest('[data-qs-close]')) { closeQS(); return; }
      var tab = e.target.closest('[data-qs-tab]');
      if (tab) { QS.tab = tab.getAttribute('data-qs-tab'); syncQSTabs(); renderQS(); QS.input.focus(); return; }
      var row = e.target.closest('[data-qs-go]');
      if (row) {
        var u = row.getAttribute('data-qs-go');
        closeQS();
        goResult(u);
      }
    });
    QS.input.addEventListener('input', function () { QS.cur = -1; renderQS(); });
    QS.input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!QS.shown.length) return;
        QS.cur = QS.cur < 0 ? 0 : clamp(QS.cur + (e.key === 'ArrowDown' ? 1 : -1), 0, QS.shown.length - 1);
        paintQS();
      } else if (e.key === 'Enter') {
        var pick = QS.cur >= 0 ? QS.shown[QS.cur] : QS.shown[0];
        if (pick) { e.preventDefault(); closeQS(); goResult(pick.u); }
      }
    });
  }

  function goResult(u) {
    // 같은 페이지 안의 해시(#t-…·#도시·#맛집카드)로 갈 때는 해시가 그대로면 hashchange 가
    // 오지 않으므로, 접힌 상세를 열고 직접 스크롤까지 해 준다.
    var same = u.charAt(0) === '/' && u.indexOf('/#') === 0 && location.pathname === '/';
    if (same) {
      var id = u.slice(2);
      if (location.hash === '#' + id) {
        var el = D.getElementById(id);
        if (el) {
          var det = el.closest('details'); if (det) det.open = true;
          setTimeout(function () {
            var hd = D.querySelector('.site-head');
            var top = el.getBoundingClientRect().top + window.scrollY - ((hd ? hd.offsetHeight : 0) + 10);
            window.scrollTo({ top: Math.max(top, 0) });
          }, 60);
        }
        return;
      }
    }
    location.href = u;
  }

  D.addEventListener('hashchange', closeQS);

  function loadQS() {
    if (QS.idx || QS.loading) return;
    QS.loading = true;
    QS.cur = -1;
    renderQS();
    fetch('/search_index.json', { credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (data) {
        QS.idx = data;
        QS.loading = false;
        buildQSTabs();
        renderQS();
      })
      .catch(function () {
        QS.loading = false;
        QS.err = true;
        renderQS();
      });
  }

  var KIND_LABEL = { city: '도시', guide: '가이드', stay: '숙소', tour: '투어', food: '맛집' };
  var KIND_ORDER = ['city', 'guide', 'stay', 'tour', 'food'];

  function buildQSTabs() {
    var items = QS.idx.items || [];
    var counts = {};
    items.forEach(function (it) { counts[it.k] = (counts[it.k] || 0) + 1; });
    var html = '<button class="qs-tab on" type="button" role="tab" data-qs-tab="all" aria-selected="true">전체 <i>' + items.length + '</i></button>';
    KIND_ORDER.forEach(function (k) {
      if (!counts[k]) return;
      html += '<button class="qs-tab" type="button" role="tab" data-qs-tab="' + k + '" aria-selected="false">' + KIND_LABEL[k] + ' <i>' + counts[k] + '</i></button>';
    });
    QS.tabs.innerHTML = html;
    QS.foot.textContent = KIND_ORDER.filter(function (k) { return counts[k]; })
      .map(function (k) { return KIND_LABEL[k] + ' ' + counts[k]; }).join(' · ') + ' — 한 번에 찾습니다';
  }

  function syncQSTabs() {
    Array.prototype.forEach.call(QS.tabs.querySelectorAll('[data-qs-tab]'), function (b) {
      var on = b.getAttribute('data-qs-tab') === QS.tab;
      b.classList.toggle('on', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
  }

  function qsScore(it, toks, q) {
    var t = (it.t || '').toLowerCase();
    var body = (it.q || '').toLowerCase();
    var s = 0;
    for (var i = 0; i < toks.length; i++) {
      var k = toks[i];
      if (t.indexOf(k) >= 0) s += 8;
      else if (body.indexOf(k) >= 0) s += 3;
      else return -1;
    }
    if (q && t.indexOf(q) === 0) s += 10;
    if (q && t === q) s += 6;
    return s;
  }

  function renderQS() {
    if (!QS.list) return;
    if (QS.err) {
      QS.list.innerHTML = '<div class="qs-empty"><b>검색 색인을 불러오지 못했어요.</b><p>잠시 뒤 다시 열거나 <a href="/guides/">가이드 전체</a>에서 직접 찾아보세요.</p></div>';
      return;
    }
    if (!QS.idx) {
      QS.list.innerHTML = '<div class="qs-empty"><b>' + (QS.loading ? '검색 색인을 불러오는 중…' : '검색을 준비하고 있어요') + '</b></div>';
      return;
    }
    var q = (QS.input.value || '').trim().toLowerCase();
    var toks = q.split(/\s+/).filter(Boolean);
    var items = QS.idx.items || [];
    var out = [];
    if (!toks.length && QS.tab === 'all') {
      // 빈 검색어·전체 탭: 종류별 대표 3개씩만 보여 준다(도시에 쏠리지 않게)
      var seen = {};
      items.forEach(function (it, i) {
        seen[it.k] = (seen[it.k] || 0) + 1;
        if (seen[it.k] <= 3) out.push({ it: it, s: 0, i: i });
      });
    } else {
      items.forEach(function (it, i) {
        if (QS.tab !== 'all' && it.k !== QS.tab) return;
        var s = toks.length ? qsScore(it, toks, q) : 1;
        if (s >= 0) out.push({ it: it, s: s, i: i });
      });
    }
    var kindRank = { city: 0, guide: 1, stay: 2, tour: 3, food: 4 };
    function krank(k) { return kindRank[k] == null ? 9 : kindRank[k]; }
    out.sort(function (a, b) {
      if (b.s !== a.s) return b.s - a.s;
      var k = krank(a.it.k) - krank(b.it.k);
      if (k) return k;
      return a.i - b.i;
    });
    var limit = toks.length ? 40 : (QS.tab === 'all' ? 14 : 60);
    out = out.slice(0, limit);
    QS.shown = out.map(function (x) { return x.it; });
    if (QS.cur >= QS.shown.length) QS.cur = QS.shown.length - 1;

    if (!out.length) {
      QS.list.innerHTML = '<div class="qs-empty"><b>‘' + esc(QS.input.value.trim()) + '’ 결과가 없습니다.</b>' +
        '<p>도시 이름(오사카·파리), 테마(온천·야경·쇼핑), 상품 이름 일부로 다시 찾아보세요.</p></div>';
      return;
    }
    var html = '';
    if (!toks.length) html += '<p class="qs-lead">' + (QS.tab === 'all' ? '바로 가기 — 종류별 대표' : KIND_LABEL[QS.tab] + ' 전체') + '</p>';
    out.forEach(function (x, n) {
      var it = x.it;
      var title = esc(it.t);
      if (toks.length) {
        toks.forEach(function (k) {
          try { title = title.replace(new RegExp('(' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); } catch (e) {}
        });
      }
      html += '<a class="qs-row' + (n === QS.cur ? ' on' : '') + '" role="option" aria-selected="' + (n === QS.cur) + '" href="' + esc(it.u) + '" data-qs-go="' + esc(it.u) + '">' +
        '<span class="qs-k k-' + esc(it.k) + '">' + (KIND_LABEL[it.k] || it.k) + '</span>' +
        '<span class="qs-b"><b class="qs-t">' + title + '</b><span class="qs-m">' + esc(it.m) + '</span></span>' +
        '<span class="qs-go">열기</span></a>';
    });
    QS.list.innerHTML = html;
  }

  function paintQS() {
    var rows = QS.list.querySelectorAll('.qs-row');
    Array.prototype.forEach.call(rows, function (r, n) {
      r.classList.toggle('on', n === QS.cur);
      r.setAttribute('aria-selected', String(n === QS.cur));
    });
    var on = rows[QS.cur];
    if (on && on.scrollIntoView) on.scrollIntoView({ block: 'nearest' });
  }

  var qsLastFocus = null;
  function openQS() {
    buildQS();
    loadQS();
    qsLastFocus = D.activeElement;
    QS.modal.hidden = false;
    D.body.classList.add('qs-on');
    QS.input.focus();
    if (QS.input.select) QS.input.select();
  }
  function closeQS() {
    if (!QS.modal || QS.modal.hidden) return;
    QS.modal.hidden = true;
    D.body.classList.remove('qs-on');
    if (qsLastFocus && qsLastFocus.focus) qsLastFocus.focus();
  }

  D.addEventListener('click', function (e) {
    if (e.target.closest('[data-qs-open]')) { e.preventDefault(); openQS(); }
  });
  D.addEventListener('keydown', function (e) {
    var k = (e.key || '').toLowerCase();
    if ((e.metaKey || e.ctrlKey) && k === 'k') { e.preventDefault(); if (QS.modal && !QS.modal.hidden) closeQS(); else openQS(); return; }
    if (k === 'escape' && QS.modal && !QS.modal.hidden) { closeQS(); }
  });

  /* =========================================================
     2. 찜
     ========================================================= */
  var WKEY = 'trippick.wish.v1';
  var wish = read(WKEY, []);
  if (!Array.isArray(wish)) wish = [];
  var WL = { modal: null, body: null, count: null };

  function wishIdx(k) { for (var i = 0; i < wish.length; i++) if (wish[i].k === k) return i; return -1; }

  function syncWish() {
    Array.prototype.forEach.call(D.querySelectorAll('[data-wish]'), function (b) {
      var on = wishIdx(b.getAttribute('data-wish')) >= 0;
      b.setAttribute('aria-pressed', String(on));
      b.title = on ? '찜 해제' : '찜하기 (이 브라우저에 저장)';
      b.setAttribute('aria-label', on ? '찜 해제' : '찜하기');
      var t = b.querySelector('.wish-t');
      if (t) t.textContent = on ? '찜함' : '찜';
    });
    Array.prototype.forEach.call(D.querySelectorAll('[data-wl-count]'), function (n) {
      n.textContent = wish.length > 99 ? '99+' : String(wish.length);
      n.hidden = wish.length === 0;
    });
    if (WL.modal && !WL.modal.hidden) renderWish();
  }

  function toggleWish(btn) {
    var key = btn.getAttribute('data-wish');
    if (!key) return;
    var i = wishIdx(key);
    if (i >= 0) {
      wish.splice(i, 1);
      toast('찜에서 뺐어요');
    } else {
      var d = {};
      try { d = JSON.parse(btn.getAttribute('data-wish-item') || '{}'); } catch (e) {}
      wish.push({
        k: key, n: d.n || '', u: d.u || '', i: d.i || '', p: d.p || '',
        pr: d.pr || 0, un: d.un || '', ct: d.ct || '', tu: d.tu || '',
        t: d.t || (key.indexOf('stay:') === 0 ? '숙소' : '투어'),
        ni: 2, px: 2, at: Date.now()
      });
      toast('찜했어요 · 헤더 ♥ 에서 견적을 계산할 수 있어요');
    }
    write(WKEY, wish.slice(-80));
    syncWish();
  }

  /* ---------- 찜 견적서: 1박·1인 단가와 수량 ---------- */
  function wNum(w) {
    var n = Number(w.pr);
    if (!n) {
      var m = String(w.p || '').match(/([\d,]{2,})\s*원/);
      n = m ? Number(m[1].replace(/,/g, '')) : 0;
    }
    return n;
  }
  function wUnit(w) {
    if (w.un === '1박' || w.un === '1인' || w.un === '1팀') return w.un;
    var p = String(w.p || '');
    if (p.indexOf('1팀') >= 0) return '1팀';
    if (p.indexOf('박') >= 0) return '1박';
    return '1인';
  }
  function wQty(w) {
    if (wUnit(w) === '1박') return clamp(Number(w.ni) || 2, 1, 14);
    if (wUnit(w) === '1팀') return 1;
    return clamp(Number(w.px) || 2, 1, 9);
  }
  function wCalc(w) {
    var price = wNum(w), qty = wQty(w);
    return { price: price, qty: qty, unit: wUnit(w), total: price * qty };
  }
  function wParty() {
    for (var i = 0; i < wish.length; i++) {
      if (wUnit(wish[i]) === '1인') return clamp(Number(wish[i].px) || 2, 1, 9);
    }
    return 2;
  }
  function wCta(u) {
    var s = String(u || '');
    if (s.indexOf('trip.com') >= 0) return '트립닷컴에서 예약';
    if (s.indexOf('naver.me') >= 0) return '네이버 여행에서 예약';
    if (s.indexOf('coupang.com') >= 0) return '쿠팡에서 보기';
    if (s.indexOf('klook.com') >= 0) return '클룩에서 예약';
    return '예약 페이지';
  }
  function wTotals() {
    var stays = 0, tours = 0;
    wish.forEach(function (w) {
      var c = wCalc(w);
      if (c.unit === '1박') stays += c.total; else tours += c.total;
    });
    return { stays: stays, tours: tours, total: stays + tours };
  }

  function qtyHtml(key, qty, unit) {
    return '<span class="wl-qty">' +
      '<button type="button" data-wl-step="' + esc(key) + '" data-delta="-1" aria-label="줄이기">−</button>' +
      '<b>' + qty + unit + '</b>' +
      '<button type="button" data-wl-step="' + esc(key) + '" data-delta="1" aria-label="늘리기">＋</button></span>';
  }

  function buildWL() {
    if (WL.modal) return;
    var d = D.createElement('div');
    d.className = 'cmp-modal';
    d.id = 'wlModal';
    d.hidden = true;
    d.innerHTML = '<div class="cmp-sheet wl-sheet" role="dialog" aria-modal="true" aria-labelledby="wlTitle">' +
      '<div class="cmp-head"><div><b id="wlTitle">내 여행 견적·바구니</b> <span class="hint">찜한 숙소·투어를 합쳐 계산합니다</span></div>' +
      '<span class="cmp-head-act"><button class="cmp-close" type="button" data-wl-close>닫기</button></span></div>' +
      '<div class="cmp-scroll wl-body" id="wlBody"></div></div>';
    D.body.appendChild(d);
    WL.modal = d;
    WL.body = d.querySelector('#wlBody');
  }

  function renderWish() {
    if (!WL.body) return;
    if (!wish.length) {
      WL.body.innerHTML = '<div class="qs-empty"><b>아직 찜한 항목이 없습니다.</b>' +
        '<p>숙소·투어 카드의 <b>♥</b> 를 누르면 여기에 모입니다. 숙소는 <a href="/stays">/stays</a>에서, 투어는 홈 <a href="/#regions">지역·투어</a>에서 골라 보세요.</p></div>';
      return;
    }
    var people = wParty();
    var rows = '';
    wish.slice().reverse().forEach(function (w) {
      var c = wCalc(w);
      var qty = c.unit === '1팀' ? '<span class="wl-qty"><b>1팀</b></span>' : qtyHtml(w.k, c.qty, c.unit === '1박' ? '박' : '인');
      rows += '<div class="wl-row">' +
        (w.i ? '<img src="' + esc(w.i) + '" alt="" width="64" height="46" loading="lazy" />' : '<span class="wl-ph">' + esc(w.t) + '</span>') +
        '<div class="wl-mid"><b>' + esc(w.n) + '</b>' +
        '<span class="wl-line">' + esc(w.ct && String(w.t || '').indexOf(w.ct) < 0 ? String(w.t || '') + ' · ' + w.ct : (w.t || '')) + ' · ' +
        (c.price ? won(c.price) + '원' + (c.unit === '1팀' ? ' (1팀 단가)' : ' / ' + c.unit) : '가격 확인') + '</span>' +
        '<span class="wl-line">' + qty + '</span></div>' +
        '<div class="wl-right"><span class="wl-sub' + (c.total ? '' : ' zero') + '">' + (c.total ? won(c.total) + '원' : '—') + '</span>' +
        (w.u ? '<a class="wl-cta" href="' + esc(w.u) + '" target="_blank" rel="noopener sponsored">' + esc(wCta(w.u)) + '</a>' : '') +
        (w.tu ? '<a class="wl-cta alt" href="' + esc(w.tu) + '" target="_blank" rel="noopener sponsored">트립닷컴 투어 목록</a>' : '') +
        '<button class="wl-del" type="button" data-wl-del="' + esc(w.k) + '">빼기</button></div></div>';
    });
    var T = wTotals();
    WL.body.innerHTML = rows +
      '<div class="wl-sum">' +
      '<div class="wl-sum-row"><span>숙소 소계</span><b>' + won(T.stays) + '원</b></div>' +
      '<div class="wl-sum-row"><span>투어 소계</span><b>' + won(T.tours) + '원</b></div>' +
      '<div class="wl-total"><span>예상 총액<em>' + people + '인 기준 · 1인 ' + won(Math.round(T.total / people)) + '원</em></span><b>' + won(T.total) + '원</b></div>' +
      '</div>' +
      '<div class="wl-acts"><button class="wl-btn primary" type="button" data-wl-copy>견적 요약 복사</button>' +
      '<button class="wl-btn" type="button" data-wl-clear>전체 비우기</button></div>' +
      '<p class="wl-note">숙소는 1박가 × 박수, 투어는 1인가 × 인원으로 계산했습니다. 세금·현장 추가금·식비는 빠져 있고, 저장은 이 브라우저(localStorage)에만 됩니다.</p>';
  }

  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  function quoteText() {
    var lines = [];
    var people = wParty();
    var d = new Date();
    var day = d.getFullYear() + '.' + pad2(d.getMonth() + 1) + '.' + pad2(d.getDate());
    wish.forEach(function (w) {
      var c = wCalc(w);
      var q = c.unit === '1박' ? c.qty + '박' : (c.unit === '1팀' ? '1팀' : c.qty + '인');
      lines.push('· ' + (c.unit === '1박' ? '숙소' : '투어') + ' | ' + w.n + ' — ' + won(c.price) + '원 × ' + q + ' = ' + won(c.total) + '원');
    });
    var T = wTotals();
    return '트립픽 여행 견적 (' + day + ')\n' + lines.join('\n') +
      '\n\n예상 총액 ' + won(T.total) + '원 · 1인 ' + won(Math.round(T.total / people)) + '원' +
      '\n※ 1박·1인 표시가 기준, 세금·현장 추가금·식비 제외' +
      '\n' + (location.origin || 'https://trippick.pages.dev');
  }
  function copyText(text) {
    function fallback() {
      try {
        var ta = D.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        D.body.appendChild(ta);
        ta.select();
        var ok = D.execCommand('copy');
        D.body.removeChild(ta);
        if (ok) { toast('견적 요약을 복사했어요 · 카톡·메모장에 붙여넣으세요'); return; }
      } catch (e) {}
      toast('복사가 막혔어요. 아래 견적을 길게 눌러 복사해 주세요');
      var box = D.createElement('textarea');
      box.value = text; box.className = 'wl-copybox'; box.rows = 6;
      WL.body.appendChild(box);
      box.focus(); box.select();
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        toast('견적 요약을 복사했어요 · 카톡·메모장에 붙여넣으세요');
      }, fallback);
    } else fallback();
  }

  var wlLastFocus = null;
  function openWL() {
    buildWL();
    wlLastFocus = D.activeElement;
    renderWish();
    WL.modal.hidden = false;
    D.body.classList.add('qs-on');
    var c = WL.modal.querySelector('[data-wl-close]');
    if (c) c.focus();
  }
  function closeWL() {
    if (!WL.modal || WL.modal.hidden) return;
    WL.modal.hidden = true;
    D.body.classList.remove('qs-on');
    if (wlLastFocus && wlLastFocus.focus) wlLastFocus.focus();
  }

  D.addEventListener('click', function (e) {
    if (e.target.closest('[data-wl-open]')) { e.preventDefault(); openWL(); return; }
    if (e.target.closest('[data-wl-close]')) { closeWL(); return; }
    var w = e.target.closest('[data-wish]');
    if (w) { e.preventDefault(); toggleWish(w); return; }
    var step = e.target.closest('[data-wl-step]');
    if (step) {
      var i = wishIdx(step.getAttribute('data-wl-step'));
      if (i < 0) return;
      var delta = Number(step.getAttribute('data-delta')) || 0;
      var it = wish[i];
      if (wUnit(it) === '1박') it.ni = clamp((Number(it.ni) || 2) + delta, 1, 14);
      else if (wUnit(it) === '1인') it.px = clamp((Number(it.px) || 2) + delta, 1, 9);
      write(WKEY, wish);
      renderWish();
      syncWish();
      return;
    }
    var del = e.target.closest('[data-wl-del]');
    if (del) {
      var j = wishIdx(del.getAttribute('data-wl-del'));
      if (j >= 0) { wish.splice(j, 1); write(WKEY, wish); syncWish(); renderWish(); toast('찜에서 뺐어요'); }
      return;
    }
    if (e.target.closest('[data-wl-copy]')) { copyText(quoteText()); return; }
    if (e.target.closest('[data-wl-clear]')) {
      if (!wish.length) return;
      wish.length = 0; write(WKEY, wish); syncWish(); renderWish();
      toast('찜을 모두 비웠어요');
      return;
    }
  });
  D.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && WL.modal && !WL.modal.hidden) closeWL();
  });
  syncWish();

  /* =========================================================
     3. 어디든지 1초 추천 파인더 (홈)
     ========================================================= */
  var FD_EL = D.getElementById('tpFinder');
  if (FD_EL) {
    var FD = null;
    try { FD = JSON.parse(FD_EL.textContent); } catch (e) { FD = null; }
    var fdList = D.getElementById('fdList');
    var fdNote = D.getElementById('fdNote');
    var FD_BUDGET = {
      b50: { min: 0, max: 500000, label: '50만원 이하' },
      b100: { min: 500000, max: 1000000, label: '50~100만원' },
      b200: { min: 1000000, max: 2000000, label: '100~200만원' },
      b200p: { min: 2000000, max: 0, label: '200만원 이상' }
    };
    var MONTH_SEASON = { 3: 'spring', 4: 'spring', 5: 'spring', 6: 'summer', 7: 'summer', 8: 'summer',
      9: 'autumn', 10: 'autumn', 11: 'autumn', 12: 'winter', 1: 'winter', 2: 'winter' };
    var fd = { season: MONTH_SEASON[new Date().getMonth() + 1] || 'any', people: 2, budget: 'b200' };

    function fdSeasonName(code) {
      var nm = { spring: '봄', summer: '여름', autumn: '가을', winter: '겨울', any: '상관없음' };
      return nm[code] || '상관없음';
    }
    function fdMan(n) { return won(Math.round(n / 10000) * 10000) + '원'; }
    function fdPickSeason(c) {
      if (fd.season !== 'any') return { code: fd.season, se: c.se[fd.season] };
      var best = null;
      ['spring', 'summer', 'autumn', 'winter'].forEach(function (k) {
        var se = c.se[k];
        if (!se) return;
        if (!best || se.score > best.se.score) best = { code: k, se: se };
      });
      return best;
    }
    function fdEst(c, se) {
      var band = c.fare[se.band] || c.fare.off;
      return band[0] * fd.people + Math.round(c.stay.p * 2) + c.tour.p * fd.people;
    }
    function fdRender() {
      if (!FD || !fdList) return;
      var b = FD_BUDGET[fd.budget] || FD_BUDGET.b200;
      var rows = [];
      (FD.cities || []).forEach(function (c) {
        var pick = fdPickSeason(c);
        if (!pick || !pick.se) return;
        var est = fdEst(c, pick.se);
        var cls = 0;
        if (est > b.max && b.max) cls = est > b.max ? 2 : 0;
        if (b.min && est < b.min) cls = 1;
        if (b.max && est <= b.max && est >= b.min) cls = 0;
        rows.push({ c: c, se: pick.se, code: pick.code, est: est, cls: cls });
      });
      rows.sort(function (x, y) {
        if (x.cls !== y.cls) return x.cls - y.cls;
        if (y.se.score !== x.se.score) return y.se.score - x.se.score;
        return x.est - y.est;
      });
      var top = rows.slice(0, 3);
      var over = 0;
      var html = '';
      top.forEach(function (r, i) {
        var c = r.c, se = r.se;
        var gapTxt = '';
        if (r.cls === 2) { over++; gapTxt = '예산 +' + Math.round((r.est - b.max) / 10000) + '만원'; }
        else if (r.cls === 1) gapTxt = '예산보다 ' + Math.round((b.min - r.est) / 10000) + '만원 낮음';
        else gapTxt = '예산 안';
        var why = [];
        if (se.themes && se.themes.length) why.push(se.themes.join('·'));
        why.push(fdSeasonName(r.code) + ' 평균 ' + se.temp + '도 · 비 ' + se.rain + '일');
        why.push('시즌 점수 ' + se.score);
        html += '<article class="fd-item">' +
          '<div class="fd-top"><span class="fd-rank">' + (i + 1) + '</span>' +
          '<div class="fd-name"><b>' + esc(c.n) + '</b><span>' + esc(c.country) + ' · ' + esc(gapTxt) + '</span></div>' +
          '<span class="fd-price' + (r.cls === 2 ? ' over' : '') + '">' + fdMan(r.est) + '<em>' + (fd.people > 1 ? fd.people + '인 총액 · 1인 ' + fdMan(r.est / fd.people) : '1인 총액') + '</em></span></div>' +
          '<p class="fd-why">' + esc(why.join(' · ')) + '</p>' +
          '<div class="fd-parts">' +
          '<a class="fd-part" href="' + esc(c.stay.u) + '" target="_blank" rel="noopener sponsored"><span>숙소 · 최저가</span><b>' + esc(c.stay.n) + '</b><em>1박 ' + won(c.stay.p) + '원 · ' + c.stay.sc + '점 · ' + esc(c.stay.z) + '</em></a>' +
          '<a class="fd-part" href="' + esc(c.tour.u) + '" target="_blank" rel="noopener sponsored"><span>투어 · 최저가</span><b>' + esc(c.tour.n) + '</b><em>1인 ' + won(c.tour.p) + '원 · ' + esc(c.tour.d) + '</em></a>' +
          '</div>' +
          '<div class="fd-acts">' +
          '<a class="fd-go primary" href="' + esc(c.stay.u) + '" target="_blank" rel="noopener sponsored">숙소 예약</a>' +
          '<a class="fd-go" href="' + esc(c.tour.u) + '" target="_blank" rel="noopener sponsored">투어 보기</a>' +
          '<a class="fd-go" href="' + esc(c.hub) + '">도시 페이지</a>' +
          '</div></article>';
      });
      fdList.innerHTML = html || '<p class="fd-note">조건에 맞는 도시를 찾지 못했습니다. 예산을 한 단계 올려 보세요.</p>';
      if (fdNote) {
        var msg = fdSeasonName(fd.season) + ' · ' + fd.people + '인 · ' + b.label + ' — ' + (FD.cities || []).length + '개 도시에서 3곳을 골랐습니다. ';
        msg += over ? '<span class="fd-warn">위에서 ' + over + '곳은 예산을 넘습니다(가까운 순).</span>' : '<span class="fd-good">세 곳 모두 예산 안입니다.</span>';
        fdNote.innerHTML = msg + ' 예상 총액은 항공 최저가 + 숙소 2박 + 대표 투어 1개이고, 세금·식비·현지 교통은 빠져 있습니다.';
      }
    }
    function fdSync() {
      Array.prototype.forEach.call(D.querySelectorAll('[data-fd-season]'), function (btn) {
        var on = btn.getAttribute('data-fd-season') === fd.season;
        btn.classList.toggle('on', on);
        btn.setAttribute('aria-pressed', String(on));
      });
      Array.prototype.forEach.call(D.querySelectorAll('[data-fd-people]'), function (btn) {
        var on = Number(btn.getAttribute('data-fd-people')) === fd.people;
        btn.classList.toggle('on', on);
        btn.setAttribute('aria-pressed', String(on));
      });
      Array.prototype.forEach.call(D.querySelectorAll('[data-fd-budget]'), function (btn) {
        var on = btn.getAttribute('data-fd-budget') === fd.budget;
        btn.classList.toggle('on', on);
        btn.setAttribute('aria-pressed', String(on));
      });
    }
    D.addEventListener('click', function (e) {
      var s1 = e.target.closest('[data-fd-season]');
      if (s1) { fd.season = s1.getAttribute('data-fd-season'); fdSync(); fdRender(); return; }
      var p1 = e.target.closest('[data-fd-people]');
      if (p1) { fd.people = Number(p1.getAttribute('data-fd-people')) || 2; fdSync(); fdRender(); return; }
      var b1 = e.target.closest('[data-fd-budget]');
      if (b1) { fd.budget = b1.getAttribute('data-fd-budget'); fdSync(); fdRender(); return; }
    });
    fdSync();
    fdRender();
  }

  /* =========================================================
     3. 나란히 비교 (홈 투어 · /stays 숙소)
     ========================================================= */
  var dataEl = D.getElementById('tpCompare');
  if (!dataEl) return;
  var bar = D.getElementById('cmpBar');
  var modal = D.getElementById('cmpModal');
  var list = D.getElementById('cbList');
  var countEl = D.getElementById('cbCount');
  var openBtn = D.getElementById('cbOpen');
  var clearBtn = D.getElementById('cbClear');
  var closeBtn = D.getElementById('cmpClose');
  var modalBody = D.getElementById('cmpBody');
  if (!bar || !modal || !list || !modalBody) return;

  var MAP = {};
  try { MAP = JSON.parse(dataEl.textContent) || {}; } catch (e) { return; }
  var SKIND = dataEl.getAttribute('data-kind') || 'tour';
  var MAX = parseInt(dataEl.getAttribute('data-max') || '3', 10) || 3;
  var CKEY = 'trippick.cmp.' + SKIND + '.v1';
  var picked = read(CKEY, []);
  if (!Array.isArray(picked)) picked = [];
  picked = picked.filter(function (k) { return !!MAP[k]; }).slice(0, MAX);
  var cmpLastFocus = null;

  function savePicked() { write(CKEY, picked); }

  function syncButtons() {
    Array.prototype.forEach.call(D.querySelectorAll('[data-cmp-add]'), function (b) {
      var on = picked.indexOf(b.getAttribute('data-cmp-add')) >= 0;
      b.setAttribute('aria-pressed', String(on));
      b.textContent = on ? '담김' : '비교';
      b.title = on ? '비교에서 빼기' : '이 상품을 비교 바구니에 담기';
    });
  }

  function renderBar() {
    list.innerHTML = picked.map(function (k) {
      var t = MAP[k];
      return '<div class="cb-item"><img src="' + esc(t.im) + '" alt="" width="26" height="26" loading="lazy" />' +
        '<span>' + esc((t.n || '').length > 26 ? t.n.slice(0, 25) + '…' : t.n) + '</span>' +
        '<button class="cb-x" type="button" data-cmp-del="' + esc(k) + '" aria-label="비교에서 빼기">✕</button></div>';
    }).join('');
    var compact = window.matchMedia && window.matchMedia('(max-width:620px)').matches;
    countEl.textContent = compact ? picked.length + '개 선택' : picked.length + ' / ' + MAX;
    openBtn.disabled = picked.length < 2;
    openBtn.textContent = picked.length >= 2 ? '나란히 비교 (' + picked.length + ')' : '나란히 비교';
    bar.classList.toggle('on', picked.length > 0);
    D.body.classList.toggle('cmp-on', picked.length > 0);
    syncButtons();
  }

  function toggleCmp(k) {
    if (!MAP[k]) return;
    var i = picked.indexOf(k);
    if (i >= 0) picked.splice(i, 1);
    else {
      if (picked.length >= MAX) { toast('비교는 최대 ' + MAX + '개까지 담을 수 있어요. 하나를 빼고 담아주세요.'); return; }
      picked.push(k);
      toast(SKIND === 'stay' ? '비교에 담았어요 · ' + picked.length + '/' + MAX : '비교에 담았어요 · ' + picked.length + '/' + MAX);
    }
    savePicked();
    renderBar();
    if (!modal.hidden) { if (picked.length < 2) closeCmp(); else renderCmp(); }
  }

  function badges(t) {
    if (!t.bd || !t.bd.length) return '';
    return '<span class="cmpt-badges">' + t.bd.map(function (b) {
      return '<span class="db db--' + esc(b[1] || 'm') + '">' + esc(b[0]) + '</span>';
    }).join('') + '</span>';
  }

  function tourRows() {
    var best = Math.min.apply(null, picked.map(function (k) { return MAP[k].real || MAP[k].p; }));
    return [
      ['1인 상품가', function (t) {
        return '<b>' + won(t.p) + '원</b>' + (t.was && t.was > t.p ? '<br><s class="cmpt-soft">' + won(t.was) + '원</s>' : '') +
          (t.ptm ? '<br><span class="cmpt-soft">1팀(1척) 단가</span>' : '');
      }],
      ['현장 추가금', function (t) {
        if (!t.ex) return '<span class="cmpt-soft">' + (t.exas ? '금액 표기 없음<br>' + esc(t.exas) : '없음') + '</span>';
        return '<b>' + won(t.ex) + '원</b><br><span class="cmpt-soft">' + esc(t.exb || '') + '</span>';
      }],
      ['실질 1인가', function (t) {
        var v = t.real || t.p;
        return '<span class="cmpt-real">' + won(v) + '원</span>' + (v === best ? '<span class="cmpt-best">최저</span>' : '');
      }],
      ['평점·리뷰', function (t) {
        if (!t.rt) return '<span class="cmpt-soft">' + esc(t.book || '판매 조건 기준') + '</span>';
        return '<b>' + esc(t.rt) + '</b> / 5' + (t.rv ? '<br><span class="cmpt-soft">리뷰 ' + won(t.rv) + '개</span>' : '');
      }],
      ['출발·소요', function (t) {
        return esc(t.de || '현지 집결') + '<br><span class="cmpt-soft">' + esc(t.du || '') + (t.gui ? ' · ' + esc(t.gui) : '') + '</span>';
      }],
      ['포함 내역', function (t) { return '<span class="cmpt-soft">' + esc(t.inc || '상세페이지 확인') + '</span>'; }],
      ['특징', function (t) { return badges(t) || '<span class="cmpt-soft">—</span>'; }],
      ['취소 규정', function (t) { return esc(t.ca || '판매처 확인') + (t.caf ? '<br><span class="cmpt-soft">' + esc(t.caf) + '</span>' : ''); }],
      ['예약', function (t) {
        return '<a class="cmpt-cta" href="' + esc(t.u) + '" target="_blank" rel="noopener sponsored">' + esc(t.cta || '예약 페이지') + '</a>';
      }]
    ];
  }

  function stayRows() {
    var best = Math.min.apply(null, picked.map(function (k) { return MAP[k].p; }));
    return [
      ['1박 가격', function (t) {
        return '<span class="cmpt-real">' + won(t.p) + '원</span>' + (t.p === best ? '<span class="cmpt-best">최저</span>' : '') +
          '<br><span class="cmpt-soft">' + esc(t.pl || '1박·2인·세금 포함') + '</span>';
      }],
      ['평점·리뷰', function (t) {
        return '<b>' + Number(t.sc).toFixed(1) + '</b> / 10<br><span class="cmpt-soft">리뷰 ' + won(t.rv) + '개</span>';
      }],
      ['세부 점수', function (t) {
        var s = t.ss || {};
        var parts = ['청결도', '위치', '서비스', '시설'].filter(function (n) { return s[n]; })
          .map(function (n) { return n + ' <b>' + esc(s[n]) + '</b>'; });
        return parts.length ? '<span class="cmpt-sub">' + parts.join(' · ') + '</span>' : '<span class="cmpt-soft">—</span>';
      }],
      ['위치', function (t) {
        return '<b>' + esc(t.zone || '') + '</b>' + (t.ac ? '<br><span class="cmpt-soft">' + esc(t.ac) + '</span>' : '');
      }],
      ['테마·포인트', function (t) {
        var tags = (t.th || []).concat(t.pt || []);
        return tags.length ? '<span class="cmpt-soft">' + tags.map(esc).join(' · ') + '</span>' : '<span class="cmpt-soft">—</span>';
      }],
      ['가격 기준', function (t) { return '<span class="cmpt-soft">' + esc(t.basis || '') + '</span>'; }],
      ['특징', function (t) { return badges(t) || '<span class="cmpt-soft">—</span>'; }],
      ['예약', function (t) {
        return '<a class="cmpt-cta" href="' + esc(t.u) + '" target="_blank" rel="noopener sponsored">' + esc(t.cta || '트립닷컴에서 예약') + '</a>';
      }]
    ];
  }

  function renderCmp() {
    if (!picked.length) return;
    var rows = SKIND === 'stay' ? stayRows() : tourRows();
    var head = '<tr><th scope="col">항목</th>' + picked.map(function (k) {
      var t = MAP[k];
      return '<th scope="col"><div class="cmpt-prod"><img src="' + esc(t.im) + '" alt="" loading="lazy" />' +
        '<b>' + esc(t.n) + '</b><span>' + esc(t.sub || '') + '</span>' +
        '<button class="cmpt-del" type="button" data-cmp-del="' + esc(k) + '">이 항목 빼기</button></div></th>';
    }).join('') + '</tr>';
    var body = rows.map(function (r) {
      return '<tr><th scope="row">' + r[0] + '</th>' + picked.map(function (k) { return '<td>' + r[1](MAP[k]) + '</td>'; }).join('') + '</tr>';
    }).join('');
    modalBody.innerHTML = '<table class="cmpt"><caption class="sr-only">선택한 ' + (SKIND === 'stay' ? '숙소 ' : '상품 ') + picked.length +
      '개 비교표</caption><thead>' + head + '</thead><tbody>' + body + '</tbody></table>';
  }

  function openCmp() {
    if (picked.length < 2) return;
    cmpLastFocus = D.activeElement;
    renderCmp();
    modal.hidden = false;
    D.body.style.overflow = 'hidden';
    if (closeBtn) closeBtn.focus();
  }
  function closeCmp() {
    modal.hidden = true;
    D.body.style.overflow = '';
    if (cmpLastFocus && cmpLastFocus.focus) cmpLastFocus.focus();
  }

  D.addEventListener('click', function (e) {
    var add = e.target.closest('[data-cmp-add]');
    if (add) { e.preventDefault(); toggleCmp(add.getAttribute('data-cmp-add')); return; }
    var del = e.target.closest('[data-cmp-del]');
    if (del) { toggleCmp(del.getAttribute('data-cmp-del')); return; }
    if (e.target.closest('#cbOpen')) { openCmp(); return; }
    if (e.target.closest('#cbClear')) {
      picked.length = 0; savePicked(); renderBar();
      if (!modal.hidden) closeCmp();
      toast('비교 바구니를 비웠어요');
      return;
    }
    if (e.target.closest('#cmpClearAll')) {
      picked.length = 0; savePicked(); closeCmp(); renderBar();
      toast('비교 바구니를 비웠어요');
      return;
    }
    if (e.target.closest('#cmpClose') || e.target === modal) closeCmp();
  });
  D.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modal.hidden) closeCmp();
  });

  renderBar();
})();
